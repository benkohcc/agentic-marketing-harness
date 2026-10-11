# journeys/<id>.yaml — a campaign's journey as a state machine

A journey declared as config can be checked without customers (structure) and with
synthetic ones (traces, fuzz). A journey clicked together in a canvas cannot. This is the
form `hooks/run-fixtures.py` simulates. Keep it small; most campaigns are three states.

```yaml
journey_id: camp-004
campaign_id: camp-004
channel: email
start: send_main
states:
  send_main:
    type: send
    asset: email                 # assets/email.md must exist and pass lint
    on:
      click:       exit_converted
      unsubscribe: exit_unsub
      wait_3d:     reminder      # a wait_* event is time passing; the max wait is enforced
    max_wait_days: 3
  reminder:
    type: send
    asset: email_reminder
    on:
      click:       exit_converted
      unsubscribe: exit_unsub
      wait_4d:     exit_timeout
    max_wait_days: 4
  exit_converted: { type: exit }
  exit_unsub:     { type: exit, suppress: true }
  exit_timeout:   { type: exit }
```

## Semantics

- `type: send` emits one send on entry and records it against the customer. `type: exit`
  ends the trace; `suppress: true` marks the customer suppressed from then on.
- `on` maps events to next states. Events are strings: `open`, `click`, `purchase`,
  `unsubscribe`, `bounce`, or `wait_<n>d`. An event with no mapping is ignored (the
  customer stays in the state). `wait_<n>d` advances the clock by n days. A state's
  `wait_*` edge is a **timer**: it fires at exactly `max_wait_days` after entry, whatever
  the sizes of the waits that got there — the same as an ESP's "wait 3 days" node. A
  state with a `wait_*` edge and no `max_wait_days` is a structural error.
- Write the key as `"on":` or `on:` — the simulator accepts both (YAML 1.1 reads a bare
  `on` as boolean true).
- The simulator tracks per customer: `sends`, `path`, `days`, `suppressed`.

## Structural checks (no customers)

- `every_state_reaches_exit` — from every state there is a path of `on` edges to an exit.
- `no_cycle_without_exit` — every cycle contains a state with an edge out of the cycle.
- `every_send_references_linted_asset` — each `asset` has `assets/<asset>.md` and no
  copy-lint failure recorded.
- `every_wait_has_max_days` — each send state with a `wait_*` edge has `max_wait_days`.

## Properties (fuzzed)

`run-fixtures.py` generates `runs` random event sequences (default 2000) over the
journey's event vocabulary and asserts, per trace:

| never | meaning |
|---|---|
| `sends_over_cap` | `sends` > the channel's `frequency_cap.count` within `per_days` (and any audience override) |
| `send_to_suppressed` | a send after `suppressed` became true |
| `send_outside_window` | a send on a day/hour outside `channels.<ch>.send_window` (the clock starts at the brief's `start` date, 10:00 local) |
| `send_after_end_date` | a send after `brief.dates.end` |

A single-send campaign with no `journeys/<id>.yaml` is simulated as the implicit
`send → exit`, which still runs the cap, suppression, window and end-date checks.
