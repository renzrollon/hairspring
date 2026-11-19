#!/usr/bin/env python3
"""Deterministic helpers for the spec-assembler skill.

Stdlib only, Python 3.9+. Subcommands:

  blocks   Print requirement blocks (#### R-nnn, verbatim text, attributes, rationale) from
           requirements.csv, optionally followed by the story's acceptance criteria.
  summary  Print aggregating attribute views: counts by Type x Status and Type x Priority.
  trace    Print the traceability appendix from trace/trace.csv, or a backward trace from the
           Source and Links columns when trace.csv does not exist.
  check    Check an assembled spec.md: every in-scope requirement appears once with verbatim
           text, no excluded or unknown requirement appears, every internal link resolves.

Exit codes: 0 ok, 1 findings (check only), 2 usage or read error.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

EXCLUDED_DEFAULT = ("withdrawn", "rejected")
STATUS_ORDER = ["draft", "proposed", "agreed", "implemented", "verified", "deferred", "rejected", "withdrawn"]
PRIORITY_ORDER = ["must", "should", "could", "wont", "TBD"]
TYPE_LABEL = {"F": "F (functional)", "Q": "Q (quality)", "C": "C (constraint)"}
BASE_COLUMNS = ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale"]
OPTIONAL_COLUMNS = ["Title", "Owner", "Version", "Stability", "Risk", "Verification", "Kano", "Links", "Tags"]
REQ_ID = re.compile(r"^R-\d{3,}$")
ID_IN_TEXT = re.compile(r"(?<![A-Za-z0-9_-])(R-\d{3,})(?:\.AC\d+)?(?![A-Za-z0-9])")
BLOCK_HEADING = re.compile(r"^#{3,6} (R-\d{3,})\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK = re.compile(r"\]\(#([^)\s]+)\)")
HTML_ANCHOR = re.compile(r"<a\s+(?:id|name)=\"([^\"]+)\"")
FENCE = re.compile(r"^\s*(```|~~~)")


class UsageError(Exception):
    pass


# --------------------------------------------------------------------------- reading


def find_requirements(explicit: Optional[str]) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise UsageError(f"requirements file not found: {path}")
        return path
    here = Path.cwd().resolve()
    for base in [here, *here.parents]:
        workspace = "requirements"
        schema = base / "requirements" / "schema.json"
        if schema.is_file():
            try:
                workspace = json.loads(schema.read_text(encoding="utf-8")).get("workspace") or workspace
            except (json.JSONDecodeError, AttributeError):
                pass
        candidate = base / workspace / "requirements.csv"
        if candidate.is_file():
            return candidate
        if (base / ".git").exists():
            break
    raise UsageError("requirements/requirements.csv not found; pass --requirements")


def read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("﻿"):
        text = text[1:]
    reader = csv.DictReader(io.StringIO(text))
    rows = [{k: (v or "").strip() for k, v in row.items() if k is not None} for row in reader]
    return list(reader.fieldnames or []), rows


def requirement_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    columns, rows = read_csv(path)
    if "ID" not in columns or "Text" not in columns:
        raise UsageError(f"{path}: needs at least the columns ID and Text")
    return columns, [r for r in rows if REQ_ID.match(r.get("ID", ""))]


def in_scope(row: Dict[str, str], status_in: Optional[List[str]]) -> bool:
    status = row.get("Status", "")
    if status_in:
        return status in status_in
    return status not in EXCLUDED_DEFAULT


def parse_list(value: Optional[str]) -> Optional[List[str]]:
    if not value:
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


# --------------------------------------------------------------------------- blocks


def story_criteria(stories_dir: Path) -> Dict[str, Tuple[str, List[str]]]:
    """Map story ID -> (stories file path, acceptance-criterion lines from its paste block)."""
    found: Dict[str, Tuple[str, List[str]]] = {}
    if not stories_dir.is_dir():
        raise UsageError(f"stories folder not found: {stories_dir}")
    for path in sorted(stories_dir.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        current = None
        collecting = False
        buf: List[str] = []
        for line in lines:
            m = re.match(r"^## (R-\d{3,}):", line)
            if m:
                current, collecting, buf = m.group(1), False, []
                continue
            if current and re.match(rf"^\*\*{re.escape(current)}\.AC\d+", line):
                collecting = True
            if collecting and (line.startswith("**Notes:**") or line.startswith("<!-- paste-end")):
                while buf and not buf[-1].strip():
                    buf.pop()
                found[current] = (path.as_posix(), buf)
                collecting = False
                continue
            if collecting:
                buf.append(line)
    return found


def render_block(row: Dict[str, str], columns: List[str], criteria: Optional[Tuple[str, List[str]]]) -> str:
    attrs = [f"Type {row.get('Type') or 'TBD'}", f"Priority {row.get('Priority') or 'TBD'}",
             f"Status {row.get('Status') or 'TBD'}", f"Source {row.get('Source') or 'TBD'}"]
    for col in OPTIONAL_COLUMNS:
        if col in columns and row.get(col):
            attrs.append(f"{col} {row[col]}")
    out = [f"#### {row['ID']}", "", row.get("Text", ""), "", " · ".join(attrs), "",
           f"Rationale: {row.get('Rationale') or 'TBD'}"]
    if criteria:
        path, lines = criteria
        out += ["", f"Acceptance criteria (from `{path}`):", ""] + lines
    return "\n".join(out)


def cmd_blocks(args: argparse.Namespace) -> int:
    columns, rows = requirement_rows(find_requirements(args.requirements))
    by_id = {r["ID"]: r for r in rows}
    status_in = parse_list(args.status_in)
    types = parse_list(args.type)
    if args.ids:
        ids = parse_list(args.ids) or []
        missing = [i for i in ids if i not in by_id]
        if missing:
            raise UsageError(f"not in requirements.csv: {', '.join(missing)}")
        selected = [by_id[i] for i in ids]
    else:
        selected = [r for r in rows if in_scope(r, status_in) and (not types or r.get("Type") in types)]
    criteria = story_criteria(Path(args.stories)) if args.stories else {}
    print("\n\n".join(render_block(r, columns, criteria.get(r["ID"])) for r in selected))
    return 0


# --------------------------------------------------------------------------- summary


def table(header: List[str], body: Iterable[List[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in body]
    return "\n".join(lines)


def crosstab(rows: List[Dict[str, str]], key: str, order: List[str]) -> str:
    values = [v for v in order if any((r.get(key) or "TBD") == v for r in rows)]
    values += sorted({(r.get(key) or "TBD") for r in rows} - set(values))
    types = [t for t in ("F", "Q", "C") if any(r.get("Type") == t for r in rows)]
    types += sorted({r.get("Type") or "TBD" for r in rows} - set(types))
    body = []
    for t in types:
        counts = [sum(1 for r in rows if (r.get("Type") or "TBD") == t and (r.get(key) or "TBD") == v) for v in values]
        body.append([TYPE_LABEL.get(t, t)] + [str(c) for c in counts] + [str(sum(counts))])
    totals = [sum(1 for r in rows if (r.get(key) or "TBD") == v) for v in values]
    body.append(["Total"] + [str(c) for c in totals] + [str(sum(totals))])
    return table(["Type"] + values + ["Total"], body)


def cmd_summary(args: argparse.Namespace) -> int:
    _, rows = requirement_rows(find_requirements(args.requirements))
    status_in = parse_list(args.status_in)
    scope = [r for r in rows if in_scope(r, status_in)]
    excluded = [r for r in rows if not in_scope(r, status_in)]
    print("Requirements by type and status:\n")
    print(crosstab(scope, "Status", STATUS_ORDER))
    print("\nRequirements by type and priority:\n")
    print(crosstab(scope, "Priority", PRIORITY_ORDER))
    if excluded:
        kinds: Dict[str, int] = {}
        for r in excluded:
            kinds[r.get("Status") or "TBD"] = kinds.get(r.get("Status") or "TBD", 0) + 1
        detail = ", ".join(f"{k}: {v}" for k, v in sorted(kinds.items()))
        print(f"\nExcluded from this document: {len(excluded)} ({detail}).")
    return 0


# --------------------------------------------------------------------------- trace


def _bucket(kind: str) -> str:
    k = kind.lower()
    if any(w in k for w in ("source", "stakeholder", "interview")):
        return "Sources"
    if any(w in k for w in ("decision", "adr", "rdr")):
        return "Decisions"
    if "test" in k:
        return "Tests"
    if any(w in k for w in ("code", "file")):
        return "Code"
    return "Other"


def cmd_trace(args: argparse.Namespace) -> int:
    req_path = find_requirements(args.requirements)
    _, rows = requirement_rows(req_path)
    status_in = parse_list(args.status_in)
    scope = [r for r in rows if in_scope(r, status_in)]
    trace_path = Path(args.trace) if args.trace else req_path.parent / "trace" / "trace.csv"
    if args.trace and not trace_path.is_file():
        raise UsageError(f"trace file not found: {trace_path}")
    if trace_path.is_file():
        _, links = read_csv(trace_path)
        cols = ["Sources", "Decisions", "Code", "Tests", "Other"]
        body = []
        for r in scope:
            rid = r["ID"]
            cells: Dict[str, List[str]] = {c: [] for c in cols}
            for link in links:
                if link.get("From") == rid:
                    other, kind = link.get("To", ""), link.get("ToType", "")
                elif link.get("To") == rid:
                    other, kind = link.get("From", ""), link.get("FromType", "")
                else:
                    continue
                bucket = _bucket(kind)
                if other and other not in cells[bucket]:
                    cells[bucket].append(f"`{other}`" if "/" in other else other)
            body.append([f"[{rid}](#{rid.lower()})"] + [", ".join(cells[c]) or "none" for c in cols])
        print(f"From `{trace_path.as_posix()}`.\n")
        print(table(["Requirement"] + cols, body))
    else:
        body = [[f"[{r['ID']}](#{r['ID'].lower()})", r.get("Source") or "TBD", r.get("Links") or "none"] for r in scope]
        print("`trace/trace.csv` not found: backward trace from the Source and Links attributes only. "
              "Run `traceability-matrix` for decision, code and test links.\n")
        print(table(["Requirement", "Source", "Links"], body))
    return 0


# --------------------------------------------------------------------------- check


def slugify(text: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*]", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def cmd_check(args: argparse.Namespace) -> int:
    spec = Path(args.spec)
    if not spec.is_file():
        raise UsageError(f"spec file not found: {spec}")
    _, rows = requirement_rows(find_requirements(args.requirements))
    by_id = {r["ID"]: r for r in rows}
    status_in = parse_list(args.status_in)
    lines = spec.read_text(encoding="utf-8").splitlines()
    findings: List[Dict] = []

    def add(rule: str, severity: str, line: int, message: str) -> None:
        findings.append({"rule": rule, "severity": severity, "file": spec.as_posix(), "line": line, "message": message})

    anchors: Dict[str, int] = {}
    blocks: Dict[str, int] = {}
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for a in HTML_ANCHOR.findall(line):
            anchors.setdefault(a, i + 1)
        h = HEADING.match(line)
        if h:
            base = slugify(h.group(2))
            slug, n = base, 1
            while slug in anchors:
                slug, n = f"{base}-{n}", n + 1
            anchors[slug] = i + 1
        b = BLOCK_HEADING.match(line)
        if b:
            rid = b.group(1)
            if rid in blocks:
                add("duplicate-block", "error", i + 1, f"{rid} already has a block on line {blocks[rid]}")
                continue
            blocks[rid] = i + 1
            row = by_id.get(rid)
            if row is None:
                add("unknown-requirement", "error", i + 1, f"{rid} is not in requirements.csv")
                continue
            if not in_scope(row, status_in):
                add("excluded-requirement", "error", i + 1, f"{rid} has Status {row.get('Status')} and is outside the document scope")
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            para = []
            while j < len(lines) and lines[j].strip():
                para.append(lines[j])
                j += 1
            if norm(" ".join(para)) != norm(row.get("Text", "")):
                add("text-drift", "error", i + 2, f"{rid}: text differs from requirements.csv (copy it verbatim)")
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]) and "ID" in cells:
                add("id-column", "warning", i + 1, "table with an 'ID' column: re-lint reads it as a register; name it 'Requirement'")

    for r in rows:
        if in_scope(r, status_in) and r["ID"] not in blocks:
            add("missing-requirement", "error", 1, f"{r['ID']} is in scope but has no '#### {r['ID']}' block")

    in_fence = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in LINK.findall(line):
            if target not in anchors:
                add("broken-link", "error", i + 1, f"link to #{target} has no matching heading or anchor")
        for rid in ID_IN_TEXT.findall(line):
            if rid not in by_id:
                add("unknown-reference", "warning", i + 1, f"{rid} is mentioned but not in requirements.csv")

    findings.sort(key=lambda f: f["line"])
    if args.format == "json":
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']}: {f['severity']} {f['rule']}: {f['message']}")
        errors = sum(1 for f in findings if f["severity"] == "error")
        print(f"{errors} error(s), {len(findings) - errors} warning(s); {len(blocks)} requirement block(s)")
    levels = ("error",) if args.fail_on == "error" else ("error", "warning")
    return 1 if any(f["severity"] in levels for f in findings) else 0


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spec_tool.py",
        description="Deterministic helpers for assembling requirements/spec/spec.md.",
    )
    sub = parser.add_subparsers(dest="command", metavar="{blocks,summary,trace,check}")
    sub.required = True

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--requirements", metavar="CSV",
                       help="requirements.csv (default: <workspace>/requirements.csv found from the current folder)")
        p.add_argument("--status-in", metavar="S1,S2",
                       help="statuses in scope, e.g. agreed,implemented (default: every status except withdrawn and rejected)")

    p = sub.add_parser("blocks", help="print requirement blocks with verbatim text")
    common(p)
    p.add_argument("--ids", metavar="R-001,R-002", help="exact IDs in output order (ignores --type and --status-in)")
    p.add_argument("--type", metavar="F,Q,C", help="only these requirement types, in requirements.csv order")
    p.add_argument("--stories", metavar="DIR", help="stories folder; append each story's acceptance criteria to its block")
    p.set_defaults(func=cmd_blocks)

    p = sub.add_parser("summary", help="print counts by type x status and type x priority")
    common(p)
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("trace", help="print the traceability appendix table")
    common(p)
    p.add_argument("--trace", metavar="CSV", help="trace.csv (default: <workspace>/trace/trace.csv if it exists)")
    p.set_defaults(func=cmd_trace)

    p = sub.add_parser("check", help="check an assembled spec.md against requirements.csv")
    common(p)
    p.add_argument("spec", metavar="SPEC_MD", help="the assembled specification, e.g. requirements/spec/spec.md")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    p.add_argument("--fail-on", choices=["error", "warning"], default="error",
                   help="lowest severity that makes the exit code 1 (default: error)")
    p.set_defaults(func=cmd_check)
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        return int(args.func(args) or 0)
    except UsageError as exc:
        sys.stderr.write(f"spec_tool.py: {exc}\n")
        return 2
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        sys.stderr.write(f"spec_tool.py: {exc}\n")
        return 2


def main(argv: Optional[List[str]] = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
