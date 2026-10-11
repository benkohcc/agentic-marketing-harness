# memory

Campaign-shaped memory, not chat transcripts.

```
memory/
├── campaigns/<camp-id>/   one directory per campaign; formats in docs/formats.md
├── instincts.jsonl        learned instincts with confidence and support (written by /learn)
├── send-log.jsonl         one line per recipient id per send; preflight reads it for caps
└── HALT                   the kill switch — if this file exists, nothing ships
```

This directory in the repo root is empty on purpose; a business's memory lives next to
its `MARKETING.md`. See `examples/cellar-and-co/memory/` for a populated one.

What goes where:
- What the business *means* → `MARKETING.md`
- What happened → `memory/campaigns/`
- What was learned → `memory/instincts.jsonl`, then `rules/learned/` once promoted
