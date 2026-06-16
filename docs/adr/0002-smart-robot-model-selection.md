# Smart Robot model selection: switch from Qwen3.6-35B-A3B to Qwen2.5-7B-Instruct

We decided to replace `Qwen/Qwen3.6-35B-A3B` with `Qwen/Qwen2.5-7B-Instruct` as the default Smart Robot model for Reconstructing. The original model produced text-only output for a multimodal (image-text-to-text) model, caused provider routing issues with serverless InferenceClient, had high latency (>20s) per call, and failed to produce reliable structured output with the locked 4 Cleaning Steps markers.

**Status**: accepted

**Considered Options**:
- `Qwen/Qwen3.6-35B-A3B` (original) — rejected. Multimodal model used for a text-only task. InferenceClient provider (featherless-ai) exposed it only for the `conversational` task, requiring a `text_generation` → `chat_completion` migration. 20s+ latency. Failed to reliably produce the locked 4 Cleaning Steps markers in structured output.
- `meta-llama/Meta-Llama-3-8B-Instruct` — rejected. Only 4/5 markers produced; too creative (hallucination), format adherence unreliable.
- `google/gemma-2-2b-it` — rejected. 16s slow, produced almost exact copy of input (no Quiet Rewrite), too small at 2B params.
- `Qwen/Qwen2.5-7B-Instruct` — adopted. Text-only instruct model, ~4s latency, correct markers every time in testing, genuine Quiet Rewrite behavior produced, broad HF provider support (together, featherless-ai). 7.6B params fits nvidia-l4 comfortably.

**Consequences**:
- The default model string in `reconstruct_coordinator.py` is `Qwen/Qwen2.5-7B-Instruct`, overridable via `FUZZ_SMART_ROBOT_MODEL` env var.
- The existing sample artifacts (`sample-reconstruction-01.md`, `sample-fight-end-data.json`) reference the old model in their historical metadata but remain valid as representative format samples.
- Future model changes are cheap: update one env var or default string and re-validate output format adherence.
- The ADR-0001 architecture (nvidia-l4 dedicated endpoint) is unchanged; only the default dev/fallback model changes.
