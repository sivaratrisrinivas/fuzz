# Fuzz

Fuzz is a free, private, open web game that helps anyone *feel* how AI rebuilds meaning from damaged data.

## How it works

1. You write a private **Memory**. **Dissolving** turns it into **Fuzz** through **The Waves** at different **Fuzz Levels**.
2. You fight back by **Rewriting** during the **Endless Fight**, leaving **Fresh Clues** at the right time for **Perfect Help**.
3. When you stop, the **Smart Robot** performs **Reconstructing** using exactly **4 Cleaning Steps**, producing a **Reconstructed Memory** with a visible **Quiet Rewrite**. It is Creative Guessing, not an Exact Copy.
4. You see your original side-by-side with the reconstructed version. **Play again** instantly wipes everything.

Private by design — your full original text stays in your browser. The server receives only damaged data, does one AI call, then forgets everything.

## Run locally

```bash
cd box && bun install && bun dev          # http://localhost:3000
cd helper && pip install -r requirements.txt && python -m uvicorn src.thin_helper.main:app --reload
```

Tests: `bun test` (box), `python -m pytest helper/tests` (helper).

## Tech

- **Box**: Bun + TypeScript — live fight, visuals (sand/wave textures), Reveal Comparator, resilience UI
- **Helper**: Python/FastAPI — prompt constructor, AI model caller, ephemeral coordinator
- **AI**: Hugging Face InferenceClient → `Qwen/Qwen2.5-7B-Instruct` (overridable via `FUZZ_SMART_ROBOT_MODEL`)
- **ADR**: Architecture decisions in `docs/adr/`

All slices #2–#10 (PRD #1) are implemented — 20 frontend + 13 Python tests pass. Glossary terms from `CONTEXT.md` are enforced throughout.
