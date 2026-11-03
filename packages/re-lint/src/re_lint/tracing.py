#!/usr/bin/env python3
"""Build the trace matrix, report coverage gaps and follow change impact.

Usage::

    re-lint trace build  [--repo DIR] [--out DIR] [--since REV] [--code-glob G ...]
                         [--test-glob G ...] [--format text|json]
    re-lint trace impact ID [ID ...] [--trace FILE] [--depth 1|2|3] [--format text|json|md]
    re-lint trace gaps   [--trace FILE] [--format text|json|github] [--fail-on-gaps]
                         [--only KIND ...] [--status S ...]

``build`` reads requirement IDs from the workspace registers (``requirements.csv``,
``stories/*.md``) and finds trace links in:

* the ``Source`` column and ``sources.csv`` (backward links, ``derives-from``),
* the ``Links`` column (decision IDs and repo paths),
* ``decisions/*.md`` and the ADR folders in ``schema.trace.adr_dirs`` (``decided-by``),
* code files matching ``schema.trace.code_globs`` (``implemented-by``),
* test files matching ``schema.trace.test_globs`` (``verified-by``), including test-name
  forms ``test_r_012_*``, ``test_R012``, ``TestR012_*`` and ``r012``/``R012``/``r_012``,
* ``git log`` messages when ``schema.trace.scan_git_log`` is true (``mentioned-in``).

It writes three files to ``--out`` (default ``<workspace>/trace``):

``trace.csv``
    ``From,FromType,To,ToType,Relation,Evidence``. Every row starts at a requirement
    (``FromType=requirement``; ``From`` keeps an acceptance-criterion suffix such as
    ``R-012.AC2`` when the citation names one). ``ToType`` is ``source``, ``decision``,
    ``code``, ``test`` or ``commit``; ``Relation`` is ``derives-from``, ``decided-by``,
    ``implemented-by``, ``verified-by`` or ``mentioned-in``. ``To`` is an ID, a repo-relative
    path, ``path::test name`` for a test whose name is found, or a short commit hash.
    ``Evidence`` is ``file:line`` or the commit short hash. One row per distinct
    (``From``, ``To``, ``Relation``), sorted by those columns; no timestamps.
``trace.md``
    Header table, coverage summary, Mermaid ``graph LR`` (truncated with a note when large),
    one gap table per gap kind, and a requirement-by-artifact matrix.
``gaps.json``
    ``{"summary": {...}, "gaps": [{"kind", "id", "file", "line", "detail", ...}]}``.

Gap kinds (``--only``):

=================================  =============================================================
``requirement-without-test``       status agreed/implemented/verified, ``Verification`` empty or
                                   ``test``, no ``verified-by`` link
``requirement-without-source``     ``Source`` empty or ``TBD``, or citing an ``S-``/``SH-`` ID
                                   missing from ``sources.csv``/``stakeholders.md`` (when present)
``agreed-without-implementation``  status agreed/implemented/verified, no code reference and no
                                   commit citing the ID
``test-cites-unknown-id``          a test cites an ID that is not in the register
``test-cites-retired-id``          a test cites a withdrawn or rejected ID
``code-cites-unknown-id``          the same for code files
``code-cites-retired-id``          the same for code files
=================================  =============================================================

Commit messages are history and cannot be fixed, so they never produce a gap. ``--status``
replaces the statuses that requirement-level gaps apply to.

Test-name forms (``r_012``, ``r012``, ``R012``, ``_ac2`` suffixes) count inside identifiers that
start with ``test`` (``test_r_012_export``, ``TestR012_Export``). Elsewhere in a test file only the
marker spelling ``R012`` counts (``@pytest.mark.R012``), and only for IDs in the register, so
fixture strings such as ``"r080"`` never become citations. Set
``"trace": {"test_name_forms": false}`` in ``schema.json`` to accept only ``R-012``.

``impact`` follows ``trace.csv`` and the ``Links`` column breadth-first: requirement ->
artifact (1 hop) -> other requirements sharing that decision, code file or test (2 hops).
Sources and commits are reported but not followed.

Exit codes: 0 ok, 1 gaps found with ``--fail-on-gaps``, 2 usage, schema or parse error.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

if not __package__:  # run as a plain script: make the sibling reqio.py importable
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # inside the package
    from . import reqio
except ImportError:  # vendored next to reqio.py in a skill's scripts/
    import reqio

TRACE_COLUMNS = ["From", "FromType", "To", "ToType", "Relation", "Evidence"]
NODE_TYPES = ("source", "requirement", "decision", "code", "test", "commit")
RELATIONS = ("derives-from", "decided-by", "implemented-by", "verified-by", "mentioned-in")
RELATION_FOR_TYPE = {
    "source": "derives-from",
    "decision": "decided-by",
    "code": "implemented-by",
    "test": "verified-by",
    "commit": "mentioned-in",
}
RETIRED = {"withdrawn", "rejected"}
COMMITTED_STATUSES = {"agreed", "implemented", "verified"}
NON_TEST_VERIFICATION = {"inspection", "analysis", "demonstration"}
GAP_KINDS = (
    "requirement-without-test",
    "requirement-without-source",
    "agreed-without-implementation",
    "test-cites-unknown-id",
    "test-cites-retired-id",
    "code-cites-unknown-id",
    "code-cites-retired-id",
)
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", "vendor", ".venv", "venv",
    "virtualenv", "__pycache__", ".tox", ".nox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "build", "dist", "target", ".gradle", ".next", ".nuxt", "coverage", "htmlcov", ".terraform",
    ".cache", "site-packages", ".eggs", ".idea", ".vscode",
}
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".pdf", ".zip", ".gz", ".tgz",
    ".bz2", ".xz", ".7z", ".jar", ".war", ".class", ".so", ".dylib", ".dll", ".exe", ".o", ".a",
    ".whl", ".pyc", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".mp3", ".mp4", ".mov", ".avi",
    ".sqlite", ".db", ".bin", ".xlsx", ".docx", ".pptx", ".reqifz",
}
DEFAULT_MAX_BYTES = 1_000_000
DEFAULT_MAX_GRAPH_EDGES = 80
DEFAULT_MAX_COMMITS = 10_000
EMPTY_VALUES = {"", "tbd", "tbc", "?", "??", "n/a", "-"}

# Test declarations, used to name the test a citation belongs to (``path::name``).
_TEST_DECLS = (
    re.compile(r"^\s*(?:async\s+)?def\s+(test\w*)\s*\("),  # Python
    re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?(Test\w*)\s*\("),  # Go
    re.compile(r"""\b(?:it|test|describe|context|specify|scenario)(?:\.\w+)?\s*\(\s*(?:'([^']+)'|"([^"]+)"|`([^`]+)`)"""),
    re.compile(r"""@DisplayName\(\s*"([^"]+)"\s*\)"""),  # JUnit 5
    re.compile(r"^\s*(?:(?:public|private|protected|internal|static|async|override)\s+)*(?:void|Task|fun)\s+`?([^`(\s]+(?: [^`(]+)?)`?\s*\("),
)


