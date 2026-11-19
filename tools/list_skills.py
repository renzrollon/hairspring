#!/usr/bin/env python3
"""List the skills in this catalogue, optionally filtered.

Examples:
  python3 tools/list_skills.py                         # name, stage, invocation, priority
  python3 tools/list_skills.py --priority P0 --paths   # folder paths of the P0 skills
  python3 tools/list_skills.py --invocation user --names
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_KEY = re.compile(r"^\s*(name|stage|invocation|priority):\s*['\"]?([^'\"#\n]+?)['\"]?\s*$")


def read_meta(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    meta = {}
    for line in text[3:end].splitlines():
        m = _KEY.match(line)
        if m and m.group(1) not in meta:
            meta[m.group(1)] = m.group(2).strip()
    return meta


def skills(root: Path = ROOT):
    for skill_md in sorted((root / "skills").glob("*/*/SKILL.md")):
        meta = read_meta(skill_md)
        meta["path"] = str(skill_md.parent.relative_to(root))
        yield meta


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--priority", choices=["P0", "P1", "P2"])
    p.add_argument("--stage")
    p.add_argument("--invocation", choices=["user", "model", "primitive"])
    out = p.add_mutually_exclusive_group()
    out.add_argument("--paths", action="store_true", help="print folder paths only")
    out.add_argument("--names", action="store_true", help="print skill names only")
    args = p.parse_args(argv)
    rows = [
        s for s in skills()
        if (not args.priority or s.get("priority") == args.priority)
        and (not args.stage or s.get("stage") == args.stage)
        and (not args.invocation or s.get("invocation") == args.invocation)
    ]
    for s in rows:
        if args.paths:
            print(s["path"])
        elif args.names:
            print(s.get("name", ""))
        else:
            print(f"{s.get('name',''):<24} {s.get('stage',''):<14} {s.get('invocation',''):<10} {s.get('priority','')}")
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
