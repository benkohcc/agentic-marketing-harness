#!/usr/bin/env python3
"""send-blocker — the last line. Blocks any write to memory/campaigns/<id>/shipped/ when:

  * the kill switch file (MARKETING.md kill_switch.file) exists, or
  * ship.approved.md (G3) is missing or not approved, or
  * the send is outside channels.<ch>.send_window (checked against the `scheduled_for`
    front-matter field of the file being written, if present).

gate-guard covers G2 and preflight; this hook exists separately so that the kill
switch is checked by the smallest, most boring script in the repo.

Hook mode: PreToolUse on Write|Edit. CLI: send-blocker.py <shipped/<channel>.md>
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _amh import block, campaign_dir, gate_ok, load_context, ok, read_hook_payload, split_front_matter, written_file

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def main(argv):
    payload = read_hook_payload()
    hook_mode = payload is not None
    if hook_mode:
        path, content = written_file(payload)
        if path is None:
            sys.exit(0)
    else:
        if len(argv) < 2:
            print(__doc__); return 2
        path = Path(argv[1]); content = path.read_text(encoding="utf-8") if path.exists() else ""

    cdir = campaign_dir(path)
    if cdir is None or "shipped" not in path.parts:
        sys.exit(0)

    md, ctx = load_context(path)
    if ctx is None:
        block("no MARKETING.md found above this path", hook_mode)

    problems = []
    ks = ctx["kill_switch"]["file"]
    if (md.parent / ks).exists():
        problems.append(f"KILL SWITCH ACTIVE: {ks} exists (owner: {ctx['kill_switch']['owner']}). Nothing ships until it is removed.")

    if not gate_ok(cdir, "ship.approved.md"):
        problems.append("ship.approved.md (G3) missing or not approved")

    fm, _ = split_front_matter(content or "")
    ch = (fm or {}).get("channel")
    sched = (fm or {}).get("scheduled_for")
    win = ((ctx.get("channels") or {}).get(ch) or {}).get("send_window")
    if win and sched:
        try:
            dt = datetime.fromisoformat(str(sched))
            day = DAYS[dt.weekday()]
            lo, hi = win["hours"]
            if day not in win["days"] or not (lo <= dt.hour < hi):
                problems.append(f"scheduled_for {sched} is outside {ch} send_window ({', '.join(win['days'])} {lo:02d}–{hi:02d} {win['tz']})")
        except ValueError:
            problems.append(f"scheduled_for '{sched}' is not an ISO datetime")

    if problems:
        block(f"{cdir.name}: send blocked [kind: deterministic]", hook_mode, problems)
    ok(f"{cdir.name}/shipped/{path.name}: cleared to send [kind: deterministic]")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
