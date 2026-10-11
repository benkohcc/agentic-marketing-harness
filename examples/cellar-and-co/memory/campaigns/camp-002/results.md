---
campaign_id: camp-002
kind: outcome
measured_at: 2026-08-05
window_days: 7
sample: 7044
primary: { metric: reactivation_rate, value: 1.1, threshold: 2.5, met: false }
secondary: []
guardrails: [{ metric: unsubscribe_rate, value: 0.46, threshold: 0.5, breached: false }]
verdict: miss
---
## Observations
Unsubscribe rate nearly breached the guardrail. Reactivations skewed to customers lapsed < 270 days; > 400 days barely moved.
