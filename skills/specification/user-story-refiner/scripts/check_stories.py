#!/usr/bin/env python3
"""Check a stories file written by the user-story-refiner skill.

Stdlib only, Python 3.9+. Checks the fixed shape of requirements/stories/<epic-slug>.md:
the Cohn story sentence, acceptance-criterion labels and Given/When/Then lines, at least one
unwanted-behavior criterion per story, the paste block, the INVEST and Definition of Ready
tables, and (with --requirements) that each story has a matching Type F row whose Text equals
the story sentence.

Exit codes: 0 no findings at or above --fail-on, 1 findings, 2 usage or read error.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

STORY_HEADING = re.compile(r"^## (R-\d{3,}): (.+?)\s*$")
SECTION_HEADING = re.compile(r"^## ")
STORY_LINE = re.compile(r"^\*\*Story:\*\*\s+(.*\S)\s*$")
COHN = re.compile(r"^As an? (?P<role>[^,]+), I want (?P<goal>.+), so that (?P<benefit>.+)\.$")
AC_LIKE = re.compile(r"^\*\*R-\d{3,}\.AC")
AC_LABEL = re.compile(
    r"^\*\*(?P<id>(?P<story>R-\d{3,})\.AC\d+): (?P<name>.+?)\*\*\s+"
    r"_\((?P<kind>happy path|alternative|unwanted behavior|withdrawn)\)_\s*$"
)
STEP = re.compile(r"^- \*\*(?P<kw>Given|When|Then|And|But)\*\*\s+\S")
FLAG = re.compile(r"^- \*\*Flag:\*\*\s+(?P<text>.+)$")
PASTE_START = re.compile(r"^<!-- paste-start (R-\d{3,}) -->\s*$")
PASTE_END = re.compile(r"^<!-- paste-end (R-\d{3,}) -->\s*$")
GENERIC_ROLES = {"user", "users", "system", "the system", "developer", "a developer", "someone", "anyone", "stakeholder"}
INVEST = ["Independent", "Negotiable", "Valuable", "Estimable", "Small", "Testable"]


class Finding(dict):
    """rule, severity, id, file, line, message"""


def _cells(line: str) -> List[str]:
    text = line.strip().strip("|")
    return [c.strip() for c in text.split("|")]


def _tables(lines: Sequence[str], start: int, end: int) -> List[Dict]:
    """Pipe tables between line indexes [start, end): header cells, rows with line numbers."""
    out = []
    i = start
    while i < end:
        if lines[i].lstrip().startswith("|") and i + 1 < end and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = _cells(lines[i])
            rows = []
            j = i + 2
            while j < end and lines[j].lstrip().startswith("|"):
                rows.append((j + 1, _cells(lines[j])))
                j += 1
            out.append({"line": i + 1, "header": header, "rows": rows})
            i = j
            continue
        i += 1
    return out


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _read_requirements(path: Path) -> Dict[str, Dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("﻿"):
        text = text[1:]
    reader = csv.DictReader(io.StringIO(text))
    return {(row.get("ID") or "").strip(): row for row in reader if (row.get("ID") or "").strip()}


def check_file(path: Path, requirements: Optional[Dict[str, Dict[str, str]]] = None) -> List[Finding]:
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: List[Finding] = []

    def add(rule: str, severity: str, line: int, message: str, rid: str = "") -> None:
        findings.append(Finding(rule=rule, severity=severity, id=rid, file=str(path), line=line, message=message))

    for table in _tables(lines, 0, len(lines)):
        if table["header"] and table["header"][0] == "ID":
            add("id-column", "warning", table["line"],
                "table with an 'ID' column: re-lint reads it as a requirement register; use 'Story' or 'Requirement'")

    starts = [i for i, line in enumerate(lines) if STORY_HEADING.match(line)]
    if not starts:
        add("no-stories", "error", 1, "no '## R-nnn: <Title>' story section found")
    seen_ac: Dict[str, int] = {}
    for n, start in enumerate(starts):
        sid = STORY_HEADING.match(lines[start]).group(1)
        end = len(lines)
        for k in range(start + 1, len(lines)):
            if SECTION_HEADING.match(lines[k]):
                end = k
                break
        body = range(start + 1, end)

        # story sentence
        sentence, sentence_line = None, start + 1
        for i in body:
            m = STORY_LINE.match(lines[i])
            if m:
                sentence, sentence_line = m.group(1), i + 1
                break
        if sentence is None:
            add("story-missing", "error", start + 1, "no '**Story:** As a ..., I want ..., so that ....' line", sid)
        else:
            m = COHN.match(sentence)
            if not m:
                add("story-template", "error", sentence_line,
                    "story does not match 'As a <role>, I want <goal>, so that <benefit>.'", sid)
            else:
                if m.group("role").strip().lower() in GENERIC_ROLES:
                    add("role-generic", "warning", sentence_line,
                        f"generic role '{m.group('role').strip()}': name a real role from stakeholders.md", sid)
                goal = re.sub(r"^to\s+", "", m.group("goal").strip().lower())
                benefit = re.sub(r"^(i can|i could|i am able to|i will be able to)\s+", "", m.group("benefit").strip().lower())
                if _norm(goal) == _norm(benefit):
                    add("benefit-restates-goal", "warning", sentence_line, "the benefit restates the goal", sid)

        # paste block
        p_start = [i for i in body if PASTE_START.match(lines[i])]
        p_end = [i for i in body if PASTE_END.match(lines[i])]
        if not p_start or not p_end:
            add("paste-block", "error", start + 1, "missing <!-- paste-start --> / <!-- paste-end --> markers", sid)
        else:
            if PASTE_START.match(lines[p_start[0]]).group(1) != sid or PASTE_END.match(lines[p_end[0]]).group(1) != sid:
                add("paste-block", "error", p_start[0] + 1, "paste markers name a different story ID", sid)
            for i in range(p_start[0] + 1, p_end[0]):
                if lines[i].lstrip().startswith("|") or lines[i].startswith("#"):
                    add("paste-format", "error", i + 1, "paste block must not contain tables or headings", sid)

        # acceptance criteria
        acs = []
        for i in body:
            line = lines[i]
            if not AC_LIKE.match(line):
                continue
            m = AC_LABEL.match(line)
            if not m:
                add("ac-label", "error", i + 1,
                    "criterion label must be '**R-nnn.ACn: <name>** _(happy path|alternative|unwanted behavior)_'", sid)
                continue
            acs.append((i, m))
        if not acs:
            add("ac-missing", "error", start + 1, "story has no acceptance criteria", sid)
        if acs and not any(m.group("kind") == "unwanted behavior" for _, m in acs):
            add("unwanted-missing", "error", start + 1, "no criterion tagged _(unwanted behavior)_", sid)
        for idx, (i, m) in enumerate(acs):
            acid = m.group("id")
            if m.group("story") != sid:
                add("ac-prefix", "error", i + 1, f"{acid} is inside story {sid}", sid)
            if acid in seen_ac:
                add("ac-duplicate", "error", i + 1, f"{acid} already used on line {seen_ac[acid]}", sid)
            seen_ac.setdefault(acid, i + 1)
            if m.group("kind") == "withdrawn":
                continue
            stop = acs[idx + 1][0] if idx + 1 < len(acs) else end
            kws: List[str] = []
            for j in range(i + 1, stop):
                text = lines[j]
                if not text.strip() or PASTE_END.match(text) or text.startswith("**Notes:**"):
                    break
                f = FLAG.match(text)
                if f:
                    if "untestable" in f.group("text").lower() and "testability-check" not in f.group("text"):
                        add("flag-route", "error", j + 1, f"{acid}: untestable flag must say 'routed to testability-check'", sid)
                    continue
                s = STEP.match(text)
                if s:
                    kws.append(s.group("kw"))
            if kws.count("Given") < 1 or kws.count("When") != 1 or kws.count("Then") < 1:
                add("ac-gwt", "error", i + 1, f"{acid}: needs Given, exactly one When, and Then", sid)
            elif not (kws.index("Given") < kws.index("When") < kws.index("Then")):
                add("ac-gwt", "error", i + 1, f"{acid}: order must be Given, When, Then", sid)

        # INVEST and Definition of Ready tables
        tables = _tables(lines, start + 1, end)
        invest = [t for t in tables if t["header"][:2] == ["Criterion", "Result"]]
        if not invest:
            add("invest-table", "error", start + 1, "no INVEST table (Criterion | Result | Evidence)", sid)
        else:
            rows = invest[0]["rows"]
            names = [r[1][0] for r in rows]
            if names != INVEST:
                add("invest-table", "error", invest[0]["line"], f"INVEST rows must be {', '.join(INVEST)} in order", sid)
            for line_no, cells in rows:
                if len(cells) < 2 or cells[1] not in ("pass", "fail"):
                    add("invest-table", "error", line_no, "INVEST result must be 'pass' or 'fail'", sid)
        dor = [t for t in tables if t["header"][:2] == ["Item", "Result"]]
        if not dor or not dor[0]["rows"]:
            add("dor-table", "error", start + 1, "no Definition of Ready table (Item | Result | Evidence)", sid)
        else:
            for line_no, cells in dor[0]["rows"]:
                if len(cells) < 2 or cells[1] not in ("pass", "fail", "n/a"):
                    add("dor-table", "error", line_no, "Definition of Ready result must be 'pass', 'fail' or 'n/a'", sid)

        # register row
        if requirements is not None:
            row = requirements.get(sid)
            if row is None:
                add("csv-missing", "error", start + 1, f"{sid} has no row in requirements.csv", sid)
            else:
                if (row.get("Type") or "").strip() != "F":
                    add("csv-type", "error", start + 1, f"{sid} must have Type F in requirements.csv", sid)
                if sentence is not None and _norm(row.get("Text", "")) != _norm(sentence):
                    add("csv-drift", "error", sentence_line, f"{sid}: story sentence differs from requirements.csv Text", sid)
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_stories.py",
        description="Check the fixed shape of a user-story-refiner stories file.",
    )
    parser.add_argument("paths", nargs="+", metavar="STORIES_MD", help="stories file(s), e.g. requirements/stories/redeem-points.md")
    parser.add_argument("--requirements", metavar="CSV",
                        help="requirements.csv to cross-check: each story needs a Type F row whose Text equals the story sentence")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    parser.add_argument("--fail-on", choices=["error", "warning"], default="error",
                        help="lowest severity that makes the exit code 1 (default: error)")
    return parser


def run(args: argparse.Namespace) -> int:
    requirements = None
    try:
        if args.requirements:
            requirements = _read_requirements(Path(args.requirements))
        findings: List[Finding] = []
        for p in args.paths:
            findings.extend(check_file(Path(p), requirements))
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        sys.stderr.write(f"check_stories.py: {exc}\n")
        return 2
    if args.format == "json":
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']}: {f['severity']} {f['rule']}: {f['message']}")
        errors = sum(1 for f in findings if f["severity"] == "error")
        print(f"{errors} error(s), {len(findings) - errors} warning(s)")
    levels = {"error": ("error",), "warning": ("error", "warning")}[args.fail_on]
    return 1 if any(f["severity"] in levels for f in findings) else 0


def main(argv: Optional[List[str]] = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
