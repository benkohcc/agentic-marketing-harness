"""Generate the README illustrations as SVG (vector), then PNG screenshots via Chromium."""
import html
from pathlib import Path

OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

BLUE, BLUE_BG = "#3056D3", "#EEF2FD"
ORANGE, ORANGE_BG = "#D9541E", "#FDF0E9"
INK, GREY, LINE, PALE = "#1B1B1F", "#5A5A60", "#8a8378", "#B0ADA6"
FONT = "font-family=\"DejaVu Sans, Helvetica, Arial, sans-serif\""


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.parts, self.n = w, h, [], 0

    def esc(self, s):
        return html.escape(str(s), quote=True)

    def rect(self, x, y, w, h, fill="#fff", stroke=INK, sw=1, r=8, dash=None, extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>')

    def text(self, x, y, s, size=14, weight="normal", fill=INK, anchor="start", italic=False, mono=False):
        fam = 'font-family="DejaVu Sans Mono, Menlo, monospace"' if mono else FONT
        st = ' font-style="italic"' if italic else ""
        self.parts.append(f'<text x="{x}" y="{y}" {fam} font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{st}>{self.esc(s)}</text>')

    def lines(self, x, y, lines, size=13, lh=17, weight="normal", fill=INK, anchor="start"):
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, size, weight, fill, anchor)

    def card(self, x, y, w, h, title, body=(), fill="#fff", stroke=INK, sw=1, size=13, tsize=14, align="left", r=8):
        self.rect(x, y, w, h, fill, stroke, sw, r)
        ax = x + w / 2 if align == "center" else x + 12
        anchor = "middle" if align == "center" else "start"
        total = (1 if title else 0) * (tsize + 4) + len(body) * (size + 4)
        ty = y + (h - total) / 2 + tsize - 1
        if title:
            self.text(ax, ty, title, tsize, "bold", INK, anchor)
            ty += tsize + 4
        for ln in body:
            self.text(ax, ty, ln, size, "normal", INK, anchor)
            ty += size + 4

    def arrow(self, x1, y1, x2, y2, color=LINE, sw=2, dash=None, head=True):
        self.n += 1
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if head:
            self.parts.append(f'<defs><marker id="h{self.n}" orient="auto" markerWidth="8" markerHeight="8" refX="7" refY="4"><path d="M0 0 L8 4 L0 8 Z" fill="{color}"/></marker></defs>')
            m = f' marker-end="url(#h{self.n})"'
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{d}{m}/>')

    def label(self, x, y, s, size=10, fill=GREY, anchor="middle"):
        w = len(s) * size * 0.62 + 8
        lx = x - w / 2 if anchor == "middle" else x - 4
        self.parts.append(f'<rect x="{lx}" y="{y - size}" width="{w}" height="{size + 5}" fill="#fff"/>')
        self.text(x, y, s, size, "normal", fill, anchor)

    def pill(self, x, y, w, h, s, fill=INK, color="#fff", size=12, weight="bold"):
        self.rect(x, y, w, h, fill, fill, 1, h / 2)
        self.text(x + w / 2, y + h / 2 + size * 0.36, s, size, weight, color, "middle")

    def save(self, name):
        body = "\n".join(self.parts)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>\n{body}\n</svg>\n'
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        return OUT / f"{name}.svg"


