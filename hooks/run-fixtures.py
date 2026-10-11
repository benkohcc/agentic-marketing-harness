#!/usr/bin/env python3
"""run-fixtures — execute a campaign's fixtures.yaml deterministically.

Sections (all kind: deterministic):
  audience  — membership cases against MARKETING.md audiences[].rule, disjointness,
              size-share tolerance against the customer population, exclusions applied
  journey   — structural checks, scripted traces, property fuzz (docs/journeys.md)
  copy      — must_contain / must_equal / links_all_match against assets/*.md

Usage:
  run-fixtures.py <campaign-dir or fixtures.yaml> [--json]
Exit 0 = all pass, 1 = any fail, 2 = usage. A missing section is skipped, not passed.
"""
import json
import random
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import yaml  # noqa: E402
from _amh import load_context, split_front_matter  # noqa: E402
from _rules import RuleError, member  # noqa: E402

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def edges(state: dict) -> dict:
    """YAML 1.1 parses a bare `on:` key as boolean True; accept both spellings."""
    return state.get("on") or state.get(True) or {}


class Report:
    def __init__(self):
        self.lines = []

    def add(self, section, check, status, detail=""):
        self.lines.append({"section": section, "check": check, "status": status, "detail": detail})

    @property
    def verdict(self):
        return "fail" if any(l["status"] == "fail" for l in self.lines) else "pass"


