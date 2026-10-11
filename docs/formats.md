# Campaign artifact formats

Every campaign lives in `memory/campaigns/<camp-id>/`. The files below are written by one
skill and read by hooks and later skills, so their shapes are fixed. All are markdown with
YAML front matter; the front matter is the machine-readable part.

```
memory/campaigns/camp-007/
├── trigger.md            what started this (inventory alert, request, calendar)
├── brief.md              /brief  — the plan                                  → G1
├── brief.approved.md     human   — gate artifact
├── criteria.md           /criteria — the tests, written before any copy
├── fixtures.yaml         /criteria (test-writer) — deterministic cases preflight runs; see validators/fixtures.md
├── assets/               /generate — one file per channel
│   ├── email.md
│   └── paid_social.md
├── validations/          /validate — one file per validator in validators/pack.yaml (kind: rubric)
├── review/               /review — one file per reviewer, fresh context
│   ├── brand.md
│   └── compliance.md
├── assets.approved.md    human   — gate artifact                            → G2
├── preflight.md          /preflight — deterministic report
├── ship.approved.md      human   — gate artifact                            → G3
├── shipped/              /ship — what actually went out, per channel
├── results.md            /measure — outcomes against criteria
└── retro.md              /retro — hypothesis, result, surprise, decision
```

## trigger.md

```yaml
---
campaign_id: camp-007
source: inventory_alert | request | calendar | proactive_scan
raised_at: 2026-10-06
raised_by: check-inventory | human:<name> | strategist
payload:                 # free-form, source-specific
  sku: CC-0412
  days_of_supply: 210
---
One paragraph: what happened and why it might warrant a campaign.
```

## brief.md

```yaml
---
campaign_id: camp-007
name: "Too much 2019 Médoc"
campaign_type: promotion            # MARKETING.md campaign_types[].id
audiences: [explorers, collectors]  # MARKETING.md audiences[].id
channels: [email, paid_social]      # MARKETING.md channels keys
offer:
  discount_pct: 12                  # 0 if none; ≤ max_discount_pct
  skus: [CC-0412]
dates: { start: 2026-10-14, end: 2026-10-24 }
budget: { media: 1500, currency: USD }
hypothesis: "Explorers who bought Bordeaux-adjacent regions will buy a mid-priced Médoc at a modest, honestly explained discount"
primary_metric: contribution_margin   # metrics.catalog[].id
estimated_reach: 7400
learnings_applied: [inst-0003, inst-0011]   # instincts consulted
status: draft | approved | cancelled
---
## Rationale
## Risks
## Open questions for the approver
```

## brief.approved.md (and the other gate artifacts)

```yaml
---
campaign_id: camp-007
gate: g1_brief            # g1_brief | g2_assets | g3_ship
decision: approved        # approved | rejected
approved_by: "Jess (marketing_lead)"
approved_at: 2026-10-07T15:12:00-04:00
conditions: []            # free text; the next skill must honor these
---
```

A rejected gate is still written (`decision: rejected`) so the history is complete; the
file name stays `*.approved.md` because hooks check for existence *and* decision.

## criteria.md

Written **before** any asset exists. `/generate` will not run without it.

```yaml
---
campaign_id: camp-007
measurement:
  primary: { metric: contribution_margin, threshold: 2200, window_days: 7 }
  secondary: [{ metric: revenue_per_recipient, threshold: 0.95 }]
  guardrails: inherit                 # from MARKETING.md metrics.guardrails
  minimum_sample: 500
  decision_rule: "success if primary ≥ threshold AND no guardrail breached; inconclusive below minimum_sample"
rubrics:
  brand_voice: { min_score: 4, scale: 5, anchors: docs/voice-examples.md }
  audience_fit: { min_score: 4, scale: 5 }
  claims: { mode: block }             # any unsubstantiated claim blocks
deterministic:
  limits: inherit                     # channel character limits
  never_say: inherit
  links: must_resolve
  utm: { source: email, medium: campaign, campaign: camp-007 }
  frequency_cap: inherit
  suppression: inherit
exclusions: ["anyone emailed in the last 14 days"]
---
## What good looks like
Two or three sentences a reviewer could hold the assets up against.
```

