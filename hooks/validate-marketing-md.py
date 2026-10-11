#!/usr/bin/env python3
"""validate-marketing-md — the first AMH hook.

Validates a MARKETING.md file: YAML front matter against marketing.schema.json,
required body headings, and cross-references between sections (campaign types
point at real channels and metrics; audiences point at real campaign types).

Exit 0 = valid. Exit 1 = invalid (hook blocks the session). Exit 2 = usage error.

Usage: validate-marketing-md.py <path/to/MARKETING.md> [--schema marketing.schema.json]
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("validate-marketing-md: needs `pip install pyyaml`", file=sys.stderr)
    sys.exit(2)
try:
    import jsonschema
    from jsonschema import FormatChecker
except ImportError:
    print("validate-marketing-md: needs `pip install jsonschema`", file=sys.stderr)
    sys.exit(2)
# Prefer the 2020-12 validator; fall back to Draft 7 on older jsonschema (<4.0),
# which still understands everything marketing.schema.json uses.
Validator = getattr(jsonschema, "Draft202012Validator", None) or jsonschema.Draft7Validator

REQUIRED_HEADINGS = [
    "## Who we are",
    "## Positioning",
    "## Voice, with examples",
    "## Audience notes",
    "## Operating notes",
]


def split_front_matter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, None
    return m.group(1), m.group(2)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = Path(argv[1])
    schema_path = Path(argv[argv.index("--schema") + 1]) if "--schema" in argv else Path(__file__).resolve().parent.parent / "marketing.schema.json"

    errors = []
    text = path.read_text(encoding="utf-8")
    fm_text, body = split_front_matter(text)
    if fm_text is None:
        print(f"{path}: no YAML front matter block found")
        return 1

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        print(f"{path}: front matter is not valid YAML: {e}")
        return 1

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Validator(schema, format_checker=FormatChecker())
    for err in sorted(validator.iter_errors(fm), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        errors.append(f"schema: {loc}: {err.message}")

    # Cross-references — things a JSON Schema cannot express.
    # Run even when the schema complained, as long as the shape is navigable.
    try:
        channel_ids = set(fm["channels"].keys())
        metric_ids = {m["id"] for m in fm["metrics"]["catalog"]}
        ctype_ids = {c["id"] for c in fm["campaign_types"]}
        for c in fm["campaign_types"]:
            for ch in c["default_channels"]:
                if ch not in channel_ids:
                    errors.append(f"xref: campaign_types/{c['id']}: channel '{ch}' is not defined in channels")
                elif not fm["channels"][ch]["enabled"]:
                    errors.append(f"xref: campaign_types/{c['id']}: channel '{ch}' is disabled")
            if c["primary_metric"] not in metric_ids:
                errors.append(f"xref: campaign_types/{c['id']}: metric '{c['primary_metric']}' is not in metrics.catalog")
        for a in fm["audiences"]:
            for ct in a.get("fit", []):
                if ct not in ctype_ids:
                    errors.append(f"xref: audiences/{a['id']}: fit '{ct}' is not a campaign type")
            for ch in a.get("frequency_cap_override", {}):
                if ch not in channel_ids:
                    errors.append(f"xref: audiences/{a['id']}: frequency_cap_override channel '{ch}' is not defined")
        for g in fm["metrics"].get("guardrails", []):
            if g["metric"] not in metric_ids:
                errors.append(f"xref: metrics.guardrails: metric '{g['metric']}' is not in metrics.catalog")
    except (KeyError, TypeError, AttributeError):
        errors.append("xref: skipped — front matter shape too broken to cross-check (fix schema errors first)")

    for h in REQUIRED_HEADINGS:
        if not re.search(rf"^{re.escape(h)}\s*$", body, re.M):
            errors.append(f"body: missing required heading '{h}'")

    if errors:
        print(f"{path}: INVALID ({len(errors)} problem{'s' if len(errors) != 1 else ''})")
        for e in errors:
            print(f"  - {e}")
        return 1

    n_aud = len(fm["audiences"]); n_ct = len(fm["campaign_types"]); n_ch = len(fm["channels"])
    print(f"{path}: valid — {n_aud} audiences, {n_ct} campaign types, {n_ch} channels, amh_version {fm['amh_version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
