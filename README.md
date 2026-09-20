# Fuzz

Like drawing in sand at the shore: write something real, watch waves slowly wash it away, fight to save the pieces, and see a computer guess the whole thing from what's left — learning that rebuilding from damage is never an exact copy.

## What, why, how

**What it is.** You write a private paragraph. Then waves come and slowly scramble it — real letters turn into junk. You can type to fix them while the waves keep coming. When you let go, your scrambled text gets sent to an AI that tries to rebuild what you originally wrote. You see them side by side.

**Why it exists.** This is what AI image generators actually do under the hood. They start with random noise and slowly remove it in steps, guided by a prompt. Fuzz lets you *feel* that process with words instead of pictures. You live through the destroying, the fighting, and the rebuilding yourself — so you understand what "diffusion" really means without any math or diagrams.

**How it works.** The game has three parts:
- A live fight screen (**Box**, Bun + TypeScript) where waves dissolve your text and you rewrite to save it
- A thin server (**Helper**, FastAPI) that sends only your scrambled text (never your original) to an AI
- The AI (**Smart Robot**, Hugging Face Qwen2.5 Instruct) does 4 careful steps: first using your saved corrections as hints, then filling in around them, then guessing the rest from its training, and finally making small creative changes so the result is close but not exact

**The lesson.** The AI doesn't make a perfect copy. It makes a *best guess* using what you saved plus what it learned from millions of other texts. The quiet rewrites — the parts it changed — are where you see the computer's imagination at work. That's the whole point: rebuilding from damage is creative, not mechanical.

**Privacy.** Your original text never leaves your browser. Only the scrambled version goes to the server. After one guess, the server forgets everything. The helper rejects any payload that includes original Memory fields.

## Play it

Local two-process:

```bash
cd box && bun install && bun dev          # http://localhost:3000
cd helper && pip install -r requirements.txt && python -m uvicorn src.thin_helper.main:app --reload
```

One-command prod-like:

```bash
docker compose up --build                 # Box :3000, helper :8000
```

Set `HF_TOKEN` for real AI reconstruction on Hugging Face (default model `Qwen/Qwen2.5-7B-Instruct`, swap with `FUZZ_SMART_ROBOT_MODEL`). Without it, Reconstructing returns empty markers and the Box uses its local fallback. Optional local LoRA: `FUZZ_SMART_ROBOT_ADAPTER=train/artifacts/qwen25-0.5b-reconstruct-lora` and `FUZZ_SMART_ROBOT_BACKEND=local`.

Tests: `bun test` (box), `python -m pytest tests` from `helper/` (helper). CI runs both plus a stub Reconstructing smoke.

## How to train the Smart Robot

Offline only. Original Memory never enters the helper at play time. Training targets are Quiet Rewrite paraphrases of synthetic Memories, **not** verbatim originals. Exact match 0 is by design.

```bash
pip install -r train/requirements.txt     # CPU torch: pip install torch --index-url https://download.pytorch.org/whl/cpu
python3 train/synthesize_dataset.py       # 72 Memories × 4 Fuzz Levels; stars via box/src/fuzz-simulator.ts
python3 train/train_lora.py               # PEFT LoRA on Qwen/Qwen2.5-0.5B-Instruct
```

Locked eval is the GS-T6 set (`night-bus`, `kitchen-radio`, `library-rain`, `porch-storm`). `oak-tree` (the sample in `helper/prompts/sample-fight-end-data.json`) is excluded from scoring and from Training data.

Play, bench, and Training share `thin_helper.smart_robot.build_smart_robot_messages` (format system prompt + locked 4 Cleaning Steps user prompt). GS-T32 numbers are production-identical. The older GS-T6 table below used user-only chat and is kept as a historical measured run.

Eval (CPU, play-identical chat):

```bash
python3 bench/gs_t6_reconstruction_accuracy.py \
  --gate GS-T32 --backend transformers --model Qwen/Qwen2.5-0.5B-Instruct \
  --quiet-rewrite-targets train/data/locked_eval.json \
  --output bench/gs-t32-before.json

python3 bench/gs_t6_reconstruction_accuracy.py \
  --gate GS-T32 --backend transformers --model Qwen/Qwen2.5-0.5B-Instruct \
  --adapter train/artifacts/qwen25-0.5b-reconstruct-lora \
  --quiet-rewrite-targets train/data/locked_eval.json \
  --output bench/gs-t32-after.json

python3 bench/gs_t32_compare.py bench/gs-t32-before.json bench/gs-t32-after.json
```

GPU path (optional, not used for committed demo numbers):

```bash
FUZZ_TRAIN_GPU=1 FUZZ_SMART_ROBOT_ADAPTER_BASE=Qwen/Qwen2.5-7B-Instruct \
  python3 train/train_lora.py --output train/artifacts/qwen25-7b-reconstruct-lora
```

If weights are missing, `python3 train/download_adapter.py` prints the train commands. Set `FUZZ_SMART_ROBOT_ADAPTER_REPO` to pull a published adapter.

## How to deploy

**Box (Vercel or similar static host).** `vercel.json` copies `box/src/index.html` and rewrites `POST /reconstruct` to `api/reconstruct.py` (thin helper). Set `HF_TOKEN` (and optional `FUZZ_HF_ENDPOINT_URL`, `FUZZ_SMART_ROBOT_MODEL`) in the host's environment. Original Memory is still rejected. Hobby plans may time out on a slow Smart Robot; a container helper is more reliable.

