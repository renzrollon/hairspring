#!/usr/bin/env python3
# VENDORED from packages/re-lint/src/re_lint/reqio.py by tools/vendor_scripts.py; do not edit.
# Change the package module, then run `python3 tools/vendor_scripts.py` to refresh this copy.
"""Shared reader/writer for re-skills work products.

Stdlib only, Python 3.9+. This file is vendored verbatim into skills' ``scripts/``
folders by ``tools/vendor_scripts.py``; edit it only in ``packages/re-lint``.
"""
from __future__ import annotations

import copy
import csv
import io
import json
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Union

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_SCHEMA",
    "ID_IN_TEXT",
    "Row",
    "Table",
    "find_repo_root",
    "find_workspace",
    "load_schema",
    "id_regex",
    "id_prefix_regex",
    "read_table",
    "read_tables",
    "read_requirements",
    "requirement_files",
    "write_csv",
    "format_id",
    "parse_id_number",
    "ordered_columns",
]

PathLike = Union[str, Path]

DEFAULT_SCHEMA: Dict = {
    "version": 1,
    "workspace": "requirements",
    "process": {
        "lifecycle": "iterative",
        "approach": "explorative",
        "target": "customer-specific",
        "change_authority": "product-owner",
    },
    "ids": {
        "requirement": {"prefix": "R-", "digits": 3},
        "source": {"prefix": "S-", "digits": 2},
        "stakeholder": {"prefix": "SH-", "digits": 2},
        "interview": {"prefix": "I-", "digits": 2},
        "candidate": {"prefix": "CAN-", "digits": 3},
        "conflict": {"prefix": "CF-", "digits": 2},
        "decision": {"prefix": "RDR-", "digits": 3},
        "open-decision": {"prefix": "D-", "digits": 2},
        "change": {"prefix": "CR-", "digits": 3},
        "finding": {"prefix": "F-", "digits": 2},
    },
    "attributes": {
        "columns": ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale"],
        "required": ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale"],
        "optional": [
            "Title", "Owner", "Version", "Stability", "Risk",
            "Verification", "Kano", "Links", "Tags",
        ],
        "enums": {
            "Type": ["F", "Q", "C"],
            "Priority": ["must", "should", "could", "wont"],
            "Status": [
                "draft", "proposed", "agreed", "implemented", "verified",
                "deferred", "rejected", "withdrawn",
            ],
            "Stability": ["stable", "volatile", "unknown"],
            "Risk": ["high", "medium", "low"],
            "Verification": ["test", "inspection", "analysis", "demonstration"],
            "Kano": ["dissatisfier", "satisfier", "delighter", "indifferent"],
        },
    },
    "lifecycle": {
        "initial": "draft",
        "transitions": {
            "draft": ["proposed", "rejected", "withdrawn"],
            "proposed": ["agreed", "draft", "rejected", "deferred", "withdrawn"],
            "agreed": ["implemented", "deferred", "withdrawn", "proposed"],
            "implemented": ["verified", "agreed", "withdrawn"],
            "verified": ["agreed", "withdrawn"],
            "deferred": ["proposed", "withdrawn"],
            "rejected": ["draft"],
            "withdrawn": [],
        },
    },
    "lint": {"disable": [], "severity": {}, "extra_weak_words": [], "allow_words": []},
    "trace": {
        "code_globs": [
            "src/**", "app/**", "lib/**", "pkg/**", "internal/**", "cmd/**", "services/**",
        ],
        "test_globs": [
            "tests/**", "test/**", "spec/**", "**/*_test.*", "**/*.test.*",
            "**/*.spec.*", "**/test_*.py", "e2e/**",
        ],
        "adr_dirs": ["docs/adr", "doc/adr", "adr", "docs/decisions"],
        "scan_git_log": True,
    },
    "issues": {
        "status_map": {
            "github": {"open": "agreed", "closed": "implemented"},
            "jira": {"To Do": "agreed", "In Progress": "agreed", "Done": "implemented"},
            "ado": {
                "New": "agreed", "Active": "agreed",
                "Resolved": "implemented", "Closed": "verified",
            },
        }
    },
    "views": {},
    "definition_of_ready": [
        "Has an ID, type, source, priority and rationale",
        "Passes re-lint check with no errors",
        "Has a verification method and a measurable acceptance criterion",
        "Open questions are resolved or explicitly deferred with an owner",
        "Dependencies and constraints are named",
    ],
}

# Any requirement-like ID in free text: R-012, R-012.AC2. Word-bounded so "PR-12" or "CR-012"
# do not match as requirements. Test-name forms (r_012, R012) are handled by normalize helpers
# in the tracing module.
ID_IN_TEXT = re.compile(r"(?<![A-Za-z0-9_-])(R-\d{3,})(?:\.AC\d+)?(?![A-Za-z0-9])")

_MARKERS = (".git", "requirements", ".hg")


