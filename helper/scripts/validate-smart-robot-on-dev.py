#!/usr/bin/env python3
"""
Reproduction / validation script for the locked Smart Robot prompt + 4 Cleaning Steps on Qwen (issue #3).

DEV TOOLS ONLY (ZeroGPU / Pro subscription and quotas).
NEVER use the production dedicated nvidia-l4 Inference Endpoint for prompt development or re-generating these samples.

Usage (after obtaining HF token with appropriate access for dev iteration):
  cd helper
  pip install huggingface_hub
  # For full ZeroGPU experience with large MoE (recommended for this model size): follow huggingface-zerogpu skill
  #   to create a temporary Gradio Space with @spaces.GPU + transformers or vLLM, then call it.
  # Serverless via InferenceClient may work for smaller experiments or if HF hosts the model.
  export HF_TOKEN=...
  python scripts/validate-smart-robot-on-dev.py

This script:
- Loads the locked prompt from ../prompts/smart-robot-prompt.txt
- Loads sample input from ../prompts/sample-fight-end-data.json
- Substitutes and (optionally) calls the model
- Prints the result or can save a new sample-*.md

The callable helpers below (format_fresh_clues, build_full_prompt, call_smart_robot, extract_chat_content)
are the shared Smart Robot one-call path. GS-T6 reconstruction accuracy in
bench/gs_t6_reconstruction_accuracy.py imports them rather than growing a second client.

The authoritative artifacts (prompt + samples) live in helper/prompts/ and were validated against the exact 4 Cleaning Steps,
Fresh Clues usage, Creative Guessing, Quiet Rewrite requirement, parsable marked format, and Feeling Lesson goals
from PRD #1 and issue #3. See the sample-reconstruction-01.md for a representative captured output.

All terms are from CONTEXT.md glossary. References: PRD #1, issue #3, ADR-0001, handoff docs.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
MAX_TOKENS = 1200
TEMPERATURE = 0.7


def helper_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_locked_prompt(base: Optional[Path] = None) -> str:
    root = base or helper_root()
    return (root / "prompts" / "smart-robot-prompt.txt").read_text(encoding="utf-8")


def load_sample_fight_end(base: Optional[Path] = None) -> dict:
    root = base or helper_root()
    with open(root / "prompts" / "sample-fight-end-data.json", encoding="utf-8") as f:
        return json.load(f)


def format_fresh_clues(fresh_clues: list) -> str:
    clues_lines = []
    for c in fresh_clues:
        clues_lines.append(
            f"- At Fuzz Level {c['fuzz_level']}, spot/position {c['spot']}, fixed the words: {c['words']}"
        )
    return "\n".join(clues_lines)


def build_full_prompt(
    final_fuzz: str,
    fresh_clues: list,
    prompt_template: Optional[str] = None,
) -> str:
    template = prompt_template if prompt_template is not None else load_locked_prompt()
    return template.replace("{FINAL_FUZZ}", final_fuzz).replace(
        "{FRESH_CLUES}", format_fresh_clues(fresh_clues)
    )


def resolved_model_name() -> str:
    return os.environ.get("FUZZ_SMART_ROBOT_MODEL", DEFAULT_MODEL)


def extract_chat_content(result: Any) -> str:
    """Return message content, or "" if choices/content are missing.

    A missing field must not become str(result). That dump is non-empty, so
    call_smart_robot would treat a response object as Smart Robot text.
    """
    if isinstance(result, str):
        return result
    content = None
    choices = getattr(result, "choices", None)
    if choices and len(choices) > 0:
        first_choice = choices[0]
        message = getattr(first_choice, "message", None)
        if message is not None:
            content = getattr(message, "content", None)
            if content is None and isinstance(message, dict):
                content = message.get("content")
    if content is None and isinstance(result, dict):
        dict_choices = result.get("choices") or []
        if dict_choices:
            message = dict_choices[0].get("message") or {}
            content = message.get("content")
    if content is None:
        return ""
    return str(content)


def call_smart_robot(prompt: str) -> str:
    """One Smart Robot chat call. Raises if the client or token is missing.

    Empty text is returned as "" so GS-T6 can persist raw_output, then mark the
    trial failed. Same persist-then-fail path as the local GGUF caller. Used by
    this CLI and by bench/gs_t6_reconstruction_accuracy.py. Sends a user message
    only, with no extra format system prompt. Play still sends a format system
    prompt in ReconstructCoordinator._default_model_caller, so this path is not
    production-identical. Does not fall back to empty markers or the sample
    reconstruction file.
    """
    if InferenceClient is None:
        raise RuntimeError("huggingface_hub is not installed")
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is not set")
    model = resolved_model_name()
    endpoint = os.environ.get("FUZZ_HF_ENDPOINT_URL")
    use_model = endpoint or model
    client = InferenceClient(model=use_model, token=token)
    messages = [{"role": "user", "content": prompt}]
    try:
        result = client.chat.completions.create(
            model=use_model,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        text = extract_chat_content(result)
    except (AttributeError, TypeError):
        result = client.chat_completion(
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        text = extract_chat_content(result)
    return str(text)


def main():
    base = helper_root()
    prompt_path = base / "prompts" / "smart-robot-prompt.txt"
    data_path = base / "prompts" / "sample-fight-end-data.json"

    print("=== Fuzz Smart Robot Prompt Validation (dev tools / ZeroGPU / Pro only) ===")
    print(f"Using locked prompt: {prompt_path}")
    print(f"Using sample data: {data_path}")
    print(f"Model target: {resolved_model_name()} (per handoff model selection)")
    print("Constraint: ZeroGPU/Pro for iteration. No nvidia-l4 production calls.\n")

    sample = load_sample_fight_end(base)
    full_prompt = build_full_prompt(sample["final_fuzz"], sample["fresh_clues"])

    print("--- Formatted prompt (first 800 chars) ---")
    print(full_prompt[:800] + "...\n")

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if InferenceClient is None or not token:
        print("No huggingface_hub client or HF_TOKEN in env.")
        print("To perform a live dev run on the model: install huggingface_hub, set HF_TOKEN, and re-run.")
        print("For production-grade dev iteration with a GPU-backed model: use a Gradio Space + @spaces.GPU")
        print("  (see the huggingface-zerogpu skill and references/ in the agents skills dir).")
        print("\nThe representative sample output captured during prior dev validation lives at:")
        print("  helper/prompts/sample-reconstruction-01.md")
        print("It was produced following the exact locked prompt + data and demonstrates the required properties.")
        return

    print(f"Attempting InferenceClient call to {resolved_model_name()} (text-only instruct, ~4s latency, good format adherence).")
    print("If it fails or is slow, fall back to a dedicated ZeroGPU Space as noted above.\n")

    result_text = call_smart_robot(full_prompt)
    print("=== Raw model response (truncated for console) ===")
    print(result_text[:2000] if len(result_text) > 2000 else result_text)
    print("\n(If good, copy relevant sections into a new sample-*.md following the format of sample-reconstruction-01.md)")


if __name__ == "__main__":
    main()
