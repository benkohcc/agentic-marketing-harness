---
# TEMPLATE — copy to your repo root as MARKETING.md and replace every value.
# Validate with: python3 hooks/validate-marketing-md.py MARKETING.md
# This is the Cellar & Co. example with its values left in as worked illustrations.
amh_version: "0.1"

business:
  name: Cellar & Co.
  vertical: dtc wine
  model: dtc
  markets: [US]
  currency: USD
  fiscal_year_start: "01-01"

brand:
  voice: [knowledgeable, warm, specific]
  register: second_person
  never_say:
    - "act now"
    - "limited time only"
    - "world's best"
    - "don't miss out"
    - "click here"
  avoid:
    - wine jargon without a plain-language gloss
    - superlatives without substance
    - urgency the inventory does not justify
  embrace:
    - sensory language tied to a specific wine
    - the winemaker, the vineyard, the vintage, the occasion
    - one concrete detail per paragraph
  cta_style: "specific verb + specific object — 'Reserve your case', 'Explore the Loire' — never 'Shop now'"
  proof_standard: "a claim about a wine must trace to the tasting note, the producer's technical sheet, or a named critic score on file"
  reading_level_max: 9
  examples_ref: docs/voice-examples.md

audiences:
  - id: collectors
    name: Collectors
    definition: "3+ orders in 12 months and average order value above $180; or any purchase from the allocation list"
    rule: "(orders_12m >= 3 and aov > 180) or allocation_list == true"
    exclusion_rules: ["allocation_opt_out == true", "last_order_days_ago >= 180"]
    size_hint: 2400
    fit: [limited_allocation, new_arrival, pre_order]
    exclusions: ["anyone who opted out of allocation emails"]
  - id: explorers
    name: Explorers
    definition: "2+ orders across 3+ distinct regions in 12 months"
    rule: "orders_12m >= 2 and regions_12m >= 3"
    size_hint: 6100
    fit: [new_arrival, promotion, educational, bundle]
  - id: occasion_buyers
    name: Occasion buyers
    definition: "orders cluster within 10 days of a gifting holiday; otherwise dormant"
    rule: "gift_cluster == true and orders_12m <= 2"
    size_hint: 9800
    fit: [seasonal, bundle]
    frequency_cap_override:
      email: { count: 2, per_days: 30 }
  - id: lapsed
    name: Lapsed
    definition: "last order 180–540 days ago, not unsubscribed"
    rule: "last_order_days_ago >= 180 and last_order_days_ago <= 540 and unsubscribed == false"
    exclusion_rules: ["open_support_ticket == true", "last_emailed_days_ago < 14"]
    size_hint: 7300
    fit: [winback]
    exclusions: ["customers with an open support ticket", "anyone emailed in the last 14 days"]

campaign_types:
  - id: new_arrival
    default_channels: [email, social]
    primary_metric: revenue_per_recipient
    lead_time_days: 5
    default_duration_days: 14
    discount_allowed: false
  - id: promotion
    default_channels: [email, paid_social, paid_search]
    primary_metric: contribution_margin
    lead_time_days: 7
    default_duration_days: 10
    discount_allowed: true
    max_discount_pct: 20
  - id: limited_allocation
    default_channels: [email]
    primary_metric: allocation_sell_through
    lead_time_days: 3
    default_duration_days: 5
    discount_allowed: false
    tone_override: "quieter and more direct; scarcity is real here, so state it plainly and once"
  - id: seasonal
    default_channels: [email, paid_social, social]
    primary_metric: revenue_per_recipient
    lead_time_days: 21
    default_duration_days: 21
    discount_allowed: true
    max_discount_pct: 15
  - id: winback
    default_channels: [email]
    primary_metric: reactivation_rate
    lead_time_days: 5
    default_duration_days: 14
    discount_allowed: true
    max_discount_pct: 15
  - id: educational
    default_channels: [email, social, seo]
    primary_metric: engaged_read_rate
    lead_time_days: 10
    default_duration_days: 30
    discount_allowed: false
  - id: bundle
    default_channels: [email, paid_social]
    primary_metric: contribution_margin
    lead_time_days: 7
    default_duration_days: 14
    discount_allowed: true
    max_discount_pct: 12
  - id: pre_order
    default_channels: [email]
    primary_metric: pre_order_units
    lead_time_days: 14
    default_duration_days: 21
    discount_allowed: false
    requires_legal_review: true

channels:
  email:
    enabled: true
    required_assets: [subject_a, subject_b, preview, headline, body, cta]
    limits: { subject_a: 60, subject_b: 60, preview: 90, headline: 70, body: 2800, cta: 30 }
    frequency_cap: { count: 3, per_days: 7 }
    send_window: { days: [tue, wed, thu, sat], hours: [9, 18], tz: America/New_York }
    suppression: [unsubscribed, bounced_hard, age_unverified, open_support_ticket]
    rules_pack: rules/channels/email
  paid_social:
    enabled: true
    required_assets: [primary_text, headline, description]
    limits: { primary_text: 125, headline: 40, description: 30 }
    rules_pack: rules/channels/paid-social
  paid_search:
    enabled: true
    required_assets: [headline_1, headline_2, headline_3, description_1, description_2]
    limits: { headline_1: 30, headline_2: 30, headline_3: 30, description_1: 90, description_2: 90 }
    rules_pack: rules/channels/paid-search
  social:
    enabled: true
    required_assets: [instagram_caption, facebook_caption, pinterest_description]
    limits: { instagram_caption: 2200, facebook_caption: 500, pinterest_description: 500 }
    rules_pack: rules/channels/social-organic
  seo:
    enabled: true
    required_assets: [meta_title, meta_description, h1]
    limits: { meta_title: 60, meta_description: 160, h1: 70 }
    rules_pack: rules/channels/seo

