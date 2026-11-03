#!/usr/bin/env python3
# VENDORED from packages/re-lint/src/re_lint/ids.py by tools/vendor_scripts.py; do not edit.
# Change the package module, then run `python3 tools/vendor_scripts.py` to refresh this copy.
"""Allocate, list and check IDs: ``re-lint ids`` (vendored as ``re_ids.py``).

``next``  prints the next free IDs of a kind. It scans every file under the workspace (and the
          ``git log`` messages of the repository, when git is available) for the kind's prefix,
          takes the highest number in use, withdrawn and rejected IDs included, and counts up.
``check`` reports duplicate IDs, IDs that do not match the schema pattern and empty required
          attributes in the registers where IDs are defined (a structural subset of ``check``).
``list``  prints every ID in the workspace with the file and line that defines it.

Stdlib only, Python 3.9+. Exit codes: 0 ok, 1 findings (``check``), 2 usage, schema or parse
error. Edit this file only in ``packages/re-lint``; skills carry a vendored copy.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

if not __package__:  # run as a script: make the sibling reqio.py importable from any cwd
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # inside the package
    from . import reqio
except ImportError:  # vendored next to reqio.py in a skill's scripts/
    import reqio

# Where each kind's IDs are defined (one row per ID), relative to the workspace.
HOME_REGISTERS = {
    "requirement": "requirements.csv",
    "source": "sources.csv",
    "stakeholder": "stakeholders.md",
    "candidate": "candidates.csv",
    "conflict": "conflicts.md",
}
# Kinds whose IDs are defined by file names (decisions/RDR-007-slug.md).
HOME_FOLDERS = {"decision": "decisions", "change": "changes"}

_SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv"}
_MAX_BYTES = 5 * 1024 * 1024


class UsageError(Exception):
    """Bad usage or configuration (exit code 2)."""


def _display(path) -> str:
    p = Path(path)
    try:
        rel = os.path.relpath(str(p.resolve()), os.getcwd())
    except ValueError:
        rel = str(p)
    if rel.startswith(".." + os.sep) and p.is_absolute():
        rel = str(p)
    return rel.replace(os.sep, "/")


def _kinds(schema: Dict) -> List[str]:
    return list((schema.get("ids") or reqio.DEFAULT_SCHEMA["ids"]).keys())


def _check_kind(kind: str, schema: Dict) -> str:
    if kind not in _kinds(schema):
        raise UsageError(f"unknown ID kind {kind!r}; choose from {', '.join(_kinds(schema))}")
    return kind


def _context(args: argparse.Namespace) -> Tuple[Path, Dict]:
    schema_path = getattr(args, "schema", None)
    if schema_path and not Path(schema_path).is_file():
        raise UsageError(f"--schema: file not found: {schema_path}")
    if getattr(args, "workspace", None):
        ws = Path(args.workspace)
        return ws, reqio.load_schema(path=schema_path) if schema_path else workspace_schema(ws)
    schema = reqio.load_schema(path=schema_path) if schema_path else None
    ws = reqio.find_workspace(".", schema=schema)
    return ws, schema if schema is not None else workspace_schema(ws)


def workspace_schema(ws: Path) -> Dict:
    """``<ws>/schema.json``, else ``<repo root>/requirements/schema.json``, else the defaults."""
    if (ws / "schema.json").is_file():
        return reqio.load_schema(workspace=ws)
    return reqio.load_schema(path=reqio.find_repo_root(ws) / "requirements" / "schema.json")


def iter_text_files(folder: Path) -> Iterator[Path]:
    """Every readable text file under ``folder`` (skips VCS folders and binary files)."""
    if not folder.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            try:
                if path.stat().st_size > _MAX_BYTES:
                    continue
                with open(path, "rb") as handle:
                    if b"\0" in handle.read(8192):
                        continue
            except OSError:
                continue
            yield path


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def git_log_text(start: Path) -> str:
    """All commit messages reachable from any ref, or "" when git is unavailable."""
    root = reqio.find_repo_root(start if start.exists() else Path("."))
    try:
        proc = subprocess.run(["git", "log", "--all", "--format=%B"], cwd=str(root),
                              capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ""
    return proc.stdout if proc.returncode == 0 else ""


def occurrences(ws: Path, kind: str, schema: Dict) -> List[Tuple[str, int, Path, int]]:
    """``(id, number, file, line)`` for every mention of ``kind`` IDs under the workspace."""
    pattern = reqio.id_prefix_regex(kind, schema)
    found: List[Tuple[str, int, Path, int]] = []
    for path in iter_text_files(ws):
        text = _read(path)
        if not pattern.search(text):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in pattern.finditer(line):
                number = int(m.group(1))
                found.append((reqio.format_id(kind, number, schema), number, path, lineno))
    return found


def highest_number(ws: Path, kind: str, schema: Dict, use_git: bool = True) -> int:
    pattern = reqio.id_prefix_regex(kind, schema)
    best = 0
    for path in iter_text_files(ws):
        for m in pattern.finditer(_read(path)):
            best = max(best, int(m.group(1)))
    if use_git:
        for m in pattern.finditer(git_log_text(ws)):
            best = max(best, int(m.group(1)))
    return best


def next_ids(ws: Path, kind: str, schema: Dict, count: int = 1, use_git: bool = True) -> List[str]:
    start = highest_number(ws, kind, schema, use_git=use_git) + 1
    return [reqio.format_id(kind, n, schema) for n in range(start, start + count)]


# --------------------------------------------------------------------------- check


def _detect_kind(values: Sequence[str], schema: Dict) -> Optional[str]:
    best, best_hits = None, 0
    for kind in _kinds(schema):
        pattern = reqio.id_regex(kind, schema)
        hits = sum(1 for v in values if pattern.match(v))
        if hits > best_hits:
            best, best_hits = kind, hits
    return best


def _finding(rule: str, file, line: int, rid: str, message: str) -> Dict:
    return {"rule": rule, "severity": "error", "id": rid, "file": _display(file), "line": line,
            "message": message}


def check_registers(paths: Sequence[Path], schema: Dict, ws: Optional[Path] = None,
                    explicit: bool = True) -> Tuple[List[Dict], int]:
    """Structural checks; returns ``(findings, rows_checked)``.

    ``ws`` also checks file-name IDs in ``decisions/`` and ``changes/``. With ``explicit`` a file
    without an ``ID`` table is a usage error; otherwise it is skipped.
    """
    findings: List[Dict] = []
    rows_checked = 0
    seen: Dict[Tuple[str, str], Tuple[Path, int]] = {}
    attrs = schema.get("attributes") or {}
    required = [c for c in attrs.get("required", []) if isinstance(c, str)]
    for path in paths:
        tables = [t for t in reqio.read_tables(path) if "ID" in t.columns]
        if not tables:
            if explicit:
                raise UsageError(f"{_display(path)}: no table with an 'ID' column")
            continue
        table = tables[0]  # the register table; later tables in a Markdown file are views
        values = [r.get_str("ID") for r in table.rows if r.get_str("ID")]
        kind = _detect_kind(values, schema) or ("requirement" if path.suffix.lower() == ".csv" else None)
        if kind is None:
            continue
        pattern = reqio.id_regex(kind, schema)
        is_requirements = kind == "requirement" and (
            path.name == "requirements.csv" or "Text" in table.columns)
        if is_requirements:
            for column in required:
                if column not in table.columns:
                    findings.append(_finding("missing-attribute", path, table.header_line, "",
                                             f'required column "{column}" is missing from the header'))
        for row in table.rows:
            rows_checked += 1
            rid = row.get_str("ID")
            if not rid:
                findings.append(_finding("missing-attribute", path, row.line, "", 'required attribute "ID" is empty'))
            elif not pattern.match(rid):
                example = reqio.format_id(kind, 1, schema)
                findings.append(_finding("invalid-id", path, row.line, rid,
                                         f'"{rid}" does not match the {kind} ID pattern {pattern.pattern} (e.g. {example})'))
            else:
                key = (kind, rid)
                if key in seen:
                    first, first_line = seen[key]
                    findings.append(_finding("duplicate-id", path, row.line, rid,
                                             f"{rid} is already defined at {_display(first)}:{first_line}"))
                else:
                    seen[key] = (path, row.line)
            if is_requirements:
                for column in required:
                    if column != "ID" and column in table.columns and not row.get_str(column):
                        findings.append(_finding("missing-attribute", path, row.line, rid,
                                                 f'required attribute "{column}" is empty'))
    if ws is not None:
        for kind, folder in HOME_FOLDERS.items():
            directory = ws / folder
            if not directory.is_dir() or kind not in _kinds(schema):
                continue
            spec = (schema.get("ids") or {}).get(kind) or {}
            prefix = re.compile(rf"^{re.escape(str(spec.get('prefix', '')))}(\d+)(?!\d)")
            by_number: Dict[int, Path] = {}
            for path in sorted(directory.iterdir()):
                m = prefix.match(path.name)
                if not m or not path.is_file():
                    continue
                rows_checked += 1
                number = int(m.group(1))
                rid = reqio.format_id(kind, number, schema)
                if number in by_number:
                    findings.append(_finding("duplicate-id", path, 1, rid,
                                             f"{rid} is already used by {_display(by_number[number])}"))
                else:
                    by_number[number] = path
    return findings, rows_checked


def default_check_paths(ws: Path) -> List[Path]:
    return [ws / name for name in HOME_REGISTERS.values() if (ws / name).is_file()]


# --------------------------------------------------------------------------- commands


def _gh(value: str, prop: bool = False) -> str:
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return value.replace(":", "%3A").replace(",", "%2C") if prop else value


def cmd_next(args: argparse.Namespace) -> int:
    ws, schema = _context(args)
    kind = _check_kind(args.kind, schema)
    if args.count < 1:
        raise UsageError("--count must be at least 1")
    for rid in next_ids(ws, kind, schema, count=args.count, use_git=not args.no_git):
        print(rid)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    ws, schema = _context(args)
    if args.paths:
        paths = [Path(p) for p in args.paths]
        for p in paths:
            if not p.is_file():
                raise UsageError(f"file not found: {p}")
        folder_ws = None
    else:
        paths = default_check_paths(ws)
        folder_ws = ws
        if not paths and not any((ws / f).is_dir() for f in HOME_FOLDERS.values()):
            raise UsageError(f"no ID registers found under {_display(ws)} (looked for "
                             f"{', '.join(HOME_REGISTERS.values())}); pass PATH")
    findings, rows = check_registers(paths, schema, folder_ws, explicit=bool(args.paths))
    findings.sort(key=lambda f: (f["file"], f["line"]))
    if args.format == "json":
        print(json.dumps({"tool": "re-lint ids", "rows_checked": rows, "findings": findings}, indent=2))
    else:
        for f in findings:
            rid = f" {f['id']}" if f["id"] else ""
            if args.format == "github":
                text = f"{f['id']}: {f['message']}" if f["id"] else f["message"]
                print(f"::error file={_gh(f['file'], True)},line={f['line']},"
                      f"title={_gh('re-lint ' + f['rule'], True)}::{_gh(text)}")
            else:
                print(f"{f['file']}:{f['line']}: error {f['rule']}{rid}: {f['message']}")
        n = len(findings)
        print(f"re-lint ids: {n} error{'s' if n != 1 else ''} in {rows} row{'s' if rows != 1 else ''}"
              if n else f"re-lint ids: no findings in {rows} row{'s' if rows != 1 else ''}")
    return 1 if findings else 0


def cmd_list(args: argparse.Namespace) -> int:
    ws, schema = _context(args)
    kinds = [_check_kind(args.kind, schema)] if args.kind else _kinds(schema)
    entries = []
    for kind in kinds:
        home = ws / HOME_REGISTERS.get(kind, "")
        by_id: Dict[str, List[Tuple[Path, int]]] = {}
        numbers: Dict[str, int] = {}
        for rid, number, path, line in occurrences(ws, kind, schema):
            by_id.setdefault(rid, []).append((path, line))
            numbers[rid] = number
        for rid in sorted(by_id, key=lambda r: numbers[r]):
            places = by_id[rid]
            defining = next((p for p in places if p[0] == home), places[0])
            entries.append({"id": rid, "kind": kind, "file": _display(defining[0]), "line": defining[1],
                            "occurrences": [{"file": _display(p), "line": n} for p, n in places]})
    if args.format == "json":
        print(json.dumps(entries, indent=2))
        return 0
    for e in entries:
        if args.all:
            for o in e["occurrences"]:
                print(f"{e['id']}\t{o['file']}:{o['line']}")
        else:
            refs = len(e["occurrences"]) - 1
            extra = f"\t(+{refs} reference{'s' if refs != 1 else ''})" if refs else ""
            print(f"{e['id']}\t{e['file']}:{e['line']}{extra}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Allocate the next free IDs, list IDs, and check registers for duplicate, "
                    "malformed or incomplete IDs.",
        epilog="Exit codes: 0 ok, 1 findings (check), 2 usage, schema or parse error.")
    sub = parser.add_subparsers(dest="action", metavar="ACTION")
    sub.required = True

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--workspace", metavar="DIR",
                       help="workspace folder (default: <repo root>/requirements, or the schema's workspace)")
        p.add_argument("--schema", metavar="FILE", help="schema.json to use (default: <workspace>/schema.json)")

    nxt = sub.add_parser("next", help="print the next free IDs of a kind, one per line",
                         description="Print the next free IDs: the highest number in use under the "
                                     "workspace or in git log messages (withdrawn IDs included) plus one.")
    nxt.add_argument("--kind", default="requirement",
                     help="ID kind: requirement (default), source, stakeholder, interview, candidate, "
                          "conflict, decision, open-decision, change, finding")
    nxt.add_argument("--count", type=int, default=1, metavar="N", help="how many IDs to allocate (default 1)")
    nxt.add_argument("--no-git", action="store_true", help="do not scan git log messages")
    common(nxt)

    chk = sub.add_parser("check", help="check registers for duplicate, malformed or incomplete IDs",
                         description="Check ID registers (default: requirements.csv, sources.csv, "
                                     "stakeholders.md, candidates.csv, conflicts.md, decisions/, changes/).")
    chk.add_argument("paths", nargs="*", metavar="PATH", help="register files (.csv or .md)")
    chk.add_argument("--format", choices=("text", "json", "github"), default="text",
                     help="output format (default: text)")
    common(chk)

    lst = sub.add_parser("list", help="list every ID in the workspace with its file:line",
                         description="List every ID in the workspace with the file and line that defines it.")
    lst.add_argument("--kind", help="only this ID kind (default: every kind)")
    lst.add_argument("--all", action="store_true", help="print every occurrence, not just the defining one")
    lst.add_argument("--format", choices=("text", "json"), default="text", help="output format (default: text)")
    common(lst)
    return parser


def run(args: argparse.Namespace) -> int:
    handlers = {"next": cmd_next, "check": cmd_check, "list": cmd_list}
    try:
        return handlers[args.action](args)
    except UsageError as exc:
        sys.stderr.write(f"re-lint ids: error: {exc}\n")
        return 2
    except (ValueError, OSError, KeyError) as exc:
        sys.stderr.write(f"re-lint ids: error: {exc}\n")
        return 2


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
