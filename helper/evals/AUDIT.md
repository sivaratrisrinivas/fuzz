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

**Status:** OK for format failures, observed in 132 real traces (split markers, out-of-tokens stops, task talk, prompt echo). Faithfulness failures were first seen on 25 allam-2-7b traces. The 2026-10-03 Qwen 72B held-out run shows the same pattern on a Qwen model: 11 of 11 faithful at Fuzz 0.0, 1 of 11 at Fuzz 0.3 (9 swap key nouns, such as power -> phone and tea -> teacher), and 0 of 21 at Fuzz 0.6 and 0.9 (mostly invented stories). The output checks blocked all 3 task-talk outputs and showed all 40 readable ones; `residual_fuzz` matched all 3 echoes with no false flags. In the GS-T6 sweep, 3 of 4 Fuzz 1.0 outputs were task talk and are blocked by the output checks.

## 5. Labeled data

### Held-out traces come from a different model
**Status:** Problem exists (partly unblocked, 2026-10-03). The 48 original held-out traces are from allam-2-7b. The HF token here still has no provider for the production `Qwen/Qwen2.5-7B-Instruct` (router: "not supported by any provider you have enabled"; the Hub lists only featherless-ai as live, and it is not enabled on this account). As the closest same-family model, `Qwen/Qwen2.5-72B-Instruct` was run through Hugging Face Inference Providers (deepinfra): 43 held-out traces (`traces_heldout_qwen72b.json`) plus a 44-trial GS-T6 sweep (`bench/gs-t6-qwen72b-hf.json`). The held-out run stopped at 43 of 48 when the account hit HTTP 402 (monthly included credits used up). Faithfulness labels now total 65 (25 allam + 40 shown Qwen 72B: 12 faithful, 24 unfaithful, 3 echo, 1 garbled). Still too few faithful cases for judge validation (aim for about 50 faithful and 50 not), and still not the 7B.

## 4. Human review

**Status:** Problem exists. All labels are agent-made. Reviewers saw the original Memory, Final Fuzz and shown text side by side, which is the right view. A person should spot-check.

## 3. Judge validation

**Status:** Not applicable yet (all checks are code). The one flag compared with labels is reported as caught / passed per class, not accuracy.

## 6. Pipeline hygiene

**Status:** OK. CI gates on the real and synthetic sets. Production returns `quality_flags` per reconstruction, so echo and reject rates can be tracked without logging player text.
