---
name: learn
description: Mine retros into instincts with confidence and support, and propose rules for promotion. Use periodically, after several retros, or "/amh:learn".
---

# /learn — retros → instincts → (proposed) rules

Delegate to the **analyst**. Writes `memory/instincts.jsonl`; may write
`rules/learned/<slug>.proposed.md`.

## Steps
1. Read every `memory/campaigns/*/retro.md` and the existing `instincts.jsonl`.
2. Extract candidates from each retro's Decision. Cluster duplicates and near-duplicates.
   Merge into existing instincts where the scope overlaps; otherwise create with the next
   `inst-NNNN` id and `status: candidate`.
3. For each instinct, recompute `support`, `contradicted_by`, and `confidence` from the
   agent definition's rule. `candidate` → `active` once support ≥ 2.
4. Promotion: support ≥ `memory.instinct_promotion_min_support` and confidence ≥
   `memory.instinct_min_confidence` → write `rules/learned/<slug>.proposed.md`:

```markdown
# <instinct text>
- source: inst-0012 · support: camp-001, camp-003, camp-007 · confidence: 0.72
- scope: audiences [explorers] · types [promotion] · channels [email]
## Rule
One directive sentence the copywriter / strategist can follow.
## Evidence
One line per supporting campaign: what happened.
```

5. **Calibrate the validators.** Join `evals/calibration.jsonl` to each campaign's
   `results.md`. For every validator, compute how often `pass` preceded `success` and
   `fail`/`flag` preceded `miss`. Write `evals/validator-weights.json`
   (`{validator: {n, precision, recall, weight}}`). Propose demoting a blocking validator
   whose verdicts show no relationship to outcomes after 10 campaigns; a human decides.
6. Report: instincts created / updated / retired, and rules proposed. Say plainly: "A
   human renames `.proposed.md` to `.md` to promote it. I do not."

## Never
- Edit `MARKETING.md`.
- Delete an instinct. Retire it with a reason.
- Promote without a human.
