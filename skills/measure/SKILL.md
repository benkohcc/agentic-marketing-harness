---
name: measure
description: Score a shipped campaign against the criteria written before launch. Use after the attribution window or "/amh:measure camp-NNN".
---

# /measure — against the yardstick, not the vibes

Delegate to the **analyst**. Output `results.md` per docs/formats.md, `kind: outcome`.

## Steps
1. Confirm `shipped/` exists. Load `criteria.md` — its `measurement` block is the contract
   and may not be edited now.
2. Get data: `integrations.analytics` connector if present; otherwise
   `data/results.<ch>.json` in the campaign folder (file-based). If no data: write
   `verdict: inconclusive`, `reason: no data`, and tell the human what file or connector
   would fix it.
3. Apply `decision_rule` literally. Sample below `minimum_sample` is inconclusive.
   A breached blocking guardrail is a miss.
4. Report:

```
=== RESULTS · camp-NNN  [outcome] ===
Primary    contribution_margin   $2,610  vs ≥ $2,200   met
Secondary  revenue_per_recipient  $1.04  vs ≥ $0.95    met
Guardrail  unsubscribe_rate       0.21%  vs < 0.5%     ok
Sample     7,112 (min 500)
Verdict    success
Observations (not in criteria): …
```

5. Say: "Retro is due by <end_date + memory.retro_due_days>. `/amh:retro camp-NNN`."
