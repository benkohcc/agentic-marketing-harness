---
name: generate
description: Produce every channel asset for a campaign from its approved brief and criteria. Use after /criteria, for revision passes after /review, or "/amh:generate camp-NNN".
---

# /generate — make the assets

Delegate to the **copywriter**. One `assets/<channel>.md` per channel in the brief.

## Steps
1. Confirm `brief.approved.md` (approved) and `criteria.md` exist. The gate-guard hook
   blocks otherwise; do not try to route around it.
2. For each channel in `brief.channels`, hand the copywriter: the brief, the criteria,
   `MARKETING.md`, `rules/channels/<ch>.md`, `rules/learned/*.md`, and the active instincts
   scoped to this campaign. Ask for the asset file in docs/formats.md shape.
3. The copy-lint hook runs on every write. If it blocks, show the copywriter the reasons
   and have it fix them. Up to three attempts; then stop and show the human what will not
   pass and why.
4. When all channel files exist and pass lint, say so — list the files, nothing else.
   Do **not** paste the copy into chat. The reviewers must see it cold, and the human
   sees it at Gate 2 next to the review scores.
5. Say: "Assets are on disk and pass lint [deterministic]. Next: `/amh:review camp-NNN`."

## Revision passes
If `review/*.md` files exist with `verdict: revise`, pass their findings to the copywriter
and regenerate only the named assets. Increment `revision` in the file front matter.
