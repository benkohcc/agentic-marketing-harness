---
name: status
description: Show where every campaign is in the loop and what is blocking it. Use for "status", "where are we", "what's pending", or "/amh:status [camp-NNN]".
---

# /status — the loop, at a glance

Read-only. Walk `memory/campaigns/*/` and derive each campaign's step from which files
exist, exactly as the hooks would:

| Files present | Step |
|---|---|
| trigger.md only | triggered |
| brief.md, no approval | **G1 pending** |
| brief.approved.md rejected | cancelled |
| approved, no criteria.md | criteria due |
| criteria.md, no assets/ | generating |
| assets/, no review/ | review due |
| review/, no assets.approved.md | **G2 pending** (show verdicts) |
| assets.approved.md, no preflight.md | preflight due |
| preflight fail | preflight failed (show failing checks) |
| preflight pass, no ship.approved.md | **G3 pending** |
| shipped/, no results.md | in market · measure after <date> |
| results.md, no retro.md | retro due by <date> |
| retro.md | done |

Also show: kill switch present or not; count of active instincts; any
`rules/learned/*.proposed.md` awaiting a human.

Format as one line per campaign, pending gates first. Nothing else.
