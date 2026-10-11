---
name: retro
description: Write the campaign retrospective — hypothesis, result, surprise, decision — in the fixed format that /learn mines. Use after /measure or "/amh:retro camp-NNN".
---

# /retro — four sections, every time

Delegate to the **analyst**. Output `retro.md` per docs/formats.md.

## Steps
1. Load `brief.md` (hypothesis), `criteria.md`, `results.md`, and every `review/*.md`.
   If `results.md` is missing, run `/amh:measure` first.
2. Draft the four sections. The **Surprise** is mandatory and singular: the one biggest
   gap between what the brief predicted and what happened. "Nothing surprised us" is not
   accepted; look at reach, timing, channel split, or the review findings.
3. The **Decision** is one to three candidate instincts, each a single falsifiable
   sentence with the audiences / type / channels it applies to.
4. Show the draft; ask the human for one correction or addition. Write the file.
5. Say: "Retro written. When three or more retros exist, `/amh:learn` can mine them."

A retro unblocks the next campaign of this type when `memory.retro_required` is on. That
is the point: no learning, no next campaign.
