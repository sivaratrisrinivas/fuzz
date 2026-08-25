# Fuzz

Like drawing in sand at the shore: write something real, watch waves slowly wash it away, fight to save the pieces, and see a computer guess the whole thing from what's left — learning that rebuilding from damage is never an exact copy.

## What, why, how

**What it is.** You write a private paragraph. Then waves come and slowly scramble it — real letters turn into junk. You can type to fix them while the waves keep coming. When you let go, your scrambled text gets sent to an AI that tries to rebuild what you originally wrote. You see them side by side.

**Why it exists.** This is what AI image generators actually do under the hood. They start with random noise and slowly remove it in steps, guided by a prompt. Fuzz lets you *feel* that process with words instead of pictures. You live through the destroying, the fighting, and the rebuilding yourself — so you understand what "diffusion" really means without any math or diagrams.

**How it works.** The game has three parts:
- A live fight screen where waves dissolve your text and you rewrite to save it
- A thin server that sends only your scrambled text (never your original) to an AI
- The AI does 4 careful steps: first using your saved corrections as hints, then filling in around them, then guessing the rest from its training, and finally making small creative changes so the result is close but not exact

**The lesson.** The AI doesn't make a perfect copy. It makes a *best guess* using what you saved plus what it learned from millions of other texts. The quiet rewrites — the parts it changed — are where you see the computer's imagination at work. That's the whole point: rebuilding from damage is creative, not mechanical.

**Privacy.** Your original text never leaves your browser. Only the scrambled version goes to the server. After one guess, the server forgets everything.

## Results

GS-T6 measures Reconstructing accuracy as Fuzz Levels rise. Four Memories, eleven Fuzz points from 0.0 to 1.0, no Fresh Clues. oak-tree is the validation sample in `helper/prompts/sample-fight-end-data.json` and is excluded from the evaluation set. Starring uses `box/src/fuzz-simulator.ts`. Smart Robot calls are user-only, with no extra format system prompt. The locked prompt asks for a Quiet Rewrite, so exact match is 0 even on an intact Memory.

Measured on 2026-08-24. Model `Qwen/Qwen2.5-7B-Instruct` as a Q4_K_M GGUF on CPU via llama.cpp. Dataset size 4. Hardware: Intel Xeon, 4 CPUs, 15.64 GB RAM, no GPU. `HF_TOKEN` was not set, so this run used local weights of the same model rather than Hugging Face InferenceClient.

| Fuzz level | Remaining clues | Word F1 | Edit similarity | Exact match | Failures |
| ---------- | --------------- | ------- | --------------- | ----------- | -------- |
| 0.0        | 1.000           | 0.785   | 0.668           | 0/4         | 0/4      |
| 0.1        | 0.900           | 0.761   | 0.736           | 0/4         | 0/4      |
| 0.2        | 0.800           | 0.524   | 0.669           | 0/4         | 0/4      |
| 0.3        | 0.700           | 0.429   | 0.393           | 0/4         | 0/4      |
| 0.4        | 0.600           | 0.326   | 0.437           | 0/3         | 1/4      |
| 0.5        | 0.499           | 0.115   | 0.278           | 0/4         | 0/4      |
| 0.6        | 0.400           | 0.150   | 0.264           | 0/4         | 0/4      |
| 0.7        | 0.300           | 0.116   | 0.208           | 0/4         | 0/4      |
| 0.8        | 0.200           | 0.152   | 0.222           | 0/4         | 0/4      |
| 0.9        | 0.100           | 0.104   | 0.214           | 0/3         | 1/4      |
| 1.0        | 0.000           | 0.208   | 0.266           | 0/4         | 0/4      |

Word F1 stays above 0.76 through Fuzz 0.1, then drops to 0.524 at 0.2 and 0.115 at 0.5. Fuzz 1.0 Word F1 0.208 is prompt-boilerplate regurgitation. The Reconstructed Memory echoes locked-prompt tokens such as Fresh Clues and Cleaning Steps instead of a Memory. The measured 0.208 is kept. Two of 44 trials returned an empty parsed Reconstructed Memory. Those are failures, not zeros. Raw Smart Robot text is stored on every trial before parse.

```bash
pip install -r helper/requirements.txt -r bench/requirements.txt && python3 bench/gs_t6_reconstruction_accuracy.py
```

The result file is `bench/gs-t6-reconstruction-accuracy.json`.

## Play it

```bash
cd box && bun install && bun dev          # http://localhost:3000
cd helper && pip install -r requirements.txt && python -m uvicorn src.thin_helper.main:app --reload
```

Set `HF_TOKEN` for real AI reconstruction. Without it, the game uses a local fallback (synonym substitution).

Tests: `bun test` (box), `python -m pytest helper/tests` (helper).

## What's inside

- **Box** (Bun + TypeScript): the game screen — waves, typing, animations, side-by-side compare, procedural ocean audio
- **Helper** (Python/FastAPI): builds the prompt, calls the AI, forgets everything after
- **AI robot**: configurable Hugging Face model (default: `Qwen/Qwen2.5-7B-Instruct`, swap via `FUZZ_SMART_ROBOT_MODEL`)
- **Mode selector**: Freeform (fight at your own pace) or Timed (60-second countdown round)
- **Fresh Clues**: every successful rewrite at the right time is captured as a clue that helps the AI reconstruct better
- **Procedural audio**: ocean ambience, wave crashes, tension drone, reveal chime — all synthesized, no audio files

20 frontend tests + 17 Python tests pass.
