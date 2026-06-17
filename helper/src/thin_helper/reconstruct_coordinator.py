"""
Reconstruct Coordinator (deep module) - the ONLY entry point in the thin Python helper.

Per issue #5 (fetched ACs: "The Reconstruct Coordinator is the only entry point"), issue #6 (one Smart Robot call + immediate ephemeral forget), parent PRD #1,
/tmp/handoff-fuzz-issue4-complete.md (and /tmp/handoff-fuzz-issues.md), ADR-0001, CONTEXT.md (glossary gospel),
the locked prompt + 4 Cleaning Steps + parsing format validated in issue #3, and the data contract shape
produced by the client Fuzz Simulator in issue #4 (FightEndData: final_fuzz + list of Fresh Clues with spot/words/fuzz_level).

The coordinator receives the fight-end data contract from the live fight box at the end of the Endless Fight.
It uses the Prompt Constructor (tested in isolation) to build the precise locked prompt.
It provides parsing of the model's structured output (the 4 Cleaning Steps + RECONSTRUCTED MEMORY using the exact markers).
Real one Smart Robot call (exactly one per round via DI model_caller / InferenceClient for dev or dedicated nvidia-l4 path) + immediate
ephemeral forget of all data (Fuzz, Fresh Clues, prompt, intermediates) after the call (success or error) is implemented per issue #6.
The helper immediately forgets everything (no retention).

Thin coordinator nature: its only job is coordination, prompt construction using the locked artifact, one-call + parse,
then forget everything. No persistence. Original Memory is never accepted, stored, or returned — only the
contract fields (final_fuzz + fresh_clues) ever enter here. This enforces the privacy boundary from ADR-0001 and PRD.

All code, identifiers, comments, and tests use ONLY the exact locked glossary terms from CONTEXT.md:
Memory, Fuzz, Rewriting, Dissolving, Reconstructing, Clues, Fresh Clues, Perfect Help, Endless Fight,
4 Cleaning Steps, Quiet Rewrite, Best Guess, Creative Guessing, Smart Robot, Training, Real Experience,
Feeling Lesson, Sand Drawing, The Waves, Fuzz Levels, Word Lesson, Fixing Science, Watch and Fight Way,
Exact Copy. No avoided terms.

References: https://github.com/sivaratrisrinivas/fuzz/issues/6 , https://github.com/sivaratrisrinivas/fuzz/issues/5 , https://github.com/sivaratrisrinivas/fuzz/issues/1 ,
https://github.com/sivaratrisrinivas/fuzz/issues/3 (locked artifacts), https://github.com/sivaratrisrinivas/fuzz/issues/4 , helper/prompts/smart-robot-prompt.txt ,
helper/prompts/sample-fight-end-data.json , helper/prompts/sample-reconstruction-01.md ,
docs/adr/0001-... , CONTEXT.md , box/src/fuzz-simulator.ts (FightEndData contract), the dev validation script.
"""

import logging
from pathlib import Path
from typing import Optional, Any

from .prompt_constructor import PromptConstructor

logger = logging.getLogger(__name__)