# ------------------------------------------------------------------ 1. the loop
def fig_loop():
    s = SVG(1440, 520)
    s.text(40, 44, "The loop: ten steps, three human gates, every step done by a sub-agent that sees only what it needs", 18, "bold")
    steps = ["Brief", "Criteria", "Generate", "Validate", "Review", "Preflight", "Ship", "Measure", "Retro", "Learn"]
    agents = ["strategist", "strategist +\ntest-writer", "copywriter", "10 validators\n+ fixtures", "brand +\ncompliance", "channel-ops", "channel-ops", "analyst", "analyst", "analyst"]
    hooks = {0: "gate-guard\nretro_required", 1: "fixtures.yaml", 2: "copy-lint", 3: "run-fixtures", 5: "run-fixtures\ngate-guard", 6: "send-blocker\nkill switch"}
    x0, w, gap = 60, 118, 20
    cy_chip, y, y_hook = 80, 178, 262
    for i, st in enumerate(steps):
        x = x0 + i * (w + gap)
        s.card(x, y, w, 56, st, fill=ORANGE_BG, stroke=ORANGE, align="center", tsize=15)
        if i < len(steps) - 1:
            s.arrow(x + w + 2, y + 28, x + w + gap - 3, y + 28)
        s.rect(x, cy_chip, w, 40, "#fff", ORANGE, 1, 20, dash="3 3")
        s.lines(x + w / 2, cy_chip + 17, agents[i].split("\n"), 11, 14, fill="#9A3412", anchor="middle")
        if i in hooks:
            s.rect(x, y_hook, w, 40, "#fff", INK, 1, 6)
            s.lines(x + w / 2, y_hook + 17, hooks[i].split("\n"), 11, 14, fill=INK, anchor="middle")
    s.text(x0, 70, "SUB-AGENTS", 11, "bold", GREY)
    s.text(x0 + 9 * (w + gap) + w, 254, "HOOKS THAT REFUSE", 11, "bold", GREY, "end")
    # inner loop: validate back to generate, drawn in the band between chips and cards
    gx = x0 + 2 * (w + gap) + w / 2; vx = x0 + 3 * (w + gap) + w / 2
    s.parts.append(f'<path d="M {vx} {y} C {vx} {y-40}, {gx} {y-40}, {gx} {y-2}" fill="none" stroke="{ORANGE}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    s.parts.append(f'<path d="M {gx-5} {y-10} L {gx} {y-1} L {gx+5} {y-10} Z" fill="{ORANGE}"/>')
    s.label((gx + vx) / 2, y - 26, "fix & rerun ≤3×", 11, "#9A3412")
    # gates: in the gaps after Brief, after Review, after Preflight
    def gate(i_after, label):
        x = x0 + i_after * (w + gap) + w + gap / 2
        s.arrow(x, y + 60, x, 328, INK, 1.5, dash="4 3", head=False)
        s.pill(x - 66, 330, 132, 26, label, size=11)
    gate(0, "G1 · approve brief")
    gate(4, "G2 · approve assets")
    gate(5, "G3 · approve send")
    # learn -> brief return, routed around the outside
    lx = x0 + 9 * (w + gap) + w; bx = x0
    s.parts.append(f'<path d="M {lx} {y+28} L {lx+22} {y+28} L {lx+22} {y+196} L {bx-22} {y+196} L {bx-22} {y+28} L {bx-4} {y+28}" fill="none" stroke="{PALE}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    s.parts.append(f'<path d="M {bx-12} {y+23} L {bx-2} {y+28} L {bx-12} {y+33} Z" fill="{PALE}"/>')
    s.label(720, y + 200, "retros → instincts.jsonl → rules/learned/ → the next brief", 11, GREY)
    s.lines(40, 412, [
        "Gate approval is a file (brief.approved.md, assets.approved.md, ship.approved.md), not a chat message. gate-guard refuses the next step's write",
        "until the previous gate's file exists with decision: approved. copy-lint refuses an asset with a never_say phrase, a prohibited claim, a broken",
        "limit or a bad UTM. send-blocker refuses a send with no G3, outside the window, or while memory/HALT exists. The model cannot argue with any of them.",
    ], 12, 17, fill=GREY)
    s.text(40, 486, "kind: deterministic", 11, "bold", INK)
    s.text(170, 486, "for every hook and fixture ·", 11, "normal", GREY)
    s.text(330, 486, "kind: rubric", 11, "bold", INK)
    s.text(410, 486, "for validators and reviewers ·", 11, "normal", GREY)
    s.text(590, 486, "kind: outcome", 11, "bold", INK)
    s.text(680, 486, "for /measure. Never collapsed into one tick.", 11, "normal", GREY)
    return s.save("loop")


# ------------------------------------------------------------------ 2. context isolation
def fig_isolation():
    s = SVG(1400, 570)
    s.text(40, 44, "Context isolation: each sub-agent is handed files, never the conversation that produced them", 18, "bold")
    files = [("MARKETING.md", "intent"), ("retros + instincts", "history"), ("brief.md", "G1"), ("criteria.md", "the yardstick"),
             ("fixtures.yaml", "the tests"), ("assets/*.md", "the work"), ("review/*.md", "verdicts"), ("results.md", "outcome")]
    fx0, fw, fgap, fy = 40, 150, 14, 100
    fxs = {}
    for i, (f, sub) in enumerate(files):
        x = fx0 + i * (fw + fgap); fxs[f] = x + fw / 2
        s.card(x, fy, fw, 52, f, [sub], fill="#F6F6F4", stroke=PALE, align="center", tsize=13, size=11)
    s.text(40, 90, "FILES ON DISK (memory/campaigns/<id>/)", 11, "bold", GREY)
    agents = [("strategist", ["MARKETING.md", "retros + instincts"], "writes brief.md, criteria.md"),
              ("test-writer", ["MARKETING.md", "brief.md"], "writes fixtures.yaml"),
              ("copywriter", ["MARKETING.md", "brief.md", "criteria.md"], "writes assets/*.md — never sees review/"),
              ("validator ×10", ["criteria.md", "assets/*.md"], "one question each — never sees the chat"),
              ("reviewers", ["criteria.md", "assets/*.md"], "score & find — never rewrite"),
              ("channel-ops", ["assets/*.md", "fixtures.yaml"], "preflight, ship — never edits copy"),
              ("analyst", ["criteria.md", "results.md", "review/*.md"], "measure, retro, learn")]
    ax0, aw, agap, ay = 40, 176, 18, 330
    for i, (name, sees, does) in enumerate(agents):
        x = ax0 + i * (aw + agap)
        words, lines_, cur = does.split(), [], ""
        for wd in words:
            if len(cur) + len(wd) + 1 > 28:
                lines_.append(cur); cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines_.append(cur)
        s.card(x, ay, aw, 70, name, lines_, fill=ORANGE_BG, stroke=ORANGE, align="center", tsize=14, size=10)
        for f in sees:
            s.arrow(fxs[f], fy + 54, x + aw / 2, ay - 2, PALE if name != "copywriter" else ORANGE, 1.2)
    s.text(40, ay + 92, "SUB-AGENTS — arrows show what each one is handed", 11, "bold", GREY)
    s.rect(40, 440, 1320, 96, "#fff", INK, 1, 8)
    s.lines(56, 466, [
        "Why it matters: a model reviewing its own reasoning mostly agrees with itself. Handing the reviewer the files and not the chat is what makes its",
        "verdict independent. The same rule gives the copywriter nothing to optimise for except the criteria, and gives each validator one question it can",
        "answer from one or two files. The hooks enforce the order of the files; the isolation enforces the honesty of the verdicts.",
    ], 12, 18)
    s.text(56, 524, "ECC equivalent: reviewer agents read the diff cold; the implementer never grades its own PR.", 11, "normal", GREY)
    return s.save("isolation")


# ------------------------------------------------------------------ 3. three kinds of green
def fig_greens():
    s = SVG(1400, 380)
    s.text(40, 44, "Three kinds of green: code has a compiler, a campaign answers in two weeks — so every check says which kind it is", 18, "bold")
    cols = [("Deterministic", INK, "2", None, ["true or false, instant, free to rerun", "hooks · copy-lint · run-fixtures:", "audience rules, disjointness, size share,", "journey structure, traces, 2,000-run fuzz,", "links, UTMs, caps, suppression, PII, window", "", "they BLOCK"]),
            ("Rubric", LINE, "2", None, ["an LLM judge against criteria written first,", "fresh context, structured verdict", "10 narrow validators + 2 reviewers,", "calibrated against outcomes in", "evals/calibration.jsonl", "", "block below a threshold, otherwise FLAG"]),
            ("Outcome", PALE, "2", "6 4", ["the real test, which arrives late", "/measure against criteria.md thresholds,", "never post-hoc metrics", "feeds retros → instincts → rules/learned/", "and the validator weights", "", "never the gate for the campaign it measures"])]
    for i, (name, stroke, sw, dash, body) in enumerate(cols):
        x = 40 + i * 445
        s.rect(x, 80, 425, 200, "#fff", stroke, 2, 10, dash=dash)
        s.text(x + 16, 110, name, 18, "bold")
        s.lines(x + 16, 138, body, 12.5, 17, fill=INK)
    s.text(700, 318, "Compiler-shaped work moves left over time: the test-writer spends judgment once on fixtures.yaml; a script runs it forever.", 12, "normal", GREY, "middle")
    s.text(700, 340, "What stays right is exactly what should: whether the creative was good, and whether the hypothesis was true.", 12, "normal", GREY, "middle")
    s.text(700, 364, "Anyone selling a marketing agent with a single “verified ✓” is collapsing these three, and the collapse is where the trust leaks out.", 12, "bold", INK, "middle")
    return s.save("three-greens")


# ------------------------------------------------------------------ 4. fixtures + journey
def fig_fixtures():
    s = SVG(1400, 610)
    s.text(40, 44, "Testing the plumbing: audience rules with fixtures, and a journey as a state machine the fuzzer can break", 18, "bold")
    # left: audience rules
    s.rect(40, 70, 620, 510, "#fff", PALE, 1, 10)
    s.text(60, 98, "Audience rules → fixtures (deterministic)", 15, "bold")
    s.rect(60, 112, 580, 70, BLUE_BG, BLUE, 1, 6)
    s.text(72, 132, "MARKETING.md · audiences[].rule", 11, "bold", BLUE)
    s.text(72, 152, "collectors:  (orders_12m >= 3 and aov > 180) or allocation_list == true", 11.5, mono=True)
    s.text(72, 170, "             exclusion_rules: [allocation_opt_out == true, last_order_days_ago >= 180]", 11.5, mono=True)
    s.arrow(350, 184, 350, 206, LINE)
    s.text(362, 200, "test-writer, before any copy", 11, "normal", GREY)
    s.rect(60, 210, 580, 150, ORANGE_BG, ORANGE, 1, 6)
    s.text(72, 230, "memory/campaigns/camp-004/fixtures.yaml", 11, "bold", "#9A3412")
    rows = [("aov 190, 3 orders, recent", "collectors: true", True), ("aov 180.00 exactly", "collectors: false  (strict >)", True),
            ("aov 400, allocation_opt_out", "collectors: false  (exclusion wins)", True), ("disjoint [collectors, lapsed]", "0 in both", True),
            ("size share vs size_hint", "9.5% vs 9.4%  within ±35%", True), ("disjoint [explorers, lapsed]", "26 in both → FAIL", False)]
    for i, (a, b, ok) in enumerate(rows):
        y = 252 + i * 18
        s.text(72, y, a, 11.5, mono=True)
        s.text(330, y, b, 11.5, fill=("#166534" if ok else "#B91C1C"), mono=True)
    s.arrow(350, 362, 350, 384, LINE)
    s.text(362, 378, "hooks/run-fixtures.py · exit 1 on any fail", 11, "normal", GREY)
    s.rect(60, 388, 580, 124, "#fff", INK, 1, 6)
    s.lines(72, 410, ["A rule is a predicate in a deliberately tiny language (comparisons, and/or/not, in),",
                      "evaluated by an AST-whitelisted interpreter — nothing can hide in a rule.",
                      "Cases cover every boundary and every exclusion. Disjointness and size-share tolerance",
                      "run against the 600-customer synthetic population. ECC equivalent: unit tests,",
                      "written by the model, run by a dumb runner, same answer every time."], 11.5, 17)
    # right: journey
    s.rect(700, 70, 660, 510, "#fff", PALE, 1, 10)
    s.text(720, 98, "journeys/camp-004.yaml → simulator + fuzz (deterministic)", 15, "bold")
    st = {"send_main": (740, 195), "reminder": (940, 195), "exit_converted": (1170, 142), "exit_unsub": (1170, 212), "exit_timeout": (1170, 282)}
    for k, (x, y) in st.items():
        ex = k.startswith("exit")
        s.card(x, y, 150, 44, k, fill=("#F6F6F4" if ex else ORANGE_BG), stroke=(PALE if ex else ORANGE), align="center", tsize=12, r=(22 if ex else 6))
    # send_main -> reminder (timer)
    s.arrow(892, 217, 938, 217); s.label(915, 210, "wait_3d", 10)
    # reminder -> exits
    s.arrow(1092, 210, 1168, 170); s.label(1128, 180, "click", 10)
    s.arrow(1092, 220, 1168, 232); s.label(1128, 238, "unsubscribe", 10)
    s.arrow(1092, 228, 1168, 296); s.label(1118, 276, "wait_4d", 10)
    # send_main -> exit_converted over the top, send_main -> exit_unsub under the bottom
    s.parts.append(f'<path d="M 815 195 C 815 122, 1140 116, 1168 158" fill="none" stroke="{LINE}" stroke-width="2"/>')
    s.parts.append(f'<path d="M 1160 151 L 1169 159 L 1157 161 Z" fill="{LINE}"/>')
    s.label(980, 130, "click", 10)
    s.parts.append(f'<path d="M 815 239 C 815 330, 1140 326, 1168 244" fill="none" stroke="{LINE}" stroke-width="2"/>')
    s.parts.append(f'<path d="M 1158 252 L 1169 243 L 1169 256 Z" fill="{LINE}"/>')
    s.label(980, 320, "unsubscribe → suppressed", 10)
    s.text(730, 352, "timer: a wait edge fires at exactly max_wait_days — like an ESP's wait node", 10.5, fill=GREY)
    s.rect(720, 366, 620, 196, "#fff", INK, 1, 6)
    s.text(732, 388, "run-fixtures.py · journey", 11, "bold")
    jr = [("every_state_reaches_exit · no_cycle_without_exit · every_wait_has_max_days", True),
          ("trace [click] → [send_main, exit_converted], 1 send", True),
          ("trace [open, wait_3d, wait_4d] → reminder → exit_timeout, 2 sends", True),
          ("never sends_over_cap · send_to_suppressed · send_outside_window · send_after_end_date", True),
          ("   2,000 random event sequences, seed 42", True),
          ("max_wait_days: 2 → reminder lands on a Friday → send_outside_window 157/2000", False),
          ("end: 2026-10-15 → reminder after end date → send_after_end_date", False)]
    for i, (t, ok) in enumerate(jr):
        y = 410 + i * 19
        s.text(732, y, ("pass  " if ok else "FAIL  ") + t, 11, fill=("#166534" if ok else "#B91C1C"), mono=True)
    s.text(732, 552, "The fuzzer's first catch on the example: a 3-day reminder from a Wednesday launch is fine; a 2-day one is a Friday.", 10.5, fill=GREY)
    return s.save("fixtures")


# ------------------------------------------------------------------ 5. ECC → AMH mapping
def fig_mapping():
    rows = [("CLAUDE.md", "freeform conventions", "MARKETING.md", "schema-validated context layer"),
            ("Agents (≈67)", "planner, reviewers, build-repair…", "Agents (8)", "strategist, test-writer, copywriter, validator, 2 reviewers, analyst, channel-ops"),
            ("Skills (≈293)", "on-demand workflows", "Skills (13)", "one per loop step + approve, status"),
            ("Commands", "/plan, /tdd…", "Commands", "/amh:* and plain words at gates"),
            ("Rules", "common + language packs", "Rules", "common + channel + vertical + learned"),
            ("Hooks", "block on tool events", "Hooks (5)", "gate-guard, copy-lint, pii-guard, send-blocker, validate-md"),
            ("Compiler + tests + repair", "the free oracle", "Validators + fixtures + /validate", "10 narrow sub-agents, run-fixtures.py, ≤3 passes"),
            ("Memory & sessions", "save/resume, vault", "Campaign memory", "memory/campaigns/<id>/, /status"),
            ("Continuous learning", "instincts → skills", "/learn", "retros → instincts.jsonl → rules/learned/"),
            ("AgentShield", "prompts, hooks, MCP, secrets", "scanner/scan.py", "config, hooks, assets, data, memory"),
            ("MCP connectors", "one default, rest opt-in", "integrations/ by role", "cdp, esp, ads, analytics — file_based default"),
            ("npx installer, adapters", "Claude Code, Codex, Cursor…", "bin/amh-setup.sh + /init", "self-check + install; adapters v1")]
    s = SVG(1400, 70 + len(rows) * 46 + 30)
    s.text(40, 44, "Every part of ECC and its AMH counterpart", 18, "bold")
    for i, (e, ed, a, ad) in enumerate(rows):
        y = 70 + i * 46
        s.rect(40, y, 520, 38, BLUE_BG, BLUE, 1, 6)
        s.text(52, y + 24, e, 13, "bold", BLUE)
        s.text(290, y + 24, ed, 12, fill=INK)
        s.arrow(566, y + 19, 598, y + 19)
        s.rect(604, y, 756, 38, ORANGE_BG, ORANGE, 1, 6)
        s.text(616, y + 24, a, 13, "bold", "#9A3412")
        s.text(880, y + 24, ad, 12, fill=INK)
    return s.save("mapping")


paths = [fig_loop(), fig_isolation(), fig_greens(), fig_fixtures(), fig_mapping()]
print("\n".join(str(p) for p in paths))
