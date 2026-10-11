# evals

How AMH answers "is the harness any good?" — separately from "did the campaign work?"

Three layers, matching the three kinds of green:

| Layer | What it tests | Where |
|---|---|---|
| deterministic | hooks block what they should and pass what they should | `hooks/selftest.py` (33 cases: hooks, run-fixtures, scanner) |
| rubric | validators and reviewers score known-good and known-bad assets correctly; verdicts logged and weighted against outcomes | `validators/pack.yaml`, `evals/calibration.jsonl`, `evals/validator-weights.json` |
| outcome | over many campaigns, instincts improve threshold hit-rate | `evals/outcome-ledger.md` (v0.3) |

## Rubric evals (next)

`evals/cases/<name>/` holds an asset file and an `expected.yaml` with the score range a
good reviewer gives it. The eval runner spawns the brand-reviewer against each case and
reports agreement. Cases are built from the voice-examples file: every "Not this" should
score ≤ 2, every "This" ≥ 4. A reviewer that can't separate them is not a reviewer.

`evals/rubrics/brand-voice.md` is the reviewer's scoring guide, kept here rather than in
the agent so that it can be versioned and evaluated on its own.

## What is deliberately not an eval

Campaign outcomes. A single campaign's result says almost nothing about the harness; the
ledger over dozens does. Until then, the honest statement is "the hooks work, the
reviewers are calibrated against the examples, and the outcomes are being recorded."
