"""Shared helpers for AMH hooks.

Hooks run in two modes:
  * hook mode  — Claude Code pipes a JSON payload on stdin
                 ({"tool_name": "Write", "tool_input": {"file_path": ..., "content": ...}}).
                 Blocking = exit 2 with the reason on stderr (Claude sees it and must respond).
  * cli mode   — invoked by a skill or a human with explicit args. Blocking = exit 1.

Resolution: MARKETING.md is found by walking up from the file being written. This is
what lets the same hooks serve the repo root and examples/cellar-and-co/.
"""
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("AMH hooks need `pip install pyyaml jsonschema`", file=sys.stderr)
    sys.exit(2)

BLOCK_EXIT_HOOK = 2
BLOCK_EXIT_CLI = 1


def read_hook_payload():
    """Return the stdin JSON payload if we are in hook mode, else None."""
    if sys.stdin.isatty():
        return None
    raw = sys.stdin.read()
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def written_file(payload):
    """(path, content) for a Write/Edit payload, else (None, None)."""
    if not payload:
        return None, None
    ti = payload.get("tool_input", {}) or {}
    path = ti.get("file_path")
    content = ti.get("content")
    if content is None:
        content = ti.get("new_string")
    return (Path(path) if path else None), content


def find_marketing_md(start: Path):
    """Walk up from `start` to find MARKETING.md. Env AMH_MARKETING_MD overrides."""
    env = os.environ.get("AMH_MARKETING_MD")
    if env:
        return Path(env)
    p = start if start.is_dir() else start.parent
    for d in [p, *p.parents]:
        cand = d / "MARKETING.md"
        if cand.exists():
            return cand
    return None


def split_front_matter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    try:
        return yaml.safe_load(m.group(1)) or {}, m.group(2)
    except yaml.YAMLError:
        return None, text


def load_context(start: Path):
    """Return (marketing_md_path, front_matter_dict) or (None, None)."""
    md = find_marketing_md(start)
    if not md:
        return None, None
    fm, _ = split_front_matter(md.read_text(encoding="utf-8"))
    return md, fm


def campaign_dir(path: Path):
    """If `path` is inside memory/campaigns/<id>/, return that dir, else None."""
    parts = path.resolve().parts
    for i in range(len(parts) - 1):
        if parts[i] == "memory" and i + 2 < len(parts) and parts[i + 1] == "campaigns":
            return Path(*parts[: i + 3])
    return None


def gate_ok(cdir: Path, artifact: str):
    """True if the gate artifact exists AND says decision: approved."""
    f = cdir / artifact
    if not f.exists():
        return False
    fm, _ = split_front_matter(f.read_text(encoding="utf-8"))
    return bool(fm) and fm.get("decision") == "approved"


def block(reason: str, hook_mode: bool, lines=None):
    print(f"AMH BLOCK: {reason}", file=sys.stderr)
    for ln in lines or []:
        print(f"  - {ln}", file=sys.stderr)
    sys.exit(BLOCK_EXIT_HOOK if hook_mode else BLOCK_EXIT_CLI)


def ok(msg: str):
    print(f"AMH ok: {msg}")
    sys.exit(0)


PERSON_KEYS = re.compile(r"^(email|e-mail|phone|mobile|first_?name|last_?name|full_?name|address|street|dob|date_of_birth|ssn)$", re.I)


def person_fields(text: str, suffix: str):
    """Field/key names in a CSV header or JSON/JSONL object keys that identify a person.
    Matches KEYS only, so a value like "email" (a channel name) is not a hit."""
    found = set()
    if suffix == ".csv":
        head = text.splitlines()[0] if text.splitlines() else ""
        for col in head.split(","):
            if PERSON_KEYS.match(col.strip().strip('"')):
                found.add(col.strip().lower())
        return sorted(found)

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if PERSON_KEYS.match(str(k)):
                    found.add(str(k).lower())
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    try:
        if suffix == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    walk(json.loads(line))
        else:
            walk(json.loads(text))
    except json.JSONDecodeError:
        pass
    return sorted(found)
