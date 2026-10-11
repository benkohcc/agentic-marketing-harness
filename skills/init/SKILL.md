---
name: init
description: Create or upgrade MARKETING.md for this business by interview, then validate it. Use when there is no MARKETING.md, when the user says "set up AMH", or "/amh:init".
---

# /init — build the context layer

Goal: a `MARKETING.md` in the current directory that passes
`hooks/validate-marketing-md.py`. Nothing else in the harness works without it.

## If MARKETING.md exists
Run the validator. If valid, report the counts and stop. If invalid, show the problems
and offer to fix each one, asking only for what is missing.

## If it does not exist
Interview in this order, one block at a time, and show the YAML you are about to write
before moving on. Prefer concrete examples over definitions. Start from
`templates/MARKETING.md` and replace values; never leave Cellar & Co. values behind.

1. **business** — name, what you sell, to whom, in which countries, in what currency.
2. **brand** — "Paste two emails you were proud of and one you regret." Derive `voice`
   (2–5 adjectives), `register`, `never_say` (ask: "words your team would veto on sight"),
   `cta_style`, `proof_standard`. Write the body section **Voice, with examples** from
   the pasted emails as Not this / This pairs.
3. **audiences** — "Who are the three or four kinds of customer you actually think
   about?" Each needs an id, a definition in words, and who must never be targeted.
4. **campaign_types** — "What kinds of campaigns do you run?" Fill defaults; ask about
   discounts explicitly: allowed, and the ceiling.
5. **channels** — only the ones they use. Required assets and limits come from
   `rules/channels/<ch>.md` defaults; frequency cap and send window from them.
6. **metrics** — "When a campaign works, what number moved?" Define it with a
   denominator. Ask for the one guardrail they would stop a campaign over.
7. **claims** — "What do you say about yourselves that you could prove in court?" and
   "What are you not allowed to say?"
8. **compliance** — choose packs from `rules/verticals/` by vertical and markets; confirm
   consent basis and any age gate.
9. **gates** — who approves briefs, assets, and sends. Role names, not people.
10. **memory**, **kill_switch** — accept defaults unless they object.

Write the five body sections. Run the validator. Fix until it passes. Then say:
"MARKETING.md is valid. Try `/amh:brief` with a request, or drop a trigger into
memory/campaigns/."
