# Fuzz

Fuzz is a free, private, open web game that helps anyone *feel* how AI systems rebuild meaningful content from heavily damaged or noisy data.

## What it is

You type a short private text — a memory, story, or description. Random letters and junk slowly overwrite it in real time while you watch. As the damage happens, you fight back by retyping and fixing parts of it. When you stop, a remote AI model receives only the final damaged version plus the specific fixes you made (and when you made them). 

The AI then tries to reconstruct your original text. It shows its work in four visible steps and usually produces something very close but not identical — it makes small creative changes. You see your original text side-by-side with the AI version, with the differences highlighted, plus one short explanation. "Play again" instantly clears everything from your browser. Nothing is ever saved on a server.

## Why it exists

Most explanations of generative AI and diffusion-style models are abstract diagrams or math. This game turns the core ideas into a direct experience: gradual loss of information, the power of corrections made at the right moments, and the fact that the AI does not make an exact copy — it creatively guesses the whole from partial evidence using what it has learned.

It is built to be:
- Hands-on and memorable (you live the "damage and repair" instead of just reading about it)
- Private by design (your full original text stays in your browser; only limited damaged data is sent)
- Free and accessible (no account or login required)
- Low cost to run (one short AI call per game; the supporting server can sleep when idle)
- Lightweight (uses text so anyone can play and understand it)

## How it works (high level)

1. The interactive damage and repair ("the fight") runs entirely in your browser. This keeps it fast and private during play. The browser tracks exactly what you fixed and when.

2. When you stop, your browser sends two small pieces of information: the final damaged text and the list of fixes (with their timing).

3. A tiny server program takes that data and makes exactly one call to a powerful AI model (hosted on remote GPUs that can turn off when no one is using the game). The model is instructed to reconstruct the text in four clear stages, starting with the fixes you provided.

4. The stages stream back one by one so you can watch the reconstruction. At the end you see the side-by-side view with changes lit up and a plain note about what the AI did.

5. "Play again" wipes the round from your browser. The server forgets the data immediately after the AI call finishes.

Current state: The browser game shell and backend coordinator are in place. The instructions for the remote AI model (four clear stages) were finalized and tested on development tools in an earlier slice. The full client-side real-time damage simulation, live Rewriting, and precise capture of your fixes at the right moments (the playable Endless Fight with Fresh Clues for Perfect Help) are now implemented and runnable in the browser via the deep Fuzz Simulator (issue #4 complete). The deep Reconstruct Coordinator and Prompt Constructor (locked 4 Cleaning Steps + prompt fidelity + parsing) are implemented in the thin helper. The one Smart Robot call (exactly one per round via DI + default) + immediate ephemeral forget is now wired (issue #6 complete), and the live fight box sends the data contract on stop and receives the structured result. Progressive 4 Cleaning Steps waiting UX during Reconstructing (auto-activate + client-side pauses for the Sand Drawing metaphor) is implemented in the box (issue #7 complete). Side-by-side reveal with Quiet Rewrite highlights via the deep Reveal Comparator (client-side original Memory vs Reconstructed Memory, marks only on creative changes) plus short Feeling Lesson message is implemented (issue #8 complete via full TDD vertical). Play again instant full clear and round reset flows (client-side; refresh during fight handling) is implemented: prominent Play again button instantly clears every piece of the prior round (Memory, Fuzz, Fresh Clues, 4 Cleaning Steps, Reconstructed Memory, all state) with zero trace and returns to fresh empty Memory input; page refresh during live Endless Fight resets cleanly to starting empty state with a gentle glossary message (issue #9 complete via full TDD vertical + 17/17 tests). Resilience paths, full E2E player journey verification, privacy/cost/glossary audit complete (issue #10 via full TDD vertical + 20/20 tests): friendly "Wait longer" / "Try again (reusing the exact same fight-end data contract)" / "Start a new Memory" on Smart Robot slow/fail (30s Abort timeout + lastFightEndData stash + tryAgainReconstruct in client); all paths preserve privacy (original Memory client-only, never sent; helper forgets ephemerally after one call); E2E source tests + explicit audits cover complete journey (Memory entry -> Endless Fight/#4 + Fresh Clues/Perfect Help -> stop + one Smart Robot call/#6 -> 4 Cleaning Steps progressive/#7 -> side-by-side Quiet Rewrite reveal/#8 + short Feeling Lesson -> resilience recover or Play again/#9 clear) + glossary fidelity (CONTEXT.md only), single call per round, immediate forget, client-only Memory, open/no-auth/https, low-cost dedicated nvidia-l4 (scale-to-zero). The full game now matches the PRD (#1) and handoff decisions end-to-end. Ready for further iteration or dedicated endpoint activation (out of scope).

## Run locally (current development shells)

```bash
# Browser front-end shell
cd box
bun install
bun dev          # open http://localhost:3000

# Small backend coordinator shell
cd helper
pip install -r requirements.txt
python -m uvicorn src.thin_helper.main:app --reload
```

Tests: `bun test` inside the `box` folder, and the Python unittest or pytest commands inside `helper`.

## Technology and approach

- Bun + TypeScript for the live browser part (instant response, no server round-trips while you are actively playing).
- Minimal Python (FastAPI) backend that only exists to talk to the AI model once per round and then forget everything.
- The AI model runs on Hugging Face infrastructure (development uses low-cost or free GPU time; real play uses cheap dedicated hardware).

See the GitHub issues in this repository for the full plan and detailed specification (the main planning document is issue #1). This is a small side project whose goal is to make an important concept in modern AI tangible and understandable through direct experience.

Privacy, low cost, and open access are non-negotiable constraints.
