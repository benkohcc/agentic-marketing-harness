---
name: approve
description: Record a human gate decision as the artifact file the hooks check. Use when the user says "approve camp-NNN", "reject camp-NNN", or "/amh:approve camp-NNN <gate>".
---

# /approve — a decision is a file

Gates are enforced by hooks that look for a file. This skill writes that file on the
human's behalf, with their words in it.

## Usage
`approve camp-NNN [as <role>]` · `reject camp-NNN [reason]` ·
`/amh:approve camp-NNN g1_brief|g2_assets|g3_ship [--reject] [--as role] [--condition "…"]`

## Steps
1. Infer the gate from campaign state if not given: no `brief.approved.md` → g1;
   assets exist and reviews exist → g2; `preflight.md` pass → g3. If ambiguous, ask.
2. Confirm the approver role against `MARKETING.md gates.<gate>.approver`. If the human
   did not say a role, ask "as which role?" once; accept their answer.
3. Write `<artifact>` named in `gates.<gate>.artifact`, in the docs/formats.md shape,
   with `approved_by: "<name> (<role>)"`, the current timestamp, and any conditions
   stated in chat copied verbatim.
4. Echo one line: "G1 approved by Jess (marketing_lead) · camp-007 · 2 conditions."

## Never
- Write an approval the human did not state in this session.
- Write `decision: approved` when the human said anything other than approve.
