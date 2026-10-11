# MARKETING.md — specification (v0.1)

`MARKETING.md` is the context layer. It is the one file every agent in the harness reads
before doing anything, and it is the only place business meaning is allowed to live. If a
rule, a voice constraint, an audience definition, or a KPI threshold is not in this file
(or in a rules pack it names), the harness does not know it.

It is modeled on `CLAUDE.md`, with one difference that matters: it has a schema. The
front matter is YAML, validated against [`marketing.schema.json`](../marketing.schema.json)
by the `validate-marketing-md` hook on every session start and every edit. Prose lives in
the body under fixed headings so agents can locate it by name.

## Design goals

- **Machine-first, human-editable.** Front matter is the API. The body is for things that
  resist structure (voice examples, positioning narrative). Nothing load-bearing lives only
  in the body.
- **Everything a gate needs is here.** Who approves, what artifact proves it, what the
  thresholds are.
- **Small.** A complete `MARKETING.md` for a single-brand business should fit in a few
  hundred lines. If it grows past that, the overflow belongs in a rules pack or a
  per-audience file the front matter points to.
- **Stable identifiers.** Audiences, campaign types, channels, and metrics all have `id`s.
  Briefs, criteria, retros, and instincts reference those ids, which is what makes memory
  queryable across campaigns.

## File shape

```markdown
---
amh_version: "0.1"
business: { ... }
brand: { ... }
audiences: [ ... ]
campaign_types: [ ... ]
channels: { ... }
metrics: { ... }
claims: { ... }
compliance: { ... }
gates: { ... }
memory: { ... }
integrations: { ... }     # optional
kill_switch: { ... }
---

## Who we are
## Positioning
## Voice, with examples
## Audience notes
## Operating notes
```

## Front matter, section by section

### `business`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `name` | string | yes | Brand or business unit name as it appears in copy |
| `vertical` | string | yes | Free text (`"dtc wine"`, `"b2b fintech"`) — used by `/init` to choose default rules packs |
| `model` | enum `dtc` \| `b2b` \| `marketplace` \| `subscription` \| `mixed` | yes | Drives default KPIs and campaign types |
| `markets` | string[] | yes | ISO country codes; drives compliance packs |
| `currency` | string | yes | ISO 4217 |
| `fiscal_year_start` | string `MM-DD` | no | For "this quarter" resolution |

### `brand`

The voice contract. Reviewers score against this.

| Field | Type | Required | Purpose |
|---|---|---|---|
| `voice` | string[] (2–5) | yes | Adjectives, e.g. `["knowledgeable", "warm", "specific"]` |
| `register` | enum `first_person_plural` \| `second_person` \| `third_person` | yes | Default grammatical stance |
| `never_say` | string[] | yes | Literal strings and phrases. `copy-lint` treats these as hard failures. |
| `avoid` | string[] | no | Patterns to steer away from, e.g. `"superlatives without substance"`. Rubric-scored, not linted. |
| `embrace` | string[] | no | Patterns to lean into |
| `cta_style` | string | yes | One-line rule, e.g. `"specific verb + specific object; never 'click here'"` |
| `proof_standard` | string | yes | What counts as evidence for a claim in copy |
| `reading_level_max` | number | no | Flesch-Kincaid grade ceiling; linted |
| `examples_ref` | string | no | Path to a longer voice-examples file |

### `audiences[]`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `id` | slug | yes | Stable identifier |
| `name` | string | yes | |
| `definition` | string | yes | How membership is determined, in words. Points at a segment in a CDP if one exists. |
| `rule` | string | no | The same membership, as a machine-evaluable predicate (below). When present, `fixtures.yaml` audience cases, disjointness and size checks run against it. |
| `exclusion_rules` | string[] | no | Predicates; matching any one excludes the customer even when `rule` matches. The machine form of `exclusions`. |
| `size_hint` | integer | no | Rough count, for reach estimates and the size-share tolerance check |
| `fit` | slug[] | no | `campaign_types[].id`s this audience responds to |
| `exclusions` | string[] | no | Who must never be targeted from this audience |
| `frequency_cap_override` | object | no | Per-channel overrides of `channels.*.frequency_cap` |

#### Audience rules — the predicate language

A `rule` is one expression over a customer's attributes, evaluated by
`hooks/run-fixtures.py` (and by preflight when resolving audiences from a file-based
customer list). Deliberately tiny, so a marketer can read it and a script can run it:

- attributes by name: `orders_12m`, `aov`, `last_order_days_ago`, `allocation_opt_out` …
  (whatever columns the customer file or CDP exposes; a missing attribute is `null`)
- comparisons `== != < <= > >=`, arithmetic `+ - * /`, membership `in`
- boolean `and`, `or`, `not`, parentheses
- literals: numbers, quoted strings, `true`, `false`, `null`, lists `["a", "b"]`

```yaml
- id: collectors
  definition: "3+ orders in 12 months and AOV above $180; or anyone on the allocation list"
  rule: "(orders_12m >= 3 and aov > 180) or allocation_list == true"
  exclusion_rules: ["allocation_opt_out == true"]
```

