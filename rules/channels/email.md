# Channel rules — email

Loaded when a campaign's `channels` includes `email`.

## Defaults for /init (overridden by MARKETING.md channels.email)
```yaml
required_assets: [subject_a, subject_b, preview, headline, body, cta]
limits: { subject_a: 60, subject_b: 60, preview: 90, headline: 70, body: 2800, cta: 30 }
frequency_cap: { count: 3, per_days: 7 }
send_window: { days: [tue, wed, thu], hours: [9, 17], tz: <business tz> }
suppression: [unsubscribed, bounced_hard]
```

## Writing
- Subject A benefit-led, Subject B curiosity-led. Neither restates the preview.
- Preview text completes the subject; it does not repeat it.
- Headline ≤ 10 words. Body opens with the occasion or the story, not the offer.
- The offer appears once, plainly, with the end date. Scarcity only if `tone_override`
  or the brief says it is real.
- One CTA. The CTA text names the action and the object (`cta_style`).
- Body paragraphs ≤ 60 words. One concrete detail each.
- No images are described here; copy must stand alone with images blocked.

## Must
- Every link: `utm_source=email`, `utm_medium=campaign`, `utm_campaign=<id>`.
- Physical mailing address and unsubscribe link are template-level; confirm the template
  has them in preflight, do not write them into the body.
- A/B pair tested on subject only, same body, same send time.

## Preflight extras
- Render check: plain-text version reads correctly top to bottom.
- Seed list send recorded in `preflight.md` when an ESP connector exists.

## Instinct scope
When `/learn` writes an instinct from an email campaign, `scope.channels: [email]` unless
the retro says the finding was channel-independent.
