# CLAUDE.md — Agentic Marketing Harness

You are working inside the AMH repo. Read this before touching anything.

## What this repo is

A harness for running marketing campaigns through AI agents: a loop, three human gates,
hooks that enforce them, and a schema-validated context layer (`MARKETING.md`). It is
modeled on Everything Claude Code (ECC). README.md is the manifesto; it is the source of
truth for intent. docs/ is the source of truth for formats and the spec.

## Design decisions (do not relitigate without updating README.md)

1. **Criteria before copy.** `/generate` refuses to run unless `criteria.md` exists for the
   campaign. The measurement plan and rubrics are the "tests."
2. **Enforcement is code.** Anything that must not happen is a hook in `hooks/` that exits
   non-zero. Prose in a skill is a suggestion; never rely on it for a hard rule.
3. **Three kinds of green.** Every check reports `deterministic`, `rubric`, or `outcome`.
   Never collapse them into one "verified."
4. **Fresh-eyes review.** Reviewer agents receive only the criteria and the asset. They
   never see the generation conversation.
5. **MARKETING.md is intent, not log.** Learned instincts are promoted into
   `rules/learned/`, never written into MARKETING.md front matter.
6. **File-based by default.** Every integration is optional. With no MCP connectors, the
   loop still runs end to end, writing to `memory/campaigns/<id>/`. A "send" with
   `esp: file_based` writes to `shipped/`.
7. **Small and legible.** If a file cannot be read in five minutes, split it.
8. **Validators are narrow, fresh, and calibrated.** One question each
   (`validators/pack.yaml`), inputs limited to what the question needs, verdicts logged
   to `evals/calibration.jsonl`. The test-writer spends judgment once writing
   `fixtures.yaml`; preflight runs it mechanically. Rubric green and deterministic green
   stay labeled.
9. **Fictional brands only.** Example data is Cellar & Co. (invented). Never add real
   customer data, real brand guidelines, or anything traceable to a real employer.

## Layout

```
MARKETING.md            context layer — schema in marketing.schema.json, spec in docs/
agents/                 subagents (strategist, test-writer, copywriter, validator, brand-reviewer,
                        compliance-reviewer, analyst, channel-ops)
skills/<name>/SKILL.md  one per loop step: init brief criteria generate validate review preflight ship
                        measure retro learn approve status
validators/             pack.yaml (10 narrow validators), fixtures.md (what test-writer emits)
rules/common            always loaded
rules/channels/<ch>.md  loaded when a campaign uses that channel
rules/verticals/<v>.md  loaded per MARKETING.md compliance.packs
rules/learned/          promoted instincts (written by /learn, reviewed by a human)
hooks/                  python scripts + hooks.json + run-fixtures.py + selftest.py; see hooks/README.md
scanner/scan.py         AgentShield analogue: config, hooks, assets, data, memory audit
integrations/           role contracts (cdp, esp, ads, analytics) + vendor notes; file_based by default
journeys/<id>.yaml      a campaign's journey as a state machine (docs/journeys.md); simulated by run-fixtures
bin/amh-setup.sh        v0 installer: prerequisites, self-check, install commands
memory/campaigns/<id>/  per-campaign state (formats in docs/formats.md)
memory/instincts.jsonl  learned instincts with confidence and support
evals/                  rubrics, calibration.jsonl (validator verdicts), validator-weights.json
examples/cellar-and-co/ a complete fictional business: MARKETING.md + data + past retros
```

## Working conventions

- Campaign ids are `camp-NNN`. Everything about a campaign lives in
  `memory/campaigns/camp-NNN/`; nothing about a campaign lives anywhere else.
- Gate approval is a file: `brief.approved.md`, `assets.approved.md`, `ship.approved.md`.
  A human writes it (or says "approve camp-NNN" and the skill writes it on their behalf
  with their name). Hooks check for the file; they do not parse chat.
- Formats in docs/formats.md are fixed. Skills write them, hooks and later skills parse
  them. Changing a format means updating the doc, the writer, and every reader.
- Hooks read `MARKETING.md` by walking up from the file being written. Run the demo from
  `examples/cellar-and-co/` so that resolution finds the example's context layer.
- Python only in hooks/ and scanner/. No dependencies beyond `pyyaml` and `jsonschema`.
- When a hook blocks you, do not work around it. Fix the input or ask the human.

## Testing

```
bash bin/amh-setup.sh            # everything below, plus prerequisites
python3 hooks/validate-marketing-md.py examples/cellar-and-co/MARKETING.md
python3 hooks/selftest.py        # 33 cases: hooks, run-fixtures, scanner
python3 hooks/run-fixtures.py examples/cellar-and-co/memory/campaigns/camp-004
python3 scanner/scan.py examples/cellar-and-co
```

All must pass before any commit.

## Roadmap pointers

README.md → Roadmap. v0.1 and v0.2 components are all in place as files and scripts;
the remaining step is the first end-to-end run in Claude Code, which will find skill
wording the model reads differently than intended. Not yet: a real vendor connector
exercised live, other-harness adapters, the outcome ledger.
