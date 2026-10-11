---
name: criteria
description: Write the acceptance criteria — measurement plan, rubrics, deterministic checks — for an approved brief, before any copy exists. Use after Gate 1, or "/amh:criteria camp-NNN".
---

# /criteria — the tests, written first

This is the step every other marketing-agent setup skips. Do not skip it.

## Steps
1. Confirm `memory/campaigns/camp-NNN/brief.approved.md` exists with `decision: approved`.
   Read its `conditions`. If missing, say "Gate 1 first" and stop.
2. Delegate to the **strategist**: write `criteria.md` per docs/formats.md. It must:
   - set a numeric `measurement.primary.threshold`, with the basis stated under
     "What good looks like" (past results for this type, or a reasoned floor);
   - inherit guardrails and deterministic checks from `MARKETING.md`;
   - set `utm.campaign` to the campaign id;
   - list every audience exclusion that applies;
   - honor every G1 `condition` explicitly.
3. Delegate to the **test-writer**: write `fixtures.yaml` (format in
   validators/fixtures.md) — audience cases, journey traces, copy assertions. These are
   the deterministic tests; they exist before any copy, like the criteria.
4. Show the human the `measurement` block, "What good looks like", and the count of
   fixture cases, and ask one question: "Is this the yardstick you want to be held to?"
   Edit on request.
5. Say: "Criteria and fixtures are on disk. `/amh:generate camp-NNN` will now run."

## Why a human sees this
Thresholds set after the fact are not thresholds. This is the last moment the yardstick
is honest, so the person who approved the brief sees it before copy exists.
