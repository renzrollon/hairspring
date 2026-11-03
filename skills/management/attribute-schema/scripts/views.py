#!/usr/bin/env python3
# VENDORED from packages/re-lint/src/re_lint/views.py by tools/vendor_scripts.py; do not edit.
# Change the package module, then run `python3 tools/vendor_scripts.py` to refresh this copy.
"""Generate selective, projective and aggregating views of the requirement register.

Usage::

    re-lint views [--view NAME ...] [--out DIR] [--format md|csv] [--stdout] [--list]

Each view writes ``<workspace>/views/<name>.md`` (or ``.csv``). Rows come from
``requirements.csv`` and ``stories/*.md`` (``requirements.csv`` wins on a duplicate ID).

Built-in views (a custom view with the same name replaces it):

``po``         functional requirements and stories (Type ``F`` or empty): ID, Title, Status,
               Priority; counts by Status
``architect``  quality requirements and constraints (Type ``Q``, ``C``) with Status ``agreed``
               or ``proposed``; counts by Type
``qa``         requirements without a ``Verification`` method (withdrawn and rejected ones
               excluded); counts by Type

Custom views live in ``schema.json`` under ``views``::

    "views": {
      "security": {
        "title": "Security-relevant requirements",
        "filter": {"Type": ["Q", "C"], "Status": ["agreed"], "Tags": {"has": "security"}},
        "columns": ["ID", "Title|Text", "Status", "Owner"],
        "group_by": "Status",
        "sort_by": "Priority"
      }
    }

``filter`` (selective view): every condition must hold. A condition is

* a list (or one string) of allowed values, compared case-insensitively; ``""`` matches an
  empty cell: ``"Type": ["Q", "C"]``;
* ``{"not": [...]}``: the value is none of these;
* ``{"empty": true}`` / ``{"empty": false}``: the cell is empty (or ``TBD``) / filled;
* ``{"contains": "text"}``: case-insensitive substring;
* ``{"has": "tag"}`` or ``{"has": ["a", "b"]}``: a space- or comma-separated cell
  (``Tags``, ``Links``) holds at least one of these tokens.

``columns`` (projective view): the columns shown, in order (default: the register columns).
``A|B`` shows A, falling back to B when A is empty; the header is ``A``.
``group_by`` (aggregating view): a column name or a list of names; adds a count table per value
(per combination for a list). ``sort_by``: a column; enum columns (Priority, Status, ...) sort in
schema order; default is ID order. ``title``: the heading.

Exit codes: 0 ok, 2 usage, schema or view-definition error.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

if not __package__:  # run as a plain script: make the sibling reqio.py importable
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # inside the package
    from . import reqio
except ImportError:  # vendored next to reqio.py in a skill's scripts/
    import reqio

BUILTIN_VIEWS: Dict[str, Dict] = OrderedDict(
    [
        ("po", {
            "title": "Product owner view: functional requirements and stories",
            "filter": {"Type": ["F", ""]},
            "columns": ["ID", "Title|Text", "Status", "Priority"],
            "group_by": "Status",
        }),
        ("architect", {
            "title": "Architect view: quality requirements and constraints (agreed or proposed)",
            "filter": {"Type": ["Q", "C"], "Status": ["agreed", "proposed"]},
            "columns": ["ID", "Type", "Text", "Status", "Priority", "Rationale"],
            "group_by": "Type",
        }),
        ("qa", {
            "title": "QA view: requirements without a verification method",
            "filter": {"Verification": {"empty": True}, "Status": {"not": ["withdrawn", "rejected"]}},
            "columns": ["ID", "Type", "Text", "Status", "Priority"],
            "group_by": "Type",
        }),
    ]
)
EMPTY_VALUES = {"", "tbd", "tbc"}
_VIEW_KEYS = {"title", "filter", "columns", "group_by", "sort_by", "description"}
_COND_KEYS = {"not", "empty", "contains", "has"}
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class UsageError(Exception):
    """A problem the user can fix (exit 2)."""


def _workspace(args: argparse.Namespace) -> Tuple[Path, Dict]:
    schema_path = getattr(args, "schema", None)
    if schema_path and not Path(schema_path).is_file():
        raise UsageError(f"schema file not found: {schema_path}")
    if getattr(args, "workspace", None):
        ws = Path(args.workspace).resolve()
    else:
        base = reqio.load_schema(schema_path) if schema_path else None
        ws = reqio.find_workspace(".", base).resolve()
    return ws, reqio.load_schema(schema_path, workspace=ws)


def _id_key(value: str) -> Tuple:
    match = re.match(r"^(.*?)(\d+)(.*)$", value or "")
    if not match:
        return (value or "", -1, "")
    return (match.group(1), int(match.group(2)), match.group(3))


def _md_cell(value: object) -> str:
    return " ".join(str(value if value is not None else "").split()).replace("|", "\\|")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def load_rows(ws: Path, schema: Dict) -> Tuple[List[reqio.Row], List[str]]:
    """Unique requirement rows and the union of their columns (register order first)."""
    rows: "OrderedDict[str, reqio.Row]" = OrderedDict()
    columns: List[str] = []
    try:
        for path in reqio.requirement_files(ws):
            for table in reqio.read_tables(path):
                if "ID" not in table.columns:
                    continue
                pattern = reqio.id_regex("requirement", schema)
                matched = False
                for row in table.rows:
                    rid = row.get_str("ID")
                    if pattern.match(rid):
                        matched = True
                        rows.setdefault(rid, row)
                if matched:
                    columns += [c for c in table.columns if c not in columns]
    except UnicodeDecodeError as exc:
        raise UsageError(f"cannot read the requirement registers as UTF-8: {exc}") from exc
    return list(rows.values()), columns


# --------------------------------------------------------------------------- view definitions


def validate_view(name: str, view: object) -> Dict:
    """Check a view definition; raise ``UsageError`` with a precise message."""
    where = f"view {name!r}"
    if not _NAME_RE.match(name):
        raise UsageError(f"{where}: names use letters, digits, '-' and '_' (it becomes a file name)")
    if not isinstance(view, dict):
        raise UsageError(f"{where}: must be an object with filter, columns, group_by, title")
    unknown = set(view) - _VIEW_KEYS
    if unknown:
        raise UsageError(f"{where}: unknown key(s) {', '.join(sorted(unknown))}; use {', '.join(sorted(_VIEW_KEYS))}")
    flt = view.get("filter", {})
    if not isinstance(flt, dict):
        raise UsageError(f"{where}: 'filter' must be an object of column -> condition")
    for col, cond in flt.items():
        if isinstance(cond, (str, int, float)):
            continue
        if isinstance(cond, list):
            if not all(isinstance(v, (str, int, float)) for v in cond):
                raise UsageError(f"{where}: filter {col!r} lists must hold strings")
            continue
        if isinstance(cond, dict):
            bad = set(cond) - _COND_KEYS
            if bad or not cond:
                raise UsageError(f"{where}: filter {col!r} uses {', '.join(sorted(bad)) or 'an empty object'}; "
                                 f"conditions are a value list or one of {', '.join(sorted(_COND_KEYS))}")
            if "empty" in cond and not isinstance(cond["empty"], bool):
                raise UsageError(f"{where}: filter {col!r}: 'empty' must be true or false")
            continue
        raise UsageError(f"{where}: filter {col!r} must be a value, a list or a condition object")
    cols = view.get("columns")
    if cols is not None and (not isinstance(cols, list) or not cols or not all(isinstance(c, str) and c for c in cols)):
        raise UsageError(f"{where}: 'columns' must be a non-empty list of column names")
    group = view.get("group_by")
    if group is not None and not (isinstance(group, str) or (isinstance(group, list) and group
                                                              and all(isinstance(g, str) for g in group))):
        raise UsageError(f"{where}: 'group_by' must be a column name or a list of names")
    if view.get("sort_by") is not None and not isinstance(view.get("sort_by"), str):
        raise UsageError(f"{where}: 'sort_by' must be a column name")
    if view.get("title") is not None and not isinstance(view.get("title"), str):
        raise UsageError(f"{where}: 'title' must be a string")
    return view


def all_views(schema: Dict) -> "OrderedDict[str, Dict]":
    custom = schema.get("views") or {}
    if not isinstance(custom, dict):
        raise UsageError("schema.json 'views' must be an object of name -> view definition")
    views: "OrderedDict[str, Dict]" = OrderedDict(BUILTIN_VIEWS)
    for name, view in custom.items():
        views[name] = validate_view(name, view)
    return views


def _tokens(value: str) -> List[str]:
    return [t.lower() for t in re.split(r"[\s,;]+", value) if t]


def matches(row: reqio.Row, flt: Dict) -> bool:
    for col, cond in flt.items():
        value = row.get_str(col)
        low = value.lower()
        if isinstance(cond, dict):
            if "not" in cond:
                excluded = cond["not"] if isinstance(cond["not"], list) else [cond["not"]]
                if low in {str(v).strip().lower() for v in excluded}:
                    return False
            if "empty" in cond and (low in EMPTY_VALUES) != cond["empty"]:
                return False
            if "contains" in cond and str(cond["contains"]).lower() not in low:
                return False
            if "has" in cond:
                wanted = cond["has"] if isinstance(cond["has"], list) else [cond["has"]]
                if not {str(w).lower() for w in wanted} & set(_tokens(value)):
                    return False
        else:
            allowed = cond if isinstance(cond, list) else [cond]
            if low not in {str(v).strip().lower() for v in allowed}:
                return False
    return True


def _cell(row: reqio.Row, spec: str) -> str:
    for part in spec.split("|"):
        value = row.get_str(part.strip())
        if value:
            return value
    return ""


def _header(spec: str) -> str:
    return spec.split("|", 1)[0].strip()


def _sort_rows(rows: List[reqio.Row], sort_by: Optional[str], schema: Dict) -> List[reqio.Row]:
    by_id = sorted(rows, key=lambda r: _id_key(r.get_str("ID")))
    if not sort_by:
        return by_id
    enum = [v.lower() for v in ((schema.get("attributes") or {}).get("enums") or {}).get(sort_by, [])]
    if enum:
        return sorted(by_id, key=lambda r: (enum.index(r.get_str(sort_by).lower())
                                           if r.get_str(sort_by).lower() in enum else len(enum)))
    return sorted(by_id, key=lambda r: _cell(r, sort_by).lower())


def _describe_filter(flt: Dict) -> str:
    parts = []
    for col, cond in flt.items():
        if isinstance(cond, dict):
            for key, val in cond.items():
                vals = val if isinstance(val, list) else [val]
                if key == "empty":
                    parts.append(f"{col} is {'empty' if val else 'filled'}")
                else:
                    verb = {"not": "not in", "contains": "contains", "has": "has"}[key]
                    parts.append(f"{col} {verb} {', '.join(str(v) for v in vals)}")
        else:
            vals = cond if isinstance(cond, list) else [cond]
            parts.append(f"{col} in " + ", ".join(str(v) if str(v) else "(empty)" for v in vals))
    return "; ".join(parts) or "all requirements"


def build_view(name: str, view: Dict, rows: List[reqio.Row], columns: List[str], schema: Dict) -> Dict:
    selected = [r for r in rows if matches(r, view.get("filter") or {})]
    selected = _sort_rows(selected, view.get("sort_by"), schema)
    specs = list(view.get("columns") or columns or ["ID"])
    group = view.get("group_by")
    groups = [group] if isinstance(group, str) else list(group or [])
    counts: Counter = Counter(tuple(_cell(r, g) or "(empty)" for g in groups) for r in selected) if groups else Counter()
    return {"name": name, "title": view.get("title") or f"View: {name}", "filter": view.get("filter") or {},
            "columns": specs, "rows": selected, "group_by": groups, "counts": counts}


def render_md(result: Dict, register: str) -> str:
    out = [f"# {result['title']}", "",
           f"Generated by `re-lint views --view {result['name']}` from `{register}`; rerun it instead of editing.",
           "", f"- Filter: {_md_cell(_describe_filter(result['filter']))}",
           f"- Requirements: {len(result['rows'])}", ""]
    if result["group_by"]:
        out += ["## Counts", "", "| " + " | ".join(result["group_by"]) + " | Count |",
                "| " + " | ".join("---" for _ in result["group_by"]) + " | --- |"]
        for key, count in sorted(result["counts"].items(), key=lambda kv: (-kv[1], kv[0])):
            out.append("| " + " | ".join(_md_cell(k) for k in key) + f" | {count} |")
        out.append("")
    headers = [_header(c) for c in result["columns"]]
    out += ["## Requirements", ""]
    if not result["rows"]:
        out += ["None.", ""]
    else:
        out += ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
        for row in result["rows"]:
            out.append("| " + " | ".join(_md_cell(_cell(row, c)) for c in result["columns"]) + " |")
        out.append("")
    return "\n".join(out)


def cmd_views(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    views = all_views(schema)
    if args.list:
        for name, view in views.items():
            kind = "custom" if name in (schema.get("views") or {}) else "built-in"
            print(f"{name:<12} {kind:<9} {view.get('title') or ''}")
        return 0
    wanted = []
    for value in args.view or []:
        wanted += [v for v in re.split(r"[,\s]+", value) if v]
    unknown = [v for v in wanted if v not in views]
    if unknown:
        raise UsageError(f"unknown view(s) {', '.join(unknown)}; available: {', '.join(views)}")
    names = wanted or list(views)
    rows, columns = load_rows(ws, schema)
    if not rows:
        raise UsageError(f"no requirements found in {ws} (expected requirements.csv or stories/*.md)")
    known_cols = set(columns) | set((schema.get("attributes") or {}).get("columns") or []) \
        | set((schema.get("attributes") or {}).get("optional") or [])
    out_dir = Path(args.out) if args.out else ws / "views"
    register = os.path.relpath(ws / "requirements.csv", reqio.find_repo_root(ws)).replace(os.sep, "/")
    for name in names:
        view = views[name]
        referenced = list((view.get("filter") or {}).keys()) + [p.strip() for c in view.get("columns") or [] for p in c.split("|")]
        referenced += [view["group_by"]] if isinstance(view.get("group_by"), str) else list(view.get("group_by") or [])
        typos = sorted({c for c in referenced if c and c not in known_cols})
        if typos:
            print(f"warning: view {name!r} uses column(s) not in the register or schema: {', '.join(typos)}",
                  file=sys.stderr)
        result = build_view(name, view, rows, columns, schema)
        if args.format == "csv":
            headers = [_header(c) for c in result["columns"]]
            records = [{h: _cell(r, c) for h, c in zip(headers, result["columns"])} for r in result["rows"]]
            if args.stdout:
                buf = io.StringIO()
                writer = csv.writer(buf, lineterminator="\n")
                writer.writerow(headers)
                for rec in records:
                    writer.writerow([rec[h] for h in headers])
                print(buf.getvalue(), end="")
            else:
                path = out_dir / f"{name}.csv"
                reqio.write_csv(path, records, headers)
                print(f"wrote {path} ({len(records)} requirements)")
        else:
            text = render_md(result, register)
            if args.stdout:
                print(text)
            else:
                path = out_dir / f"{name}.md"
                _write_text(path, text)
                print(f"wrote {path} ({len(result['rows'])} requirements)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="views.py",
        description="Write audience views of the requirement register: selective (filter), projective "
                    "(columns) and aggregating (group_by counts). Built-in views: po, architect, qa; "
                    "custom views come from schema.json 'views'.",
        epilog=(
            "Custom view format (schema.json):\n"
            '  "views": {"security": {"title": "...", "filter": {"Type": ["Q","C"], "Status": ["agreed"],\n'
            '            "Tags": {"has": "security"}}, "columns": ["ID", "Title|Text", "Status"],\n'
            '            "group_by": "Status", "sort_by": "Priority"}}\n'
            "Conditions: a value list, {\"not\": [...]}, {\"empty\": true|false}, {\"contains\": \"x\"}, "
            "{\"has\": \"tag\"}.\n"
            "'A|B' in columns falls back to B when A is empty.\n"
            "Exit codes: 0 ok, 2 usage or view-definition error."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--view", metavar="NAME", nargs="+", action="extend",
                        help="views to generate (default: all built-in and custom views)")
    parser.add_argument("--out", metavar="DIR", help="output folder (default: <workspace>/views)")
    parser.add_argument("--format", choices=("md", "csv"), default="md",
                        help="md (default; with counts) or csv (projected rows only)")
    parser.add_argument("--stdout", action="store_true", help="print the views instead of writing files")
    parser.add_argument("--list", action="store_true", help="list the available views and exit")
    parser.add_argument("--workspace", metavar="DIR", help="workspace folder (default: <repo root>/requirements)")
    parser.add_argument("--schema", metavar="FILE", help="schema.json to use (default: <workspace>/schema.json)")
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        return cmd_views(args)
    except (UsageError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
