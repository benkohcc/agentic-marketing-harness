# Cellar & Co. — the worked example

A fictional family-owned online wine shop, invented for this repo. Every customer id,
product, result, and retro here is made up. Nothing is derived from a real business.

```
MARKETING.md               the context layer — validates against ../../marketing.schema.json
docs/voice-examples.md     brand reviewer anchors (brand.examples_ref)
data/products.json         4 SKUs with tasting notes, COGS, and what is (not) on file
data/inventory.json        stock status; CC-0412 is the overstock that triggers camp-004
data/customers.json        600 synthetic customers, attributes only — audiences[].rule resolves against this
data/segments.json         audience samples — ids and flags only, never people
journeys/camp-004.yaml     the live campaign's journey: send → 3-day timer → reminder → exits
memory/campaigns/          camp-001..003 complete with retros; camp-004 is the live trigger
                           (its brief.md is a draft so the fixtures have dates; delete it to
                           watch the strategist write its own)
memory/campaigns/camp-004/fixtures.yaml   10 audience cases, 4 traces, a 2,000-run fuzz
memory/instincts.jsonl     three candidate instincts mined from those retros
```

## Run the loop

Install the plugin from the repo root, then work from this directory so hooks resolve
this `MARKETING.md`:

```
cd examples/cellar-and-co
claude
> /amh:status
> /amh:brief camp-004
> approve camp-004 as marketing_lead
> /amh:criteria camp-004
> /amh:generate camp-004          # copy-lint runs on every asset write
> /amh:review camp-004            # two fresh-context reviewers, then Gate 2
> approve camp-004 as marketing_lead
> /amh:preflight camp-004
> /amh:ship camp-004              # Gate 3; send-blocker runs on the write
> approve camp-004 as marketing_ops
```

Integrations are `file_based`, so the "send" lands in `memory/campaigns/camp-004/shipped/`
and nothing leaves your machine. To see a hook refuse, try `/amh:generate camp-004`
before criteria exist, or `touch memory/HALT` before shipping.

## Without Claude

```
python3 ../../hooks/run-fixtures.py memory/campaigns/camp-004     # 30 pass, 2 skipped (no assets yet)
python3 ../../scanner/scan.py .                                   # 1 medium: G1 and G2 share an approver
```

## Try to break it

- Ask the copywriter for "a limited time only" subject line.
- Add a customer email column to the audience export.
- Schedule the send for a Friday.
- Start a new promotion brief before camp-004 has a retro (after it ships).
- Change `max_wait_days: 3` to `2` in `journeys/camp-004.yaml` and rerun the fixtures:
  the reminder now lands on a Friday and the fuzzer reports `send_outside_window`.
- Set `disjoint: [[explorers, lapsed]]` in the fixtures: 26 customers are in both, and
  the harness tells you so before anyone is emailed twice.

Each should be refused by a hook, with the reason, and the agent should not route around it.
