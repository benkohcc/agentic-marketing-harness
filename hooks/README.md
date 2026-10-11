# hooks

Enforcement lives here, as scripts that exit non-zero. Prose in a skill is a suggestion;
a hook is a rule. Every hook reports its kind — all of these are `deterministic`.

| Hook | Fires on | Blocks when |
|---|---|---|
| `validate-marketing-md.py` | SessionStart | front matter fails `marketing.schema.json`, a cross-reference dangles, or a required body heading is missing |
| `gate-guard.py` | Write/Edit under `memory/campaigns/<id>/` | the prerequisite gate artifact for that file is missing or rejected: `criteria.md` needs G1; `assets/*` needs G1 + `criteria.md`; `preflight.md` needs G2; `shipped/*` needs G2 + preflight pass + G3. Also blocks a new `brief.md` when `memory.retro_required` and the last shipped campaign of that type has no retro |
| `copy-lint.py` | Write/Edit of `assets/<channel>.md` | a `brand.never_say` phrase or `claims.prohibited` text appears, a channel limit is exceeded, a required asset is missing, body reading level > `brand.reading_level_max`, or a link lacks `utm_campaign=<id>` |
| `pii-guard.py` | Write/Edit of `.csv/.json/.jsonl` under a campaign | an email, phone, or person-identifying field is present — audience files carry ids only |
| `send-blocker.py` | Write/Edit under `shipped/` | `kill_switch.file` exists, G3 is missing, or `scheduled_for` is outside the channel `send_window` |
| `run-fixtures.py` | called by /preflight and /validate (not a write hook) | any audience case, disjointness, size-share, journey structural check, trace, property fuzz, or copy assertion in `fixtures.yaml` fails |

`hooks.json` registers the write hooks for the Claude Code plugin; `run-fixtures.py` is
invoked by skills. In hook mode a block is exit 2
with the reason on stderr, which Claude Code feeds back to the model; in CLI mode it is
exit 1.

## Running them

```
python3 hooks/validate-marketing-md.py examples/cellar-and-co/MARKETING.md
python3 hooks/selftest.py                     # 33 expectations: hooks, run-fixtures, scanner
python3 hooks/run-fixtures.py examples/cellar-and-co/memory/campaigns/camp-004
echo '{"tool_name":"Write","tool_input":{"file_path":"memory/campaigns/camp-001/criteria.md","content":"---\n---"}}' | python3 hooks/gate-guard.py
```

## Resolution

Hooks find `MARKETING.md` by walking up from the file being written (or `AMH_MARKETING_MD`
if set). Campaign state is recognised by the path segment `memory/campaigns/<id>/`. This
is why the demo runs from `examples/cellar-and-co/`.

## Adding a hook

1. Import from `_amh.py`; read the payload with `read_hook_payload()`.
2. Exit 0 fast for anything that is not your business. Hooks run on every Write.
3. Block with `block(reason, hook_mode, lines)`; state the kind in the reason.
4. Add passing and failing cases to `selftest.py`. No test, no hook.
