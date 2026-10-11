# Channel rules — paid social (Meta, Pinterest, TikTok paid)

Loaded when a campaign's `channels` includes `paid_social`.

## Defaults for /init (overridden by MARKETING.md channels.paid_social)
```yaml
required_assets: [primary_text, headline, description]
limits: { primary_text: 125, headline: 40, description: 30 }
```

## Writing
- Primary text leads with the single strongest benefit in the first 40 characters —
  that is what survives truncation.
- Headline is a noun phrase or a short imperative; never a question that the ad does
  not answer.
- Description is a fact, not a slogan: price, date, quantity, place.
- Write for a cold audience unless the brief's audiences are all existing customers.
  Cold copy explains who you are in five words.
- No claim in an ad that is not also in the email for the same campaign. Ads get the
  closest scrutiny; keep the claim set identical.

## Must
- Landing URL carries `utm_source=<platform>`, `utm_medium=paid_social`,
  `utm_campaign=<id>`.
- Budget in `brief.budget.media` is the cap across ad sets. Channel-ops records the per-set
  split in `shipped/paid_social.md`.
- Age-gated verticals: audience targeting minimum age = `compliance.age_gate`, and the
  platform's own category restrictions apply on top (see vertical pack).

## Preflight extras
- Creative spec present (aspect ratios, safe zones) or `skipped` with "no creative" —
  never `pass` without one.
- Platform policy category checked against the vertical pack's list.

## Measurement
- Paid results are reported by platform attribution **and** by UTM-attributed site
  outcomes; `results.md` records both and says which the criteria used.
