---
name: brief
description: Turn a trigger or a request into a campaign brief and present it for Gate 1. Use for "plan a campaign", "brief this", a new trigger.md, or "/amh:brief".
---

# /brief — plan before anything is made

Delegate to the **strategist** agent. You orchestrate; it decides.

## Steps
1. Resolve the campaign id: next unused `camp-NNN` under `memory/campaigns/`. Create the
   directory. If the user gave a request in chat, write it as `trigger.md`
   (`source: request`, `raised_by: human:<name>`).
2. Hand the strategist the trigger and ask for `brief.md` per docs/formats.md. The
   gate-guard hook may block the write if `memory.retro_required` is on and the last
   shipped campaign of this type has no retro — if so, say which campaign needs
   `/amh:retro` and stop.
3. Present Gate 1 to the human, in this shape and nothing fancier:

```
=== GATE 1 · Brief · camp-NNN ===
Name:        …
Type:        …            Audiences: …           Reach: ~…
Channels:    …            Offer: …               Dates: … → …
Hypothesis:  …
Metric:      … (threshold to be set in /criteria)
Learnings:   inst-… applied; inst-… deliberately not (why)
Risks:       …
Questions for you:
  1. …
→ approve camp-NNN [as <role>]   |   edit camp-NNN: <instruction>   |   reject camp-NNN
```

4. On `approve`: run `/amh:approve camp-NNN g1_brief`. On `edit`: pass the instruction to
   the strategist, rewrite `brief.md`, re-present. On `reject`: write
   `brief.approved.md` with `decision: rejected`, set brief `status: cancelled`.
5. After approval, say: "Next: `/amh:criteria camp-NNN` — the tests get written before
   any copy."

Do not proceed to criteria in the same breath. The human may want to think.
