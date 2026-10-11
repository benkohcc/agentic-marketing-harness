#!/usr/bin/env bash
# amh-setup — v0 installer. Checks prerequisites, runs the harness's own tests, and
# prints the Claude Code install commands. No network, no writes outside this repo.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

say() { printf '%s\n' "$*"; }
ok()  { printf '  \033[32m✓\033[0m %s\n' "$*"; }
bad() { printf '  \033[31m✗\033[0m %s\n' "$*"; }

say "AMH setup — $ROOT"
say ""
say "Prerequisites"
command -v python3 >/dev/null && ok "python3 $(python3 --version 2>&1 | cut -d' ' -f2)" || { bad "python3 missing"; exit 1; }
if python3 -c "import yaml, jsonschema" 2>/dev/null; then ok "pyyaml + jsonschema"; else
  say "  installing pyyaml + jsonschema for this python…"
  python3 -m pip install --quiet --user pyyaml jsonschema 2>/dev/null || python3 -m pip install --quiet --break-system-packages pyyaml jsonschema
  python3 -c "import yaml, jsonschema" && ok "pyyaml + jsonschema" || { bad "could not import pyyaml/jsonschema"; exit 1; }
fi
command -v claude >/dev/null && ok "claude $(claude --version 2>/dev/null | head -1)" || say "  · claude CLI not on PATH (fine for the checks below; needed to run the loop)"

say ""
say "Self-check"
python3 hooks/validate-marketing-md.py examples/cellar-and-co/MARKETING.md >/dev/null && ok "example MARKETING.md validates" || { bad "example MARKETING.md invalid"; exit 1; }
if python3 hooks/selftest.py >/tmp/amh-selftest.log 2>&1; then ok "$(tail -1 /tmp/amh-selftest.log)"; else bad "self-test failed — see /tmp/amh-selftest.log"; exit 1; fi
python3 hooks/run-fixtures.py examples/cellar-and-co/memory/campaigns/camp-004 >/dev/null && ok "camp-004 fixtures pass" || { bad "camp-004 fixtures fail"; exit 1; }
python3 scanner/scan.py examples/cellar-and-co >/dev/null && ok "scanner: no high findings on the example" || { bad "scanner found high findings"; exit 1; }

say ""
say "Install into Claude Code (pick one)"
say "  A. plugin, from this checkout:   claude --plugin-dir \"$ROOT\""
say "  B. marketplace:                  /plugin marketplace add <your-github-user>/agentic-marketing-harness"
say "                                   /plugin install amh@amh"
say ""
say "Then run the worked example"
say "  cd \"$ROOT/examples/cellar-and-co\" && claude"
say "  > /amh:status"
say "  > /amh:brief camp-004"
say ""
say "Your own business"
say "  mkdir my-brand && cd my-brand && claude"
say "  > /amh:init          # interviews you into a valid MARKETING.md"
