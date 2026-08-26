# Fuzz

Fuzz is a browser game where you write a private paragraph, watch waves wash it into junk, type to save pieces, and see a computer guess the original from what is left.

## Who it is for

It is for anyone who has heard that AI rebuilds pictures from random specks, or repairs damaged text, and still has no gut feel for what that means. You do not need a machine-learning class or an account.

The problem the game solves is that the idea stays abstract until you live it. Image tools start from junk and slowly guess a picture. Fuzz does that with words, in your browser, on a paragraph you wrote. Waves replace letters with junk. You type to put letters back while the waves keep coming. When you stop, a computer looks at the damaged text plus the pieces you saved and guesses what you wrote. You see your original next to that guess. The guess is never a photocopy. A few words come back changed on purpose. That gap is the lesson.

Your original paragraph never leaves the browser. Only the damaged text and the saved pieces go to a small Python helper. After one guess, the helper forgets them.

## How to try it

This repo has no hosted demo. Run the game on your machine. Install Bun, the JavaScript runtime this repo uses, from https://bun.sh. You also need Python 3.

Start the game screen from the repo root. It serves http://localhost:3000

```bash
cd box && bun install && bun dev
```

In a second terminal, start the helper that talks to the model.

```bash
cd helper && pip install -r requirements.txt && python -m uvicorn src.thin_helper.main:app --reload
```

Open http://localhost:3000. Type a paragraph. Pick Freeform to fight at your own pace, or Timed for a 60-second round. Waves start. Type to repair letters. Stop when you want a guess.

Set `HF_TOKEN` if you want the helper to call `Qwen/Qwen2.5-7B-Instruct` through Hugging Face, a hosted model API. Without that token, the last step still finishes on your machine by swapping some words from a synonym list.

## What the numbers mean

On 2026-08-25 we asked: if nobody types to save letters, how close is the computer's guess as more of the paragraph is washed away?

Four sample paragraphs, n=4. Eleven wash amounts from 0.0, fully intact, to 1.0, fully washed. The wash is the same code the game uses, `box/src/fuzz-simulator.ts`. The model is `Qwen/Qwen2.5-7B-Instruct`, run locally as Q4_K_M compressed weights on CPU through llama.cpp, a local model runner. `HF_TOKEN` was not set. Each model call was a user-only chat_completion. That means one user message and no extra format system prompt. The live game still sends a format system prompt, so these numbers are not a player-round score. The prompt asks for a quiet rewrite, so exact match is 0 at every level, including intact text.

Hardware: Intel Xeon, 4 CPUs, 15.64 GB RAM, no GPU.

Word F1 is the overlap of words between the original paragraph and the guess. 1 would mean the same words. 0 would mean none. Edit similarity is how close the characters are. Exact match is a full identical copy. Remaining clues is the share of original letters still visible after the wash. Failures are trials where the parsed guess came back empty. Those are not scored as zero. Word F1 and edit similarity average only the trials that parsed.

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

Read the table as a collapse, not a leaderboard. Word F1 is 0.876 at Fuzz 0.0 and 0.717 at 0.1. At Fuzz 1.0, Word F1 is 0.124. That 0.124 is prompt-boilerplate regurgitation. One parsed guess echoed locked-prompt tokens such as Fresh Clues, Endless Fight, and Cleaning Steps instead of a paragraph. The measured 0.124 is kept. Nine of 44 trials returned an empty parsed guess. Raw model text is stored on every trial before parse.

A fifth sample, oak-tree in `helper/prompts/sample-fight-end-data.json`, is used to check the prompt. It is not in the four scored paragraphs.

Rerun from the repo root. This command drives `box/src/fuzz-simulator.ts` for the wash, then scores guesses.

```bash
pip install -r helper/requirements.txt -r bench/requirements.txt && python3 bench/gs_t6_reconstruction_accuracy.py
```

The committed result file is `bench/gs-t6-reconstruction-accuracy.json`.

## For contributors

**Game screen.** `box/` is Bun and TypeScript. It owns the live wash, typing, clue capture, side-by-side compare, and ocean audio synthesized in code with no audio files. The wash engine is `box/src/fuzz-simulator.ts`.

**Helper.** `helper/` is a small Python web server built with FastAPI. It builds the prompt, calls the model once, and forgets the payload. Default model is `Qwen/Qwen2.5-7B-Instruct`. Override with `FUZZ_SMART_ROBOT_MODEL`.

**Modes.** Freeform lets the player fight at their own pace. Timed is a 60-second countdown round.

**Fresh Clues.** Every successful rewrite at the right time is captured as a clue that helps the later guess. The accuracy run above left those empty on purpose so the curve is wash amount only.

Tests from the repo root:

```bash
cd box && bun test
```

```bash
cd helper && python -m pytest tests
```
