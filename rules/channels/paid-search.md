# Channel rules — paid search (Google, Microsoft)

Loaded when a campaign's `channels` includes `paid_search`.

## Defaults for /init (overridden by MARKETING.md channels.paid_search)
```yaml
required_assets: [headline_1, headline_2, headline_3, description_1, description_2]
limits: { headline_1: 30, headline_2: 30, headline_3: 30, description_1: 90, description_2: 90 }
```

## Writing
- Headlines are independently readable: the platform combines them in any order. Never
  write a headline that only makes sense after another.
- Headline 1 carries the strongest benefit in ≤ 30 characters; headline 2 names the
  product or category; headline 3 carries the offer or the proof.
- Descriptions are facts: price, quantity, date, place. One verb each.
- Match the searcher's words. If the keyword group is "bordeaux wine delivery", the word
  "delivery" appears in a headline.
- Same claim set as the campaign's email. No claim appears only in an ad.

## Must
- Landing URL: `utm_source=google` (or `microsoft`), `utm_medium=paid_search`,
  `utm_campaign=<id>`.
- Landing page carries the age gate where `compliance.age_gate` is set.
- Negative keywords on file for the campaign type (the brief lists them or inherits the
  type default); preflight records their presence.
- Budget in `brief.budget.media` is shared with paid social when both run; the brief
  states the split.

## Preflight extras
- Ad-group ↔ keyword ↔ landing page relevance recorded as a check (`skipped` if no
  connector can read the account; never `pass` unverified).
- Platform policy category (alcohol, finance, health) declared where the vertical pack
  requires it.

## Measurement
- Report platform conversions **and** UTM-attributed site outcomes; `results.md` says
  which the criteria used. Search is last-click heavy; the retro notes cannibalisation
  of brand terms when the brief ran brand keywords.
