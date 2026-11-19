#!/usr/bin/env python3
# VENDORED from packages/re-lint/src/re_lint/baseline.py by tools/vendor_scripts.py; do not edit.
# Change the package module, then run `python3 tools/vendor_scripts.py` to refresh this copy.
"""Create and diff requirement baselines, and write requirement release notes.

Usage::

    re-lint baseline create NAME [--message TEXT] [--tag] [--force]
    re-lint baseline diff OLD NEW [--format md|json]
    re-lint baseline notes OLD NEW

``create`` writes ``<workspace>/baselines/NAME.json``::

    {"name": "v1.0", "created": "2026-11-03T09:30:00Z", "git_commit": "<sha or null>",
     "message": "...",
     "requirements": [{"ID": "R-001", "Version": "1", "Status": "agreed", "Type": "F",
                       "Priority": "must", "text_sha256": "<sha256 of the Text>"}]}

``text_sha256`` hashes the ``Text`` with whitespace normalized (runs of spaces, tabs and newlines
become one space; leading and trailing whitespace dropped), UTF-8 encoded. Requirements come
from ``requirements.csv`` and ``stories/*.md`` (``requirements.csv`` wins on a duplicate ID) and
are sorted by ID. ``git_commit`` is ``HEAD`` when the workspace is in a git repository (a warning
says when the workspace has uncommitted changes); ``--tag`` also creates the lightweight tag
``req-NAME`` on that commit. A baseline is never overwritten unless ``--force`` is given.

``OLD`` and ``NEW`` are baseline names (``<workspace>/baselines/<name>.json``) or paths to manifest
files; ``working`` means the current workspace. Diff classes, one per requirement, first match wins:

* ``added``: in NEW only;
* ``removed``: in OLD only (rows should be withdrawn, never deleted);
* ``withdrawn``: Status became ``withdrawn``;
* ``changed``: text, Version, Type or Priority changed (a status change is listed with it);
* ``status-changed``: only Status changed.

``notes`` writes Markdown release notes from the same diff, using titles, rationales and the
decision records (``RDR-``) and change requests (``CR-``) in ``Links`` from the current register.

Exit codes: 0 ok, 2 usage, schema or parse error.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

if not __package__:  # run as a plain script: make the sibling reqio.py importable
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # inside the package
    from . import reqio
except ImportError:  # vendored next to reqio.py in a skill's scripts/
    import reqio

MANIFEST_FIELDS = ["ID", "Version", "Status", "Type", "Priority", "text_sha256"]
ATTRIBUTE_FIELDS = ["Version", "Type", "Priority"]
CLASSES = ["added", "changed", "status-changed", "withdrawn", "removed"]
WORKING = "working"
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


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


# --------------------------------------------------------------------------- helpers


def _rel(path) -> str:
    """Show paths relative to the current directory when possible, like the other commands."""
    try:
        return str(Path(path).resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


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


def _load_requirements(ws: Path, schema: Dict) -> "OrderedDict[str, reqio.Row]":
    out: "OrderedDict[str, reqio.Row]" = OrderedDict()
    try:
        rows = reqio.read_requirements(reqio.requirement_files(ws), schema)
    except UnicodeDecodeError as exc:
        raise UsageError(f"cannot read the requirement registers as UTF-8: {exc}") from exc
    for row in rows:
        out.setdefault(row.get_str("ID"), row)
    return out


def normalize_text(text: str) -> str:
    """Whitespace-normalized text: what ``text_sha256`` hashes."""
    return " ".join((text or "").split())


def text_sha256(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def _git(cwd: Path, *argv: str) -> Optional[str]:
    if shutil.which("git") is None:
        return None
    try:
        proc = subprocess.run(["git", "-C", str(cwd), *argv], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", errors="replace").strip()


def _md_cell(value: object) -> str:
    return " ".join(str(value if value is not None else "").split()).replace("|", "\\|")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


# --------------------------------------------------------------------------- manifests


def build_manifest(ws: Path, schema: Dict, name: str, message: str = "",
                   created: Optional[str] = None, git_commit: Optional[str] = None) -> Dict:
    reqs = _load_requirements(ws, schema)
    entries = []
    for rid in sorted(reqs, key=_id_key):
        row = reqs[rid]
        entries.append({
            "ID": rid,
            "Version": row.get_str("Version"),
            "Status": row.get_str("Status"),
            "Type": row.get_str("Type"),
            "Priority": row.get_str("Priority"),
            "text_sha256": text_sha256(row.get_str("Text")),
        })
    return {
        "name": name,
        "created": created or _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "git_commit": git_commit,
        "message": message,
        "requirements": entries,
    }


def _validate_manifest(data: object, source: str) -> Dict:
    if not isinstance(data, dict) or not isinstance(data.get("requirements"), list):
        raise UsageError(f"{source}: not a baseline manifest (expected an object with a 'requirements' list)")
    for i, entry in enumerate(data["requirements"]):
        if not isinstance(entry, dict) or not entry.get("ID"):
            raise UsageError(f"{source}: requirements[{i}] has no ID")
    return data


def load_manifest(ref: str, ws: Path, schema: Dict) -> Dict:
    """A manifest by name, path or ``working``."""
    if ref == WORKING:
        return build_manifest(ws, schema, WORKING, created="")
    candidates = [Path(ref)]
    if not ref.endswith(".json"):
        candidates.append(ws / "baselines" / f"{ref}.json")
    else:
        candidates.append(ws / "baselines" / ref)
    for path in candidates:
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise UsageError(f"{path}: cannot read baseline: {exc}") from exc
            return _validate_manifest(data, str(path))
    existing = sorted(p.stem for p in (ws / "baselines").glob("*.json")) if (ws / "baselines").is_dir() else []
    hint = f"; existing baselines: {', '.join(existing)}" if existing else "; no baselines yet"
    raise UsageError(f"baseline {ref!r} not found (looked for {candidates[-1]}){hint}")


# --------------------------------------------------------------------------- diff


def diff_manifests(old: Dict, new: Dict) -> Dict:
    old_by = {e["ID"]: e for e in old["requirements"]}
    new_by = {e["ID"]: e for e in new["requirements"]}
    entries: List[Dict] = []
    for rid in sorted(set(old_by) | set(new_by), key=_id_key):
        a, b = old_by.get(rid), new_by.get(rid)
        if a is None:
            entries.append({"ID": rid, "class": "added", "changes": [], "new": b})
            continue
        if b is None:
            entries.append({"ID": rid, "class": "removed", "changes": [], "old": a})
            continue
        changes = []
        if a.get("text_sha256") != b.get("text_sha256"):
            changes.append({"field": "Text", "old": "", "new": ""})
        for field in ATTRIBUTE_FIELDS + ["Status"]:
            if str(a.get(field, "")) != str(b.get(field, "")):
                changes.append({"field": field, "old": str(a.get(field, "")), "new": str(b.get(field, ""))})
        if not changes:
            continue
        fields = {c["field"] for c in changes}
        new_status = str(b.get("Status", "")).lower()
        if "Status" in fields and new_status == "withdrawn":
            cls = "withdrawn"
        elif fields - {"Status"}:
            cls = "changed"
        else:
            cls = "status-changed"
        entries.append({"ID": rid, "class": cls, "changes": changes, "old": a, "new": b})
    counts = OrderedDict((c, sum(1 for e in entries if e["class"] == c)) for c in CLASSES)
    return {"old": old.get("name", ""), "new": new.get("name", ""), "counts": counts, "entries": entries}


def _describe(change: Dict) -> str:
    if change["field"] == "Text":
        return "text"
    return f"{change['field']} {change['old'] or '(empty)'} -> {change['new'] or '(empty)'}"


def render_diff_md(diff: Dict) -> str:
    out = [f"# Baseline diff: {diff['old']} -> {diff['new']}", "", "| Class | Count |", "| --- | --- |"]
    out += [f"| {cls} | {count} |" for cls, count in diff["counts"].items()]
    titles = {"added": "Added", "changed": "Changed", "status-changed": "Status changed",
              "withdrawn": "Withdrawn", "removed": "Removed"}
    for cls in CLASSES:
        items = [e for e in diff["entries"] if e["class"] == cls]
        out += ["", f"## {titles[cls]}", ""]
        if not items:
            out.append("None.")
            continue
        if cls in ("added", "removed"):
            out += ["| ID | Version | Status | Type | Priority |", "| --- | --- | --- | --- | --- |"]
            for e in items:
                m = e.get("new") or e.get("old") or {}
                out.append(f"| {e['ID']} | {m.get('Version', '')} | {m.get('Status', '')} | {m.get('Type', '')} | "
                           f"{m.get('Priority', '')} |")
        else:
            out += ["| ID | Changes |", "| --- | --- |"]
            for e in items:
                out.append(f"| {e['ID']} | {_md_cell('; '.join(_describe(c) for c in e['changes']))} |")
    return "\n".join(out) + "\n"


def _json_ready(diff: Dict) -> Dict:
    return {
        "old": diff["old"],
        "new": diff["new"],
        "counts": dict(diff["counts"]),
        "entries": [{"ID": e["ID"], "class": e["class"], "changes": e["changes"]} for e in diff["entries"]],
    }


def render_notes(diff: Dict, old: Dict, new: Dict, reqs: Dict, decision_prefixes: Sequence[str]) -> str:
    counts = diff["counts"]
    summary = ", ".join(f"{counts[c]} {c.replace('-', ' ')}" for c in CLASSES)
    out = [f"# Requirement release notes: {diff['old']} -> {diff['new']}", ""]
    for label, manifest in (("From", old), ("To", new)):
        name = manifest.get("name", "")
        if name == WORKING:
            out.append(f"- {label}: the working register (not a baseline)")
        else:
            commit = manifest.get("git_commit")
            where = f"git {str(commit)[:12]}" if commit else "no git commit"
            created = manifest.get("created") or "unknown date"
            msg = f" - {manifest['message']}" if manifest.get("message") else ""
            out.append(f"- {label}: `{name}` ({created}, {where}){msg}")
    out += ["", f"Summary: {summary}.", ""]
    decision_re = re.compile(r"(?<![A-Za-z0-9_-])(?:" + "|".join(re.escape(p) for p in decision_prefixes) + r")\d+")

    def line(e: Dict) -> str:
        row = reqs.get(e["ID"])
        m = e.get("new") or e.get("old") or {}
        label = ""
        decisions: List[str] = []
        if row is not None:
            label = row.get_str("Title") or row.get_str("Text")
            decisions = decision_re.findall(row.get_str("Links"))
        attrs = ", ".join(v for v in (m.get("Type", ""), m.get("Priority", "")) if v)
        text = f"- **{e['ID']}**" + (f" {_md_cell(label)}" if label else "") + (f" ({attrs})" if attrs else "")
        if e["class"] in ("changed", "status-changed", "withdrawn"):
            text += ": " + "; ".join(_describe(c) for c in e["changes"])
        extras = []
        if e["class"] == "withdrawn" and row is not None and row.get_str("Rationale"):
            extras.append(f"Rationale: {_md_cell(row.get_str('Rationale')).rstrip('.')}")
        if decisions:
            extras.append(f"Decision: {', '.join(decisions)}")
        return text + ("".join(f". {x}" for x in extras))

    titles = {"added": "Added", "changed": "Changed", "status-changed": "Status changes",
              "withdrawn": "Withdrawn", "removed": "Removed from the register"}
    for cls in CLASSES:
        items = [e for e in diff["entries"] if e["class"] == cls]
        if not items:
            continue
        out += [f"## {titles[cls]}", ""]
        out += [line(e) for e in items]
        if cls == "removed":
            out += ["", "> Rows should be withdrawn, not deleted: restore these rows with `Status=withdrawn` "
                        "and the reason in `Rationale`."]
        out.append("")
    if not diff["entries"]:
        out += ["No requirement changed.", ""]
    stale = [e["ID"] for e in diff["entries"] if e["ID"] in reqs and e.get("new")
             and e["new"].get("text_sha256") != text_sha256(reqs[e["ID"]].get_str("Text"))]
    if stale and new.get("name") != WORKING:
        out += [f"> Titles and texts come from the current register; {', '.join(stale)} changed again after "
                f"`{new.get('name')}`.", ""]
    return "\n".join(out).rstrip("\n") + "\n"


# --------------------------------------------------------------------------- commands


def cmd_create(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    name = args.name
    if not _NAME_RE.match(name) or ".." in name or name.endswith(".lock") or name.endswith("."):
        raise UsageError(f"invalid baseline name {name!r}: use letters, digits, '.', '_' and '-' (e.g. v1.0-contract)")
    if name == WORKING:
        raise UsageError("'working' is reserved for the current workspace")
    if not ws.is_dir():
        raise UsageError(f"workspace {ws} does not exist")
    path = ws / "baselines" / f"{name}.json"
    if path.exists() and not args.force:
        raise UsageError(f"{path} already exists; baselines are immutable (use --force to replace it)")
    commit = _git(ws, "rev-parse", "HEAD")
    tag = f"req-{name}"
    if args.tag:
        if commit is None:
            raise UsageError("--tag needs a git repository with at least one commit")
        if _git(ws, "rev-parse", "-q", "--verify", f"refs/tags/{tag}") is not None:
            raise UsageError(f"git tag {tag} already exists")
    manifest = build_manifest(ws, schema, name, args.message or "", git_commit=commit)
    if not manifest["requirements"]:
        raise UsageError(f"no requirements found in {ws}; nothing to baseline")
    if commit is not None:
        dirty = _git(ws, "status", "--porcelain", "--", ".")
        if dirty:
            print("warning: the workspace has uncommitted changes; git_commit does not include them",
                  file=sys.stderr)
    _write_text(path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {_rel(path)} ({len(manifest['requirements'])} requirements, git commit {commit[:12] if commit else 'none'})")
    if args.tag:
        if _git(ws, "tag", tag, commit) is None:
            print(f"error: could not create git tag {tag}", file=sys.stderr)
            return 2
        print(f"created lightweight git tag {tag} at {commit[:12]}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    old = load_manifest(args.old, ws, schema)
    new = load_manifest(args.new, ws, schema)
    diff = diff_manifests(old, new)
    if args.format == "json":
        print(json.dumps(_json_ready(diff), indent=2, ensure_ascii=False))
    else:
        print(render_diff_md(diff), end="")
    return 0


def cmd_notes(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    old = load_manifest(args.old, ws, schema)
    new = load_manifest(args.new, ws, schema)
    diff = diff_manifests(old, new)
    ids = schema.get("ids") or {}
    prefixes = [str((ids.get(k) or {}).get("prefix", d)) for k, d in (("decision", "RDR-"), ("change", "CR-"))]
    notes = render_notes(diff, old, new, _load_requirements(ws, schema), prefixes)
    if args.out:
        _write_text(Path(args.out), notes)
        print(f"wrote {args.out}")
    else:
        print(notes, end="")
    return 0


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", metavar="DIR", help="workspace folder (default: <repo root>/requirements)")
    parser.add_argument("--schema", metavar="FILE", help="schema.json to use (default: <workspace>/schema.json)")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        description="Cut named requirement baselines (manifest + optional git tag), diff two baselines "
                    "or a baseline against the working register, and write release notes.",
        epilog="OLD/NEW: a baseline name, a manifest path, or 'working'. Exit codes: 0 ok, 2 usage error.",
    )
    sub = parser.add_subparsers(dest="action", metavar="{create,diff,notes}")
    sub.required = True
    c = sub.add_parser("create", help="write <workspace>/baselines/NAME.json",
                       description="Write a manifest of every requirement's ID, Version, Status, Type, Priority "
                                   "and text hash, with the current git commit.")
    c.add_argument("name", metavar="NAME", help="baseline name, e.g. v1.0-contract")
    c.add_argument("--message", metavar="TEXT", default="", help="why this baseline was cut")
    c.add_argument("--tag", action="store_true", help="also create the lightweight git tag req-NAME at HEAD")
    c.add_argument("--force", action="store_true", help="replace an existing baseline with the same name")
    _common(c)
    d = sub.add_parser("diff", help="compare two baselines (classes: added, changed, status-changed, withdrawn, removed)")
    d.add_argument("old", metavar="OLD")
    d.add_argument("new", metavar="NEW")
    d.add_argument("--format", choices=("md", "json"), default="md")
    _common(d)
    n = sub.add_parser("notes", help="requirement release notes in Markdown")
    n.add_argument("old", metavar="OLD")
    n.add_argument("new", metavar="NEW")
    n.add_argument("--out", metavar="FILE", help="write the notes to FILE instead of stdout")
    _common(n)
    return parser


def run(args: argparse.Namespace) -> int:
    handlers = {"create": cmd_create, "diff": cmd_diff, "notes": cmd_notes}
    try:
        return handlers[args.action](args)
    except (UsageError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
