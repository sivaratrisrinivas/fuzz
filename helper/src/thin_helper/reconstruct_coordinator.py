"""
Reconstruct Coordinator (deep module) - the ONLY entry point in the thin Python helper.

Per issue #5 (fetched ACs: "The Reconstruct Coordinator is the only entry point"), parent PRD #1,
/tmp/handoff-fuzz-issue4-complete.md (and /tmp/handoff-fuzz-issues.md), ADR-0001, CONTEXT.md (glossary gospel),
the locked prompt + 4 Cleaning Steps + parsing format validated in issue #3, and the data contract shape
produced by the client Fuzz Simulator in issue #4 (FightEndData: final_fuzz + list of Fresh Clues with spot/words/fuzz_level).

The coordinator receives the fight-end data contract from the live fight box at the end of the Endless Fight.
It uses the Prompt Constructor (tested in isolation) to build the precise locked prompt.
It provides parsing of the model's structured output (the 4 Cleaning Steps + RECONSTRUCTED MEMORY using the exact markers).
For this vertical slice the actual Smart Robot call is stubbed (using the representative validated sample-reconstruction-01.md
from #3 so the basic endpoint can return structured 4 steps + Reconstructed Memory per ACs). Real one-call + immediate
ephemeral forget of all data (Fuzz, Fresh Clues) happens in #6.

Thin coordinator nature: its only job is coordination, prompt construction using the locked artifact, parsing,
and (later) the single call. No persistence. Original Memory is never accepted, stored, or returned — only the
contract fields (final_fuzz + fresh_clues) ever enter here. This enforces the privacy boundary from ADR-0001 and PRD.

All code, identifiers, comments, and tests use ONLY the exact locked glossary terms from CONTEXT.md:
Memory, Fuzz, Rewriting, Dissolving, Reconstructing, Clues, Fresh Clues, Perfect Help, Endless Fight,
4 Cleaning Steps, Quiet Rewrite, Best Guess, Creative Guessing, Smart Robot, Training, Real Experience,
Feeling Lesson, Sand Drawing, The Waves, Fuzz Levels, Word Lesson, Fixing Science, Watch and Fight Way,
Exact Copy. No avoided terms.

References: https://github.com/sivaratrisrinivas/fuzz/issues/5 , https://github.com/sivaratrisrinivas/fuzz/issues/1 ,
https://github.com/sivaratrisrinivas/fuzz/issues/3 (locked artifacts), helper/prompts/smart-robot-prompt.txt ,
helper/prompts/sample-fight-end-data.json , helper/prompts/sample-reconstruction-01.md ,
docs/adr/0001-... , CONTEXT.md , box/src/fuzz-simulator.ts (FightEndData contract), the dev validation script.
"""

from pathlib import Path
from typing import Optional, Any

from thin_helper.prompt_constructor import PromptConstructor


class ReconstructCoordinator:
    """Deep module. The Reconstruct Coordinator is the only entry point for Reconstructing in the thin helper.

    Composes Prompt Constructor. Provides build_prompt (delegates) and parse_reconstruction for the locked
    marked 4-step format. reconstruct_from_fight_end supports the stubbed path for the basic endpoint in this slice.
    """

    def __init__(self, prompt_constructor: Optional[PromptConstructor] = None):
        self.prompt_constructor = prompt_constructor or PromptConstructor()

    def build_prompt(self, fight_end_data: dict) -> str:
        """Delegate to Prompt Constructor using the data contract shape {final_fuzz, fresh_clues: [...] }.

        This is the observable used by tests and (later) by the one-call wiring.
        """
        final_fuzz = fight_end_data.get("final_fuzz", "")
        fresh_clues = fight_end_data.get("fresh_clues", [])
        return self.prompt_constructor.build_prompt(final_fuzz, fresh_clues)

    def parse_reconstruction(self, raw_output: str) -> dict:
        """Parse the locked marked format produced by the Smart Robot (4 Cleaning Steps + final).

        Returns dict with keys: step1, step2, step3, step4, reconstructed_memory.
        The implementation is the production version of the minimal parser introduced (test-only) in #3.
        Robust against the exact markers in the validated sample-reconstruction-01.md.
        """
        import re
        result: dict[str, str] = {}
        markers = [
            ("step1", "=== STEP 1 ==="),
            ("step2", "=== STEP 2 ==="),
            ("step3", "=== STEP 3 ==="),
            ("step4", "=== STEP 4 ==="),
            ("reconstructed_memory", "=== RECONSTRUCTED MEMORY ==="),
        ]
        for key, marker in markers:
            # Capture content after this marker until the next === marker or end of text.
            pattern = re.escape(marker) + r"\s*(.*?)(?=\n===|\Z)"
            match = re.search(pattern, raw_output, re.DOTALL | re.IGNORECASE)
            if match:
                result[key] = match.group(1).strip()
            else:
                result[key] = ""
        return result

    def reconstruct_from_fight_end(self, fight_end_data: dict, model_output: Optional[str] = None) -> dict:
        """High-level entry for a reconstruction round (the coordinator's main public behavior).

        - Always exercises build_prompt (for fidelity and for the endpoint to surface a preview if desired).
        - If model_output is None (the common stub case for this slice), loads and uses the content of the
          validated sample-reconstruction-01.md so the caller (endpoint) can return structured 4 steps +
          Reconstructed Memory without a real Smart Robot call. This satisfies the AC "basic endpoint ... can return
          structured 4 Cleaning Steps + Reconstructed Memory (call may be stubbed for this slice)".
        - Real path (#6): build the prompt, make exactly one call with it, take the raw result, parse it,
          return the structure, then forget everything.
        - Privacy: fight_end_data must only contain final_fuzz + fresh_clues (no original Memory keys allowed).
        """
        # Exercise the prompt path (observable side-effect for tests / endpoint preview).
        prompt_built = self.build_prompt(fight_end_data)

        if model_output is None:
            # Stub using the authoritative validated sample from #3 (contains the progressive steps + Quiet Rewrite).
            # Resolve from the module file: .parent (dir) = thin_helper/, .parent = src/, .parent.parent of dir = helper/
            here = Path(__file__).resolve().parent
            sample_path = here.parent.parent / "prompts" / "sample-reconstruction-01.md"
            model_output = sample_path.read_text(encoding="utf-8")

        parsed = self.parse_reconstruction(model_output)

        # Return structure for the endpoint / callers. Include a preview so tests can assert prompt was exercised.
        return {
            "reconstructed_memory": parsed.get("reconstructed_memory", ""),
            "steps": {
                "step1": parsed.get("step1", ""),
                "step2": parsed.get("step2", ""),
                "step3": parsed.get("step3", ""),
                "step4": parsed.get("step4", ""),
            },
            "prompt_preview": (prompt_built[:400] + "...") if prompt_built else "",
            "note": "Stubbed using #3 sample-reconstruction-01 for this slice (issue #5 ACs). Real one Smart Robot call + immediate ephemeral forget of Fuzz + Fresh Clues in #6.",
        }
