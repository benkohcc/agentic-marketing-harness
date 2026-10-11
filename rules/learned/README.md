# rules/learned

Promoted instincts. `/learn` writes `<slug>.proposed.md` here when an instinct clears
`memory.instinct_promotion_min_support` and `memory.instinct_min_confidence`. A human
renames it to `<slug>.md` to promote it; agents load only `*.md`, never `*.proposed.md`.

Each file keeps its source instinct id and supporting campaigns so a rule can be traced
back to the retros that earned it — and retired when later campaigns contradict it.

This directory is why MARKETING.md stays a statement of intent: what the business
*learned* lives here, what the business *means* lives there.
