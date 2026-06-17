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
