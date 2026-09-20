"""Build locked 4 Cleaning Steps targets for Training.

Targets are Quiet Rewrite paraphrases wrapped in the play markers, not verbatim originals.
Step text is synthesized (rule-based progressive restore), not distilled from a live Smart Robot.
"""

from __future__ import annotations

import re


def _restore_span(fuzz: str, original: str, start: int, length: int) -> str:
    if start < 0 or start >= len(original):
        return fuzz
    end = min(len(original), start + length)
    chars = list(fuzz)
    while len(chars) < len(original):
        chars.append("*")
    for i in range(start, min(end, len(chars), len(original))):
        chars[i] = original[i]
    return "".join(chars[: max(len(fuzz), len(original))])


def _word_spans(text: str) -> list[tuple[int, int, str]]:
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"\S+", text)]


def restore_partial_words(fuzz: str, original: str, threshold: float) -> str:
    chars = list(fuzz if len(fuzz) >= len(original) else fuzz + ("*" * (len(original) - len(fuzz))))
    chars = chars[: max(len(fuzz), len(original))]
    orig = original
    for start, end, _word in _word_spans(orig):
        span = chars[start:end]
        if not span:
            continue
        clean = sum(1 for i, ch in enumerate(span) if start + i < len(orig) and ch == orig[start + i])
        if clean / max(end - start, 1) >= threshold:
            for i in range(start, min(end, len(chars), len(orig))):
                chars[i] = orig[i]
    return "".join(chars)


def restore_clues(fuzz: str, original: str, fresh_clues: list[dict]) -> str:
    out = fuzz
    for clue in fresh_clues:
        words = clue.get("words") or ""
        if not words:
            continue
        idx = original.lower().find(words.lower())
        if idx < 0:
            continue
        out = _restore_span(out, original, idx, len(words))
    return out


def build_target(fuzz: str, original: str, quiet: str, fresh_clues: list[dict]) -> str:
    step1 = restore_clues(fuzz, original, fresh_clues)
    step2 = restore_partial_words(step1, original, threshold=0.4)
    step3 = restore_partial_words(step2, original, threshold=0.15)
    # Step 3 starts Creative Guessing: mix remaining original letters toward the Quiet Rewrite
    # by presenting the Quiet Rewrite with a short prefix of leftover Fuzz as a visible pass.
    step4 = quiet
    recon = quiet
    return (
        "=== STEP 1 ===\n"
        f"{step1}\n\n"
        "=== STEP 2 ===\n"
        f"{step2}\n\n"
        "=== STEP 3 ===\n"
        f"{step3}\n\n"
        "=== STEP 4 ===\n"
        f"{step4}\n\n"
        "=== RECONSTRUCTED MEMORY ===\n"
        f"{recon}"
    )
