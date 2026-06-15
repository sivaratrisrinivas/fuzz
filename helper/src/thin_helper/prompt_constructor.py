"""
Prompt Constructor (deep module) - thin Python helper.

Per issue #5 (fetched ACs), issue #6 (wiring for one Smart Robot call + ephemeral), parent PRD #1, /tmp/handoff-fuzz-issue4-complete.md (and /tmp/handoff-fuzz-issues.md),
ADR-0001, CONTEXT.md (glossary is gospel), the locked prompt + samples validated in issue #3.

The Prompt Constructor is tested in isolation. It is responsible for always emitting the exact locked prompt text
(using the authoritative reference artifact from the dev validation slice) with the received final Fuzz and
Fresh Clues details injected. It guarantees the format is reliably parsable for the 4 Cleaning Steps results
plus final Reconstructed Memory. The built prompt is fed to exactly one Smart Robot call in the coordinator.

It uses the validated structure and wording:
- Training reminder + "You are the Smart Robot. You use Creative Guessing..."
- FINAL FUZZ + FRESH CLUES placeholders replaced with concrete data contract values
- Exact 4 Cleaning Steps instructions (verbatim)
- Requirements for Creative Guessing and visible Quiet Rewrite (not an Exact Copy)
- Request for structured output using the exact === STEP 1 === ... === RECONSTRUCTED MEMORY === markers

The Reconstruct Coordinator (the only entry point) uses this for the one-call path. This module has a small stable public interface
(build_prompt) hiding the template loading + clue formatting details.

All code, identifiers, comments, and tests use ONLY the exact locked glossary terms from CONTEXT.md:
Memory, Fuzz, Rewriting, Dissolving, Reconstructing, Clues, Fresh Clues, Perfect Help, Endless Fight,
4 Cleaning Steps, Quiet Rewrite, Best Guess, Creative Guessing, Smart Robot, Training, Real Experience,
Feeling Lesson, Sand Drawing, The Waves, Fuzz Levels, Word Lesson, Fixing Science, Watch and Fight Way,
Exact Copy. No avoided terms.

Privacy: this receives only final_fuzz + fresh_clues records from the data contract produced by the live fight box.
The original Memory never leaves the box and is never seen here.

References: https://github.com/sivaratrisrinivas/fuzz/issues/6 , https://github.com/sivaratrisrinivas/fuzz/issues/5 , https://github.com/sivaratrisrinivas/fuzz/issues/1 ,
https://github.com/sivaratrisrinivas/fuzz/issues/3 , helper/prompts/smart-robot-prompt.txt (locked),
helper/prompts/sample-fight-end-data.json , docs/adr/0001-... , CONTEXT.md , the client FightEndData shape.
"""

from pathlib import Path
from typing import Optional


class PromptConstructor:
    """Deep module with small public interface for building the exact locked Smart Robot prompt.

    Tested in isolation per issue #5 ACs. The Reconstruct Coordinator is the only entry point for callers.
    """

    def __init__(self, template_path: Optional[Path] = None):
        if template_path is None:
            # Default: prompts/ lives at helper/prompts/ when this file is at helper/src/thin_helper/prompt_constructor.py
            here = Path(__file__).resolve().parent  # thin_helper/ dir
            # here.parent = src/ ; here.parent.parent = helper/
            self.template_path: Path = here.parent.parent / "prompts" / "smart-robot-prompt.txt"
        else:
            self.template_path = template_path

        if not self.template_path.exists():
            # Defer failure to call time for testability in some layouts; existence is asserted in consuming tests.
            pass

    def build_prompt(self, final_fuzz: str, fresh_clues: list[dict]) -> str:
        """Build the full prompt by injecting the data contract into the locked template.

        - Loads the verbatim locked smart-robot-prompt.txt (Training reminder, 4 Cleaning Steps, markers, etc.)
        - Formats the fresh_clues list using the exact bullet style validated in issue #3 dev script
          (this guarantees the sample-reconstruction-01.md remains representative).
        - Replaces {FINAL_FUZZ} and {FRESH_CLUES} exactly.
        - Returns the complete prompt string ready for the (future) one Smart Robot call.
        """
        template = self.template_path.read_text(encoding="utf-8")

        # Format Fresh Clues exactly as in the dev validation script (issue #3) so the produced sample-reconstruction-01
        # remains a faithful representative of what the locked prompt + this constructor will yield at runtime.
        clues_lines = []
        for c in fresh_clues:
            clues_lines.append(
                f"- At Fuzz Level {c['fuzz_level']}, spot/position {c['spot']}, fixed the words: {c['words']}"
            )
        fresh_clues_text = "\n".join(clues_lines)

        full_prompt = (
            template
            .replace("{FINAL_FUZZ}", final_fuzz)
            .replace("{FRESH_CLUES}", fresh_clues_text)
        )
        return full_prompt