class Row(dict):
    """A table row (column -> value) that remembers where it came from."""

    file: str = ""
    line: int = 0
    end_line: int = 0

    def __init__(self, data: Optional[Dict[str, str]] = None, file: str = "", line: int = 0):
        super().__init__(data or {})
        self.file = file
        self.line = line
        # Last physical line of the row (a quoted CSV field may span several lines).
        self.end_line = line

    def get_str(self, key: str) -> str:
        value = self.get(key)
        return "" if value is None else str(value).strip()


class Table:
    """Rows plus the column order they were read with."""

    def __init__(self, columns: Sequence[str], rows: List[Row], file: str = "", header_line: int = 1):
        self.columns = list(columns)
        self.rows = rows
        self.file = file
        self.header_line = header_line  # 1-based line of the header row in ``file``

    def __iter__(self) -> Iterator[Row]:
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)


# --------------------------------------------------------------------------- locations


def find_repo_root(start: PathLike = ".") -> Path:
    """Walk up from ``start`` to the nearest directory holding ``.git``.

    Falls back to the nearest directory holding a ``requirements/`` folder, then to ``start``.
    """
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    candidates = [here, *here.parents]
    for path in candidates:
        if (path / ".git").exists():
            return path
    for path in candidates:
        if (path / "requirements").is_dir():
            return path
    return here


def find_workspace(start: PathLike = ".", schema: Optional[Dict] = None) -> Path:
    """Return the workspace folder (``<repo root>/requirements`` by default)."""
    root = find_repo_root(start)
    if schema is None:
        schema = load_schema(workspace=root / "requirements")
    return root / str(schema.get("workspace") or "requirements")


def _deep_merge(base: Dict, override: Dict) -> Dict:
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_schema(path: Optional[PathLike] = None, workspace: Optional[PathLike] = None) -> Dict:
    """Load ``schema.json`` merged over :data:`DEFAULT_SCHEMA`.

    Looks at ``path`` if given, else ``<workspace>/schema.json``, else ``./requirements/schema.json``
    under the repo root. A missing file yields the defaults. A malformed file raises ``ValueError``.
    """
    candidate: Optional[Path] = None
    if path:
        candidate = Path(path)
    elif workspace:
        candidate = Path(workspace) / "schema.json"
    else:
        candidate = find_repo_root(".") / "requirements" / "schema.json"
    if candidate and candidate.is_file():
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{candidate}: invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"{candidate}: schema must be a JSON object")
        merged = _deep_merge(DEFAULT_SCHEMA, data)
        merged["_path"] = str(candidate)
        return merged
    merged = copy.deepcopy(DEFAULT_SCHEMA)
    merged["_path"] = ""
    return merged


# --------------------------------------------------------------------------- IDs


def _id_spec(kind: str, schema: Optional[Dict]) -> Dict:
    ids = (schema or DEFAULT_SCHEMA).get("ids", {})
    spec = ids.get(kind) or DEFAULT_SCHEMA["ids"].get(kind)
    if not spec:
        raise KeyError(f"unknown ID kind: {kind}")
    return spec


def id_regex(kind: str = "requirement", schema: Optional[Dict] = None) -> "re.Pattern[str]":
    """Full-match pattern for one ID of ``kind`` (``R-012``), honoring a custom ``pattern``."""
    spec = _id_spec(kind, schema)
    if spec.get("pattern"):
        return re.compile(spec["pattern"])
    prefix = re.escape(spec.get("prefix", ""))
    digits = int(spec.get("digits", 3))
    return re.compile(rf"^{prefix}\d{{{digits},}}$")


def id_prefix_regex(kind: str = "requirement", schema: Optional[Dict] = None) -> "re.Pattern[str]":
    """Search pattern finding IDs of ``kind`` inside text; group 1 is the number."""
    spec = _id_spec(kind, schema)
    prefix = re.escape(spec.get("prefix", ""))
    return re.compile(rf"(?<![A-Za-z0-9_-]){prefix}(\d+)(?![A-Za-z0-9])")


def format_id(kind: str, number: int, schema: Optional[Dict] = None) -> str:
    spec = _id_spec(kind, schema)
    return f"{spec.get('prefix', '')}{number:0{int(spec.get('digits', 3))}d}"


def parse_id_number(value: str, kind: str = "requirement", schema: Optional[Dict] = None) -> Optional[int]:
    match = id_prefix_regex(kind, schema).search(value or "")
    return int(match.group(1)) if match else None


# --------------------------------------------------------------------------- reading

_SEP_CELL = re.compile(r"^:?-{1,}:?$")