## assets/<channel>.md

```yaml
---
campaign_id: camp-007
channel: email
generated_by: copywriter
generated_at: 2026-10-08T10:02:00-04:00
assets:                    # keys must equal MARKETING.md channels.<ch>.required_assets
  subject_a: "We bought more 2019 Médoc than we should have"
  subject_b: "A Médoc you'd actually open on a Tuesday"
  preview: "Until the 24th it's $4 less than it ought to be."
  headline: "Our buyer got carried away"
  body: |
    ...
  cta: "Reserve your six"
claims_made:               # every factual claim, for the compliance reviewer
  - "2019 vintage"
  - "Family-owned since 1998"
links:
  - https://cellarandco.example/medoc-2019?utm_source=email&utm_medium=campaign&utm_campaign=camp-007
---
```

## review/<reviewer>.md

```yaml
---
campaign_id: camp-007
reviewer: brand-reviewer
kind: rubric               # deterministic | rubric | outcome — always stated
reviewed_at: 2026-10-08T10:30:00-04:00
scores:
  email: { brand_voice: 4, audience_fit: 5 }
  paid_social: { brand_voice: 3, audience_fit: 4 }
verdict: pass | revise | block
---
## Findings
Per asset: what scored low, quoted, and what would fix it. No rewrites — that is the
copywriter's job on the next pass.
```

## preflight.md

```yaml
---
campaign_id: camp-007
kind: deterministic
ran_at: 2026-10-09T09:00:00-04:00
checks:
  - { check: limits, status: pass }
  - { check: never_say, status: pass }
  - { check: links, status: pass, detail: "3/3 resolved" }
  - { check: utm, status: pass }
  - { check: frequency_cap, status: pass, detail: "0 recipients over cap" }
  - { check: suppression, status: pass, detail: "412 suppressed" }
  - { check: age_gate, status: pass }
  - { check: pii, status: pass }
  - { check: kill_switch, status: pass }
verdict: pass | fail
---
```

## results.md

```yaml
---
campaign_id: camp-007
kind: outcome
measured_at: 2026-10-31
window_days: 7
sample: 7112
primary: { metric: contribution_margin, value: 2610, threshold: 2200, met: true }
secondary: [{ metric: revenue_per_recipient, value: 1.04, threshold: 0.95, met: true }]
guardrails: [{ metric: unsubscribe_rate, value: 0.21, threshold: 0.5, breached: false }]
verdict: success | miss | inconclusive
---
```

## retro.md

```yaml
---
campaign_id: camp-007
written_at: 2026-11-02
verdict: success
hypothesis_held: true
---
## Hypothesis
## Result
## Surprise
The one thing that did not go the way the brief predicted.
## Decision
What we will do differently, stated as a testable instinct candidate:
- "Honest over-purchase framing beats discount framing for explorers" (candidate instinct)
```

## validations/<validator-id>.md

```yaml
---
campaign_id: camp-007
validator: claims_declared
kind: rubric
pass: 2                      # which validate pass produced this
runs: 2                      # blocking validators run twice
agree: true
status: pass | fail | flag
findings: [{ asset: email, quote: "…", reason: "…" }]
---
```

## evals/calibration.jsonl

One line per validator verdict, written by `/validate`; joined to `results.md` by `/learn`.

```json
{"campaign_id":"camp-007","validator":"opener_specificity","status":"flag","findings_count":1,"pass":1,"run_at":"2026-10-08T10:10:00-04:00"}
```

## memory/instincts.jsonl

One JSON object per line. Written by `/learn`, read by `/brief` and `/criteria`.

```json
{"id":"inst-0012","text":"Honest over-purchase framing outperforms discount-led framing for explorers","scope":{"audiences":["explorers"],"campaign_types":["promotion"],"channels":["email"]},"confidence":0.72,"support":["camp-007","camp-003","camp-001"],"contradicted_by":[],"status":"active","promoted_to":null,"created":"2026-11-02"}
```

`status` is `candidate | active | promoted | retired`. Promotion to a rule in
`rules/learned/` requires `support ≥ memory.instinct_promotion_min_support` and
`confidence ≥ memory.instinct_min_confidence`, and a human merges it.
