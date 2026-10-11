# fixtures.yaml — tests the test-writer writes, that preflight runs

Written by `agents/test-writer.md` during `/criteria`, stored at
`memory/campaigns/<id>/fixtures.yaml`, executed by `/preflight` (and by `/validate` for
the copy assertions). Everything here is `kind: deterministic`: the judgment was spent
writing the file; running it is mechanical.

```yaml
campaign_id: camp-004
written_by: test-writer
written_at: 2026-10-08T09:40:00-04:00

# 1. Audience membership — the predicate under test is MARKETING.md audiences[].definition
#    applied to data/segments.json (file-based) or the CDP connector.
audience:
  cases:
    - { customer: { orders_12m: 3, aov: 190, allocation_opt_out: false }, expect: { collectors: true,  explorers: false } }
    - { customer: { orders_12m: 3, aov: 190, allocation_opt_out: true  }, expect: { collectors: false } }          # exclusion wins
    - { customer: { orders_12m: 2, aov: 179.99, regions_12m: 3 },          expect: { collectors: false, explorers: true } }  # boundary
    - { customer: { last_order_days_ago: 200, unsubscribed: false },       expect: { lapsed: true } }
    - { customer: { last_order_days_ago: 200, open_support_ticket: true }, expect: { lapsed: false } }          # exclusion
  disjoint: [[collectors, lapsed], [explorers, lapsed]]      # must never overlap
  size_tolerance: 0.35                                      # resolved size within ±35% of size_hint, else fail
  exclusions_applied: ["emailed_within_days: 14"]           # from criteria.exclusions

# 2. Journey — the state machine under test is journeys/<id>.yaml (v0.2) or, for a
#    single-send campaign, the implicit send → wait → exit.
journey:
  structural:
    every_state_reaches_exit: true
    no_cycle_without_exit: true
    every_send_references_linted_asset: true
    every_wait_has_max_days: true
  traces:
    - { events: [send, open, click],                    expect: { sends: 1, path: [send, exit] } }
    - { events: [send, open, wait_3d],                  expect: { sends: 2, path: [send, reminder, exit] } }
    - { events: [send, unsubscribe],                    expect: { sends: 1, suppressed_after: true } }
  properties:                                           # fuzzed over N random event sequences
    runs: 2000
    never: [sends_over_cap, send_to_suppressed, send_outside_window, send_after_end_date]

# 3. Copy assertions — things a script can check on assets/*.md beyond copy-lint
copy:
  must_contain:
    email.body: ["2019", "Médoc", "24"]                  # vintage, wine, offer end date
  must_equal:
    "email.body discount_pct": 12                        # parsed from text, == brief.offer.discount_pct
  links_all_match: "utm_campaign=camp-004"
```

## Running

```
python3 hooks/run-fixtures.py memory/campaigns/camp-004   # exit 1 on any fail; --json for the report
```

Output is a `preflight.md`-style block with one line per case and a `verdict`. A
missing `fixtures.yaml` is a preflight `fail` with `detail: "no fixtures — run /criteria"`.

## Why the test-writer is a separate agent

The strategist decides what the campaign is; the test-writer decides how we will know
the plumbing is right. Keeping them apart means the fixtures are written against the
brief rather than against whatever the strategist found convenient — the same reason a
test author and an implementer are different people on a careful team.
