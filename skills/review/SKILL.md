---
name: review
description: Fresh-context brand and compliance review of generated assets, then Gate 2. Use after /generate or "/amh:review camp-NNN".
---

# /review — fresh eyes, then Gate 2

Two reviewers, run as **separate subagents** so neither sees the generation context or
each other: **brand-reviewer** → `review/brand.md`; **compliance-reviewer** →
`review/compliance.md`. Give each only the files its agent definition lists.

## Steps
0. Run `/amh:validate camp-NNN` first. Its inner loop (validator pack + fixtures,
   fix-and-rerun up to three passes) clears mechanical and narrow-judgment failures so
   the reviewers below spend their judgment on what is left. If validate ends in
   `block`, stop here and show the human.
1. Run both reviewers. Wait for both files.
2. Combine:
   - any `block` → overall `block`
   - any `revise` → overall `revise`
   - else `pass`
3. If `revise`: summarize findings per asset in one line each, run `/amh:generate` for a
   revision pass, then re-run **only the reviewer(s)** that said revise. Maximum two
   cycles; then present to the human with the unresolved findings.
4. If `block` with `requires: legal_review`: stop. Tell the human what needs legal and
   that `legal.approved.md` in the campaign folder unblocks it.
5. Present Gate 2:

```
=== GATE 2 · Assets · camp-NNN ===
Brand       [rubric]   email 4/5 · paid_social 4/5         pass
Compliance  [rubric]   claims 5/5, 0 undeclared            pass
Lint        [deterministic]                                pass
Open findings: none | …
Assets: memory/campaigns/camp-NNN/assets/{email,paid_social}.md   ← read them
→ approve camp-NNN [as <role>]   |   edit camp-NNN: <instruction>   |   reject camp-NNN
```

   Show the assets themselves on request or when the human asks "show me"; otherwise
   point at the files. Score tables are not a substitute for reading the copy — say so.
6. On approve: `/amh:approve camp-NNN g2_assets`. Then: "Next: `/amh:preflight camp-NNN`."
