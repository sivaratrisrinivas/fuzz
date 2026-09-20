"""GS-T32: Training data must never include locked GS-T6 eval or oak-tree."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TRAIN_JSONL = ROOT / "train" / "data" / "train.jsonl"
LOCKED = ROOT / "train" / "data" / "locked_eval.json"
SAMPLE = ROOT / "helper" / "prompts" / "sample-fight-end-data.json"
GS_T6 = ROOT / "bench" / "gs-t6-memories.json"


class TestTrainingHoldout(unittest.TestCase):
    def test_quiet_rewrite_is_not_an_exact_copy(self):
        sys.path.insert(0, str(ROOT / "train"))
        from quiet_rewrite import quiet_rewrite

        original = (
            "The first time I rode the night bus home from the city the windows were fogged."
        )
        rewritten = quiet_rewrite(original, salt="holdout-test")
        self.assertNotEqual(rewritten.strip(), original.strip())
        self.assertGreater(len(rewritten), 20)

    def test_train_jsonl_excludes_locked_eval_and_oak_tree_when_present(self):
        if not TRAIN_JSONL.exists():
            self.skipTest("train.jsonl not synthesized yet")
        banned = []
        gs = json.loads(GS_T6.read_text(encoding="utf-8"))
        banned.extend(m["text"] for m in gs["memories"])
        banned.append(
            json.loads(SAMPLE.read_text(encoding="utf-8"))["original_memory_for_reference_only"]
        )
        locked = json.loads(LOCKED.read_text(encoding="utf-8")) if LOCKED.exists() else {}
        excluded = set(locked.get("excluded_memory_ids") or [])
        self.assertIn("oak-tree", excluded)
        for mem in gs["memories"]:
            self.assertIn(mem["id"], excluded)

        with TRAIN_JSONL.open(encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                self.assertNotIn(row.get("memory_id"), excluded)
                self.assertIn("=== RECONSTRUCTED MEMORY ===", row["target"])
                self.assertNotEqual(row["quiet_rewrite"].strip(), row["memory"].strip())
                blob = json.dumps(row)
                for text in banned:
                    self.assertNotIn(text[:80], blob)


if __name__ == "__main__":
    unittest.main()
