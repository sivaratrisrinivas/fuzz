# Eval audit (eval-audit skill, 2026-10-03)

Routed by evals-start: an eval pipeline exists (output-quality eval plus the GS-T6/GS-T32 benches), so `eval-audit`. Findings by impact.

## 2. Evaluator design

### Reconstruction quality is scored with similarity metrics
**Status:** Problem exists (documented, not replaced).
GS-T6/GS-T32 score reconstructions with Word F1 and edit similarity. The prompt asks for a paraphrase ("Quiet Rewrite"), so overlap punishes good rewrites and rewards echoing the input. The GS-T6 note already says Fuzz 1.0 F1 comes from boilerplate.
**Fix:** a binary faithfulness check ("does the shown Memory swap or invent people, objects or events?"). Start with the hand labels added here. Build a judge with `write-judge-prompt` and validate it with `validate-evaluator` on production-model traces.

### Output eval measured format, not faithfulness
**Status:** Fixed in part in this branch.
"Usable" meant showable without task talk. A second label pass on the 25 shown held-out outputs found 5 faithful, 8 unfaithful and 12 echoes of the Fuzz stars (`faithfulness_heldout.json`). The existing `residual_fuzz` flag agrees with the echo label on all 25. That agreement is now reported and gated in CI.

## 1. Error analysis

**Status:** OK for format failures, observed in 132 real traces (split markers, out-of-tokens stops, task talk, prompt echo). Faithfulness failures (object swaps, invented stories) were only observed now, on 25 traces, and need more traces.

## 5. Labeled data

### Held-out traces come from a different model
**Status:** Problem exists (blocked). The 48 held-out traces are from allam-2-7b. The HF token here has no provider for the production `Qwen/Qwen2.5-7B-Instruct`. Faithfulness labels: 25, too few for judge validation (aim for about 50 faithful and 50 not).

## 4. Human review

**Status:** Problem exists. All labels are agent-made. Reviewers saw the original Memory, Final Fuzz and shown text side by side, which is the right view. A person should spot-check.

## 3. Judge validation

**Status:** Not applicable yet (all checks are code). The one flag compared with labels is reported as caught / passed per class, not accuracy.

## 6. Pipeline hygiene

**Status:** OK. CI gates on the real and synthetic sets. Production returns `quality_flags` per reconstruction, so echo and reject rates can be tracked without logging player text.
