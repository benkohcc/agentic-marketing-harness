# validators — the compiler-shaped slice, as sub-agents (v0.2)

ECC gets an oracle for free: the compiler and test suite answer "is this correct?" in
seconds, deterministically, after every edit. Marketing has no such oracle, so AMH builds
the closest thing it can out of sub-agents, and is explicit about where that stops.

A validator is a sub-agent with **one narrow question**, a **written rubric**, **fresh
context** (criteria + assets only, never the generation conversation), a **structured
verdict**, and a **calibration record**. Ten narrow validators behave far more like a
test suite than one reviewer with a vibe.

## Three design rules

1. **Narrow the question until a second reader could check the answer.**
   "Is this email good?" wobbles between runs. "Does every claim in `claims_made` appear
   in `claims.substantiated` or the product record — list any that do not" is nearly a
   lookup. Every validator in `pack.yaml` is phrased the second way.
2. **Let the sub-agent write the test rather than be the test, wherever possible.**
   The `test-writer` agent reads the brief and `MARKETING.md` and emits deterministic
   fixtures (`fixtures.yaml`): audience membership assertions, journey traces, and
   copy assertions a script can run. The LLM's judgment is spent once, writing the
   check; the check then runs for free with the same answer every time. This is how a
   chunk of rubric green becomes deterministic green.
3. **Calibrate, or it is an opinion with a badge.**
   Every verdict is logged next to the campaign id. When results arrive, `/learn` scores
   each validator's predictive value in `evals/calibration.jsonl`. A validator that cannot
   separate the voice-examples "This" from "Not this" does not ship; a validator whose
   verdicts never correlate with outcomes gets its weight cut.

## What this buys

An inner loop. `/generate` → run the pack → fix what failed → rerun, up to three passes,
before any human sees the work. That is the step toward ECC's autonomy, bounded by design
rather than hope.

## What it does not buy

Proof. A compiler's green means well-formed. The pack's green means ten narrow judges
found nothing — strong evidence, still evidence. Every validator reports `kind: rubric`;
the fixtures it writes report `kind: deterministic`. Never collapse the two.

## Failure modes, and the mitigation each one gets

| Failure | Mitigation |
|---|---|
| Judge shares the generator's blind spots | fresh context always; `model:` override in `pack.yaml` for a different model on blocking validators |
| Copywriter learns to write for the judge (Goodhart) | outcome calibration; a human audits a sample of validator verdicts, not just copy |
| Content steers the validator | asset text is data: validators are told so, and the compliance validator treats any instruction-like text in an asset as a finding |
| Verdict drift between runs | structured output, temperature 0 where the runtime allows, two runs with disagreement → `flag` not `pass` |

## Files

```
validators/
├── README.md        this
├── pack.yaml        the validators: id, question, inputs, rubric, verdict shape, blocks?
└── fixtures.md      what test-writer emits and how preflight runs it
agents/test-writer.md    writes fixtures from the brief + MARKETING.md
agents/validator.md      runs ONE pack entry in fresh context
skills/validate/         runs the pack + fixtures; /review calls it before Gate 2
evals/calibration.jsonl  verdicts next to outcomes
```
