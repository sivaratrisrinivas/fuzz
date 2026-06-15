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

The authoritative artifacts (prompt + samples) live in helper/prompts/ and were validated against the exact 4 Cleaning Steps,
Fresh Clues usage, Creative Guessing, Quiet Rewrite requirement, parsable marked format, and Feeling Lesson goals
from PRD #1 and issue #3. See the sample-reconstruction-01.md for a representative captured output.

All terms are from CONTEXT.md glossary. References: PRD #1, issue #3, ADR-0001, handoff docs.
"""

import json
import os
from pathlib import Path

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None


def main():
    base = Path(__file__).resolve().parent.parent
    prompt_path = base / "prompts" / "smart-robot-prompt.txt"
    data_path = base / "prompts" / "sample-fight-end-data.json"

    print("=== Fuzz Smart Robot Prompt Validation (dev tools / ZeroGPU / Pro only) ===")
    print(f"Using locked prompt: {prompt_path}")
    print(f"Using sample data: {data_path}")
    print("Model target: Qwen/Qwen3.6-35B-A3B (per PRD and issue #3)")
    print("Constraint: ZeroGPU/Pro for iteration. No nvidia-l4 production calls.\n")

    prompt_template = prompt_path.read_text(encoding="utf-8")
    with open(data_path, encoding="utf-8") as f:
        sample = json.load(f)

    final_fuzz = sample["final_fuzz"]
    fresh_clues = sample["fresh_clues"]

    # Format the Fresh Clues section as simple readable list for the prompt.
    clues_lines = []
    for c in fresh_clues:
        clues_lines.append(f"- At Fuzz Level {c['fuzz_level']}, spot/position {c['spot']}, fixed the words: {c['words']}")
    fresh_clues_text = "\n".join(clues_lines)

    full_prompt = prompt_template.replace("{FINAL_FUZZ}", final_fuzz).replace("{FRESH_CLUES}", fresh_clues_text)

    print("--- Formatted prompt (first 800 chars) ---")
    print(full_prompt[:800] + "...\n")

    # Attempt actual call if client and token available (dev only).
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if InferenceClient is None or not token:
        print("No huggingface_hub client or HF_TOKEN in env.")
        print("To perform a live dev run on the model: install huggingface_hub, set HF_TOKEN, and re-run.")
        print("For production-grade dev iteration with the full 35B-A3B MoE on GPU: use a Gradio Space + @spaces.GPU")
        print("  (see the huggingface-zerogpu skill and references/ in the agents skills dir).")
        print("\nThe representative sample output captured during prior dev validation lives at:")
        print("  helper/prompts/sample-reconstruction-01.md")
        print("It was produced following the exact locked prompt + data and demonstrates the required properties.")
        return

    print("Attempting InferenceClient call to Qwen/Qwen3.6-35B-A3B (this may queue, require Pro/credits, or fail for large MoE on serverless).")
    print("If it fails or is slow, fall back to a dedicated ZeroGPU Space as noted above.\n")

    client = InferenceClient(model="Qwen/Qwen3.6-35B-A3B", token=token)
    # Conservative generation params for structured multi-step instruction following.
    result = client.text_generation(
        full_prompt,
        max_new_tokens=1200,
        temperature=0.7,
        do_sample=True,
    )
    print("=== Raw model response (truncated for console) ===")
    print(result[:2000] if len(result) > 2000 else result)
    print("\n(If good, copy relevant sections into a new sample-*.md following the format of sample-reconstruction-01.md)")


if __name__ == "__main__":
    main()
