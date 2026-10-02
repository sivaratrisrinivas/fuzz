# Output-quality eval

What the player sees after Reconstructing is the parsed RECONSTRUCTED MEMORY. Reading all 132 real
traces in `bench/` showed the old parser often returned the wrong thing:

- The model stopped before the final marker (out of tokens), so the player got nothing even when
  STEP 4 held a usable Memory.
- A marker was split across lines (`===\nSTEP 1 ===`), so no marker matched and the whole raw
  output, step markers included, was shown.
- The final text was prompt placeholder text, task talk ("The player felt the Feeling Lesson..."),
  a refusal, or a usable Memory followed by a paragraph of task talk.

The new parser tolerates marker variants, lets the last repeated section win, and falls back to
STEP 4 when the final marker is missing. `thin_helper/output_check.py` trims trailing task talk and
rejects outputs that are empty, leak markers, echo the prompt, or talk about the game. Rejected
outputs come back empty, and the Box uses its local fallback. All checks are code rules.

## Sets

| Set | Cases | Labels |
|---|---:|---|
| Real dev traces (`traces_dev.jsonl`) | 132 | Hand labeled. 97 usable, 35 not. Rules were written from these. |
| Real held-out traces (`traces_heldout.json`) | 48 | 12 new Memories x 4 Fuzz Levels from `allam-2-7b` on Groq, a model the rules never saw. Labeled by hand before scoring. 25 usable, 23 not. |
| Synthetic outputs | 931 | Generated with a known answer: 7 marker styles x 4 wrappers x 3 endings x 5 trailers, plus 6 kinds of bad final text and stopped-at-step-3 cases. Split dev 452 / test 479 by case hash. |

Labels are agent-made and need a human spot check.

## Results

| Set | Pipeline | Usable shown cleanly | Bad output blocked | Shown with task talk or markers |
|---|---|---:|---:|---:|
| Real dev | old | 63/97 | 21/35 | 40/132 |
| Real dev | new | 96/97 | 34/35 | 0/132 |
| Real held-out | old | 17/25 | 11/23 | 18/48 |
| Real held-out | new | 24/25 | 22/23 | 0/48 |

Synthetic: old 42/452 dev and 40/479 test exactly right; new 452/452 and 479/479.

Known misses: a usable Memory followed by a numbered list of task talk is rejected
(held-out first-bike/0.6); a STEP 4 fallback that is pure Fuzz is shown when the final section was
task talk (held-out exam-morning/0.9).

The "shown with task talk" count for the new pipeline is 0 by construction, since the same rules
decide what is blocked. The usable and blocked counts use the hand labels.

## What the player reads (faithfulness, held-out)

"Usable" above only means the output can be shown without task talk or markers. A second hand-label
pass on the 25 held-out outputs the new pipeline shows (`faithfulness_heldout.json`) asks whether the
text is a faithful reconstruction:

| Label | Count of 25 |
|---|---:|
| faithful (keeps who, what, where, outcome) | 5 |
| unfaithful (swaps or invents people, objects, events) | 8 |
| echo_fuzz (shows the Fuzz itself, mostly stars) | 12 |

At Fuzz 0.0 (nothing hidden), only 5 of 11 rewrites were faithful. Above Fuzz 0.0, 12 of 14
outputs echoed the stars and 2 invented a new story. These are allam-2-7b outputs, not the
production Qwen 7B, so they describe the eval's held-out model, not production. The point stands:
format checks cannot tell a faithful Memory from an invented one.

The existing non-blocking `residual_fuzz` flag matches the echo label exactly (12/12 caught, 13/13
readable outputs not flagged), so production logs can count echoes. CI gates on that agreement.
Whether an echo should be shown or replaced by the Box fallback is a product decision. Faithfulness
of readable outputs needs a binary judge or human review on production-model traces. Word F1 and
edit similarity (GS-T6) are not a substitute, since the target is a paraphrase.

## Commands

```bash
cd helper
python evals/run_output_eval.py            # report
python evals/run_output_eval.py --check    # CI gate against evals/baseline.json
OPENAI_API_KEY=... python evals/collect_traces.py --model allam-2-7b --output evals/traces_heldout.json
```

## Monitoring path

The helper now returns `quality_flags` with every reconstruction and logs the reject codes (never
the text). Count flags per day. To grow the labeled set, run `collect_traces.py` against the live
model on new Memories written for testing (never player Memories, which must not leave the
browser), label the outputs, and add them as a new held-out file.
