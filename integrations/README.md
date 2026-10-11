# integrations — platforms by role, opt-in, file-based by default

ECC ships one MCP connector by default and makes everything else opt-in. AMH ships
none: the loop runs end to end with `file_based` everywhere, and a business declares real
platforms **by role** in `MARKETING.md`:

```yaml
integrations:
  esp: klaviyo-mcp         # or file_based
  cdp: semantic-layer      # or file_based
  ads: file_based
  analytics: file_based
```

A role is a contract (below), not a vendor. Channel-ops and the analyst call the role's
operations; a small adapter note per vendor says which MCP tool satisfies each
operation. If a connector lacks an operation, the skill degrades to the file-based
behaviour for that operation and says so — never a silent skip.

## Why roles

- Platforms' MCP servers vary and change monthly; the loop should not.
- Most official connectors (Klaviyo, HubSpot, MoEngage) **create drafts and stop short of
  sending**. That is Gate 3's shape exactly: the harness prepares, the platform holds the
  draft, a human publishes. `ship.md` records `status: drafted` plus the platform id.
- A connector that can create audiences can create the wrong audience. The fixtures run
  **before** anything is pushed, whatever the role's backend.

## Contracts

| Role | Operation | file_based behaviour | Used by |
|---|---|---|---|
| `cdp` | `resolve_audience(rule) → ids` | evaluate `audiences[].rule` over `data/customers.json` | preflight, run-fixtures |
| `cdp` | `attributes(ids) → rows` | rows from `data/customers.json` | preflight (age gate, suppression) |
| `esp` | `create_audience(name, ids)` | write `data/audience-<ch>.csv` (ids + `age_verified`) | preflight |
| `esp` | `create_draft(channel, assets, audience_ref, scheduled_for)` | write `shipped/<ch>.md`, `status: simulated` | ship |
| `esp` | `send_history(ids, days) → sends` | read `memory/send-log.jsonl` | preflight (caps) |
| `esp` | `suppression_list(rule) → ids` | from `data/customers.json` flags | preflight |
| `ads` | `create_campaign(platform, budget, creatives, audience_ref)` | write `shipped/paid_social.md`, `status: simulated` | ship |
| `analytics` | `results(campaign_id, window) → metrics` | read `data/results.<ch>.json` in the campaign folder | measure |

Every operation's result is logged to `memory/campaigns/<id>/integration-log.jsonl`
with the role, backend, operation, and a platform id when one came back.

## Vendor notes

`integrations/<vendor>.md` — one page each, written when a real connector is first
used. Each lists: the MCP server name, which tool satisfies each operation above, which
operations are unsupported (→ file_based fallback), and whether the connector can send
or only draft. See `klaviyo.md` for the shape.
