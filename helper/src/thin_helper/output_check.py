"""Rule-based checks on a parsed Reconstructed Memory before it is shown to the player.

Built from error analysis of 132 real Smart Robot traces in bench/ (GS-T6 and GS-T32).
Each rule is objective, so these are code checks, not an LLM judge.

Reject codes (the helper returns an empty Reconstructed Memory so the Box uses its local fallback):
  empty            nothing usable after parsing
  marker_leak      step markers or prompt section headers in the final text
  prompt_echo      the text repeats instruction or placeholder text from the locked prompt
  meta_commentary  the text talks about the game or the task instead of being a Memory

Info codes (kept, but reported):
  residual_fuzz    a large share of the text is still Fuzz stars
  from_step4       the final marker was missing and STEP 4 was used instead
  trimmed          trailing task chatter or a repeated paragraph was removed
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

REJECT_CODES = frozenset({"empty", "marker_leak", "prompt_echo", "meta_commentary"})

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "smart-robot-prompt.txt"

_MARKER_LEAK = re.compile(
    r"===|^\s*\[?\s*(?:step\s*[1-4]|final\s+fuzz|fresh\s+clues|reconstructed\s+memory)\s*\]?\s*:?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Glossary and task words from the locked prompt. A player's Memory does not talk about these.
_META = re.compile(
    r"\b(?:smart\s+robot|best\s+guess|quiet\s+rewrite|cleaning\s+steps?|fresh\s+clues?|feeling\s+lesson|"
    r"feeling\s+science|word\s+lesson|sand\s+drawing|endless\s+fight|exact\s+copy|creative\s+guessing|"
    r"perfect\s+help|fuzz\s+levels?|reconstruct(?:ed|ing|ion)?|the\s+player|"
    r"i\s+understand\s+the\s+instructions|here\s+is\s+(?:the|my)\s+(?:final|reconstructed))\b",
    re.IGNORECASE,
)

_WORD = re.compile(r"[a-z']+")
_SHINGLE = 6


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


@lru_cache(maxsize=1)
def _prompt_shingles() -> frozenset[tuple[str, ...]]:
    lines = [
        ln
        for ln in _PROMPT_PATH.read_text(encoding="utf-8").splitlines()
        if not ln.startswith("#") and "{" not in ln
    ]
    words = _words("\n".join(lines))
    return frozenset(tuple(words[i : i + _SHINGLE]) for i in range(len(words) - _SHINGLE + 1))


def residual_fuzz_ratio(text: str) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    return sum(1 for c in chars if c == "*") / len(chars)


def check_reconstruction(text: str) -> list[str]:
    """Return sorted failure codes for a parsed Reconstructed Memory. Empty list means clean."""
    if not isinstance(text, str):
        return ["empty"]
    codes: set[str] = set()
    stripped = text.strip()
    if not stripped or not re.search(r"[A-Za-z]", stripped):
        codes.add("empty")
        return sorted(codes)
    if _MARKER_LEAK.search(stripped):
        codes.add("marker_leak")
    words = _words(stripped)
    shingles = _prompt_shingles()
    if any(tuple(words[i : i + _SHINGLE]) in shingles for i in range(len(words) - _SHINGLE + 1)):
        codes.add("prompt_echo")
    if _META.search(stripped):
        codes.add("meta_commentary")
    if residual_fuzz_ratio(stripped) > 0.25:
        codes.add("residual_fuzz")
    return sorted(codes)


_TRAILER_START = re.compile(r"^\s*(?:note\b|notes\b|step\s*[1-4]\b|final\s+fuzz\b|final\s+fresh\s+clues\b|\(?changes?\b)", re.I)


def _is_chatter(paragraph: str) -> bool:
    words = _words(paragraph)
    shingles = _prompt_shingles()
    return bool(
        _META.search(paragraph)
        or _MARKER_LEAK.search(paragraph)
        or _TRAILER_START.match(paragraph)
        or any(tuple(words[i : i + _SHINGLE]) in shingles for i in range(len(words) - _SHINGLE + 1))
    )


def trim_trailing_chatter(text: str) -> str:
    """Drop trailing paragraphs that are task chatter or repeats, keep the Memory before them.

    Real traces often end with "This reconstruction is a best guess ..." or a repeat of the
    final text. The first paragraph is never dropped here; check_reconstruction judges it.
    """
    if not isinstance(text, str):
        return ""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    while len(paragraphs) > 1 and (_is_chatter(paragraphs[-1]) or paragraphs[-1] in paragraphs[:-1]):
        paragraphs.pop()
    return "\n\n".join(paragraphs)


def rejected(codes: list[str]) -> bool:
    return any(c in REJECT_CODES for c in codes)


def clean_reconstruction(parsed: dict) -> tuple[str, list[str]]:
    """Trim chatter from a parsed result and return (memory, flags). Callers blank it if rejected."""
    raw = parsed.get("reconstructed_memory", "") if isinstance(parsed, dict) else ""
    memory = trim_trailing_chatter(raw)
    flags = set(check_reconstruction(memory))
    if parsed.get("from_step4"):
        flags.add("from_step4")
    if memory != (raw or "").strip():
        flags.add("trimmed")
    return memory, sorted(flags)
