---
name: validate
description: Run the validator pack and the campaign fixtures against generated assets, feed findings back to the copywriter, and log verdicts for calibration. Called by /review before Gate 2, or "/amh:validate camp-NNN".
---

# /validate — the inner loop

The closest thing marketing has to "run the tests". Rubric validators plus deterministic
fixtures, then fix-and-rerun before a human sees anything.

## Steps
1. Confirm `assets/*.md` exist and pass copy-lint. Confirm `fixtures.yaml` exists
   (else: "run `/amh:criteria` — the test-writer has not written fixtures").
2. **Deterministic first.** Run the `copy` section of `fixtures.yaml` against the
   assets. Any failure → straight to step 5 with findings; do not spend validator runs
   on copy that fails a mechanical check.
3. **Pack.** For every entry in `validators/pack.yaml`, spawn one **validator**
   subagent with only that entry's `inputs`. Run the entries marked `model: different`
   on another model when the runtime allows. Run blocking validators twice; if the two
   runs disagree, record `flag`.
4. Write `validations/<validator-id>.md` per verdict (kind: rubric) and append one line
   per verdict to `evals/calibration.jsonl`:
   `{"campaign_id","validator","status","findings_count","run_at"}`.
5. Combine: any blocking `fail` → `block`; any `fail`/`flag` → `revise`; else `pass`.
   On `revise`, hand only the findings (never the verdict files) to the copywriter via
   `/amh:generate` for a revision pass, then rerun only the validators that did not pass.
   Maximum three passes; then stop and show the human what will not clear and why.
6. Report, in this shape and no more:

```
=== VALIDATE · camp-004 · pass 2 of 3 ===
fixtures/copy   [deterministic]   3/3 pass
claims_declared [rubric][blocks]  pass       (run 2× · agree)
offer_consistency [rubric][blocks] pass
opener_specificity [rubric]       flag · paid_social: "Save 12% on Bordeaux." — no concrete detail
… 
Overall: revise → regenerating paid_social
```

7. On overall `pass`, return to `/review` for the brand and compliance reviewers and
   Gate 2. Validators do not replace the reviewers; they clear the ground so the
   reviewers spend their judgment on what is left.

## Never
- Mark a validator `pass` because it timed out or could not read an input.
- Let the copywriter see a validator's full verdict file; findings only.
- Skip the calibration log. A validator without a record cannot be weighted later.