class UsageError(Exception):
    """A problem the user can fix (exit 2)."""


class _Parser(argparse.ArgumentParser):
    """Keeps subcommand usage in step with ``prog``, even when a caller sets it after
    ``build_parser()`` (``re-lint`` does: ``parser.prog = "re-lint <command>"``)."""

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "prog":
            for action in getattr(self, "_actions", []):
                if isinstance(action, argparse._SubParsersAction):
                    action._prog_prefix = value
                    for choice, sub in action.choices.items():
                        sub.prog = f"{value} {choice}"


# --------------------------------------------------------------------------- shared helpers


def _workspace(args: argparse.Namespace) -> Tuple[Path, Dict]:
    schema_path = getattr(args, "schema", None)
    if schema_path and not Path(schema_path).is_file():
        raise UsageError(f"schema file not found: {schema_path}")
    if getattr(args, "workspace", None):
        ws = Path(args.workspace).resolve()
    else:
        start = getattr(args, "repo", None) or "."
        base = reqio.load_schema(schema_path) if schema_path else None
        ws = reqio.find_workspace(start, base).resolve()
    schema = reqio.load_schema(schema_path, workspace=ws)
    return ws, schema


def _id_key(value: str) -> Tuple:
    match = re.match(r"^(.*?)(\d+)(.*)$", value or "")
    if not match:
        return (value or "", -1, "")
    return (match.group(1), int(match.group(2)), match.group(3))


def _load_requirements(ws: Path, schema: Dict) -> "OrderedDict[str, reqio.Row]":
    """Requirement rows by ID; the first occurrence wins (``requirements.csv`` before stories)."""
    out: "OrderedDict[str, reqio.Row]" = OrderedDict()
    try:
        rows = reqio.read_requirements(reqio.requirement_files(ws), schema)
    except UnicodeDecodeError as exc:
        raise UsageError(f"cannot read the requirement registers as UTF-8: {exc}") from exc
    for row in rows:
        out.setdefault(row.get_str("ID"), row)
    return out


def _status(row: Optional[reqio.Row]) -> str:
    return row.get_str("Status").lower() if row is not None else ""


def _md_cell(value: object) -> str:
    text = " ".join(str(value if value is not None else "").split())
    return text.replace("|", "\\|")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _rel(path: "os.PathLike[str] | str", root: Path) -> str:
    try:
        rel = os.path.relpath(os.path.abspath(path), str(root))
    except ValueError:  # different drive on Windows
        rel = os.path.abspath(path)
    return Path(rel).as_posix()


