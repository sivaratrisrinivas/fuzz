"""TDD vertical slices for issue #3: Validate the Smart Robot prompt and 4 Cleaning Steps on the Qwen model using dev tools only.

Per PRD #1, issue #3, /tmp/handoff-fuzz-issues.md, ADR-0001, CONTEXT.md (glossary gospel).
This slice ONLY produces the locked prompt + representative samples as reference artifacts (for later verbatim use by Prompt Constructor / Reconstruct Coordinator in #5).
No Reconstruct Coordinator implementation, no one-call wiring, no Fuzz Simulator, no changes to live fight box, no production endpoint usage.
All terminology: exact locked glossary only (Memory, Fuzz, Rewriting, Dissolving, Reconstructing, Clues, Fresh Clues, Perfect Help, Endless Fight, 4 Cleaning Steps, Quiet Rewrite, Best Guess, Creative Guessing, Smart Robot, Training, Real Experience, Feeling Lesson, Sand Drawing, The Waves, Fuzz Levels, Word Lesson, Fixing Science, Watch and Fight Way, Exact Copy). No avoided terms.

DEV-ONLY constraint: All prompt engineering, model runs, and sample capture used Hugging Face ZeroGPU + Pro tools/quotas exclusively. Never the dedicated nvidia-l4 production endpoint.

TDD: vertical, one behavior tracer at a time. This file holds the successive RED-then-GREEN tests.
"""

import unittest
from pathlib import Path


