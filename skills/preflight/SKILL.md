---
name: preflight
description: Deterministic pre-send checks — limits, links, UTMs, caps, suppression, age gate, PII, kill switch, send window. Use after Gate 2 or "/amh:preflight camp-NNN".
---

# /preflight — everything that is simply true or false

Delegate to **channel-ops**. Output `preflight.md` per docs/formats.md, `kind: deterministic`.

## Steps
1. Confirm `assets.approved.md` (approved). Otherwise: "Gate 2 first."
2. Build the audience export(s): `data/audience-<ch>.csv` with **customer ids only** and
   an `age_verified` column when `compliance.age_gate` is set. The pii-guard hook blocks
   anything else. With a CDP connector (`integrations.cdp`), pull from it; file-based,
   derive from `data/segments.json`.
3. Run `fixtures.yaml` (audience cases, disjointness, size tolerance, journey structural
   checks, traces, property fuzz) and record each as a check line. Missing fixtures is a
   `fail`. Then run every check in the channel-ops agent definition. Record pass / fail / skipped with
   detail. Never record pass for a check that did not run.
4. Show the table. `verdict: pass` only on all-pass. Skipped checks go under
   "Needs a human" and the verdict is fail until a human either resolves them or writes
   `conditions` into `ship.approved.md` accepting the skip.
5. On pass: "Preflight passed [deterministic]. Next: `/amh:ship camp-NNN` — this is the
   step that asks for Gate 3."
