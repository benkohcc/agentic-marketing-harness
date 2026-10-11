#!/usr/bin/env python3
"""gate-guard — nothing moves to the next loop step without the previous gate's artifact.

Prerequisites, keyed on what is being written inside memory/campaigns/<id>/:

  criteria.md          requires brief.approved.md (decision: approved)
  assets/*             requires brief.approved.md AND criteria.md
  review/*             requires assets/ to contain at least one file
  preflight.md         requires assets.approved.md
  shipped/*            requires assets.approved.md AND preflight.md verdict: pass AND ship.approved.md
                       (send-blocker additionally checks the kill switch)

Also enforces memory.retro_required: writing a new brief.md for campaign type T is blocked
if the most recent *completed* campaign of type T has no retro.md.

Hook mode: PreToolUse on Write|Edit. CLI: gate-guard.py <path-about-to-be-written>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _amh import (block, campaign_dir, gate_ok, load_context, ok, read_hook_payload,
                  split_front_matter, written_file)


def rel(path: Path, cdir: Path):
    return path.resolve().relative_to(cdir.resolve()).as_posix()


def check_retro_required(cdir: Path, content: str, fm_ctx: dict):
    mem = fm_ctx.get("memory", {})
    if not mem.get("retro_required"):
        return None
    fm, _ = split_front_matter(content or "")
    ctype = (fm or {}).get("campaign_type")
    if not ctype:
        return None
    campaigns_root = cdir.parent
    latest = None
    for other in sorted(campaigns_root.iterdir()):
        if other == cdir or not other.is_dir():
            continue
        b = other / "brief.md"
        if not b.exists():
            continue
        bfm, _ = split_front_matter(b.read_text(encoding="utf-8"))
        if (bfm or {}).get("campaign_type") != ctype:
            continue
        if (other / "shipped").exists() or (other / "results.md").exists():
            latest = other  # sorted ascending → last one wins
    if latest and not (latest / "retro.md").exists():
        return f"memory.retro_required is true and {latest.name} ({ctype}) shipped without a retro.md — run /retro {latest.name} first"
    return None


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
        path, content = Path(argv[1]), (Path(argv[1]).read_text(encoding="utf-8") if Path(argv[1]).exists() else "")

    cdir = campaign_dir(path)
    if cdir is None:
        sys.exit(0)  # not a campaign artifact; not our business

    md, ctx = load_context(path)
    if ctx is None:
        block("no MARKETING.md found above this path; run /init or set AMH_MARKETING_MD", hook_mode)

    r = rel(path, cdir)
    missing = []

    if r == "brief.md":
        why = check_retro_required(cdir, content, ctx)
        if why:
            block(why, hook_mode)
        ok(f"{cdir.name}: brief may be written")

    if r == "criteria.md":
        if not gate_ok(cdir, "brief.approved.md"):
            missing.append("brief.approved.md (G1) with decision: approved")

    elif r.startswith("assets/"):
        if not gate_ok(cdir, "brief.approved.md"):
            missing.append("brief.approved.md (G1) with decision: approved")
        if not (cdir / "criteria.md").exists():
            missing.append("criteria.md — criteria are written BEFORE copy (run /criteria)")

    elif r.startswith("review/"):
        if not any((cdir / "assets").glob("*.md")) if (cdir / "assets").exists() else True:
            missing.append("assets/ has nothing to review")

    elif r == "preflight.md":
        if not gate_ok(cdir, "assets.approved.md"):
            missing.append("assets.approved.md (G2) with decision: approved")

    elif r.startswith("shipped/"):
        if not gate_ok(cdir, "assets.approved.md"):
            missing.append("assets.approved.md (G2) with decision: approved")
        pf = cdir / "preflight.md"
        if not pf.exists():
            missing.append("preflight.md (run /preflight)")
        else:
            pfm, _ = split_front_matter(pf.read_text(encoding="utf-8"))
            if (pfm or {}).get("verdict") != "pass":
                missing.append("preflight.md verdict is not 'pass'")
        if not gate_ok(cdir, "ship.approved.md"):
            missing.append("ship.approved.md (G3) with decision: approved")

    if missing:
        block(f"cannot write {cdir.name}/{r} — prerequisites missing", hook_mode, missing)
    ok(f"{cdir.name}/{r}: gate prerequisites satisfied")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
