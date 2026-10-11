#!/usr/bin/env python3
"""pii-guard — audience exports carry ids, never people.

Runs on any write of a .csv / .json / .jsonl file inside memory/campaigns/<id>/.
Blocks when the content contains an email address, a phone number, or a header /
key that names a person (email, phone, first_name, last_name, name, address, dob).

MARKETING.md compliance.data_handling is the policy; this is the enforcement.

Hook mode: PreToolUse on Write|Edit. CLI: pii-guard.py <file>
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _amh import block, campaign_dir, ok, person_fields, read_hook_payload, written_file

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)")


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

    if campaign_dir(path) is None or path.suffix.lower() not in {".csv", ".json", ".jsonl"}:
        sys.exit(0)

    text = content or ""
    problems = []
    emails = EMAIL.findall(text)
    if emails:
        problems.append(f"{len(emails)} email address(es), e.g. {emails[0][:3]}***")
    phones = PHONE.findall(text)
    if phones:
        problems.append(f"{len(phones)} phone number(s)")
    keys = person_fields(text, path.suffix.lower())
    if keys:
        problems.append(f"person-identifying field(s) in header/keys: {', '.join(keys)}")

    if problems:
        block(f"{path.name} contains PII — audience files carry customer ids only [kind: deterministic]", hook_mode, problems)
    ok(f"{path.name}: no PII detected [kind: deterministic]")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
