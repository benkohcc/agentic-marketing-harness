#!/usr/bin/env python3
"""scan — AMH's AgentShield: a deterministic brand, compliance and configuration scan.

Scans a business directory (the one holding MARKETING.md) and reports, by severity:

  config    MARKETING.md risks a schema cannot see: a gate whose approver is the same role
            as the previous gate; a kill switch with no owner; an enabled channel with
            no send_window or frequency_cap; a campaign type allowing discounts above 30%;
            audiences with no `rule` (fixtures cannot run); a claim past its expiry;
            no never_say list; prohibited list empty.
  hooks     hooks.json: a hook missing from PreToolUse; a hook file that does not exist.
  assets    every assets/*.md in every campaign: never_say, prohibited text, instruction-
            like text (prompt injection), links without utm_campaign, assets referencing
            SKUs not in brief.offer.skus.
  data      every .csv/.json/.jsonl under memory/ and data/: emails, phones, person fields.
  memory    campaigns shipped without a retro past retro_due_days; gate artifacts whose
            approved_by does not name the approver role; approvals dated before the brief.

Exit 0 = no high findings, 1 = at least one high finding, 2 = usage.
Usage: scan.py <business-dir> [--json]
"""
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from _amh import person_fields, split_front_matter  # noqa: E402

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)")
INJECTION = re.compile(r"(ignore (all |any )?(previous|prior|above) (instructions|rules)|as an ai|you are now|system prompt|approve (this|camp-)|disregard (the )?(rules|criteria|hooks)|\bdo not (block|lint)\b)", re.I)


class Findings:
    def __init__(self):
        self.items = []

    def add(self, area, severity, where, what):
        self.items.append({"area": area, "severity": severity, "where": str(where), "what": what})

    def highs(self):
        return [f for f in self.items if f["severity"] == "high"]


def scan_config(ctx, F, root):
    gates = ctx.get("gates", {})
    order = ["g1_brief", "g2_assets", "g3_ship"]
    for a, b in zip(order, order[1:]):
        if gates.get(a, {}).get("approver") and gates.get(a, {}).get("approver") == gates.get(b, {}).get("approver"):
            F.add("config", "medium", "MARKETING.md gates", f"{a} and {b} share approver '{gates[a]['approver']}' — one person can walk a campaign through two gates alone")
    ks = ctx.get("kill_switch", {})
    if not ks.get("owner"):
        F.add("config", "high", "MARKETING.md kill_switch", "no owner — nobody is accountable for halting")
    for ch, cfg in (ctx.get("channels") or {}).items():
        if cfg.get("enabled"):
            if ch == "email" and not cfg.get("frequency_cap"):
                F.add("config", "high", f"channels.{ch}", "enabled email channel with no frequency_cap")
            if ch == "email" and not cfg.get("send_window"):
                F.add("config", "medium", f"channels.{ch}", "no send_window — sends can land at any hour")
    for ct in ctx.get("campaign_types", []):
        if ct.get("discount_allowed") and (ct.get("max_discount_pct") or 0) > 30:
            F.add("config", "medium", f"campaign_types.{ct['id']}", f"max_discount_pct {ct['max_discount_pct']} — above 30% erodes contribution margin; confirm intentional")
    for a in ctx.get("audiences", []):
        if not a.get("rule"):
            F.add("config", "medium", f"audiences.{a['id']}", "no `rule` — fixtures and disjointness checks cannot run for this audience")
    for c in (ctx.get("claims", {}).get("substantiated") or []):
        exp = c.get("expires")
        if exp and (exp if isinstance(exp, date) else date.fromisoformat(str(exp))) < date.today():
            F.add("config", "high", "claims.substantiated", f"claim '{c['claim']}' expired {exp} — copy may still be making it")
    if not ctx.get("brand", {}).get("never_say"):
        F.add("config", "medium", "brand.never_say", "empty — copy-lint has nothing to refuse")
    if not ctx.get("claims", {}).get("prohibited"):
        F.add("config", "high", "claims.prohibited", "empty — no claim is forbidden")
    for pack in ctx.get("compliance", {}).get("packs", []):
        if not _pack_exists(root, pack):
            F.add("config", "medium", "compliance.packs", f"pack '{pack}' not found relative to the repo")


HARNESS = Path(__file__).resolve().parent.parent


def _pack_exists(root, pack):
    for base in [root, *root.parents, HARNESS]:
        if (base / pack).exists() or (base / f"{pack}.md").exists():
            return True
    return False


def scan_hooks(root, F):
    hooks_dir = None
    for base in [root, *root.parents, HARNESS]:
        if (base / "hooks" / "hooks.json").exists():
            hooks_dir = base / "hooks"; break
    if hooks_dir is None:
        F.add("hooks", "high", "hooks/hooks.json", "not found — nothing is enforced")
        return
    cfg = json.loads((hooks_dir / "hooks.json").read_text(encoding="utf-8"))
    cmds = " ".join(h["command"] for grp in cfg.get("hooks", {}).get("PreToolUse", []) for h in grp.get("hooks", []))
    for name in ["gate-guard.py", "copy-lint.py", "pii-guard.py", "send-blocker.py"]:
        if name not in cmds:
            F.add("hooks", "high", "hooks.json PreToolUse", f"{name} is not registered")
        if not (hooks_dir / name).exists():
            F.add("hooks", "high", f"hooks/{name}", "file missing")


