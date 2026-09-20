"""Fight-end data contract: only final_fuzz + fresh_clues. Original Memory is rejected.

The live fight box is the only place the Memory lives. The thin helper must refuse
any payload that tries to send original Memory (or lookalike fields) at Reconstructing.
"""

from __future__ import annotations

from typing import Any

# Keys that would pull the original Memory (or a close cousin) into the helper.
REJECTED_MEMORY_KEYS = frozenset(
    {
        "original",
        "original_memory",
        "originalmemory",
        "original_memory_for_reference_only",
        "memory",
        "memory_text",
        "memorytext",
        "source_memory",
        "sourcememory",
        "private_memory",
        "privatememory",
    }
)

MAX_FUZZ_CHARS = 20_000
MAX_CLUES = 64
MAX_CLUE_WORDS = 500


class ContractError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _norm_key(key: Any) -> str:
    return str(key).replace("-", "_").replace(" ", "_").lower()


def _walk_keys(obj: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.append(_norm_key(k))
            keys.extend(_walk_keys(v))
    elif isinstance(obj, list):
        for item in obj:
            keys.extend(_walk_keys(item))
    return keys


def sanitize_fight_end(payload: Any) -> dict:
    """Return {final_fuzz, fresh_clues} or raise ContractError.

    Rejects original Memory fields at any nesting level. Does not keep unknown keys.
    """
    if not isinstance(payload, dict):
        raise ContractError("invalid_payload", "Fight-end data must be a JSON object.")

    for key in _walk_keys(payload):
        if key in REJECTED_MEMORY_KEYS:
            raise ContractError(
                "memory_rejected",
                "Original Memory must never enter the helper. Send only final_fuzz and fresh_clues.",
            )

    if "final_fuzz" not in payload:
        raise ContractError("missing_final_fuzz", "final_fuzz is required.")

    final_fuzz = payload.get("final_fuzz")
    if not isinstance(final_fuzz, str):
        raise ContractError("invalid_final_fuzz", "final_fuzz must be a string.")
    if len(final_fuzz) > MAX_FUZZ_CHARS:
        raise ContractError("final_fuzz_too_long", f"final_fuzz exceeds {MAX_FUZZ_CHARS} characters.")

    raw_clues = payload.get("fresh_clues", [])
    if raw_clues is None:
        raw_clues = []
    if not isinstance(raw_clues, list):
        raise ContractError("invalid_fresh_clues", "fresh_clues must be a list.")
    if len(raw_clues) > MAX_CLUES:
        raise ContractError("too_many_fresh_clues", f"fresh_clues exceeds {MAX_CLUES} items.")

    fresh_clues = []
    for item in raw_clues:
        if not isinstance(item, dict):
            raise ContractError("invalid_fresh_clue", "Each Fresh Clue must be an object.")
        words = item.get("words", "")
        spot = item.get("spot", "")
        fuzz_level = item.get("fuzz_level", 0)
        if not isinstance(words, str) or not isinstance(spot, str):
            raise ContractError("invalid_fresh_clue", "Fresh Clue words and spot must be strings.")
        if len(words) > MAX_CLUE_WORDS:
            raise ContractError("fresh_clue_too_long", "Fresh Clue words exceed the size limit.")
        try:
            level_num = float(fuzz_level)
        except (TypeError, ValueError) as exc:
            raise ContractError("invalid_fresh_clue", "Fresh Clue fuzz_level must be a number.") from exc
        fresh_clues.append({"spot": spot, "words": words, "fuzz_level": level_num})

    return {"final_fuzz": final_fuzz, "fresh_clues": fresh_clues}