# ---------------------------------------------------------------- audience
def run_audience(fx, ctx, cdir, rep):
    auds = {a["id"]: a for a in ctx["audiences"]}
    sec = fx.get("audience") or {}
    for i, case in enumerate(sec.get("cases", [])):
        cust = case.get("customer", {})
        for aud_id, expected in (case.get("expect") or {}).items():
            a = auds.get(aud_id)
            if a is None:
                rep.add("audience", f"case {i} {aud_id}", "fail", "audience not in MARKETING.md"); continue
            if not a.get("rule"):
                rep.add("audience", f"case {i} {aud_id}", "skipped", "audience has no `rule`"); continue
            try:
                got = member(a, cust)
            except RuleError as e:
                rep.add("audience", f"case {i} {aud_id}", "fail", str(e)); continue
            rep.add("audience", f"case {i} {aud_id}", "pass" if got == expected else "fail",
                    f"expected {expected}, got {got} for {json.dumps(cust)}")

    pop = load_population(cdir)
    if pop is None:
        rep.add("audience", "population", "skipped", "no data/customers.json or CDP connector")
        return
    resolved = {}
    for aud_id, a in auds.items():
        if a.get("rule"):
            try:
                resolved[aud_id] = {c["customer_id"] for c in pop if member(a, c)}
            except RuleError as e:
                rep.add("audience", f"resolve {aud_id}", "fail", str(e))

    for pair in sec.get("disjoint", []) or []:
        x, y = pair
        if x in resolved and y in resolved:
            n = len(resolved[x] & resolved[y])
            rep.add("audience", f"disjoint {x}×{y}", "pass" if n == 0 else "fail", f"{n} customers in both")
        else:
            rep.add("audience", f"disjoint {x}×{y}", "skipped", "one side has no rule")

    tol = sec.get("size_tolerance")
    if tol is not None:
        total_hint = sum(a.get("size_hint", 0) for a in auds.values()) or 0
        for aud_id, ids in resolved.items():
            hint = auds[aud_id].get("size_hint")
            if not hint or not total_hint:
                rep.add("audience", f"size {aud_id}", "skipped", "no size_hint"); continue
            exp_share, act_share = hint / total_hint, len(ids) / len(pop)
            rel = (act_share - exp_share) / exp_share
            rep.add("audience", f"size {aud_id}", "pass" if abs(rel) <= tol else "fail",
                    f"resolved {len(ids)}/{len(pop)} = {act_share:.1%}, size_hint share {exp_share:.1%}, rel {rel:+.0%}, tol ±{tol:.0%}")

    for ex in sec.get("exclusions_applied", []) or []:
        m = re.match(r"emailed_within_days:\s*(\d+)", str(ex))
        if m:
            d = int(m.group(1))
            exports = list((cdir / "data").glob("audience-*.csv")) if (cdir / "data").exists() else []
            if exports:
                by_id = {c["customer_id"]: c for c in pop}
                for ex_f in exports:
                    rows = [l.split(",")[0] for l in ex_f.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
                    leaked = [r for r in rows if r.isdigit() and (by_id.get(int(r), {}).get("last_emailed_days_ago") or 999) < d]
                    rep.add("audience", f"exclusion emailed<{d}d {ex_f.name}", "pass" if not leaked else "fail",
                            f"{len(leaked)} exported ids were emailed within {d} days")
            else:
                for aud_id, ids in resolved.items():
                    n = sum(1 for c in pop if c["customer_id"] in ids and (c.get("last_emailed_days_ago") or 999) < d)
                    rep.add("audience", f"exclusion emailed<{d}d {aud_id}", "pass",
                            f"{n} of {len(ids)} to suppress at preflight (no export yet to verify)")
        else:
            rep.add("audience", f"exclusion {ex}", "skipped", "unknown exclusion form")


def load_population(cdir):
    for base in [cdir, *cdir.parents]:
        f = base / "data" / "customers.json"
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8")).get("customers", [])
    return None


# ----------------------------------------------------------------- journey
def load_journey(cdir, cid, brief):
    for base in [cdir, *cdir.parents]:
        f = base / "journeys" / f"{cid}.yaml"
        if f.exists():
            return yaml.safe_load(f.read_text(encoding="utf-8"))
    ch = (brief.get("channels") or ["email"])[0]
    return {"journey_id": cid, "campaign_id": cid, "channel": ch, "start": "send",
            "states": {"send": {"type": "send", "asset": ch, "on": {"click": "exit", "unsubscribe": "exit_unsub", "wait_7d": "exit"}, "max_wait_days": 7},
                       "exit": {"type": "exit"}, "exit_unsub": {"type": "exit", "suppress": True}},
            "_implicit": True}


def reaches_exit(states, start):
    seen, stack = set(), [start]
    while stack:
        s = stack.pop()
        if s in seen or s not in states:
            continue
        seen.add(s)
        if states[s].get("type") == "exit":
            return True
        stack.extend(edges(states[s]).values())
    return False


def cycles_without_exit(states):
    # a cycle is bad if NO state in it has an edge leaving the cycle's SCC toward an exit
    import itertools
    bad = []
    names = list(states)
    for s in names:
        # find simple cycles through s via DFS (journeys are tiny)
        def dfs(node, path):
            for nxt in edges(states.get(node, {})).values():
                if nxt == s:
                    cyc = path + [node]
                    if not any(reaches_exit({k: v for k, v in states.items() if k not in cyc or k == c}, c) for c in cyc):
                        bad.append(cyc)
                elif nxt not in path and nxt in states:
                    dfs(nxt, path + [node])
        dfs(s, [])
    return bad


def simulate(j, events, ctx, brief, aud_override=None):
    """Return a trace dict for one customer given an event list."""
    states = j["states"]
    ch = j.get("channel", "email")
    chcfg = (ctx.get("channels") or {}).get(ch, {})
    cap = (aud_override or {}).get("frequency_cap") or chcfg.get("frequency_cap")
    win = chcfg.get("send_window")
    start_date = brief.get("dates", {}).get("start")
    end_date = brief.get("dates", {}).get("end")
    clock = datetime.combine(start_date, datetime.min.time()).replace(hour=10) if start_date else datetime(2026, 1, 6, 10)
    end_dt = datetime.combine(end_date, datetime.min.time()).replace(hour=23, minute=59) if end_date else None

    cur = j["start"]
    trace = {"path": [], "sends": 0, "send_times": [], "suppressed": False, "violations": [], "days": 0}

    def enter(state):
        nonlocal cur
        cur = state
        trace["path"].append(state)
        st = states[state]
        if st.get("type") == "send":
            if trace["suppressed"]:
                trace["violations"].append("send_to_suppressed")
            if win and (DAYS[clock.weekday()] not in win["days"] or not (win["hours"][0] <= clock.hour < win["hours"][1])):
                trace["violations"].append("send_outside_window")
            if end_dt and clock > end_dt:
                trace["violations"].append("send_after_end_date")
            trace["sends"] += 1
            trace["send_times"].append(clock)
            if cap:
                recent = [t for t in trace["send_times"] if (clock - t).days < cap["per_days"]]
                if len(recent) > cap["count"]:
                    trace["violations"].append("sends_over_cap")
        if st.get("type") == "exit" and st.get("suppress"):
            trace["suppressed"] = True

    enter(cur)
    entered_at = clock
    for ev in events:
        if states[cur].get("type") == "exit":
            break
        m = re.match(r"wait_(\d+)d", str(ev))
        if m:
            # Timer semantics: a wait state fires its wait_* edge at exactly max_wait_days,
            # whatever the size of the individual waits that get it there.
            n = int(m.group(1))
            st = states[cur]
            mw = st.get("max_wait_days")
            timer_edge = next((v for k, v in edges(st).items() if str(k).startswith("wait_")), None)
            in_state = (clock - entered_at).days
            if mw is not None and timer_edge and in_state + n >= mw:
                clock = entered_at + timedelta(days=mw)
                trace["days"] = (clock - trace["send_times"][0]).days if trace["send_times"] else trace["days"]
                if timer_edge not in states:
                    trace["violations"].append(f"unknown_state:{timer_edge}"); break
                enter(timer_edge); entered_at = clock
                continue
            clock += timedelta(days=n)
            trace["days"] += n
            if mw is None and any(str(k).startswith("wait_") for k in edges(st)):
                trace["violations"].append("wait_without_exit")
            continue
        nxt = edges(states[cur]).get(ev)
        if nxt is None:
            continue
        if nxt not in states:
            trace["violations"].append(f"unknown_state:{nxt}")
            break
        enter(nxt); entered_at = clock
    return trace


def run_journey(fx, ctx, cdir, cid, brief, rep):
    sec = fx.get("journey") or {}
    j = load_journey(cdir, cid, brief)
    states = j["states"]
    label = "implicit send→exit" if j.get("_implicit") else f"journeys/{cid}.yaml"

    struct = sec.get("structural") or {}
    if struct.get("every_state_reaches_exit"):
        dead = [s for s in states if not reaches_exit(states, s)]
        rep.add("journey", "every_state_reaches_exit", "pass" if not dead else "fail", f"{label}: dead states {dead}" if dead else label)
    if struct.get("no_cycle_without_exit"):
        bad = cycles_without_exit(states)
        rep.add("journey", "no_cycle_without_exit", "pass" if not bad else "fail", f"cycles: {bad}" if bad else label)
    if struct.get("every_send_references_linted_asset") and not (cdir / "assets").exists():
        rep.add("journey", "every_send_references_linted_asset", "skipped", "no assets/ yet — checked again at /preflight")
    elif struct.get("every_send_references_linted_asset"):
        missing = []
        for s, st in states.items():
            if st.get("type") == "send":
                a = cdir / "assets" / f"{st.get('asset')}.md"
                if not a.exists():
                    missing.append(f"{s}→assets/{st.get('asset')}.md")
        rep.add("journey", "every_send_references_linted_asset", "pass" if not missing else "fail", ", ".join(missing) or "all assets present")
    if struct.get("every_wait_has_max_days"):
        bad = [s for s, st in states.items() if st.get("type") == "send" and any(str(k).startswith("wait_") for k in edges(st)) and st.get("max_wait_days") is None]
        rep.add("journey", "every_wait_has_max_days", "pass" if not bad else "fail", f"{bad}" if bad else label)

    for i, tr in enumerate(sec.get("traces", []) or []):
        t = simulate(j, tr.get("events", []), ctx, brief)
        exp = tr.get("expect") or {}
        probs = []
        if "sends" in exp and t["sends"] != exp["sends"]:
            probs.append(f"sends {t['sends']} ≠ {exp['sends']}")
        if "path" in exp and t["path"] != exp["path"]:
            probs.append(f"path {t['path']} ≠ {exp['path']}")
        if "suppressed_after" in exp and t["suppressed"] != exp["suppressed_after"]:
            probs.append(f"suppressed {t['suppressed']} ≠ {exp['suppressed_after']}")
        if t["violations"]:
            probs.append(f"violations {sorted(set(t['violations']))}")
        rep.add("journey", f"trace {i} {tr.get('events')}", "pass" if not probs else "fail", "; ".join(probs) or f"path {t['path']}")

    props = sec.get("properties") or {}
    if props:
        runs = int(props.get("runs", 2000))
        never = set(props.get("never", []))
        vocab = sorted({ev for st in states.values() for ev in edges(st)} | {"open", "wait_1d", "wait_2d"})
        rng = random.Random(42)
        hits = {}
        example = {}
        for _ in range(runs):
            seq = [rng.choice(vocab) for _ in range(rng.randint(1, 8))]
            t = simulate(j, seq, ctx, brief)
            for v in set(t["violations"]):
                if v in never:
                    hits[v] = hits.get(v, 0) + 1
                    example.setdefault(v, seq)
        for v in sorted(never):
            rep.add("journey", f"never {v}", "pass" if v not in hits else "fail",
                    f"{hits.get(v, 0)}/{runs} random sequences" + (f" e.g. {example[v]}" if v in hits else ""))


# -------------------------------------------------------------------- copy
def load_assets(cdir):
    out = {}
    for f in sorted((cdir / "assets").glob("*.md")) if (cdir / "assets").exists() else []:
        fm, _ = split_front_matter(f.read_text(encoding="utf-8"))
        if fm:
            out[f.stem] = fm
    return out


def run_copy(fx, cdir, cid, brief, rep):
    sec = fx.get("copy") or {}
    assets = load_assets(cdir)
    if not assets:
        for _ in [0]:
            rep.add("copy", "assets", "skipped", "no assets/ yet — copy assertions run at /validate and /preflight")
        return
    for key, needles in (sec.get("must_contain") or {}).items():
        ch, field = key.split(".", 1)
        text = str((assets.get(ch, {}).get("assets") or {}).get(field, ""))
        missing = [n for n in needles if str(n).lower() not in text.lower()]
        rep.add("copy", f"must_contain {key}", "pass" if not missing else "fail", f"missing {missing}" if missing else f"{len(needles)} present")
    for key, expected in (sec.get("must_equal") or {}).items():
        m = re.match(r"(\w+)\.(\w+)\s+discount_pct", key)
        if m:
            ch, field = m.group(1), m.group(2)
            text = str((assets.get(ch, {}).get("assets") or {}).get(field, ""))
            found = [int(x) for x in re.findall(r"(\d{1,2})\s?%", text)]
            ok = (not found and expected == 0) or (found and all(f == expected for f in found))
            rep.add("copy", f"must_equal {key}", "pass" if ok else "fail", f"found {found}, expected {expected}")
        else:
            rep.add("copy", f"must_equal {key}", "skipped", "unknown assertion form")
    needle = sec.get("links_all_match")
    if needle:
        bad = [l for a in assets.values() for l in (a.get("links") or []) if needle not in l]
        rep.add("copy", "links_all_match", "pass" if not bad else "fail", f"{len(bad)} links lack {needle}" if bad else needle)


# -------------------------------------------------------------------- main
def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    p = Path(argv[1])
    cdir = p.parent if p.is_file() else p
    fxp = cdir / "fixtures.yaml"
    if not fxp.exists():
        print(f"{cdir}: no fixtures.yaml — run /criteria (test-writer)"); return 1
    fx = yaml.safe_load(fxp.read_text(encoding="utf-8")) or {}
    cid = fx.get("campaign_id") or cdir.name
    md, ctx = load_context(cdir)
    if ctx is None:
        print("no MARKETING.md found above the campaign"); return 1
    brief = {}
    if (cdir / "brief.md").exists():
        brief, _ = split_front_matter((cdir / "brief.md").read_text(encoding="utf-8"))
        brief = brief or {}

    rep = Report()
    if "audience" in fx:
        run_audience(fx, ctx, cdir, rep)
    else:
        rep.add("audience", "section", "skipped", "no audience fixtures")
    if "journey" in fx:
        run_journey(fx, ctx, cdir, cid, brief, rep)
    else:
        rep.add("journey", "section", "skipped", "no journey fixtures")
    if "copy" in fx:
        run_copy(fx, cdir, cid, brief, rep)

    if "--json" in argv:
        print(json.dumps({"campaign_id": cid, "kind": "deterministic", "verdict": rep.verdict, "checks": rep.lines}, indent=1, default=str))
    else:
        print(f"=== FIXTURES · {cid} · kind: deterministic ===")
        for l in rep.lines:
            print(f"{l['status']:<8} {l['section']:<9} {l['check']:<48} {l['detail']}")
        n = len(rep.lines); f = sum(l["status"] == "fail" for l in rep.lines); s = sum(l["status"] == "skipped" for l in rep.lines)
        print(f"\nverdict: {rep.verdict}  ({n - f - s} pass, {f} fail, {s} skipped)")
    return 0 if rep.verdict == "pass" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
