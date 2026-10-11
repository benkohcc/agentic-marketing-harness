# Channel rules — SEO (owned pages and articles)

Loaded when a campaign's `channels` includes `seo`.

## Defaults for /init (overridden by MARKETING.md channels.seo)
```yaml
required_assets: [meta_title, meta_description, h1]
limits: { meta_title: 60, meta_description: 160, h1: 70 }
```

## Writing
- Meta title: primary term first, brand last, no clickbait. ≤ 60 characters or it is cut.
- Meta description: one benefit, one specific, one verb. It is ad copy for the result
  page, not a summary.
- H1 says the same thing as the meta title a different way; never identical.
- Body (when the campaign produces an article): answer the search intent in the first
  paragraph, then earn the rest. One concrete detail per paragraph, as everywhere.
- Claims in articles are claims: `claims_made` applies. Educational content about wine
  is where health-adjacent language creeps in; the compliance validator reads it all.

## Must
- Canonical URL set; internal links from at least two existing pages recorded in
  preflight or the check is `skipped`.
- Article links carry `utm_campaign=<id>` only when they point to a commerce page.
- No doorway or near-duplicate pages per campaign; one page per intent.

## Measurement
- `engaged_read_rate` inside the attribution window for `educational`; ranking changes
  are observations and arrive on their own schedule. The retro may cite them; the
  criteria may not.
