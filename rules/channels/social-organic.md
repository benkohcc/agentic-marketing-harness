# Channel rules — organic social (Instagram, Facebook, Pinterest, TikTok)

Loaded when a campaign's `channels` includes `social`.

## Defaults for /init (overridden by MARKETING.md channels.social)
```yaml
required_assets: [instagram_caption, facebook_caption, pinterest_description]
limits: { instagram_caption: 2200, facebook_caption: 500, pinterest_description: 500 }
```

## Writing
- Instagram: story first, product second. The first line stands alone (it is what shows
  before "more"). Hashtags at the end, 5–10, none in the body, none that are generic
  (`#wine`) when a specific one exists (`#hautmedoc`).
- Facebook: direct. The offer and the date in the first sentence; link in the post, not
  the comments.
- Pinterest: written for search — the occasion, the pairing, the region, in nouns.
  Description ≠ caption; do not paste one into the other.
- TikTok (when enabled): the first three seconds are a question or a provocation; the
  caption adds the fact the video left out.
- Organic is where `brand.embrace` lives: the winemaker, the vineyard, the specific
  bottle. No discount-led organic post unless the campaign type is `promotion`.

## Must
- Links: `utm_source=<platform>`, `utm_medium=social`, `utm_campaign=<id>`.
- Alcohol and other age-gated verticals: platform age-restriction set on the account and
  recorded in preflight; no content that appeals to minors (see vertical pack).
- Image/video spec present or preflight records `skipped: no creative` — never `pass`.

## Scheduling
- `send_window` applies: an organic post is a send. Preflight checks the scheduled time
  against the channel window; the kill switch halts scheduled posts too.

## Measurement
- Engaged reach and saves for `educational`; UTM-attributed outcomes for `promotion`.
  Follower counts are observations, never a primary metric.
