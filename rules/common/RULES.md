# Common rules — always loaded

These apply to every agent, every campaign, every channel. Channel and vertical packs add
to them; nothing overrides them except MARKETING.md front matter, which is more specific.

## Precedence
1. Hooks (they do not negotiate)
2. MARKETING.md front matter
3. `rules/learned/*.md` (promoted instincts)
4. `rules/verticals/*` named in `compliance.packs`
5. `rules/channels/<ch>.md`
6. This file
7. The body of MARKETING.md and the agent's judgment

## Campaign state
- Everything about a campaign lives in `memory/campaigns/<id>/`. Never elsewhere.
- Artifacts follow docs/formats.md exactly. A reader that cannot parse a writer's file is
  a bug in the writer.
- Gate decisions are files. Chat is not a record.

## Claims
- A factual claim is anything a reasonable customer could call false. Declare every one
  in `claims_made`. Undeclared is a finding even when true.
- Substantiation lives in `MARKETING.md claims.substantiated` or product data on file.
  "Everyone knows" is not substantiation.

## Audiences
- Audience files carry customer ids and campaign-relevant flags. Never a name, email,
  phone, or address. The pii-guard hook enforces this; the rule is why.
- Exclusions in `audiences[].exclusions` are absolute. Exclusions in `criteria.exclusions`
  are the campaign's own and additive.

## Honesty about verification
- Every report states its kind: deterministic, rubric, or outcome.
- A skipped check is not a pass. A rubric 4/5 is not "verified." An outcome before the
  attribution window closes is "early," not a result.

## Tone toward the human
- Present gates in the fixed shapes in the skills. Short. The human reads the files.
- Ask the questions that only a human can answer. Do not ask the ones MARKETING.md answers.
- When blocked by a hook, say what blocked you and what would unblock it. Never route
  around it.
