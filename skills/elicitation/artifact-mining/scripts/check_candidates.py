#!/usr/bin/env python3
"""Check a re-skills candidate register (requirements/candidates.csv).

Stdlib only, Python 3.9+. Single-skill helper of `artifact-mining`.

Checks the fixed column order, CAN-nnn IDs, required fields and allowed values, and, most
importantly, that every Quote really appears at the Location it cites, so no candidate
requirement rests on a quote that is not in the artifact.

Exit codes: 0 no errors (warnings may be printed), 1 errors found, 2 usage or parse error.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

COLUMNS = [
    "ID", "Statement", "Type", "Technique", "Source", "Location", "Quote",
    "Disposition", "Reason", "Owner", "Kano", "Requirement",
]
REQUIRED = ["ID", "Statement", "Type", "Technique", "Source", "Location", "Quote", "Disposition", "Reason"]
ENUMS = {
    "Type": ["F", "Q", "C", "TBD"],
    "Technique": [
        "document-analysis", "system-archaeology", "feedback-analysis",
        "interview", "workshop", "observation", "questionnaire",
    ],
    "Disposition": ["keep", "drop", "confirm"],
    "Kano": ["", "TBD", "dissatisfier", "satisfier", "delighter", "indifferent"],
}
DEFAULT_IDS = {"candidate": ("CAN-", 3), "requirement": ("R-", 3), "source": ("S-", 2)}
MAX_QUOTE = 300

# Personal data in quotes is replaced by one of these markers; they match any text.
MASK = re.compile(r"\[(?:redacted|name|member|email|phone|address|nric|card|id)\]", re.I)
GAP = re.compile(r"\.\.\.|…")
LINE_LOC = re.compile(r"^(?P<path>[^#\s][^#]*?):(?P<start>\d+)(?:-(?P<end>\d+))?$")
ANCHOR_LOC = re.compile(r"^(?P<path>[^#\s][^#]*?)#(?P<anchor>\S+)$")


class Finding:
    def __init__(self, severity: str, rule: str, line: int, cid: str, message: str):
        self.severity, self.rule, self.line, self.id, self.message = severity, rule, line, cid, message

    def as_dict(self) -> Dict[str, object]:
        return {"severity": self.severity, "rule": self.rule, "line": self.line, "id": self.id,
                "message": self.message}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_candidates.py",
        description=(
            "Check requirements/candidates.csv: column order, CAN-nnn IDs, required fields, "
            "allowed values, and that every Quote appears at its cited Location."
        ),
        epilog="Exit codes: 0 no errors, 1 errors found, 2 usage or parse error.",
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="candidate register to check (default: <root>/requirements/candidates.csv)",
    )
    parser.add_argument(
        "--root", default=".",
        help="repository root that Location paths are relative to (default: current directory)",
    )
    parser.add_argument(
        "--window", type=int, default=2,
        help="lines of tolerance around a cited line or range when matching a quote (default: 2)",
    )
    parser.add_argument(
        "--schema", default=None,
        help="schema.json for ID prefixes and digits (default: <root>/requirements/schema.json if present)",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="output format: text (default) or json",
    )
    return parser


def _load_ids(schema_path: Optional[Path]) -> Dict[str, Tuple[str, int]]:
    ids = dict(DEFAULT_IDS)
    if schema_path and schema_path.is_file():
        data = json.loads(schema_path.read_text(encoding="utf-8"))
        for kind in ids:
            spec = (data.get("ids") or {}).get(kind) or {}
            ids[kind] = (spec.get("prefix", ids[kind][0]), int(spec.get("digits", ids[kind][1])))
    return ids


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _segments(quote: str) -> List[str]:
    parts = GAP.split(MASK.sub("\u0000", quote))
    out: List[str] = []
    for part in parts:
        out.extend(_norm(p) for p in part.split("\u0000"))
    return [p for p in out if p]


def quote_in(quote: str, text: str) -> bool:
    """True if every segment of ``quote`` occurs in ``text`` in order (whitespace-insensitive)."""
    haystack = _norm(text)
    pos = 0
    segments = _segments(quote)
    if not segments:
        return False
    for seg in segments:
        found = haystack.find(seg, pos)
        if found < 0:
            return False
        pos = found + len(seg)
    return True


def _check_location(row: Dict[str, str], root: Path, window: int, ids, line: int, cid: str,
                    findings: List[Finding]) -> None:
    loc = row.get("Location", "").strip()
    quote = row.get("Quote", "")
    if not loc:
        return
    src_prefix = re.escape(ids["source"][0])
    if re.match(rf"^{src_prefix}\d+\b", loc):
        findings.append(Finding("info", "unverified-location", line, cid,
                                f"external location {loc!r} not verified"))
        return
    if "\\" in loc:
        findings.append(Finding("error", "bad-location", line, cid,
                                f"use forward slashes in {loc!r}"))
        return
    m_line, m_anchor = LINE_LOC.match(loc), ANCHOR_LOC.match(loc)
    rel = m_line.group("path") if m_line else m_anchor.group("path") if m_anchor else loc
    path = root / rel
    if not path.is_file():
        findings.append(Finding("error", "location-not-found", line, cid, f"file not found: {rel}"))
        return
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        findings.append(Finding("error", "location-not-found", line, cid, f"cannot read {path}: {exc}"))
        return
    if m_line:
        start = int(m_line.group("start"))
        end = int(m_line.group("end") or start)
        if start < 1 or end < start or start > len(lines):
            findings.append(Finding("error", "bad-location", line, cid,
                                    f"line range {start}-{end} outside {len(lines)} lines"))
            return
        lo, hi = max(1, start - window), min(len(lines), end + window)
        if not quote_in(quote, "\n".join(lines[lo - 1:hi])):
            findings.append(Finding("error", "quote-not-found", line, cid,
                                    f"quote not found in {m_line.group('path')} lines {lo}-{hi}"))
        return
    if not quote_in(quote, "\n".join(lines)):
        findings.append(Finding("error", "quote-not-found", line, cid,
                                f"quote not found anywhere in {path.name}"))
    elif not m_anchor:
        findings.append(Finding("warning", "no-line", line, cid,
                                "location has no line number; use path:line"))


def check(file: Path, root: Path, window: int, ids) -> List[Finding]:
    text = file.read_text(encoding="utf-8")
    if text.startswith("﻿"):
        text = text[1:]
    reader = csv.reader(io.StringIO(text))
    try:
        header = [h.strip() for h in next(reader)]
    except StopIteration:
        raise ValueError(f"{file}: empty file")
    findings: List[Finding] = []
    if header[: len(COLUMNS)] != COLUMNS:
        findings.append(Finding("error", "header", 1, "",
                                "header must be: " + ",".join(COLUMNS)))
        return findings
    if len(header) > len(COLUMNS):
        findings.append(Finding("warning", "header", 1, "",
                                "extra columns after Requirement: " + ",".join(header[len(COLUMNS):])))
    cand = re.compile(rf"^{re.escape(ids['candidate'][0])}\d{{{ids['candidate'][1]},}}$")
    req = re.compile(rf"^{re.escape(ids['requirement'][0])}\d{{{ids['requirement'][1]},}}$")
    seen: Dict[str, int] = {}
    for record in reader:
        line = reader.line_num
        if not any(c.strip() for c in record):
            continue
        record += [""] * (len(header) - len(record))
        row = {h: record[i].strip() if i < len(record) else "" for i, h in enumerate(header)}
        row["Quote"] = record[header.index("Quote")]
        cid = row["ID"]
        if not cand.match(cid):
            findings.append(Finding("error", "invalid-id", line, cid, f"ID {cid!r} does not match {cand.pattern}"))
        elif cid in seen:
            findings.append(Finding("error", "duplicate-id", line, cid, f"{cid} already used on line {seen[cid]}"))
        else:
            seen[cid] = line
        for col in REQUIRED:
            if not row.get(col, "").strip():
                findings.append(Finding("error", "missing-field", line, cid, f"{col} is empty"))
        for col, allowed in ENUMS.items():
            value = row.get(col, "")
            if value and value not in allowed:
                findings.append(Finding("error", "invalid-enum", line, cid,
                                        f"{col}={value!r}; allowed: {', '.join(a for a in allowed if a)}"))
        if row.get("Disposition") == "confirm" and not row.get("Owner"):
            findings.append(Finding("error", "missing-owner", line, cid,
                                    "confirm needs an Owner (person, role, SH-nn, or TBD)"))
        for ref in row.get("Requirement", "").split():
            if not req.match(ref):
                findings.append(Finding("error", "invalid-requirement-ref", line, cid,
                                        f"Requirement {ref!r} is not a requirement ID"))
        if len(row["Quote"]) > MAX_QUOTE:
            findings.append(Finding("warning", "quote-too-long", line, cid,
                                    f"quote has {len(row['Quote'])} characters; quote the minimum"))
        if row["Quote"].strip():
            _check_location(row, root, window, ids, line, cid, findings)
    return findings


def run(args: argparse.Namespace) -> int:
    root = Path(args.root)
    file = Path(args.file) if args.file else root / "requirements" / "candidates.csv"
    schema = Path(args.schema) if args.schema else root / "requirements" / "schema.json"
    if args.window < 0:
        sys.stderr.write("error: --window must be 0 or more\n")
        return 2
    if not file.is_file():
        sys.stderr.write(f"error: {file} not found\n")
        return 2
    try:
        ids = _load_ids(schema)
        findings = check(file, root, args.window, ids)
    except (ValueError, json.JSONDecodeError, csv.Error, UnicodeDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    errors = [f for f in findings if f.severity == "error"]
    if args.format == "json":
        print(json.dumps({"file": str(file), "errors": len(errors),
                          "findings": [f.as_dict() for f in findings]}, indent=2))
    else:
        for f in findings:
            label = f" {f.id}" if f.id else ""
            print(f"{file}:{f.line}: {f.severity} [{f.rule}]{label}: {f.message}")
        print(f"{len(errors)} error(s), {len(findings) - len(errors)} other finding(s)")
    return 1 if errors else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