No function calls, no attribute access, no assignment. Anything else fails validation.

### `campaign_types[]`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `id` | slug | yes | e.g. `new_arrival`, `winback`, `limited_allocation` |
| `default_channels` | slug[] | yes | Keys of `channels` |
| `primary_metric` | slug | yes | A `metrics.catalog[].id` |
| `lead_time_days` | integer | yes | Minimum days from brief to ship |
| `default_duration_days` | integer | yes | |
| `discount_allowed` | boolean | yes | |
| `max_discount_pct` | number | if discount_allowed | |
| `tone_override` | string | no | One line, e.g. `"more urgent than default; scarcity is real"` |
| `requires_legal_review` | boolean | no | Forces the compliance reviewer to block rather than flag |

### `channels`

A map keyed by channel slug. Each value:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `enabled` | boolean | yes | |
| `required_assets` | string[] | yes | Asset names the generator must produce, e.g. `subject_a`, `subject_b`, `preview`, `body`, `cta` |
| `limits` | object | no | Per-asset character limits; linted |
| `frequency_cap` | `{ count, per_days }` | no | Enforced by preflight against send history |
| `send_window` | `{ days: [...], hours: [start, end], tz }` | no | |
| `suppression` | string[] | no | Named suppression rules preflight applies |
| `rules_pack` | string | no | Path under `rules/channels/` to load for this channel |

### `metrics`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `catalog` | object[] | yes | Each: `{ id, name, definition, direction: up\|down, unit }` |
| `guardrails` | object[] | no | Each: `{ metric, threshold, action: block\|flag }` — e.g. unsubscribe rate above 0.5% blocks the retro from being marked a success |
| `attribution_window_days` | integer | yes | |
| `minimum_sample` | integer | no | Below this, `/measure` reports "inconclusive" rather than a result |

### `claims`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `substantiated` | object[] | no | `{ claim, evidence, expires }` — claims copy may make, with the proof on file |
| `prohibited` | string[] | yes | Claims that are never allowed; linted as hard failures |
| `requires_legal` | string[] | no | Claim patterns that force a blocking legal review |

### `compliance`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `packs` | string[] | yes | Paths under `rules/verticals/` and `rules/common/`; `/init` proposes these from `business.markets` and `business.vertical` |
| `consent_basis` | string | yes | How marketing consent is established |
| `age_gate` | integer | no | Minimum audience age; preflight blocks audiences without it |
| `data_handling` | string[] | no | e.g. `"no PII in exported audience files"` — enforced by `pii-guard` |

### `gates`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `g1_brief` | `{ approver, artifact, timeout_hours }` | yes | `approver` is a role name; `artifact` is the file whose existence proves approval |
| `g2_assets` | same | yes | |
| `g3_ship` | same | yes | |
| `escalation` | string | no | Who to notify when a gate times out |

The `gate-guard` hook refuses to run a skill whose prerequisite gate artifact is missing
from `memory/campaigns/<id>/`.

### `memory`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `retro_required` | boolean | yes | If true, `/brief` refuses to start a new campaign of a type whose last campaign has no retro |
| `retro_due_days` | integer | yes | Days after `end_date` |
| `instinct_promotion_min_support` | integer | yes | Number of concordant retros before an instinct is proposed as a rule |
| `instinct_min_confidence` | number | yes | |

### `integrations` (optional)

A map of role → MCP server name, e.g. `{ esp: "klaviyo-mcp", cdp: "semantic-layer" }`.
AMH never assumes any of these exist. Skills check for the role and degrade to
file-based outputs when it is absent.

### `kill_switch`

| Field | Type | Required | Purpose |
|---|---|---|---|
| `file` | string | yes | Path whose existence halts all `/ship` operations immediately |
| `owner` | string | yes | Who can create and remove it |
| `on_trigger` | string[] | yes | Actions the harness takes (pause sends, notify, write incident note) |

## Body sections

All five headings are required; the hook checks for them. Content is free prose.

- **Who we are** — two or three paragraphs an agent could read to write a founder's note.
- **Positioning** — the one-sentence positioning statement plus the alternatives customers
  actually consider.
- **Voice, with examples** — at least three paired examples: *not this* / *this*. The brand
  reviewer uses these as few-shot anchors.
- **Audience notes** — anything about `audiences[]` that resists structure.
- **Operating notes** — practical constraints: fulfillment lead times, blackout dates,
  who is on vacation.

## Versioning

`amh_version` is the spec version this file conforms to. Breaking changes bump the minor
version until 1.0. `/init --upgrade` rewrites a file to the current spec and reports
what it could not migrate.

## What deliberately is not here

- Platform credentials or endpoints — those live in MCP config.
- Per-campaign state — that lives in `memory/campaigns/<id>/`.
- Learned instincts — `memory/instincts.jsonl`. Promoted instincts become rules packs,
  not front-matter edits, so that `MARKETING.md` stays a statement of intent rather than a
  log of what happened.
