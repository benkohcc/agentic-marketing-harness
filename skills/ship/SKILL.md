---
name: ship
description: Gate 3 and execution — send, publish, or launch each channel, file-based by default. Use after /preflight passes or "/amh:ship camp-NNN".
---

# /ship — Gate 3, then the button

## Steps
1. Confirm `preflight.md` verdict pass. Otherwise: "Preflight first."
2. Present Gate 3. This one is deliberately plain:

```
=== GATE 3 · Ship · camp-NNN ===
email        1,912 recipients after suppression (412 removed, 0 over cap)
             scheduled 2026-10-14 10:00 America/New_York   [in window]
paid_social  budget $1,500 · 2 ad sets · starts 2026-10-14
Kill switch: not present
Integrations: email=file_based (simulated) · ads=file_based (simulated)
→ approve camp-NNN [as marketing_ops]   |   reject camp-NNN
```

3. On approve: `/amh:approve camp-NNN g3_ship`. Then delegate to **channel-ops** to write
   `shipped/<channel>.md` per channel. The send-blocker and gate-guard hooks run on each
   write; if either blocks, show the reason and stop. Do not retry.
4. Append the send log. Update `brief.md` `status` is unchanged (approved); shipped
   state lives in `shipped/`.
5. Say what happened per channel, with `status: simulated | sent | failed`, and:
   "Measurement window closes <end_date + attribution_window_days>. Run
   `/amh:measure camp-NNN` then."

## Kill switch
If `kill_switch.file` exists at any point, stop everything, say who owns it, and do not
offer to remove it.