class TestSmartRobotPromptValidationArtifacts(unittest.TestCase):
    def setUp(self):
        # Resolve paths relative to this test file so it works from helper/ or repo root.
        self.helper_root = Path(__file__).resolve().parent.parent
        self.prompts_dir = self.helper_root / "prompts"
        self.prompt_path = self.prompts_dir / "smart-robot-prompt.txt"

    def test_locked_smart_robot_prompt_artifact_exists_with_exact_4_cleaning_steps_and_structure(self):
        # First TDD tracer for issue #3 (behavior 1 from approved plan).
        # RED: written expecting the artifact + exact content from the locked PRD structure.
        # Will fail until the file is created with the approved full prompt text (GREEN).
        # Uses public interface: file existence + content contains (observable, survives refactors of how prompt is stored).
        # Verifies: exact 4 steps verbatim, Training reminder, Fresh Clues format, Creative Guessing + Quiet Rewrite,
        # marked output sections for reliable parsing, dev-only note, glossary fidelity, references.

        self.assertTrue(
            self.prompt_path.exists(),
            f"Locked prompt artifact must exist at {self.prompt_path} (per issue #3 ACs and approved TDD plan)"
        )

        prompt_text = self.prompt_path.read_text(encoding="utf-8")

        # Verbatim 4 Cleaning Steps from PRD Implementation Decisions (must be exact).
        self.assertIn(
            "1. Start with the strongest Fresh Clues. Put back the clearest words and short phrases first, in their right spots.",
            prompt_text
        )
        self.assertIn(
            "2. Look at the Clues still left in the Fuzz. Fill in more letters and words around the ones you already fixed.",
            prompt_text
        )
        self.assertIn(
            "3. The Fuzz is still very messy in places. Use Training to guess the rest of the Memory. Make small changes where it feels right for a real Memory.",
            prompt_text
        )
        self.assertIn(
            "4. Do one last quiet pass over the whole thing. Clean up the flow and meaning. This is where most of the Quiet Rewrite happens — change a few words or phrases so it is not an Exact Copy.",
            prompt_text
        )

        # Structure per locked decisions + issue #3: Training reminder first, FINAL_FUZZ, FRESH_CLUES, then steps, Creative Guessing, Quiet Rewrite explicit.
        self.assertIn("You are the Smart Robot", prompt_text)
        self.assertIn("Creative Guessing powered by your Training", prompt_text)
        self.assertIn("FINAL FUZZ", prompt_text)
        self.assertIn("{FINAL_FUZZ}", prompt_text)
        self.assertIn("FRESH CLUES", prompt_text)
        self.assertIn("{FRESH_CLUES}", prompt_text)
        self.assertIn("Best Guess", prompt_text)
        self.assertIn("visible Quiet Rewrite", prompt_text)
        self.assertIn("not an Exact Copy", prompt_text)

        # Marked output format for reliable parsing of 4 steps + final Reconstructed Memory (issue #3 AC).
        self.assertIn("=== STEP 1 ===", prompt_text)
        self.assertIn("=== STEP 2 ===", prompt_text)
        self.assertIn("=== STEP 3 ===", prompt_text)
        self.assertIn("=== STEP 4 ===", prompt_text)
        self.assertIn("=== RECONSTRUCTED MEMORY ===", prompt_text)

        # Dev-only constraint and references (issue #3 ACs, no production endpoint ever for this).
        self.assertIn("DEV ONLY", prompt_text)
        self.assertIn("ZeroGPU / Pro", prompt_text)
        self.assertIn("nvidia-l4", prompt_text)
        self.assertIn("https://github.com/sivaratrisrinivas/fuzz/issues/1", prompt_text)
        self.assertIn("https://github.com/sivaratrisrinivas/fuzz/issues/3", prompt_text)
        self.assertIn("CONTEXT.md", prompt_text)

        # Glossary purity: must use only approved terms; spot check no avoided terms appear in the artifact.
        avoided = ["noise", "scrambled", "fixing steps", "rebuilding", "the magic trick"]
        for word in avoided:
            self.assertNotIn(word, prompt_text.lower(), f"Avoided term '{word}' must not appear; use only glossary from CONTEXT.md")

    def test_representative_sample_fight_end_data_artifact_exists_and_is_valid_for_validation_runs(self):
        # Cycle 2 TDD tracer (behavior 3): representative sample input for the prompt validation runs.
        # Uses the oak tree Memory from the current box placeholder UI as the reference original (for constructing realistic final_fuzz).
        # RED written first: expects the json + structure. Will pass after minimal json creation (GREEN).
        # Public observable: file + json content. No production data; purely for dev prompt validation (issue #3).
        # Must be realistic (final_fuzz damaged, >=2 Fresh Clues with spot/words/fuzz_level), use only glossary, contain references.

        sample_data_path = self.prompts_dir / "sample-fight-end-data.json"
        self.assertTrue(
            sample_data_path.exists(),
            f"Sample fight end data artifact must exist at {sample_data_path}"
        )

        import json
        data = json.loads(sample_data_path.read_text(encoding="utf-8"))

        self.assertIn("description", data)
        self.assertIn("final_fuzz", data)
        self.assertIn("fresh_clues", data)
        self.assertIsInstance(data["fresh_clues"], list)
        self.assertGreaterEqual(len(data["fresh_clues"]), 2, "Need at least 2 Fresh Clues per approved plan for representative Perfect Help demo")

        for clue in data["fresh_clues"]:
            self.assertIn("spot", clue)
            self.assertIn("words", clue)
            self.assertIn("fuzz_level", clue)
            self.assertIsInstance(clue["fuzz_level"], int)

        # Realism + glossary check (based on oak tree example in box UI).
        self.assertIn("oak tree", data.get("original_memory_for_reference_only", "").lower())
        self.assertIn("Fresh Clues", data.get("description", "") + str(data))
        self.assertIn("Fuzz", data.get("description", "") + str(data))

        # Dev only + references.
        self.assertIn("dev", data.get("description", "").lower() + str(data.get("references", [])))
        self.assertIn("PRD", str(data.get("references", [])))
        self.assertIn("issue #3", str(data.get("references", [])))

        # No avoided terms.
        full_str = str(data).lower()
        for word in ["noise", "scrambled", "fixing steps"]:
            self.assertNotIn(word, full_str)

    def test_representative_sample_reconstruction_output_artifact_exists_parsable_and_shows_educational_value(self):
        # Cycle 3 TDD (behaviors 4 + 5): captured sample output from validation run(s) on the model.
        # Must contain the exact markers, progressive steps (step1 uses Fresh Clues, later steps clean more),
        # visible Quiet Rewrite (final differs creatively from what a pure clue fill would be), Feeling Lesson note.
        # The minimal parser (introduced here for format testability) must succeed on it.
        # RED first; GREEN after creating the .md artifact with representative content from dev run (ZeroGPU/Pro only).

        sample_out_path = self.prompts_dir / "sample-reconstruction-01.md"
        self.assertTrue(sample_out_path.exists(), f"Sample reconstruction output must exist at {sample_out_path}")

        output_text = sample_out_path.read_text(encoding="utf-8")

        # Marked structure present and parsable (for Reconstruct Coordinator later).
        self.assertIn("=== STEP 1 ===", output_text)
        self.assertIn("=== STEP 2 ===", output_text)
        self.assertIn("=== STEP 3 ===", output_text)
        self.assertIn("=== STEP 4 ===", output_text)
        self.assertIn("=== RECONSTRUCTED MEMORY ===", output_text)

        # Educational / AC value: progressive, Fresh Clues impact, Quiet Rewrite (Creative Guessing, not Exact Copy), Sand Drawing / Feeling Lesson.
        self.assertIn("oak tree", output_text)  # from Fresh Clue used early
        self.assertIn("silver thread", output_text)
        self.assertIn("Quiet Rewrite", output_text)
        self.assertIn("Creative Guessing", output_text)
        self.assertIn("not an Exact Copy", output_text)
        self.assertIn("Feeling Lesson", output_text)
        self.assertIn("Sand Drawing", output_text)
        self.assertIn("Smart Robot", output_text)
        self.assertIn("Fresh Clues", output_text)
        self.assertIn("ZeroGPU", output_text)  # dev only evidence
        self.assertIn("nvidia-l4", output_text)

        # No avoided.
        low = output_text.lower()
        for bad in ["noise", "scrambled", "the magic trick", "fixing steps"]:
            self.assertNotIn(bad, low)

        # Parser exercise (public, minimal, only for verifying the chosen output format is reliable).
        parsed = parse_reconstruction_output(output_text)
        self.assertIn("step1", parsed)
        self.assertIn("step2", parsed)
        self.assertIn("step3", parsed)
        self.assertIn("step4", parsed)
        self.assertIn("reconstructed_memory", parsed)
        self.assertTrue(len(parsed["reconstructed_memory"]) > 50)
        self.assertIn("ancient", parsed["reconstructed_memory"].lower() or "gentle" in parsed["reconstructed_memory"].lower())  # evidence of Quiet Rewrite creative change in this sample


def parse_reconstruction_output(text: str) -> dict:
    """Minimal public parser for the locked marked format.
    Exercises only the observable output contract chosen for the Smart Robot.
    Real production parsing + coordinator logic belongs in the deep Reconstruct Coordinator (#5).
    This exists so the sample artifacts can be verified as parsable during this TDD slice.
    """
    import re
    result = {}
    # Split on the markers. Expect text after each.
    markers = [
        ("step1", "=== STEP 1 ==="),
        ("step2", "=== STEP 2 ==="),
        ("step3", "=== STEP 3 ==="),
        ("step4", "=== STEP 4 ==="),
        ("reconstructed_memory", "=== RECONSTRUCTED MEMORY ==="),
    ]
    for key, marker in markers:
        # Capture content until next marker or end.
        pattern = re.escape(marker) + r"\s*(.*?)(?=\n===|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            result[key] = match.group(1).strip()
        else:
            result[key] = ""
    return result


if __name__ == "__main__":
    unittest.main()
