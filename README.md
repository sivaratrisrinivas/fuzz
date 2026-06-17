# Fuzz

A game where you write a secret message, watch it get scrambled by waves, fight to save it, and see a computer guess what you wrote using AI.

## How it works

1. **Write** a short memory in the text box.
2. **Waves** come and slowly mess up your words (scrambling letters into dots). You can type to fix them while the waves keep coming.
3. When you **let go**, your scrambled text gets sent to an AI robot across the internet. It looks at what's left and tries to rebuild your original message in 4 steps.
4. You see **your original** next to the **robot's version** side by side. The robot's version is close but not exact — you can see where it used its imagination.

**Privacy**: Your original message stays in your browser. Only the scrambled version gets sent to the robot. After one guess, the server forgets everything.

## Play it

```bash
cd box && bun install && bun dev          # http://localhost:3000
cd helper && pip install -r requirements.txt && python -m uvicorn src.thin_helper.main:app --reload
```

Tests: `bun test` (box), `python -m pytest helper/tests` (helper).

## What's inside

- **Box** (Bun + TypeScript): the game screen — waves, typing, animations, side-by-side compare
- **Helper** (Python/FastAPI): builds the prompt, calls the AI robot, forgets everything after
- **AI robot**: `Qwen/Qwen2.5-7B-Instruct` on Hugging Face (swap model via `FUZZ_SMART_ROBOT_MODEL`)

20 frontend tests + 18 Python tests pass.
