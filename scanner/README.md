# scanner — AMH's AgentShield

ECC's AgentShield scans prompts, hooks, MCP config, permissions and secrets. AMH's
scanner does the marketing equivalent, deterministically, over a whole business
directory rather than one campaign:

| Area | Looks for |
|---|---|
| config | gate approver reuse (one person can walk a campaign through two gates), kill switch with no owner, an enabled email channel with no cap or window, discounts above 30%, audiences without a `rule`, expired substantiated claims, empty `never_say` or `prohibited` lists, missing compliance packs |
| hooks | a hook not registered in `hooks.json`, or registered but missing on disk |
| assets | `never_say` and prohibited text, instruction-like text (prompt injection), links without the campaign UTM, SKUs mentioned that are not in the brief |
| data | email addresses, phone numbers, or person-identifying fields in any `.csv/.json/.jsonl` under `memory/` or `data/` (keys only — a channel named "email" is not a hit) |
| memory | campaigns shipped without a retro past `retro_due_days`, gate artifacts whose `approved_by` does not name the gate's approver role, approvals without a timestamp |

```
python3 scanner/scan.py examples/cellar-and-co            # exit 1 on any high finding
python3 scanner/scan.py examples/cellar-and-co --json
```

Run it before a demo, in CI, and whenever `MARKETING.md` changes. It is deliberately a
different shape from the hooks: hooks refuse one write as it happens; the scanner audits
everything that already exists. Both report `kind: deterministic`.

On the shipped example it finds one medium: Gate 1 and Gate 2 share the `marketing_lead`
approver. That is a real observation about Cellar & Co.'s setup, left in so the scanner
has something true to say.

Tested in `hooks/selftest.py` (five cases: clean example, never_say + injection in an
asset, an email column in a data file, a kill switch without owner, a gate artifact that
does not name the approver role).