```bash
npx vercel --prod
# or: docker compose up --build
```

**Helper (container).** `helper/Dockerfile` is the FastAPI app with rate limits, prod CORS (`FUZZ_CORS_ORIGINS`), request timeouts, structured errors, and logs that record sizes not Fuzz text. Put it on Fly, Render, Cloud Run, or any container host. Point the Box at it with `FUZZ_HELPER_URL` (dev server) or a reverse-proxy `/reconstruct`.

**GitHub homepage.** Set the live Box URL as the repository homepage once secrets (HF_TOKEN, CORS origins) are in place. Until then this PR ships a deployable Box + helper; Portfolio can finish the public URL.

## Results

### GS-T6 (historical, 7B GGUF, user-only chat)

GS-T6 measures Reconstructing accuracy as Fuzz Levels rise. Four Memories, eleven Fuzz points from 0.0 to 1.0, no Fresh Clues. oak-tree is the validation sample in `helper/prompts/sample-fight-end-data.json` and is excluded from the evaluation set. Starring uses `box/src/fuzz-simulator.ts`. **This table used user-only chat_completion** (no format system prompt). Play sends a format system prompt. Keep these numbers as measured history; do not treat them as production-identical. The locked prompt asks for a Quiet Rewrite, so exact match is 0 even on an intact Memory.

Measured on 2026-08-25. Model `Qwen/Qwen2.5-7B-Instruct` as a Q4_K_M GGUF on CPU via llama.cpp. Dataset size 4. Hardware: Intel Xeon, 4 CPUs, 15.64 GB RAM, no GPU. `HF_TOKEN` was not set.

| Fuzz level | Remaining clues | Word F1 | Edit similarity | Exact match | Failures |
| ---------- | --------------- | ------- | --------------- | ----------- | -------- |
| 0.0        | 1.000           | 0.876   | 0.836           | 0/4         | 0/4      |
| 0.1        | 0.900           | 0.717   | 0.628           | 0/4         | 0/4      |
| 0.2        | 0.800           | 0.757   | 0.823           | 0/2         | 2/4      |
| 0.3        | 0.700           | 0.432   | 0.567           | 0/4         | 0/4      |
| 0.4        | 0.600           | 0.243   | 0.335           | 0/3         | 1/4      |
| 0.5        | 0.499           | 0.185   | 0.297           | 0/3         | 1/4      |
| 0.6        | 0.400           | 0.180   | 0.282           | 0/2         | 2/4      |
| 0.7        | 0.300           | 0.124   | 0.235           | 0/4         | 0/4      |
| 0.8        | 0.200           | 0.117   | 0.214           | 0/4         | 0/4      |
| 0.9        | 0.100           | 0.141   | 0.188           | 0/3         | 1/4      |
| 1.0        | 0.000           | 0.124   | 0.151           | 0/2         | 2/4      |

Word F1 is 0.876 at Fuzz 0.0 and 0.717 at 0.1. Fuzz 1.0 Word F1 0.124 is prompt-boilerplate regurgitation. Nine of 44 trials returned an empty parsed Reconstructed Memory. Those are failures, not zeros. Result file: `bench/gs-t6-reconstruction-accuracy.json`.

### GS-T32 (CPU, play-identical chat, 0.5B base vs LoRA)

Task-specific Reconstructing adapter on `Qwen/Qwen2.5-0.5B-Instruct`. Same locked eval as GS-T6 (N=4, oak-tree excluded). Chat is production-identical to play. Training set is synthetic (72 Memories × 4 Fuzz Levels). Targets are Quiet Rewrite paraphrases, not originals. **Numbers below are CPU-forced.** Prefer this table for adapter claims. If a cell is still `n/a`, the run has not been committed yet — do not invent metrics.

See `bench/gs-t32-before.json` and `bench/gs-t32-after.json` after the CPU eval lands in this PR.

Short bakeoff: 0.5B was chosen because it trains and runs on the helper CPU path (0.5B–7B family). 1.5B/7B adapter Training is the optional GPU path above. Default live model stays `Qwen/Qwen2.5-7B-Instruct` unless `FUZZ_SMART_ROBOT_MODEL` is set (ADR-0002, ADR-0003).

## What's inside

- **Box** (Bun + TypeScript): the game screen — waves, typing, animations, side-by-side compare, procedural ocean audio
- **Helper** (Python/FastAPI): builds the prompt, calls the AI, forgets everything after; rate limits, CORS, health, structured errors
- **AI robot**: configurable Hugging Face model (default: `Qwen/Qwen2.5-7B-Instruct`, swap via `FUZZ_SMART_ROBOT_MODEL`); optional LoRA via `FUZZ_SMART_ROBOT_ADAPTER`
- **Training**: `train/synthesize_dataset.py`, `train/train_lora.py`, adapter under `train/artifacts/`
- **Mode selector**: Freeform (fight at your own pace) or Timed (60-second countdown round)
- **Fresh Clues**: every successful rewrite at the right time is captured as a clue that helps the AI reconstruct better
- **Procedural audio**: ocean ambience, wave crashes, tension drone, reveal chime — all synthesized, no audio files
