#!/usr/bin/env python3
"""copy-lint — deterministic checks on generated assets. Runs on any write to
memory/campaigns/<id>/assets/<channel>.md.

Hard failures (block):
  * any brand.never_say string present (case-insensitive, whole phrase)
  * any claims.prohibited pattern present — matched literally; keep prohibited entries short
  * an asset exceeds channels.<ch>.limits[asset]
  * a required asset (channels.<ch>.required_assets) is missing or empty
  * reading level above brand.reading_level_max (Flesch–Kincaid grade, approximate)
  * a link lacks the utm_campaign=<campaign_id> parameter

Reports kind: deterministic. Never scores voice — that is the brand reviewer's rubric.

Hook mode: PreToolUse on Write|Edit. CLI: copy-lint.py <assets/<channel>.md>
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _amh import block, campaign_dir, load_context, ok, read_hook_payload, split_front_matter, written_file


def syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(1, n)


def fk_grade(text: str) -> float:
    sents = max(1, len(re.findall(r"[.!?]+(?:\s|$)", text)))
    words = re.findall(r"[A-Za-z']+", text)
    if len(words) < 20:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return 0.39 * (len(words) / sents) + 11.8 * (syl / len(words)) - 15.59


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
        path = Path(argv[1]); content = path.read_text(encoding="utf-8")

    cdir = campaign_dir(path)
    if cdir is None or "assets" not in path.parts or path.suffix != ".md":
        sys.exit(0)

    _, ctx = load_context(path)
    if ctx is None:
        block("no MARKETING.md found above this path", hook_mode)

    fm, _ = split_front_matter(content or "")
    if not fm or "assets" not in fm:
        # Edit payloads carry only new_string; if it isn't a whole file, lint the fragment textually.
        text = content or ""
        problems = [f"never_say: '{p}'" for p in ctx["brand"]["never_say"] if p.lower() in text.lower()]
        problems += [f"prohibited claim: '{p}'" for p in ctx["claims"]["prohibited"] if p.lower() in text.lower()]
        if problems:
            block("fragment contains forbidden text", hook_mode, problems)
        sys.exit(0)

    channel = fm.get("channel")
    chcfg = (ctx.get("channels") or {}).get(channel)
    if not chcfg:
        block(f"channel '{channel}' is not defined in MARKETING.md", hook_mode)

    assets = fm.get("assets") or {}
    problems = []

    for req in chcfg.get("required_assets", []):
        if not str(assets.get(req, "")).strip():
            problems.append(f"missing required asset '{req}'")

    limits = chcfg.get("limits", {})
    for name, val in assets.items():
        s = str(val)
        if name in limits and len(s) > limits[name]:
            problems.append(f"{name}: {len(s)} chars > limit {limits[name]}")

    all_text = "\n".join(str(v) for v in assets.values())
    low = all_text.lower()
    for phrase in ctx["brand"].get("never_say", []):
        if phrase.lower() in low:
            problems.append(f"never_say: '{phrase}'")
    for phrase in ctx["claims"].get("prohibited", []):
        if phrase.lower() in low:
            problems.append(f"prohibited claim text: '{phrase}'")

    rl = ctx["brand"].get("reading_level_max")
    if rl and "body" in assets:
        g = fk_grade(str(assets["body"]))
        if g > rl:
            problems.append(f"body reading level {g:.1f} > brand.reading_level_max {rl}")

    cid = fm.get("campaign_id") or cdir.name
    for link in fm.get("links", []) or []:
        if f"utm_campaign={cid}" not in link:
            problems.append(f"link missing utm_campaign={cid}: {link}")

    if problems:
        block(f"{cdir.name}/assets/{path.name} failed copy-lint [kind: deterministic]", hook_mode, problems)
    ok(f"{cdir.name}/assets/{path.name}: copy-lint passed [kind: deterministic] ({len(assets)} assets)")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
