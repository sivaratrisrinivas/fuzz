#!/usr/bin/env python3
"""Print a markdown before/after Reconstructing table from two GS-T6-style JSON files."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cell(row: dict, key: str) -> str:
    value = row.get(key)
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python3 bench/gs_t32_compare.py BEFORE.json AFTER.json", file=sys.stderr)
        return 2
    before = load(Path(sys.argv[1]))
    after = load(Path(sys.argv[2]))
    before_levels = {row["fuzz_level"]: row for row in before.get("by_fuzz_level", [])}
    after_levels = {row["fuzz_level"]: row for row in after.get("by_fuzz_level", [])}
    levels = sorted(set(before_levels) | set(after_levels))
    print("| Fuzz level | Word F1 before | Word F1 after | Edit before | Edit after | Failures before | Failures after |")
    print("| ---------- | -------------- | ------------- | ----------- | ---------- | --------------- | -------------- |")
    for level in levels:
        b = before_levels.get(level, {})
        a = after_levels.get(level, {})
        n_b = b.get("n", 0)
        n_a = a.get("n", 0)
        print(
            f"| {level:.1f} | {cell(b, 'mean_word_f1')} | {cell(a, 'mean_word_f1')} | "
            f"{cell(b, 'mean_edit_similarity')} | {cell(a, 'mean_edit_similarity')} | "
            f"{b.get('n_failed', 0)}/{n_b} | {a.get('n_failed', 0)}/{n_a} |"
        )
    print()
    print(
        f"Before: model={before.get('model')} adapter={before.get('adapter')} "
        f"source={before.get('model_source')} chat={before.get('chat')}"
    )
    print(
        f"After:  model={after.get('model')} adapter={after.get('adapter')} "
        f"source={after.get('model_source')} chat={after.get('chat')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
