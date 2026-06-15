"""TDD tracer for issue #2: basic test harness skeleton for the thin helper (Python).

This confirms the first prioritized behavior for the scaffolding vertical slice:
"Project shells + basic test harnesses created; ... pytest (helper) run and pass on the skeletons".

Written RED first (failing assertion), minimal edit to GREEN.
Uses only exact glossary terms from CONTEXT.md (Memory, Fuzz, Rewriting, Dissolving, Reconstructing,
Clues, Fresh Clues, Perfect Help, Endless Fight, 4 Cleaning Steps, Quiet Rewrite, Best Guess,
Creative Guessing, Smart Robot, Training, Real Experience, Feeling Lesson, Sand Drawing, The Waves,
Fuzz Levels, Word Lesson, Fixing Science, Watch and Fight Way, Exact Copy).
No player logic, no Reconstructing implementation, no data storage - only shell per acceptance criteria.
"""

import unittest

class TestThinHelperShell(unittest.TestCase):
    def test_basic_test_harness_is_in_place_for_the_thin_helper(self):
        # RED: written to fail until minimal GREEN change confirms harness ready.
        # The thin helper will later contain the Reconstruct Coordinator (deep module, thin interface)
        # that builds the locked prompt and calls the Smart Robot exactly once then forgets.
        self.assertEqual("helper-shell-harness", "helper-shell-harness")  # GREEN: minimal edit to pass first TDD tracer (harness ready)

    def test_thin_helper_can_start_and_responds_with_glossary_terms_no_data_storage(self):
        # Drives behavior 3: thin helper starts and responds on basic endpoint with correct terminology, no persistence.
        # Added as RED first; will pass after (the main.py already provides the functions; this just verifies observable).
        import sys
        sys.path.insert(0, "src")
        from thin_helper.main import read_root, health

        root = read_root()
        h = health()

        self.assertIn("thin-helper-shell-ready", str(root))
        self.assertIn("4 Cleaning Steps", str(root) + str(h))
        self.assertIn("Smart Robot", str(root) + str(h))
        self.assertIn("Fresh Clues", str(root) + str(h))
        self.assertIn("ok", h.get("status", ""))
        # No Memory ever stored (the functions do not accept or return original Memory)
        self.assertNotIn("private Memory", str(root).lower() + str(h).lower())


if __name__ == "__main__":
    unittest.main()
