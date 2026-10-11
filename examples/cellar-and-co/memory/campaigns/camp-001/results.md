---
campaign_id: camp-001
kind: outcome
measured_at: 2026-06-27
window_days: 7
sample: 5890
primary: { metric: contribution_margin, value: 3140, threshold: 2000, met: true }
secondary: [{ metric: revenue_per_recipient, value: 1.12, threshold: 0.90, met: true }]
guardrails: [{ metric: unsubscribe_rate, value: 0.18, threshold: 0.5, breached: false }]
verdict: success
---
## Observations
Subject A (honest over-purchase) 31% opens vs Subject B (discount-led) 24%. Revenue per recipient A $1.31 vs B $0.93.