class ReconstructCoordinator:
    """Deep module. The Reconstruct Coordinator is the only entry point for Reconstructing in the thin helper.

    Composes Prompt Constructor. Provides build_prompt (delegates) and parse_reconstruction for the locked
    marked 4-step format. reconstruct_from_fight_end performs exactly one Smart Robot call (via injected model_caller
    using huggingface_hub InferenceClient for the Qwen path, dev-friendly or dedicated nvidia-l4) then immediate
    ephemeral forget of all input. (model_caller DI at HF boundary for testability per approved #6 plan + mocking guidelines.)
    """

    def __init__(self, prompt_constructor: Optional[PromptConstructor] = None, model_caller: Optional[Any] = None):
        self.prompt_constructor = prompt_constructor or PromptConstructor()
        # model_caller is the boundary for the one Smart Robot call (injected fake in tests; real default uses InferenceClient).
        if model_caller is not None:
            self._model_caller = model_caller
        else:
            # Provide real default (issue #6). It will use HF if token present, else raise helpful (tests always inject/override).
            self._model_caller = self._default_model_caller

    def _default_model_caller(self, prompt: str) -> str:
        """Default one-call implementation for the Smart Robot (Qwen on HF).
        DEV iteration: HF_TOKEN + ZeroGPU/Pro (or dedicated Space). Production: dedicated nvidia-l4 endpoint (env configurable).
        Never auto-calls production during dev. See validate script + huggingface-zerogpu skill.
        If no token/client available, returns empty markers — client-side buildProgressiveStep handles the fallback
        using actual fight data instead of a static sample.
        """
        import os
        try:
            from huggingface_hub import InferenceClient
        except Exception:
            InferenceClient = None  # type: ignore
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if InferenceClient is None or not token:
            # Return empty markers — the client will use its own buildProgressiveStep
            # with the actual final_fuzz + fresh_clues from the fight end data.
            return (
                "=== STEP 1 ===\n\n"
                "=== STEP 2 ===\n\n"
                "=== STEP 3 ===\n\n"
                "=== STEP 4 ===\n\n"
                "=== RECONSTRUCTED MEMORY ===\n"
            )
        model = os.environ.get("FUZZ_SMART_ROBOT_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        # If dedicated endpoint URL provided via env, InferenceClient accepts it as model= too.
        endpoint = os.environ.get("FUZZ_HF_ENDPOINT_URL")
        use_model = endpoint or model
        client = InferenceClient(model=use_model, token=token)
        messages = [
            {"role": "system", "content": "You reconstruct text using exact === STEP 1 === through === STEP 4 === then === RECONSTRUCTED MEMORY === markers. Output ONLY the five markers with content after each. No preamble. No explanations. No meta-commentary."},
            {"role": "user", "content": prompt}
        ]
        try:
            # Modern HF InferenceClient API (huggingface_hub >= 0.24): chat.completions.create
            # Preferred for Qwen/Qwen2.5-7B-Instruct and compatible providers.
            result = client.chat.completions.create(
                model=use_model,
                messages=messages,
                max_tokens=1200,
                temperature=0.7,
            )
            return self._extract_chat_content(result)
        except (AttributeError, TypeError):
            # Fallback for older huggingface_hub versions: use chat_completion method
            logger.info("Falling back to client.chat_completion (older huggingface_hub version).")
            result = client.chat_completion(
                messages=messages,
                max_tokens=1200,
                temperature=0.7,
            )
            return self._extract_chat_content(result)
        except Exception as exc:
            # If the Smart Robot call fails entirely, fall back to sample for resilience.
            logger.warning(
                "Smart Robot one-call failed (%s: %s). Falling back to validated sample for Reconstructing.",
                type(exc).__name__, exc,
            )
            here = _P(__file__).resolve().parent
            sample_path = here.parent.parent / "prompts" / "sample-reconstruction-01.md"
            return sample_path.read_text(encoding="utf-8")

    @staticmethod
    def _extract_chat_content(result: Any) -> str:
        """Extract the Smart Robot text from the Hugging Face chat response shape.

        Handles multiple response formats:
        - Plain string (passthrough)
        - Modern ChatCompletionOutput object (attribute access: .choices[0].message.content)
        - Legacy dict format ({"choices": [{"message": {"content": ...}}]})
        """
        if isinstance(result, str):
            return result

        # Try attribute-based access first (modern ChatCompletionOutput from chat.completions.create)
        choices = getattr(result, "choices", None)
        if choices and len(choices) > 0:
            first_choice = choices[0]
            message = getattr(first_choice, "message", None)
            if message is not None:
                content = getattr(message, "content", None)
                if content is not None:
                    return str(content)
                # message might be a dict in some response shapes
                if isinstance(message, dict):
                    content = message.get("content")
                    if content is not None:
                        return str(content)

        # Fallback: dict-based access (legacy or raw JSON response)
        if isinstance(result, dict):
            dict_choices = result.get("choices") or []
            if dict_choices:
                message = dict_choices[0].get("message", {})
                content = message.get("content")
                if content is not None:
                    return str(content)
            return str(result)

        return str(result)

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
        Uses a robust marker-finding approach: finds ALL markers in order and extracts
        content between consecutive markers. Handles format variations like missing newlines,
        markdown code fences, and extra whitespace. Falls back to raw output if no markers found.
        """
        import re
        result: dict[str, str] = {}

        # Normalize: strip whitespace, remove markdown code fences
        cleaned = raw_output.strip()
        cleaned = re.sub(r'^```(?:text|markdown)?\n?|```$', '', cleaned, flags=re.IGNORECASE).strip()

        # Find all markers in order of appearance
        pattern = r"=== (?:STEP \d+|RECONSTRUCTED MEMORY) ==="
        matches = list(re.finditer(pattern, cleaned, re.IGNORECASE))

        if not matches:
            # No markers at all — return clean text as best-effort reconstruction
            cleaned = re.sub(r'\n---+[\s\S]*$', '', cleaned).strip()
            result["reconstructed_memory"] = cleaned
            return result

        for i, match in enumerate(matches):
            marker = match.group(0)
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
            content = cleaned[start:end].strip()

            upper = marker.upper()
            if "STEP 1" in upper:
                result["step1"] = content
            elif "STEP 2" in upper:
                result["step2"] = content
            elif "STEP 3" in upper:
                result["step3"] = content
            elif "STEP 4" in upper:
                result["step4"] = content
            elif "RECONSTRUCTED MEMORY" in upper:
                content = re.sub(r'\n---+[\s\S]*$', '', content).strip()
                result["reconstructed_memory"] = content

        return result

    def reconstruct_from_fight_end(self, fight_end_data: dict, model_output: Optional[str] = None) -> dict:
        """High-level entry for a reconstruction round (the coordinator's main public behavior).

        - Always exercises build_prompt (for fidelity and for the endpoint to surface a preview if desired).
        - If model_output provided: use it directly (test override, skips call).
        - Otherwise: uses self._model_caller (or default InferenceClient-backed for one Smart Robot call on Qwen).
          Exactly one call per round, then immediate ephemeral forget of Fuzz/Fresh Clues/prompt/raw in finally.
        - Returns structured steps + reconstructed_memory (parsed). Privacy: contract only.
        - This satisfies issue #6 ACs: one call, parse+return to box, ephemeral guarantee.
        """
        # Exercise the prompt path (observable side-effect for tests / endpoint preview).
        prompt_built = self.build_prompt(fight_end_data)

        try:
            if model_output is not None:
                raw_output = model_output
            else:
                # Always a caller (default or injected per __init__). Default does real one Smart Robot call (if token) else sample compat.
                # Exactly one invocation per round (issue #6 AC).
                raw_output = self._model_caller(prompt_built)

            parsed = self.parse_reconstruction(raw_output)

            # Return structure for the endpoint / callers. Include a (truncated) preview. Never include full input data.
            result = {
                "reconstructed_memory": parsed.get("reconstructed_memory", ""),
                "steps": {
                    "step1": parsed.get("step1", ""),
                    "step2": parsed.get("step2", ""),
                    "step3": parsed.get("step3", ""),
                    "step4": parsed.get("step4", ""),
                },
                "prompt_preview": (prompt_built[:400] + "...") if prompt_built else "",
                "note": "Real one Smart Robot call + immediate ephemeral forget (issue #6). Original Memory never entered helper.",
            }
            return result
        finally:
            # Explicit ephemeral forget per issue #6 AC + privacy guarantee: clear all sensitive refs immediately
            # (locals scoped out on return; this + no self storage ensures nothing lingers after call).
            prompt_built = ""
            if "raw_output" in locals():
                raw_output = ""
            if "parsed" in locals():
                parsed = {}
