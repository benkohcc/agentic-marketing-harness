Coding agents got a harness. Marketing agents got a prompt library. That's why they fail.

Every AI marketing demo ends the same way. The agent writes a decent email. Someone asks: would you send that? No. Not because the copy is bad, but because nobody can say if the claim was substantiated, if that segment was emailed yesterday, or if the last three campaigns like it taught us anything.

Software solved this with a harness, not a better model: conventions in a file, tests before code, reviewers reading the diff cold, hooks that block the commit. Everything Claude Code (ECC) is the best example.

So I built the marketing version. Agentic Marketing Harness (AMH):

→ MARKETING.md is the context layer: audiences, claims, gates, metrics. Schema-validated so hooks can refuse, not suggest.
→ Criteria before copy. The threshold and the rubric exist before a word is generated.
→ Hooks that block a banned phrase, an unsubstantiated claim, a Friday send, a missing approval.
→ Audience rules and journeys as config, so a script can test them, including a 2,000-run fuzz.
→ Three human gates. The agent prepares; a person approves; the file is the record.

First thing the fuzzer caught: a reminder timer that would have sent on a Friday, outside the send window. Before anyone was emailed.

Open source, MIT, built on a fictional wine shop. It hasn't run a real campaign yet. That's next, and I'll post what breaks.

Where is this wrong?

github.com/benkohcc/agentic-marketing-harness

#AgenticMarketing #MarTech #AIAgents