metrics:
  catalog:
    - id: revenue_per_recipient
      name: Revenue per recipient
      definition: "attributed revenue ÷ delivered recipients, within the attribution window"
      direction: up
      unit: USD
    - id: contribution_margin
      name: Contribution margin
      definition: "attributed revenue − COGS − discount − media spend"
      direction: up
      unit: USD
    - id: allocation_sell_through
      name: Allocation sell-through
      definition: "units sold ÷ units allocated by end_date"
      direction: up
      unit: pct
    - id: reactivation_rate
      name: Reactivation rate
      definition: "lapsed recipients who order within the window ÷ delivered"
      direction: up
      unit: pct
    - id: engaged_read_rate
      name: Engaged read rate
      definition: "recipients with 8+ seconds on the linked article ÷ delivered"
      direction: up
      unit: pct
    - id: pre_order_units
      name: Pre-order units
      definition: "paid pre-orders by end_date"
      direction: up
      unit: units
    - id: unsubscribe_rate
      name: Unsubscribe rate
      definition: "unsubscribes ÷ delivered"
      direction: down
      unit: pct
    - id: complaint_rate
      name: Spam complaint rate
      definition: "complaints ÷ delivered"
      direction: down
      unit: pct
  guardrails:
    - { metric: unsubscribe_rate, threshold: 0.5, action: block }
    - { metric: complaint_rate, threshold: 0.08, action: block }
  attribution_window_days: 7
  minimum_sample: 500

claims:
  substantiated:
    - claim: "Family-owned since 1998"
      evidence: "docs/claims/incorporation.pdf"
    - claim: "Ships in 100% recycled packaging"
      evidence: "docs/claims/packaging-supplier-cert-2026.pdf"
      expires: "2027-03-31"
  prohibited:
    - any health benefit of wine
    - "'organic' or 'biodynamic' without the producer's certification on file"
    - critic scores not on file
    - price comparisons to named competitors
  requires_legal:
    - sweepstakes or giveaway mechanics
    - any claim about shipping legality in a specific state
    - futures or pre-order terms

compliance:
  packs:
    - rules/common
    - rules/verticals/dtc
    - rules/verticals/alcohol-us
  consent_basis: "express opt-in at checkout or newsletter signup; age attestation 21+ required before any marketing contact"
  age_gate: 21
  data_handling:
    - no PII in exported audience files; ids only
    - no audience file leaves memory/ without a gate artifact next to it

gates:
  g1_brief:
    approver: marketing_lead
    artifact: brief.approved.md
    timeout_hours: 48
  g2_assets:
    approver: marketing_lead
    artifact: assets.approved.md
    timeout_hours: 48
  g3_ship:
    approver: marketing_ops
    artifact: ship.approved.md
    timeout_hours: 24
  escalation: founder

memory:
  retro_required: true
  retro_due_days: 10
  instinct_promotion_min_support: 3
  instinct_min_confidence: 0.7

integrations:
  cdp: semantic-layer
  esp: file_based
  ads: file_based

kill_switch:
  file: memory/HALT
  owner: marketing_ops
  on_trigger:
    - pause all scheduled sends and ad sets
    - write memory/incidents/<timestamp>.md with the reason
    - notify founder and marketing_lead
---

## Who we are

Cellar & Co. is a family-owned online wine shop founded in 1998, selling about 400
wines from small producers in France, Italy, Spain, and the US West Coast to customers
in the 38 states we can legally ship to. We are not the cheapest and we are not the
biggest. Our customers come to us because someone on our team has tasted every bottle
we sell and can tell them, in plain language, what it is like and when to open it.

We send email like a knowledgeable friend would: not often, never breathlessly, and
always about a specific wine rather than a "sale."

## Positioning

For people who like wine more than they know about it, Cellar & Co. is the online shop
that tastes everything first, so you can buy with the confidence of a collector without
the homework.

The alternatives our customers actually consider are the large discount retailers (we
lose on price, win on curation), the wine clubs (we lose on convenience, win on choice),
and their local shop (we lose on immediacy, win on range and on the notes).

## Voice, with examples

**Not this:** "Don't miss out on our incredible Bordeaux sale — act now!"
**This:** "We bought more 2019 Médoc than we should have. Until Sunday, it's $4 a bottle less than it ought to be."

**Not this:** "This stunning, complex, elegant wine will blow you away."
**This:** "Cherries, a little pencil shaving, and tannins that behave themselves. Open it with roast chicken."

**Not this:** "Shop now"
**This:** "Reserve your six"

**Not this:** "Our award-winning selection"
**This:** "Nine of these forty wines are ones our team re-ordered for themselves this year."

## Audience notes

Collectors read everything and resent being sold to. Give them the allocation facts and
the technical sheet and get out of the way. Explorers respond to a story about a place
they haven't tried; lead with the region, not the grape. Occasion buyers need the date
in the subject line and a gift note in the body, and they do not want to hear from us in
February. Lapsed customers remember what they bought — the winback that works is "the
2021 of the thing you liked is in," not a coupon.

## Operating notes

Fulfillment lead time is two business days; nothing ships Friday because of heat and
weekend transit. No sends the week of Thanksgiving through the following Monday — the
warehouse is at capacity and late deliveries cost us more than the campaign makes. Allocation
campaigns go to collectors 24 hours before anyone else, always.
