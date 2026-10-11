# Klaviyo — vendor note (template; verify tool names against the live server)

Role: `esp`. MCP server: Klaviyo's official server (live since 2025). Declared in
`MARKETING.md` as `integrations: { esp: klaviyo-mcp }`.

Before relying on any row below, channel-ops lists the server's tools at run time and
records the mapping it actually used in `integration-log.jsonl`. Tool names here are
the expected shape, not a guarantee; connectors change.

| Operation | Expected tool | Notes |
|---|---|---|
| `create_audience(name, ids)` | list / segment creation tool | ids only; the export has already passed pii-guard |
| `create_draft(channel, assets, audience_ref, scheduled_for)` | campaign creation tool | Klaviyo's connector creates campaigns for human review; publishing stays in Klaviyo → `status: drafted` |
| `send_history(ids, days)` | campaign/flow performance tools | may be aggregate only; if per-recipient history is unavailable, fall back to `memory/send-log.jsonl` and say so |
| `suppression_list(rule)` | profile / list tools | unsubscribed and bounced from the platform; support-ticket flags stay file-based |
| `results(campaign_id, window)` | performance tools | role `analytics` can also point here |

Unsupported → file_based: anything not found at run time.

Can it send? As of the connector descriptions we have seen, it drafts and leaves
publishing to a human. If a future version can send, `send-blocker` and Gate 3 still sit
in front of it; nothing in AMH changes.

Sources to re-check before use: the Klaviyo MCP documentation and the server's own
tool listing.