def scan_assets(root, ctx, F):
    never = [p.lower() for p in ctx.get("brand", {}).get("never_say", [])]
    prohibited = [p.lower() for p in ctx.get("claims", {}).get("prohibited", [])]
    for camp in sorted((root / "memory" / "campaigns").glob("camp-*")) if (root / "memory" / "campaigns").exists() else []:
        brief, _ = split_front_matter((camp / "brief.md").read_text(encoding="utf-8")) if (camp / "brief.md").exists() else (None, "")
        skus = set((brief or {}).get("offer", {}).get("skus", []) or [])
        for a in sorted((camp / "assets").glob("*.md")) if (camp / "assets").exists() else []:
            fm, body = split_front_matter(a.read_text(encoding="utf-8"))
            text = "\n".join(str(v) for v in ((fm or {}).get("assets") or {}).values()) + "\n" + body
            low = text.lower()
            for p in never:
                if p in low:
                    F.add("assets", "high", a.relative_to(root), f"never_say phrase present: '{p}'")
            for p in prohibited:
                if p in low:
                    F.add("assets", "high", a.relative_to(root), f"prohibited claim text present: '{p}'")
            for m in INJECTION.finditer(text):
                F.add("assets", "high", a.relative_to(root), f"instruction-like text in copy: '{m.group(0)}'")
            for link in (fm or {}).get("links", []) or []:
                if f"utm_campaign={camp.name}" not in link:
                    F.add("assets", "medium", a.relative_to(root), f"link without utm_campaign={camp.name}: {link}")
            for sku in re.findall(r"\bCC-\d{4}\b", text):
                if skus and sku not in skus:
                    F.add("assets", "medium", a.relative_to(root), f"mentions {sku}, not in brief.offer.skus {sorted(skus)}")


def scan_data(root, F):
    for d in ["memory", "data"]:
        base = root / d
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if f.suffix.lower() not in {".csv", ".json", ".jsonl"}:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            if EMAIL.search(text):
                F.add("data", "high", f.relative_to(root), "contains an email address")
            if PHONE.search(text):
                F.add("data", "high", f.relative_to(root), "contains a phone number")
            keys = person_fields(text, f.suffix.lower())
            if keys:
                F.add("data", "high", f.relative_to(root), f"person-identifying field(s): {', '.join(keys)}")


def scan_memory(root, ctx, F):
    mem = ctx.get("memory", {})
    due = int(mem.get("retro_due_days", 10))
    approvers = {g: cfg.get("approver") for g, cfg in ctx.get("gates", {}).items() if isinstance(cfg, dict)}
    for camp in sorted((root / "memory" / "campaigns").glob("camp-*")) if (root / "memory" / "campaigns").exists() else []:
        brief, _ = split_front_matter((camp / "brief.md").read_text(encoding="utf-8")) if (camp / "brief.md").exists() else (None, "")
        brief = brief or {}
        end = brief.get("dates", {}).get("end")
        if ((camp / "shipped").exists() or (camp / "results.md").exists()) and not (camp / "retro.md").exists() and end:
            end_d = end if isinstance(end, date) else date.fromisoformat(str(end))
            if (date.today() - end_d).days > due:
                F.add("memory", "medium", camp.name, f"shipped, ended {end}, no retro.md after {due} days — retro_required will block the next {brief.get('campaign_type')}")
        for art, gate in [("brief.approved.md", "g1_brief"), ("assets.approved.md", "g2_assets"), ("ship.approved.md", "g3_ship")]:
            f = camp / art
            if f.exists():
                fm, _ = split_front_matter(f.read_text(encoding="utf-8"))
                fm = fm or {}
                role = approvers.get(gate)
                if role and role not in str(fm.get("approved_by", "")):
                    F.add("memory", "high", f"{camp.name}/{art}", f"approved_by '{fm.get('approved_by')}' does not name the {gate} approver role '{role}'")
                if fm.get("decision") == "approved" and not fm.get("approved_at"):
                    F.add("memory", "medium", f"{camp.name}/{art}", "approved with no approved_at timestamp")


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    root = Path(argv[1]).resolve()
    md = root / "MARKETING.md"
    if not md.exists():
        print(f"{root}: no MARKETING.md"); return 2
    ctx, _ = split_front_matter(md.read_text(encoding="utf-8"))
    if not ctx:
        print("MARKETING.md front matter unreadable"); return 1
    F = Findings()
    scan_config(ctx, F, root)
    scan_hooks(root, F)
    scan_assets(root, ctx, F)
    scan_data(root, F)
    scan_memory(root, ctx, F)
    highs = F.highs()
    if "--json" in argv:
        print(json.dumps({"root": str(root), "kind": "deterministic", "high": len(highs), "findings": F.items}, indent=1))
    else:
        print(f"=== AMH SCAN · {root.name} · kind: deterministic ===")
        for f in sorted(F.items, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]]):
            print(f"{f['severity']:<7} {f['area']:<7} {f['where']:<44} {f['what']}")
        print(f"\n{len(highs)} high · {len(F.items) - len(highs)} medium/low")
    return 1 if highs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