def _split_list(values: Optional[Sequence[str]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        out.extend(v for v in re.split(r"[,\s]+", value) if v)
    return out


def _git(repo: Path, *argv: str, timeout: int = 60) -> Optional[str]:
    """Run git in ``repo``; ``None`` when git is missing or the command fails."""
    if shutil.which("git") is None:
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *argv],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", errors="replace")


# --------------------------------------------------------------------------- ID matching


class IdMatcher:
    """Find requirement references in text and normalize them to the canonical ``R-012`` form."""

    def __init__(self, schema: Dict, known: Iterable[str] = ()):
        spec = (schema.get("ids") or {}).get("requirement") or {"prefix": "R-", "digits": 3}
        self.prefix = str(spec.get("prefix", "R-"))
        self.digits = int(spec.get("digits", 3))
        self.schema = schema
        self.known = set(known)
        p = re.escape(self.prefix)
        d = self.digits
        self.canonical = re.compile(
            rf"(?<![A-Za-z0-9_-]){p}(\d{{{d},}})(?:\.AC(\d+))?(?![A-Za-z0-9])"
        )
        letters = re.sub(r"[^A-Za-z]", "", self.prefix)
        self.letters = letters
        enabled = (schema.get("trace") or {}).get("test_name_forms", True)
        self.snake: Optional["re.Pattern[str]"] = None
        self.camel: Optional["re.Pattern[str]"] = None
        if letters and enabled:
            cls = "".join(f"[{c.upper()}{c.lower()}]" for c in letters)
            num = rf"(\d{{{d},{d + 2}}})"
            # r_012 / R012 / r012, optionally with an acceptance criterion: r_012_ac2
            self.snake = re.compile(
                rf"(?<![A-Za-z0-9]){cls}_?{num}(?:_?[Aa][Cc](\d+))?(?![0-9A-Za-z])"
            )
            # testR012Export / TestR012_Export (only inside identifiers starting with "test")
            self.camel = re.compile(rf"(?<=[a-z0-9_]){letters.upper()}{num}(?:AC(\d+))?(?![a-z0-9])")

    def normalize(self, number: str, ac: Optional[str]) -> str:
        base = f"{self.prefix}{int(number):0{self.digits}d}"
        return f"{base}.AC{int(ac)}" if ac else base

    @staticmethod
    def base(ref: str) -> str:
        return ref.split(".AC", 1)[0]

    def canonical_refs(self, line: str) -> List[str]:
        return [self.normalize(m.group(1), m.group(2)) for m in self.canonical.finditer(line)]

    def test_refs(self, line: str) -> List[str]:
        """Canonical references plus test-name forms (trusted inside ``test...`` identifiers)."""
        refs = self.canonical_refs(line)
        taken: List[Tuple[int, int]] = []
        for pattern, needs_test_ident in ((self.snake, False), (self.camel, True)):
            if pattern is None:
                continue
            for match in pattern.finditer(line):
                if any(a <= match.start() < b for a, b in taken):
                    continue
                start = match.start()
                while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
                    start -= 1
                in_test_ident = line[start:].lower().startswith("test")
                if needs_test_ident and not in_test_ident:
                    continue
                ref = self.normalize(match.group(1), match.group(2))
                if not in_test_ident:
                    # Weak form outside a test name: only the marker/tag spelling R041 (prefix
                    # letters upper case, no underscore) and only for IDs that exist.
                    token = line[match.start():match.end()]
                    if self.base(ref) not in self.known or not token[: len(self.letters)].isupper() \
                            or "_" in token:
                        continue
                taken.append((match.start(), match.end()))
                refs.append(ref)
        return refs

    def ids_of_kind(self, kind: str, text: str) -> List[str]:
        try:
            pattern = reqio.id_prefix_regex(kind, self.schema)
        except KeyError:
            return []
        spec = (self.schema.get("ids") or {}).get(kind) or {}
        prefix = str(spec.get("prefix", ""))
        return [prefix + m.group(1) for m in pattern.finditer(text or "")]


def _test_name(lines: Sequence[str], index: int) -> Optional[str]:
    """Name of the test a citation on ``lines[index]`` belongs to, if it can be found nearby.

    Looks at the line itself, the line above (a docstring under ``def test_...``) and up to three
    lines below (a comment or annotation above the declaration).
    """
    def decl(line: str) -> Optional[str]:
        for pattern in _TEST_DECLS:
            match = pattern.search(line)
            if match:
                name = next((g for g in match.groups() if g), "")
                name = " ".join(name.split())
                return name or None
        return None

    found = decl(lines[index])
    if found:
        return found
    if index > 0:
        above = decl(lines[index - 1])
        if above and re.match(r"^\s*(?:async\s+)?def\s|^\s*func\s", lines[index - 1]):
            return above
    for offset in range(1, 4):
        if index + offset >= len(lines):
            break
        below = decl(lines[index + offset])
        if below:
            return below
        if lines[index + offset].strip() and not re.match(r"^\s*(?:@|//|#|/\*|\*|\[)", lines[index + offset]):
            break  # ordinary code in between: the citation is not a header of the next test
    return None


# --------------------------------------------------------------------------- globbing and files


def _glob_segment(segment: str) -> str:
    out: List[str] = []
    i = 0
    while i < len(segment):
        ch = segment[i]
        if ch == "*":
            out.append("[^/]*")
        elif ch == "?":
            out.append("[^/]")
        elif ch == "[":
            end = segment.find("]", i + 1)
            if end == -1:
                out.append(re.escape(ch))
            else:
                body = segment[i + 1:end].replace("\\", "\\\\")
                if body.startswith("!"):
                    body = "^" + body[1:]
                out.append(f"[{body}]")
                i = end
        else:
            out.append(re.escape(ch))
        i += 1
    return "".join(out)


def glob_to_regex(pattern: str) -> "re.Pattern[str]":
    """Translate a repo-relative glob (``**`` spans folders) to a regex on POSIX paths.

    A pattern without ``/`` matches the file name at any depth, like ``.gitignore``.
    """
    pat = pattern.strip().replace("\\", "/")
    while pat.startswith("./"):
        pat = pat[2:]
    pat = pat.lstrip("/")
    if pat.endswith("/"):
        pat += "**"
    if "/" not in pat and pat != "**":
        pat = "**/" + pat
    parts = pat.split("/")
    out: List[str] = []
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        if part == "**":
            out.append(".*" if last else "(?:[^/]+/)*")
        else:
            out.append(_glob_segment(part) + ("" if last else "/"))
    return re.compile("^" + "".join(out) + "$")


def _matches(path: str, patterns: Sequence["re.Pattern[str]"]) -> bool:
    return any(p.match(path) for p in patterns)


def _skipped_dir(parts: Sequence[str]) -> bool:
    return any(p in SKIP_DIRS or p.endswith(".egg-info") for p in parts)


def list_repo_files(repo: Path) -> List[str]:
    """Repo-relative POSIX paths of candidate files (``git ls-files`` when available)."""
    files: Optional[List[str]] = None
    listing = _git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if listing is not None:
        files = [f for f in listing.split("\0") if f]
    if files is None:
        files = []
        for dirpath, dirnames, filenames in os.walk(repo):
            keep = []
            for name in dirnames:
                full = os.path.join(dirpath, name)
                if name in SKIP_DIRS or name.endswith(".egg-info") or os.path.islink(full):
                    continue
                if os.path.isfile(os.path.join(full, "pyvenv.cfg")):
                    continue  # a virtualenv with an unusual name
                keep.append(name)
            dirnames[:] = sorted(keep)
            for name in filenames:
                files.append(_rel(os.path.join(dirpath, name), repo))
    return [rel for rel in sorted(set(files)) if not _skipped_dir(rel.split("/")[:-1])]


def _read_lines(path: Path, max_bytes: int) -> Optional[List[str]]:
    """Text lines of ``path``; ``None`` for binary, oversized, unreadable files or symlinks."""
    if path.suffix.lower() in BINARY_SUFFIXES or path.is_symlink():
        return None
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace").splitlines()


# --------------------------------------------------------------------------- build


class TraceBuilder:
    """Collects trace edges from registers, files and git history."""

    def __init__(self, repo: Path, ws: Path, schema: Dict, reqs: "OrderedDict[str, reqio.Row]",
                 code_globs: Sequence[str], test_globs: Sequence[str], max_bytes: int):
        self.repo = repo
        self.ws = ws
        self.schema = schema
        self.reqs = reqs
        self.matcher = IdMatcher(schema, reqs.keys())
        self.code_patterns = [glob_to_regex(g) for g in code_globs]
        self.test_patterns = [glob_to_regex(g) for g in test_globs]
        self.max_bytes = max_bytes
        self.edges: "OrderedDict[Tuple[str, str, str], Dict[str, str]]" = OrderedDict()
        self.commits: Dict[str, str] = {}
        self.stats = {"files_scanned": 0, "files_skipped": 0, "commits_scanned": 0, "git_log": False}

    def add(self, ref: str, to: str, to_type: str, evidence: str) -> None:
        relation = RELATION_FOR_TYPE[to_type]
        key = (ref, to, relation)
        if key not in self.edges:
            self.edges[key] = {
                "From": ref, "FromType": "requirement", "To": to, "ToType": to_type,
                "Relation": relation, "Evidence": evidence,
            }

    def rel(self, path: "os.PathLike[str] | str") -> str:
        return _rel(path, self.repo)

    # -- registers

    def scan_registers(self) -> None:
        for rid, row in self.reqs.items():
            evidence = f"{self.rel(row.file)}:{row.line}"
            source = row.get_str("Source")
            ids = _source_ids(self.matcher, source)
            if ids:
                for sid in ids:
                    self.add(rid, sid, "source", evidence)
            elif source.lower() not in EMPTY_VALUES:
                self.add(rid, " ".join(source.split()), "source", evidence)
            for token in re.split(r"[\s,;]+", row.get_str("Links")):
                self.link_token(rid, token.strip(), evidence)
        sources = self.ws / "sources.csv"
        if sources.is_file():
            try:
                table = reqio.read_table(sources)
            except (OSError, UnicodeDecodeError, ValueError):
                return
            pattern = reqio.id_regex("source", self.schema)
            for row in table:
                sid = row.get_str("ID")
                if not pattern.match(sid):
                    continue
                evidence = f"{self.rel(row.file)}:{row.line}"
                for col, value in row.items():
                    if col != "ID":
                        for ref in self.matcher.canonical_refs(str(value or "")):
                            self.add(ref, sid, "source", evidence)

    def link_token(self, rid: str, token: str, evidence: str) -> None:
        if not token or "://" in token:
            return
        decisions = self.matcher.ids_of_kind("decision", token)
        if decisions and decisions[0] == token:
            self.add(rid, token, "decision", evidence)
            return
        if "/" not in token and "." not in token:
            return  # an ID of another kind (CR-, CF-, R-): impact reads it from the register
        path = token.split("#", 1)[0]
        while path.startswith("./"):
            path = path[2:]
        kind = self.classify(path)
        if kind:
            self.add(rid, path, kind, evidence)

    def classify(self, rel: str) -> Optional[str]:
        if self.is_decision_path(rel):
            return "decision"
        if _matches(rel, self.test_patterns):
            return "test"
        if _matches(rel, self.code_patterns):
            return "code"
        return None

    def decision_dirs(self) -> List[str]:
        dirs = [self.rel(self.ws / "decisions")]
        for d in (self.schema.get("trace") or {}).get("adr_dirs") or []:
            dirs.append(str(d).strip("/").replace("\\", "/"))
        return [d for d in dirs if d]

    def is_decision_path(self, rel: str) -> bool:
        return rel.lower().endswith((".md", ".markdown", ".adoc", ".rst", ".txt")) and any(
            rel.startswith(d + "/") for d in self.decision_dirs()
        )

    # -- files

    def scan_files(self) -> None:
        ws_rel = self.rel(self.ws)
        for rel in list_repo_files(self.repo):
            if self.is_decision_path(rel):
                kind: Optional[str] = "decision"
            elif ws_rel not in ("", ".") and (rel == ws_rel or rel.startswith(ws_rel + "/")):
                continue  # registers and generated work products are not code
            elif rel.startswith("openspec/"):
                continue  # hand-off specs carry IDs as anchors, not as trace evidence
            else:
                kind = self.classify(rel)
            if kind is None:
                continue
            lines = _read_lines(self.repo / rel, self.max_bytes)
            if lines is None:
                self.stats["files_skipped"] += 1
                continue
            self.stats["files_scanned"] += 1
            target = rel
            if kind == "decision":
                name_ids = self.matcher.ids_of_kind("decision", Path(rel).name)
                if name_ids and Path(rel).name.startswith(name_ids[0]):
                    target = name_ids[0]
            for index, line in enumerate(lines):
                refs = self.matcher.test_refs(line) if kind == "test" else self.matcher.canonical_refs(line)
                if not refs:
                    continue
                to = target
                if kind == "test":
                    name = _test_name(lines, index)
                    to = f"{rel}::{name}" if name else rel
                for ref in refs:
                    self.add(ref, to, kind, f"{rel}:{index + 1}")

    # -- git log

    def scan_git_log(self, since: Optional[str], max_commits: int) -> None:
        argv = ["log", "--no-color", f"--max-count={max_commits}", "--format=%h%x1f%s%x1f%b%x1e"]
        if since:
            if re.match(r"^\d{4}-\d{2}-\d{2}", since):
                argv.append(f"--since={since}")
            else:
                argv.append(f"{since}..HEAD")
        output = _git(self.repo, *argv)
        if output is None:
            if since and _git(self.repo, "rev-parse", "--git-dir") is not None:
                raise UsageError(f"git log failed for --since {since!r} (unknown revision?)")
            return
        self.stats["git_log"] = True
        for record in output.split("\x1e"):
            record = record.strip("\n")
            if not record.strip():
                continue
            parts = record.split("\x1f")
            short = parts[0].strip()
            subject = parts[1] if len(parts) > 1 else ""
            body = parts[2] if len(parts) > 2 else ""
            self.stats["commits_scanned"] += 1
            refs = self.matcher.canonical_refs(subject + "\n" + body)
            if refs:
                self.commits[short] = subject.strip()
            for ref in refs:
                self.add(ref, short, "commit", short)

    def sorted_edges(self) -> List[Dict[str, str]]:
        return sorted(self.edges.values(), key=lambda e: (_id_key(e["From"]), e["To"], e["Relation"]))


def _source_ids(matcher: IdMatcher, text: str) -> List[str]:
    ids: List[str] = []
    for kind in ("source", "stakeholder", "interview"):
        ids.extend(matcher.ids_of_kind(kind, text))
    return ids


def _registered_sources(ws: Path, schema: Dict) -> Dict[str, Set[str]]:
    """Registered IDs per kind, only for kinds whose register file exists."""
    out: Dict[str, Set[str]] = {}
    for kind, name in (("source", "sources.csv"), ("stakeholder", "stakeholders.md")):
        path = ws / name
        if not path.is_file():
            continue
        try:
            pattern = reqio.id_regex(kind, schema)
            ids: Set[str] = set()
            for table in reqio.read_tables(path):
                for row in table:
                    if pattern.match(row.get_str("ID")):
                        ids.add(row.get_str("ID"))
            out[kind] = ids
        except (OSError, UnicodeDecodeError, ValueError, KeyError):
            continue
    return out


# --------------------------------------------------------------------------- reading trace.csv


def _normalize_edge(edge: Dict[str, str]) -> Dict[str, str]:
    """Accept hand-built rows that point source -> requirement or use ``adr``/``change`` types."""
    e = dict(edge)
    from_type, to_type = e["FromType"].lower(), e["ToType"].lower()
    if from_type != "requirement" and to_type == "requirement":
        e["From"], e["To"] = e["To"], e["From"]
        from_type, to_type = "requirement", from_type
        e["Relation"] = {"source-of": "derives-from"}.get(e["Relation"].lower(), e["Relation"])
    to_type = {"adr": "decision", "change": "decision", "stakeholder": "source",
               "interview": "source"}.get(to_type, to_type)
    e["FromType"], e["ToType"] = from_type, to_type
    if to_type == "commit" and e["To"].startswith("git:"):
        e["To"] = e["To"][4:]
    return e


def read_trace(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        raise UsageError(f"{path} not found; run `re-lint trace build` first")
    try:
        table = reqio.read_table(path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise UsageError(f"cannot read {path}: {exc}") from exc
    missing = [c for c in TRACE_COLUMNS if c not in table.columns]
    if missing:
        raise UsageError(f"{path}: missing columns {', '.join(missing)} (expected {','.join(TRACE_COLUMNS)})")
    return [_normalize_edge({c: row.get_str(c) for c in TRACE_COLUMNS}) for row in table.rows]


def _trace_path(args: argparse.Namespace, ws: Path) -> Path:
    return Path(args.trace) if getattr(args, "trace", None) else ws / "trace" / "trace.csv"


# --------------------------------------------------------------------------- gaps


def _split_evidence(evidence: str) -> Tuple[str, int]:
    match = re.match(r"^(.*):(\d+)$", evidence or "")
    if match:
        return match.group(1), int(match.group(2))
    return evidence or "", 0


def compute_gaps(edges: Sequence[Dict[str, str]], reqs: "OrderedDict[str, reqio.Row]", repo: Path,
                 schema: Dict, registered: Optional[Dict[str, Set[str]]] = None,
                 statuses: Optional[Set[str]] = None) -> Dict:
    """``{"summary": counts, "gaps": [entry, ...]}`` from trace edges and the current register."""
    matcher = IdMatcher(schema, reqs.keys())
    registered = registered or {}
    committed = statuses or COMMITTED_STATUSES
    types_by_req: Dict[str, Set[str]] = defaultdict(set)
    for edge in edges:
        types_by_req[IdMatcher.base(edge.get("From", ""))].add(edge.get("ToType", ""))
    gaps: List[Dict] = []
    counts = OrderedDict(
        (k, 0) for k in ("requirements", "in_scope", "retired", "with_source", "with_decision",
                         "with_code_or_commit", "with_test")
    )
    counts["requirements"] = len(reqs)
    for rid, row in reqs.items():
        status = _status(row)
        if status in RETIRED:
            counts["retired"] += 1
            continue
        counts["in_scope"] += 1
        types = types_by_req.get(rid, set())
        for key, wanted in (("with_source", {"source"}), ("with_decision", {"decision"}),
                            ("with_code_or_commit", {"code", "commit"}), ("with_test", {"test"})):
            if types & wanted:
                counts[key] += 1
        file, line = _rel(row.file, repo), int(row.line or 0)

        def gap(kind: str, detail: str) -> None:
            gaps.append({"kind": kind, "id": rid, "file": file, "line": line, "detail": detail,
                         "status": status, "text": row.get_str("Title") or row.get_str("Text")})

        verification = row.get_str("Verification").lower()
        if status in committed and "test" not in types and verification not in NON_TEST_VERIFICATION:
            gap("requirement-without-test",
                f"status {status}, verification {verification or 'empty'}, no verified-by link")
        source = row.get_str("Source")
        if statuses is None or status in statuses:
            if source.lower() in EMPTY_VALUES and "source" not in types:
                gap("requirement-without-source", f"Source is {source or 'empty'}")
            else:
                unregistered = []
                for kind in ("source", "stakeholder"):
                    if kind in registered:
                        unregistered += [s for s in matcher.ids_of_kind(kind, source) if s not in registered[kind]]
                if unregistered:
                    gap("requirement-without-source", f"cites {', '.join(unregistered)}, not registered")
        if status in committed and not types & {"code", "commit"}:
            gap("agreed-without-implementation", f"status {status}, no code reference or commit citing it")
    seen: Set[Tuple[str, str]] = set()
    for edge in edges:
        kind = edge.get("ToType")
        if kind not in ("code", "test"):
            continue
        ref = edge.get("From", "")
        key = (ref, edge.get("Evidence", ""))
        if key in seen:
            continue
        seen.add(key)
        base = IdMatcher.base(ref)
        file, line = _split_evidence(edge.get("Evidence", ""))
        entry = {"id": ref, "file": file, "line": line, "target": edge.get("To", "")}
        if base not in reqs:
            gaps.append({"kind": f"{kind}-cites-unknown-id", **entry,
                         "detail": f"{ref} is not in the requirement register"})
        elif _status(reqs[base]) in RETIRED:
            gaps.append({"kind": f"{kind}-cites-retired-id", **entry, "status": _status(reqs[base]),
                         "detail": f"{base} is {_status(reqs[base])}"})
    order = {k: i for i, k in enumerate(GAP_KINDS)}
    gaps.sort(key=lambda g: (order.get(g["kind"], 99), _id_key(g["id"]), g["file"], g["line"]))
    by_kind = {k: sum(1 for g in gaps if g["kind"] == k) for k in GAP_KINDS}
    counts["without_tests"] = by_kind["requirement-without-test"]
    counts["without_source"] = by_kind["requirement-without-source"]
    counts["tests_citing_unknown_or_retired"] = by_kind["test-cites-unknown-id"] + by_kind["test-cites-retired-id"]
    counts["code_citing_unknown_or_retired"] = by_kind["code-cites-unknown-id"] + by_kind["code-cites-retired-id"]
    counts["agreed_without_implementation"] = by_kind["agreed-without-implementation"]
    counts["links"] = len(edges)
    return {"summary": dict(counts), "gaps": gaps}


# --------------------------------------------------------------------------- trace.md


def _render_mermaid(edges: Sequence[Dict[str, str]], reqs: Dict, gap_ids: Set[str],
                    max_edges: int) -> Tuple[List[str], int, int]:
    """Mermaid lines, links drawn and links available (code/tests grouped per file, no commits)."""
    pairs: "OrderedDict[Tuple[str, str, str], None]" = OrderedDict()
    for edge in edges:
        if edge["ToType"] == "commit":
            continue
        to = edge["To"].split("::", 1)[0] if edge["ToType"] == "test" else edge["To"]
        pairs.setdefault((IdMatcher.base(edge["From"]), to, edge["ToType"]), None)
    all_pairs = list(pairs)
    shown = all_pairs[:max_edges]
    ids: Dict[Tuple[str, str], str] = {}
    used: Set[str] = set()
    lines = ["graph LR"]
    shapes = {"requirement": ('["', '"]'), "source": ('(["', '"])'), "decision": ('{{"', '"}}'),
              "code": ('[["', '"]]'), "test": ('>"', '"]')}
    gap_nodes: List[str] = []
    retired_nodes: List[str] = []

    def node(name: str, kind: str) -> str:
        key = (kind, name)
        if key in ids:
            return ids[key]
        base = re.sub(r"[^A-Za-z0-9]", "", name) or "n"
        if base[0].isdigit():
            base = "n" + base
        candidate, n = base, 2
        while candidate in used:
            candidate, n = f"{base}_{n}", n + 1
        used.add(candidate)
        ids[key] = candidate
        left, right = shapes.get(kind, ('["', '"]'))
        lines.append(f"  {candidate}{left}{name.replace(chr(34), '#quot;')}{right}")
        if kind == "requirement":
            if name in gap_ids or name not in reqs:
                gap_nodes.append(candidate)
            elif _status(reqs[name]) in RETIRED:
                retired_nodes.append(candidate)
        return candidate

    for rid, to, to_type in shown:
        a = node(rid, "requirement")
        b = node(to, to_type)
        lines.append(f"  {b} --> {a}" if to_type == "source" else f"  {a} --> {b}")
    lines.append("  classDef gap stroke:#d33,stroke-width:3px")
    lines.append("  classDef retired stroke-dasharray: 5 5,color:#777")
    if gap_nodes:
        lines.append(f"  class {','.join(gap_nodes)} gap")
    if retired_nodes:
        lines.append(f"  class {','.join(retired_nodes)} retired")
    return lines, len(shown), len(all_pairs)


def _cell_list(values: Sequence[str], limit: int = 5) -> str:
    unique = list(OrderedDict.fromkeys(values))
    shown = ", ".join(f"`{_md_cell(v)}`" for v in unique[:limit])
    if len(unique) > limit:
        shown += f" +{len(unique) - limit} more"
    return shown


def render_trace_md(edges: Sequence[Dict[str, str]], reqs: Dict, report: Dict, commits: Dict[str, str],
                    meta: Dict[str, str], max_edges: int) -> str:
    s = report["summary"]
    gaps = report["gaps"]
    out = [
        "# Trace matrix",
        "",
        "| Field | Value |",
        "| --- | --- |",
    ]
    for field in ("Generated", "Commit", "Command", "Requirements read", "Code globs", "Test globs"):
        out.append(f"| {field} | {_md_cell(meta.get(field, ''))} |")
    out += [
        "",
        "Generated by `re-lint trace build`; rerun it instead of editing this file. "
        "Links: `trace.csv`; machine-readable gaps: `gaps.json`.",
        "",
        "## Coverage summary",
        "",
        "| Measure | Count |",
        "| --- | --- |",
        f"| Requirements in scope (not withdrawn or rejected) | {s['in_scope']} |",
        f"| ... with a source | {s['with_source']} |",
        f"| ... with a decision or ADR | {s['with_decision']} |",
        f"| ... with code or a commit | {s['with_code_or_commit']} |",
        f"| ... with a test | {s['with_test']} |",
        f"| Gaps: requirements without tests | {s['without_tests']} |",
        f"| Gaps: requirements without a source | {s['without_source']} |",
        f"| Gaps: tests citing unknown or retired IDs | {s['tests_citing_unknown_or_retired']} |",
        f"| Gaps: code citing unknown or retired IDs | {s['code_citing_unknown_or_retired']} |",
        f"| Gaps: agreed or later requirements without an implementation reference | "
        f"{s['agreed_without_implementation']} |",
        f"| Requirements in the register (all statuses) | {s['requirements']} |",
        f"| Trace links | {s['links']} |",
        "",
        "## Graph",
        "",
    ]
    gap_ids = {g["id"] for g in gaps if g["kind"].startswith(("requirement-", "agreed-"))}
    graph, shown, total = _render_mermaid(edges, reqs, gap_ids, max_edges)
    out += ["```mermaid", *graph, "```", ""]
    if total == 0:
        out += ["No links to draw yet.", ""]
    elif shown < total:
        out += [f"> Graph truncated: {shown} of {total} links drawn (raise `--max-graph-edges`). "
                "The full list is in `trace.csv`.", ""]
    out += ["## Gaps", ""]

    def table(title: str, header: str, rows: List[str]) -> None:
        nonlocal out
        out += [f"### {title}", ""]
        if rows:
            out += [header, "| " + " | ".join("---" for _ in header.strip("|").split("|")) + " |", *rows]
        else:
            out.append("None.")
        out.append("")

    def of(*kinds: str) -> List[Dict]:
        return [g for g in gaps if g["kind"] in kinds]

    table("Requirements without tests", "| ID | Status | Verification | Text |",
          [f"| {g['id']} | {g['status']} | {_md_cell(reqs[g['id']].get_str('Verification') or '-')} | "
           f"{_md_cell(g['text'])} |" for g in of("requirement-without-test")])
    table("Requirements without a source", "| ID | Status | Source cell |",
          [f"| {g['id']} | {g['status']} | {_md_cell(reqs[g['id']].get_str('Source') or '(empty)')} |"
           for g in of("requirement-without-source")])
    problem = {"test-cites-unknown-id": "unknown ID", "test-cites-retired-id": "retired ID",
               "code-cites-unknown-id": "unknown ID", "code-cites-retired-id": "retired ID"}
    table("Tests citing unknown or retired IDs", "| Test | Cited ID | Problem | Evidence |",
          [f"| `{_md_cell(g['target'])}` | {g['id']} | {problem[g['kind']]}: {_md_cell(g['detail'])} | "
           f"`{g['file']}:{g['line']}` |" for g in of("test-cites-unknown-id", "test-cites-retired-id")])
    table("Code citing unknown or retired IDs", "| File or commit | Cited ID | Problem | Evidence |",
          [f"| `{_md_cell(g['target'])}` | {g['id']} | {problem[g['kind']]}: {_md_cell(g['detail'])} | "
           f"`{g['file']}:{g['line']}` |" for g in of("code-cites-unknown-id", "code-cites-retired-id")])
    table("Agreed or later requirements without an implementation reference", "| ID | Status | Text |",
          [f"| {g['id']} | {g['status']} | {_md_cell(g['text'])} |" for g in of("agreed-without-implementation")])

    grouped: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    for edge in edges:
        grouped[IdMatcher.base(edge["From"])][edge["ToType"]].append(edge["To"])
    out += ["## Matrix", "", "| Requirement | Status | Sources | Decisions | Code | Tests | Commits |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for rid in sorted(set(reqs) | set(grouped), key=_id_key):
        g = grouped.get(rid, {})
        status = _status(reqs.get(rid)) if rid in reqs else "not in register"
        out.append(
            f"| {rid} | {status} | {_cell_list(g.get('source', []))} | {_cell_list(g.get('decision', []))} | "
            f"{_cell_list(g.get('code', []))} | {_cell_list(g.get('test', []))} | {_cell_list(g.get('commit', []))} |"
        )
    out.append("")
    if commits:
        out += ["## Commits citing requirement IDs", "", "| Commit | Subject |", "| --- | --- |"]
        for short, subject in list(commits.items())[:50]:
            out.append(f"| `{short}` | {_md_cell(subject)} |")
        if len(commits) > 50:
            out.append(f"| ... | {len(commits) - 50} more in `trace.csv` |")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


# --------------------------------------------------------------------------- commands


def cmd_build(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    repo = Path(args.repo).resolve() if args.repo else reqio.find_repo_root(ws).resolve()
    if not repo.is_dir():
        raise UsageError(f"--repo {repo} is not a folder")
    reqs = _load_requirements(ws, schema)
    if not reqs:
        raise UsageError(
            f"no requirements found in {ws} (expected requirements.csv or stories/*.md with an ID column)"
        )
    trace_cfg = schema.get("trace") or {}
    code_globs = args.code_glob or list(trace_cfg.get("code_globs") or [])
    test_globs = args.test_glob or list(trace_cfg.get("test_globs") or [])
    builder = TraceBuilder(repo, ws, schema, reqs, code_globs, test_globs, args.max_bytes)
    builder.scan_registers()
    builder.scan_files()
    if trace_cfg.get("scan_git_log", True) and not args.no_git:
        builder.scan_git_log(args.since, args.max_commits)
    edges = builder.sorted_edges()
    report = compute_gaps(edges, reqs, repo, schema, _registered_sources(ws, schema))
    out_dir = Path(args.out).resolve() if args.out else ws / "trace"
    out_dir.mkdir(parents=True, exist_ok=True)
    head = _git(repo, "rev-parse", "--short", "HEAD")
    flags = []
    for flag, value in (("--since", args.since), ("--out", args.out)):
        if value:
            flags.append(f"{flag} {value}")
    flags += [f"--code-glob {g}" for g in args.code_glob or []] + [f"--test-glob {g}" for g in args.test_glob or []]
    meta = {
        "Generated": _dt.date.today().isoformat(),
        "Commit": head.strip() if head else "not a git repository",
        "Command": "`" + " ".join(["re-lint trace build", *flags]) + "`",
        "Requirements read": ", ".join(f"`{_rel(p, repo)}`" for p in reqio.requirement_files(ws)),
        "Code globs": ", ".join(f"`{g}`" for g in code_globs),
        "Test globs": ", ".join(f"`{g}`" for g in test_globs),
    }
    reqio.write_csv(out_dir / "trace.csv", edges, TRACE_COLUMNS)
    _write_text(out_dir / "trace.md", render_trace_md(edges, reqs, report, builder.commits, meta, args.max_graph_edges))
    _write_text(out_dir / "gaps.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    outputs = {name: _rel(out_dir / name, repo) for name in ("trace.csv", "trace.md", "gaps.json")}
    if args.format == "json":
        print(json.dumps({"summary": report["summary"], "scanned": builder.stats, "outputs": outputs}, indent=2))
    else:
        s = report["summary"]
        print(f"trace: {s['requirements']} requirements, {s['links']} links "
              f"({builder.stats['files_scanned']} files, {builder.stats['commits_scanned']} commits scanned)")
        print(f"  in scope {s['in_scope']}: with source {s['with_source']}, with code or commit "
              f"{s['with_code_or_commit']}, with test {s['with_test']}")
        print(f"  gaps: {len(report['gaps'])} (without tests {s['without_tests']}, without source "
              f"{s['without_source']}, citing unknown or retired IDs "
              f"{s['tests_citing_unknown_or_retired'] + s['code_citing_unknown_or_retired']}, "
              f"no implementation reference {s['agreed_without_implementation']})")
        print("wrote " + ", ".join(outputs.values()))
    return 0


def _impact(seeds: Sequence[str], edges: Sequence[Dict[str, str]], reqs: Dict, depth: int,
            id_pattern: "re.Pattern[str]") -> Dict:
    art_by_req: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    reqs_by_art: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
    links: Dict[str, Set[str]] = defaultdict(set)
    for edge in edges:
        rid = IdMatcher.base(edge["From"])
        if edge["ToType"] == "requirement":  # hand-built linked-to rows
            other = IdMatcher.base(edge["To"])
            links[rid].add(other)
            links[other].add(rid)
            continue
        art = (edge["ToType"], edge["To"])
        art_by_req[rid].append((edge["ToType"], edge["To"], edge["Evidence"]))
        reqs_by_art[art].add(rid)
    for rid, row in reqs.items():
        for token in re.split(r"[\s,;]+", row.get_str("Links")):
            token = token.strip()
            if token and id_pattern.match(token) and token != rid:
                links[rid].add(token)
                links[token].add(rid)
    found_reqs: "OrderedDict[str, Dict]" = OrderedDict((s, {"hop": 0, "via": "seed"}) for s in seeds)
    found_arts: "OrderedDict[Tuple[str, str], Dict]" = OrderedDict()
    frontier: List[Tuple[str, str]] = [("requirement", s) for s in seeds]
    for hop in range(1, depth + 1):
        nxt: List[Tuple[str, str]] = []
        for kind, name in frontier:
            if kind == "requirement":
                for linked in sorted(links.get(name, ()), key=_id_key):
                    if linked not in found_reqs:
                        found_reqs[linked] = {"hop": hop, "via": f"Links of {name}"}
                        nxt.append(("requirement", linked))
                for to_type, to, ev in art_by_req.get(name, []):
                    key = (to_type, to)
                    if key not in found_arts:
                        found_arts[key] = {"hop": hop, "via": name, "evidence": ev}
                        if to_type in ("decision", "code", "test"):
                            nxt.append(key)
            else:
                for other in sorted(reqs_by_art.get((kind, name), ()), key=_id_key):
                    if other not in found_reqs:
                        found_reqs[other] = {"hop": hop, "via": f"{kind} {name}"}
                        nxt.append(("requirement", other))
        frontier = nxt
    result: Dict = {"seeds": list(seeds), "depth": depth, "requirements": []}
    for rid, info in found_reqs.items():
        row = reqs.get(rid)
        result["requirements"].append({
            "id": rid, "hop": info["hop"], "via": info["via"],
            "status": _status(row) if row is not None else "not in register",
            "title": (row.get_str("Title") or row.get_str("Text")) if row is not None else "",
        })
    for group, key in (("decision", "decisions"), ("code", "code"), ("test", "tests"),
                       ("source", "sources"), ("commit", "commits")):
        result[key] = [
            {"name": name, "hop": info["hop"], "via": info["via"], "evidence": info["evidence"]}
            for (kind, name), info in found_arts.items() if kind == group
        ]
    return result


_GROUP_TITLES = (("decisions", "Decisions"), ("code", "Code"), ("tests", "Tests"),
                 ("sources", "Sources"), ("commits", "Commits"))


def _impact_text(result: Dict) -> str:
    out = [f"Impact of {', '.join(result['seeds'])} (depth {result['depth']})", ""]
    out.append(f"Requirements ({len(result['requirements'])})")
    for r in result["requirements"]:
        how = "seed" if r["hop"] == 0 else f"hop {r['hop']} via {r['via']}"
        out.append(f"  {r['id']:<10} {r['status']:<12} {how}")
    for key, title in _GROUP_TITLES:
        items = result[key]
        out += ["", f"{title} ({len(items)})"]
        for item in items:
            out.append(f"  {item['name']}  (hop {item['hop']} from {item['via']}; {item['evidence']})")
    return "\n".join(out) + "\n"


def _impact_md(result: Dict) -> str:
    out = [f"## Impact of {', '.join(result['seeds'])}", "",
           f"Followed `trace.csv` and the `Links` column up to {result['depth']} hop(s) "
           "(`re-lint trace impact`).", "",
           "### Requirements", "", "| ID | Status | Hop | Via | Title or text |", "| --- | --- | --- | --- | --- |"]
    for r in result["requirements"]:
        out.append(f"| {r['id']} | {r['status']} | {r['hop']} | {_md_cell(r['via'])} | {_md_cell(r['title'])} |")
    for key, title in _GROUP_TITLES:
        out += ["", f"### {title}", ""]
        if not result[key]:
            out.append("None.")
            continue
        out += ["| Item | Hop | From | Evidence |", "| --- | --- | --- | --- |"]
        for item in result[key]:
            out.append(f"| `{_md_cell(item['name'])}` | {item['hop']} | {item['via']} | `{_md_cell(item['evidence'])}` |")
    return "\n".join(out) + "\n"


def cmd_impact(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    edges = read_trace(_trace_path(args, ws))
    reqs = _load_requirements(ws, schema)
    matcher = IdMatcher(schema, reqs.keys())
    seeds: List[str] = []
    for raw in _split_list(args.ids):
        refs = matcher.canonical_refs(raw) or matcher.test_refs("test_" + raw)
        if not refs:
            raise UsageError(f"{raw!r} is not a requirement ID (expected e.g. {matcher.normalize('12', None)})")
        base = IdMatcher.base(refs[0])
        if base not in seeds:
            seeds.append(base)
    traced = {IdMatcher.base(e["From"]) for e in edges}
    unknown = [s for s in seeds if s not in reqs and s not in traced]
    for s in unknown:
        print(f"warning: {s} is neither in the register nor in the trace", file=sys.stderr)
    if len(unknown) == len(seeds):
        raise UsageError("none of the given IDs is known; check the IDs or rebuild the trace")
    result = _impact(seeds, edges, reqs, args.depth, reqio.id_regex("requirement", schema))
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.format == "md":
        print(_impact_md(result), end="")
    else:
        print(_impact_text(result), end="")
    return 0


def _gh_data(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _gh_prop(text: str) -> str:
    return _gh_data(text).replace(":", "%3A").replace(",", "%2C")


def cmd_gaps(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    trace_path = _trace_path(args, ws)
    edges = read_trace(trace_path)
    reqs = _load_requirements(ws, schema)
    repo = reqio.find_repo_root(ws).resolve()
    kinds = _split_list(args.only) or list(GAP_KINDS)
    bad = [k for k in kinds if k not in GAP_KINDS]
    if bad:
        raise UsageError(f"unknown gap kind(s) {', '.join(bad)}; choose from {', '.join(GAP_KINDS)}")
    statuses = {s.lower() for s in _split_list(args.status)} or None
    report = compute_gaps(edges, reqs, repo, schema, _registered_sources(ws, schema), statuses)
    gaps = [g for g in report["gaps"] if g["kind"] in kinds]
    if args.format == "json":
        print(json.dumps({"summary": report["summary"], "gaps": gaps}, indent=2, ensure_ascii=False))
    elif args.format == "github":
        level = "error" if args.fail_on_gaps else "warning"
        for g in gaps:
            props = f"file={_gh_prop(g['file'])}" + (f",line={g['line']}" if g["line"] else "")
            props += f",title={_gh_prop(g['kind'])}"
            print(f"::{level} {props}::{_gh_data(g['id'] + ': ' + g['detail'])}")
        print(f"trace gaps: {len(gaps)}")
    else:
        for kind in kinds:
            items = [g for g in gaps if g["kind"] == kind]
            if not items:
                continue
            print(f"{kind} ({len(items)})")
            for g in items:
                where = f"{g['file']}:{g['line']}" if g["line"] else g["file"]
                print(f"  {g['id']:<12} {where}  {g['detail']}")
        print(f"{len(gaps)} gap(s) ({_rel(trace_path, repo)})")
    return 1 if args.fail_on_gaps and gaps else 0


# --------------------------------------------------------------------------- CLI


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", metavar="DIR", help="workspace folder (default: <repo root>/requirements)")
    parser.add_argument("--schema", metavar="FILE", help="schema.json to use (default: <workspace>/schema.json)")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        description="Build the trace matrix (source -> requirement -> decision -> code -> test, plus "
                    "commits), report coverage gaps and follow change impact.",
        epilog="Exit codes: 0 ok, 1 gaps with --fail-on-gaps, 2 usage or parse error. "
               "Run '<command> --help' for the options of each command.",
    )
    sub = parser.add_subparsers(dest="action", metavar="{build,impact,gaps}")
    sub.required = True

    b = sub.add_parser("build", help="scan the repo and write trace.csv, trace.md and gaps.json",
                       description="Scan registers, decisions/ADRs, code, tests and git log for requirement "
                                   "IDs; write <out>/trace.csv, trace.md and gaps.json.")
    b.add_argument("--repo", metavar="DIR", help="repository root to scan (default: found from the workspace)")
    b.add_argument("--out", metavar="DIR", help="output folder (default: <workspace>/trace)")
    b.add_argument("--since", metavar="REV", help="only scan commits after REV (a revision, or a date YYYY-MM-DD)")
    b.add_argument("--code-glob", metavar="G", nargs="+", action="extend",
                   help="code file globs; replaces schema trace.code_globs (** spans folders; "
                        "a pattern without / matches at any depth)")
    b.add_argument("--test-glob", metavar="G", nargs="+", action="extend",
                   help="test file globs; replaces schema trace.test_globs")
    b.add_argument("--no-git", action="store_true", help="do not scan git log even if the schema enables it")
    b.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, metavar="N",
                   help=f"skip files larger than N bytes (default {DEFAULT_MAX_BYTES})")
    b.add_argument("--max-commits", type=int, default=DEFAULT_MAX_COMMITS, metavar="N",
                   help=f"scan at most N commits (default {DEFAULT_MAX_COMMITS})")
    b.add_argument("--max-graph-edges", type=int, default=DEFAULT_MAX_GRAPH_EDGES, metavar="N",
                   help=f"links drawn in the Mermaid graph (default {DEFAULT_MAX_GRAPH_EDGES}); "
                        "a note says when it is truncated")
    b.add_argument("--format", choices=("text", "json"), default="text", help="summary format on stdout")
    _common(b)

    i = sub.add_parser("impact", help="follow trace links from requirement IDs",
                       description="List the requirements, decisions, code, tests, sources and commits "
                                   "reachable from the given IDs through trace.csv and the Links column. "
                                   "Sources and commits are reported but not followed further.")
    i.add_argument("ids", nargs="+", metavar="ID", help="requirement IDs (R-012, R-012.AC2; comma lists allowed)")
    i.add_argument("--trace", metavar="FILE", help="trace.csv to read (default: <workspace>/trace/trace.csv)")
    i.add_argument("--depth", type=int, choices=(1, 2, 3), default=2,
                   help="hops to follow (default 2: requirement -> artifact -> other requirements)")
    i.add_argument("--format", choices=("text", "json", "md"), default="text")
    _common(i)

    g = sub.add_parser("gaps", help="report coverage gaps from trace.csv and the current register",
                       description="Report requirements without tests, without a source or without an "
                                   "implementation reference, and code or tests citing unknown or "
                                   "retired IDs.")
    g.add_argument("--trace", metavar="FILE", help="trace.csv to read (default: <workspace>/trace/trace.csv)")
    g.add_argument("--format", choices=("text", "json", "github"), default="text")
    g.add_argument("--fail-on-gaps", action="store_true", help="exit 1 when any reported gap exists")
    g.add_argument("--only", metavar="KIND", nargs="+", action="extend",
                   help="gap kinds to report: " + ", ".join(GAP_KINDS) + " (default: all)")
    g.add_argument("--status", metavar="S", nargs="+", action="extend",
                   help="statuses requirement-level gaps apply to (default: agreed, implemented, verified "
                        "for tests and implementation; every status for sources)")
    _common(g)
    return parser


def run(args: argparse.Namespace) -> int:
    handlers = {"build": cmd_build, "impact": cmd_impact, "gaps": cmd_gaps}
    try:
        return handlers[args.action](args)
    except (UsageError, ValueError) as exc:  # ValueError: malformed schema.json
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