def _split_md_row(line: str) -> List[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    cells: List[str] = []
    buf: List[str] = []
    in_code = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text) and text[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def _is_separator(cells: List[str]) -> bool:
    return bool(cells) and all(_SEP_CELL.match(c.replace(" ", "")) for c in cells if c != "") and any(cells)


def _normalize_header(name: str) -> str:
    return re.sub(r"[*_`]", "", name).strip()


def _markdown_tables(path: Path, text: str) -> List[Table]:
    tables: List[Table] = []
    lines = text.splitlines()
    i = 0
    in_fence = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence or not stripped.startswith("|"):
            i += 1
            continue
        if i + 1 < len(lines) and _is_separator(_split_md_row(lines[i + 1])):
            header = [_normalize_header(c) for c in _split_md_row(line)]
            rows: List[Row] = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = _split_md_row(lines[j])
                cells += [""] * (len(header) - len(cells))
                rows.append(Row(dict(zip(header, cells[: len(header)])), file=str(path), line=j + 1))
                j += 1
            tables.append(Table(header, rows, file=str(path), header_line=i + 1))
            i = j
            continue
        i += 1
    return tables


def _csv_table(path: Path, text: str) -> Table:
    if text.startswith("﻿"):
        text = text[1:]
    reader = csv.reader(io.StringIO(text))
    try:
        header = [h.strip() for h in next(reader)]
    except StopIteration:
        return Table([], [], file=str(path))
    rows: List[Row] = []
    # csv.reader tracks physical lines: line_num after reading a record is its *last* line, so a
    # record starts on the line after the previous record ended (quoted fields may span lines).
    while True:
        start = reader.line_num + 1
        try:
            record = next(reader)
        except StopIteration:
            break
        except csv.Error as exc:
            raise ValueError(f"{path}:{reader.line_num}: malformed CSV: {exc}") from exc
        if not any(cell.strip() for cell in record):
            continue
        record += [""] * (len(header) - len(record))
        data = {h: (record[k] if k < len(record) else "") for k, h in enumerate(header)}
        row = Row(data, file=str(path), line=start)
        row.end_line = reader.line_num
        rows.append(row)
    return Table(header, rows, file=str(path))


def read_tables(path: PathLike) -> List[Table]:
    """Every table in a file: one for ``.csv``/``.tsv``; each pipe table for ``.md``."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return [_csv_table(p, text)]
    if suffix == ".tsv":
        rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
        if not rows:
            return [Table([], [], file=str(p))]
        header = [h.strip() for h in rows[0]]
        body = [Row(dict(zip(header, r)), file=str(p), line=n + 2) for n, r in enumerate(rows[1:]) if any(r)]
        return [Table(header, body, file=str(p))]
    if suffix in (".md", ".markdown"):
        return _markdown_tables(p, text)
    raise ValueError(f"{p}: unsupported file type (use .csv, .tsv or .md)")


def read_table(path: PathLike) -> Table:
    """The first table holding an ``ID`` column (or the only table) in ``path``."""
    tables = read_tables(path)
    for table in tables:
        if "ID" in table.columns:
            return table
    if tables:
        return tables[0]
    return Table([], [], file=str(path))


def requirement_files(workspace: PathLike) -> List[Path]:
    """Default files holding requirement rows: ``requirements.csv`` and ``stories/*.md``."""
    ws = Path(workspace)
    files: List[Path] = []
    main = ws / "requirements.csv"
    if main.is_file():
        files.append(main)
    stories = ws / "stories"
    if stories.is_dir():
        files.extend(sorted(stories.glob("*.md")))
    return files


def read_requirements(paths: Iterable[PathLike], schema: Optional[Dict] = None) -> List[Row]:
    """All rows whose ``ID`` matches the requirement ID pattern, across ``paths``."""
    pattern = id_regex("requirement", schema)
    out: List[Row] = []
    for path in paths:
        for table in read_tables(path):
            if "ID" not in table.columns:
                continue
            for row in table.rows:
                if pattern.match(row.get_str("ID")):
                    out.append(row)
    return out


# --------------------------------------------------------------------------- writing


def write_csv(path: PathLike, rows: Iterable[Dict[str, str]], columns: Sequence[str]) -> None:
    """Write rows with a fixed column order, LF endings, minimal quoting, UTF-8."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(list(columns))
    for row in rows:
        writer.writerow(["" if row.get(c) is None else str(row.get(c)) for c in columns])
    p.write_text(buf.getvalue(), encoding="utf-8")


def ordered_columns(existing: Sequence[str], schema: Optional[Dict] = None) -> List[str]:
    """Schema column order first, then optional columns present, then any others present."""
    attrs = (schema or DEFAULT_SCHEMA)["attributes"]
    base = list(attrs.get("columns", []))
    optional = [c for c in attrs.get("optional", []) if c in existing and c not in base]
    rest = [c for c in existing if c not in base and c not in optional]
    return base + optional + rest


if __name__ == "__main__":  # pragma: no cover - helper module, not a CLI
    import sys

    sys.stderr.write("reqio.py is a helper module used by the re-skills scripts.\n")
    sys.exit(2)
