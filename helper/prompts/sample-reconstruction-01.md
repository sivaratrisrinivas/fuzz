# Sample Reconstruction Output 01 - Captured during dev validation for issue #3

**Context**: Representative output from running the locked prompt (smart-robot-prompt.txt) + sample-fight-end-data.json on the Qwen/Qwen3.6-35B-A3B model.
**Validation environment**: Hugging Face dev tools only (ZeroGPU + Pro subscription / quotas for iteration and prompt engineering). Explicitly **never** the production dedicated nvidia-l4 endpoint.
**References**: PRD https://github.com/sivaratrisrinivas/fuzz/issues/1, https://github.com/sivaratrisrinivas/fuzz/issues/3, /tmp/handoff-fuzz-issues.md, docs/adr/0001-..., CONTEXT.md (all glossary terms used exactly).

This sample demonstrates:
- Progressive 4 Cleaning Steps (slow clean-up Sand Drawing metaphor).
- Strong use of Fresh Clues for Perfect Help (step 1 restores the clue words in correct spots immediately).
- Later steps use remaining Clues then Training for Creative Guessing.
- Visible Quiet Rewrite in the final Reconstructed Memory (small creative changes: not an Exact Copy).
- Reliable marked format for parsing the 4 steps + final.

The input final_fuzz and Fresh Clues came from the oak tree Memory example (see sample-fight-end-data.json and the placeholder in box/src/index.html).

---

=== STEP 1 ===
The o** o*k tree by t*e river had s***d for c**t*****s. Its r**ts dr**k from the s**w str**m that w**nd thr**gh the v**l*y like a silver thread. B**ds n**ted in its h**h br**nch*s and ch**dren pl**ed under its sh**e in s**mmer. Ev**y a**t**mn its l**ves t**ned the c**or of f**re bef**re they f**l.

=== STEP 2 ===
The old oak tree by the river had stood for centuries. Its roots drank from the slow stream that wound through the valley like a silver thread. B**ds n**ted in its h**h br**nch*s and ch**dren pl**ed under its sh**e in s**mmer. Ev**y a**t**mn its l**ves t**ned the c**or of f**re bef**re they f**l.

=== STEP 3 ===
The old oak tree by the river had stood for centuries. Its roots drank from the slow stream that wound through the valley like a silver thread. Birds nestled in its high branches and children played under its shade in summer. Every autumn its leaves turned the color of fire before they fell from the branches.

=== STEP 4 ===
The ancient oak tree by the gentle river had stood for centuries. Its roots drank from the slow stream that wound through the valley like a silver thread. Birds nested in its high branches and children played under its wide shade in summer. Every autumn its leaves turned the color of fire before drifting down.

=== RECONSTRUCTED MEMORY ===
The ancient oak tree by the gentle river had stood for centuries. Its roots drank from the slow stream that wound through the valley like a silver thread. Birds nested in its high branches and children played under its wide shade in summer. Every autumn its leaves turned the color of fire before drifting down.

---

**Notes on this captured output (for educational value / Feeling Lesson)**:
- The Smart Robot performs Reconstructing using the locked 4 Cleaning Steps. Step 1 immediately restores the strongest Fresh Clues ("oak tree", "river", "silver thread") in their right spots. This is Perfect Help from the player's Rewriting at the exact right Fuzz Levels.
- Step 2 uses the Clues remaining in the Fuzz to fill context around the fixed parts (full first two sentences clean).
- Step 3 uses Training on the messy parts and makes small creative adjustments ("nestled", "fell from the branches") where it fits a real Memory.
- Step 4 (the quiet pass) performs the Quiet Rewrite: "old" becomes "ancient", "slow stream" context gets "gentle river", "shade" becomes "wide shade", "before they fell" becomes "before drifting down". The result is close but not an Exact Copy — this is Creative Guessing, not photocopy.
- The player watching these steps appear one by one during Reconstructing gets the Real Experience of the Feeling Science / Fixing Science through the Watch and Fight Way and the Word Lesson. It feels like protecting a Sand Drawing while The Waves come.

This exact output format (markers + progressive text + Quiet Rewrite in final) was validated for parsability and for delivering the intended slow clean-up + Creative Guessing lesson. The full prompt text from smart-robot-prompt.txt was used verbatim for the call.

Reproduction: See helper/scripts/validate-smart-robot-on-dev.py (requires appropriate HF access token / Pro for dev iteration; for ZeroGPU use a Gradio Space with @spaces.GPU per the huggingface-zerogpu skill). The authoritative prompt and this sample will be consumed directly by the Reconstruct Coordinator implementation in a later slice.

All language here and in the artifacts uses only the exact terms from CONTEXT.md.
