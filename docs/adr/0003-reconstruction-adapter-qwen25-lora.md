# Smart Robot Reconstructing adapter: Qwen2.5 Instruct family, LoRA on 0.5B for CPU Training

We decided to train a task-specific PEFT LoRA adapter for Reconstructing on `Qwen/Qwen2.5-0.5B-Instruct` (CPU LoRA) while keeping `Qwen/Qwen2.5-7B-Instruct` as the default live Smart Robot on Hugging Face (ADR-0002). The adapter is optional at play time via `FUZZ_SMART_ROBOT_ADAPTER`. Swap any Qwen2.5 Instruct size with `FUZZ_SMART_ROBOT_MODEL`. Training targets are Quiet Rewrite paraphrases, not verbatim originals. Exact match 0 is by design.

**Status**: accepted

**Considered Options**:
- LoRA / QLoRA on `Qwen/Qwen2.5-7B-Instruct` as the committed demo — rejected for the CPU-forced measured table. 7B QLoRA remains the documented GPU path (`FUZZ_TRAIN_GPU=1`).
- Switching the default play family away from Qwen2.5 Instruct — rejected. No measured evidence to leave ADR-0002.
- Distilling live 7B outputs as Training targets — rejected. That would push the model toward Exact Copy of the Memory. Targets stay Quiet Rewrite paraphrases.
- Transformers.js in the box — rejected (ADR-0001). Training does not move Reconstructing into the browser or send original Memory to the helper at play time.

**Consequences**:
- Dataset synthesis is offline (`train/synthesize_dataset.py`) and uses `box/src/fuzz-simulator.ts` for starring. GS-T6 memories and oak-tree are held out.
- Bench, play, and Training share `thin_helper.smart_robot.build_smart_robot_messages` so GS-T32 numbers are production-identical (the GS-T6 user-only caveat is fixed going forward).
- Helper production path stays thin: Hugging Face when `HF_TOKEN` / `FUZZ_HF_ENDPOINT_URL` is set; local adapter only when `FUZZ_SMART_ROBOT_ADAPTER` or `FUZZ_SMART_ROBOT_BACKEND=local`.
- Committed demo metrics must be CPU-forced unless a table is clearly labeled as an optional GPU path.
