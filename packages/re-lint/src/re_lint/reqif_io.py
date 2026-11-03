#!/usr/bin/env python3
"""Export the requirement register to ReqIF 1.2 and import a ReqIF file back.

Usage::

    re-lint reqif export [--out FILE] [--ids R-001,R-002 ...] [--title TEXT] [--timestamp ISO]
    re-lint reqif import FILE [--diff] [--apply] [--add-columns] [--format text|json|md]

``export`` writes a minimal, valid ReqIF 1.2 document (namespace
``http://www.omg.org/spec/ReqIF/20110401/reqif.xsd``) from ``<workspace>/requirements.csv``:
one ``DATATYPE-DEFINITION-STRING``, one ``SPEC-OBJECT-TYPE`` with an
``ATTRIBUTE-DEFINITION-STRING`` per CSV column (``LONG-NAME`` = column name), one
``SPEC-OBJECT`` per requirement whose ``IDENTIFIER`` is the requirement ID, and one
``SPECIFICATION`` whose ``SPEC-HIERARCHY`` children reference every object in register order.
Identifiers of types and attribute definitions are derived from the column names, so two
exports of the same register are identical apart from ``--timestamp`` (default: now, UTC), which
sets ``CREATION-TIME`` and every ``LAST-CHANGE``. Empty cells are not written. Default ``--out``:
``<workspace>/exports/requirements.reqif`` (``-`` for stdout).

``import`` reads ``.reqif`` or ``.reqifz`` (zip) files from any tool. Attribute values of type
STRING, XHTML (flattened to one line of text), ENUMERATION (enum value names, space-separated),
INTEGER, REAL, BOOLEAN and DATE are mapped to columns by the attribute definition's
``LONG-NAME`` (case-insensitive; ``ReqIF.ForeignID`` -> ID, ``ReqIF.Text`` -> Text,
``ReqIF.Name`` -> Title). The requirement ID is the ``ID`` attribute, else the object's
``IDENTIFIER``; objects without a requirement ID (headings, notes) are skipped and counted.

The diff (default, or ``--diff``) lists requirements added, changed (column by column) and
missing from the import, compared with ``requirements.csv`` after whitespace normalization.
A column is compared only when the import defines that attribute, so a tool that drops an
attribute does not clear it. ``--apply`` writes the added rows and changed cells into
``requirements.csv``; it never deletes a row (missing ones are only reported) and ignores
attributes that are not register columns unless ``--add-columns`` is given.

Exit codes: 0 ok, 2 usage or parse error.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

if not __package__:  # run as a plain script: make the sibling reqio.py importable
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # inside the package
    from . import reqio
except ImportError:  # vendored next to reqio.py in a skill's scripts/
    import reqio

REQIF_NS = "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"
XHTML_NS = "http://www.w3.org/1999/xhtml"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
TOOL_ID = "re-lint (re-skills)"
DT_STRING = "rs-dt-string"
SPEC_OBJECT_TYPE = "rs-sot-requirement"
SPECIFICATION_TYPE = "rs-st-specification"
SPECIFICATION_ID = "rs-specification"
HEADER_ID = "rs-header"
STANDARD_NAMES = {"reqif.foreignid": "ID", "reqif.text": "Text", "reqif.name": "Title"}
_NCNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")
_XML_INVALID = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f￾￿]")
_BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "tr", "td", "th", "table", "h1", "h2", "h3", "h4",
               "h5", "h6", "blockquote", "pre"}


class UsageError(Exception):
    """A problem the user can fix (exit 2)."""


# --------------------------------------------------------------------------- helpers


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


def _split_list(values: Optional[Sequence[str]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        out.extend(v for v in re.split(r"[,\s]+", value) if v)
    return out


def _norm_ws(text: str) -> str:
    return " ".join((text or "").split())


def _md_cell(value: object) -> str:
    return _norm_ws(str(value if value is not None else "")).replace("|", "\\|")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _safe_id(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", text)


def _timestamp(value: Optional[str]) -> str:
    """An ``xsd:dateTime`` in UTC with a ``Z`` suffix."""
    if not value:
        return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = value.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        text += "T00:00:00+00:00"
    text = re.sub(r"Z$", "+00:00", text)
    try:
        moment = _dt.datetime.fromisoformat(text)
    except ValueError as exc:
        raise UsageError(f"--timestamp {value!r} is not ISO 8601 (e.g. 2026-11-03T10:00:00Z)") from exc
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=_dt.timezone.utc)
    return moment.astimezone(_dt.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_register(ws: Path, schema: Dict) -> Tuple[List[str], List[reqio.Row]]:
    path = ws / "requirements.csv"
    if not path.is_file():
        return [], []
    try:
        table = reqio.read_table(path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise UsageError(f"cannot read {path}: {exc}") from exc
    return table.columns, table.rows


# --------------------------------------------------------------------------- export


def _attribute_ids(columns: Sequence[str]) -> "OrderedDict[str, str]":
    out: "OrderedDict[str, str]" = OrderedDict()
    used = set()
    for col in columns:
        base = "rs-ad-" + _safe_id(col)
        ident, n = base, 2
        while ident in used:
            ident, n = f"{base}-{n}", n + 1
        used.add(ident)
        out[col] = ident
    return out


def _clean(value: str) -> str:
    return _XML_INVALID.sub("", (value or "").replace("\r\n", "\n").replace("\r", "\n"))


def build_reqif(columns: Sequence[str], rows: Sequence[Dict[str, str]], title: str, timestamp: str,
                comment: str = "") -> ET.Element:
    """The ReqIF tree for ``rows`` (each a column -> value mapping with an ``ID``)."""
    attr_ids = _attribute_ids(columns)
    longest = max([len(_clean(str(r.get(c) or ""))) for r in rows for c in columns] + [0])
    root = ET.Element("REQ-IF", {"xmlns": REQIF_NS, XML_LANG: "en"})
    header = ET.SubElement(ET.SubElement(root, "THE-HEADER"), "REQ-IF-HEADER", {"IDENTIFIER": HEADER_ID})
    if comment:
        ET.SubElement(header, "COMMENT").text = comment
    ET.SubElement(header, "CREATION-TIME").text = timestamp
    ET.SubElement(header, "REQ-IF-TOOL-ID").text = TOOL_ID
    ET.SubElement(header, "REQ-IF-VERSION").text = "1.0"
    ET.SubElement(header, "SOURCE-TOOL-ID").text = TOOL_ID
    ET.SubElement(header, "TITLE").text = title
    content = ET.SubElement(ET.SubElement(root, "CORE-CONTENT"), "REQ-IF-CONTENT")
    datatypes = ET.SubElement(content, "DATATYPES")
    ET.SubElement(datatypes, "DATATYPE-DEFINITION-STRING", {
        "IDENTIFIER": DT_STRING, "LAST-CHANGE": timestamp, "LONG-NAME": "String",
        "MAX-LENGTH": str(max(32000, longest)),
    })
    spec_types = ET.SubElement(content, "SPEC-TYPES")
    sot = ET.SubElement(spec_types, "SPEC-OBJECT-TYPE", {
        "IDENTIFIER": SPEC_OBJECT_TYPE, "LAST-CHANGE": timestamp, "LONG-NAME": "Requirement"})
    attrs = ET.SubElement(sot, "SPEC-ATTRIBUTES")
    for col, ident in attr_ids.items():
        ad = ET.SubElement(attrs, "ATTRIBUTE-DEFINITION-STRING", {
            "IDENTIFIER": ident, "LAST-CHANGE": timestamp, "LONG-NAME": col})
        ET.SubElement(ET.SubElement(ad, "TYPE"), "DATATYPE-DEFINITION-STRING-REF").text = DT_STRING
    ET.SubElement(spec_types, "SPECIFICATION-TYPE", {
        "IDENTIFIER": SPECIFICATION_TYPE, "LAST-CHANGE": timestamp, "LONG-NAME": "Requirements Specification"})
    objects = ET.SubElement(content, "SPEC-OBJECTS")
    object_ids: List[str] = []
    used = set()
    for row in rows:
        rid = str(row.get("ID") or "")
        ident = rid if _NCNAME.match(rid) else "rs-so-" + _safe_id(rid)
        while ident in used:
            ident += "_"
        used.add(ident)
        object_ids.append(ident)
        obj = ET.SubElement(objects, "SPEC-OBJECT", {"IDENTIFIER": ident, "LAST-CHANGE": timestamp})
        ET.SubElement(ET.SubElement(obj, "TYPE"), "SPEC-OBJECT-TYPE-REF").text = SPEC_OBJECT_TYPE
        values = ET.SubElement(obj, "VALUES")
        for col, ad_id in attr_ids.items():
            value = _clean(str(row.get(col) or ""))
            if value == "":
                continue
            av = ET.SubElement(values, "ATTRIBUTE-VALUE-STRING", {"THE-VALUE": value})
            ET.SubElement(ET.SubElement(av, "DEFINITION"), "ATTRIBUTE-DEFINITION-STRING-REF").text = ad_id
    specs = ET.SubElement(content, "SPECIFICATIONS")
    spec = ET.SubElement(specs, "SPECIFICATION", {
        "IDENTIFIER": SPECIFICATION_ID, "LAST-CHANGE": timestamp, "LONG-NAME": title})
    ET.SubElement(ET.SubElement(spec, "TYPE"), "SPECIFICATION-TYPE-REF").text = SPECIFICATION_TYPE
    children = ET.SubElement(spec, "CHILDREN")
    for ident in object_ids:
        sh = ET.SubElement(children, "SPEC-HIERARCHY", {"IDENTIFIER": "rs-sh-" + ident, "LAST-CHANGE": timestamp})
        ET.SubElement(ET.SubElement(sh, "OBJECT"), "SPEC-OBJECT-REF").text = ident
    return root


def serialize(root: ET.Element) -> str:
    if hasattr(ET, "indent"):
        ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def cmd_export(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    columns, rows = _read_register(ws, schema)
    if not rows:
        raise UsageError(f"no requirements in {ws / 'requirements.csv'}")
    pattern = reqio.id_regex("requirement", schema)
    rows = [r for r in rows if pattern.match(r.get_str("ID"))]
    wanted = _split_list(args.ids)
    if wanted:
        known = {r.get_str("ID") for r in rows}
        unknown = [i for i in wanted if i not in known]
        if unknown:
            raise UsageError(f"unknown requirement ID(s): {', '.join(unknown)}")
        keep = set(wanted)
        rows = [r for r in rows if r.get_str("ID") in keep]
    root_dir = reqio.find_repo_root(ws)
    register = os.path.relpath(ws / "requirements.csv", root_dir).replace(os.sep, "/")
    title = args.title or f"{root_dir.name} requirements"
    stamp = _timestamp(args.timestamp)
    tree = build_reqif(columns, [{c: r.get_str(c) for c in columns} for r in rows], title, stamp,
                       comment=f"Exported by re-lint reqif from {register}")
    text = serialize(tree)
    if args.out == "-":
        sys.stdout.write(text)
        return 0
    out = Path(args.out) if args.out else ws / "exports" / "requirements.reqif"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print(f"wrote {out} ({len(rows)} requirements, {len(columns)} attributes)")
    return 0


# --------------------------------------------------------------------------- import


def _read_reqif_bytes(path: Path) -> bytes:
    if not path.is_file():
        raise UsageError(f"{path} not found")
    data = path.read_bytes()
    if zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = sorted(n for n in archive.namelist() if n.lower().endswith(".reqif"))
            if not members:
                raise UsageError(f"{path}: archive holds no .reqif file")
            data = archive.read(members[0])
    if re.search(rb"<!ENTITY", data[:65536]):
        raise UsageError(f"{path}: XML entity declarations are not accepted")
    return data


def _flatten_xhtml(element: ET.Element) -> str:
    parts: List[str] = []

    def walk(node: ET.Element) -> None:
        block = _local(node.tag).lower() in _BLOCK_TAGS
        if block:
            parts.append(" ")
        if node.text:
            parts.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                parts.append(child.tail)
        if block:
            parts.append(" ")

    walk(element)
    return _norm_ws("".join(parts))


def parse_reqif(data: bytes) -> Dict:
    """Objects (``{"identifier", "values"}``) and the attribute names the file defines."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise UsageError(f"not well-formed XML: {exc}") from exc
    if _local(root.tag) != "REQ-IF":
        raise UsageError(f"not a ReqIF document (root element is {_local(root.tag)!r})")
    attr_names: Dict[str, str] = {}
    enum_names: Dict[str, str] = {}
    for el in root.iter():
        tag = _local(el.tag)
        if tag.startswith("ATTRIBUTE-DEFINITION-") and el.get("IDENTIFIER"):
            attr_names[el.get("IDENTIFIER", "")] = el.get("LONG-NAME") or el.get("IDENTIFIER", "")
        elif tag == "ENUM-VALUE" and el.get("IDENTIFIER"):
            enum_names[el.get("IDENTIFIER", "")] = el.get("LONG-NAME") or el.get("IDENTIFIER", "")
    objects: List[Dict] = []
    for obj in root.iter():
        if _local(obj.tag) != "SPEC-OBJECT":
            continue
        values: Dict[str, str] = {}
        for container in obj:
            if _local(container.tag) != "VALUES":
                continue
            for av in container:
                tag = _local(av.tag)
                if not tag.startswith("ATTRIBUTE-VALUE-"):
                    continue
                ref = None
                for child in av:
                    if _local(child.tag) == "DEFINITION" and len(child):
                        ref = (child[0].text or "").strip()
                if not ref:
                    continue
                name = attr_names.get(ref, ref)
                if tag == "ATTRIBUTE-VALUE-XHTML":
                    the_value = next((c for c in av if _local(c.tag) == "THE-VALUE"), None)
                    values[name] = _flatten_xhtml(the_value) if the_value is not None else ""
                elif tag == "ATTRIBUTE-VALUE-ENUMERATION":
                    refs = [(r.text or "").strip() for c in av if _local(c.tag) == "VALUES" for r in c]
                    values[name] = " ".join(enum_names.get(r, r) for r in refs if r)
                else:
                    values[name] = av.get("THE-VALUE", "")
        objects.append({"identifier": obj.get("IDENTIFIER", ""), "values": values})
    return {"objects": objects, "attributes": sorted(set(attr_names.values()))}


def _column_for(name: str, columns: Sequence[str]) -> Optional[str]:
    low = name.strip().lower()
    if low in STANDARD_NAMES:
        low = STANDARD_NAMES[low].lower()
    for col in columns:
        if col.lower() == low:
            return col
    return None


def import_rows(parsed: Dict, columns: Sequence[str], schema: Dict) -> Tuple["OrderedDict[str, Dict[str, str]]",
                                                                             List[str], List[str], int, List[str]]:
    """Imported rows by ID, compared columns, unknown attributes, skipped count and warnings."""
    pattern = reqio.id_regex("requirement", schema)
    mapping: Dict[str, str] = {}
    unknown: List[str] = []
    for name in parsed["attributes"]:
        col = _column_for(name, columns)
        if col:
            mapping[name] = col
        elif name.lower() == "reqif.foreignid":
            mapping[name] = "ID"  # the requirement ID even when the register lacks a column for it
        else:
            unknown.append(name)
    rows: "OrderedDict[str, Dict[str, str]]" = OrderedDict()
    skipped = 0
    warnings: List[str] = []
    for obj in parsed["objects"]:
        values: Dict[str, str] = {}
        extra: Dict[str, str] = {}
        for name, value in obj["values"].items():
            if name in mapping:
                values[mapping[name]] = value
            else:
                extra[name] = value
        rid = (values.get("ID") or obj["identifier"]).strip()
        if not pattern.match(rid):
            skipped += 1
            continue
        values["ID"] = rid
        if rid in rows:
            warnings.append(f"{rid} appears twice in the import; the first occurrence is used")
            continue
        values.update({f"\0{k}": v for k, v in extra.items()})
        rows[rid] = values
    compared = sorted(set(mapping.values()), key=lambda c: list(columns).index(c) if c in columns else 999)
    return rows, compared, unknown, skipped, warnings


def diff_import(imported: "OrderedDict[str, Dict[str, str]]", compared: Sequence[str],
                register: Sequence[reqio.Row]) -> Dict:
    current = OrderedDict((r.get_str("ID"), r) for r in register)
    added, changed, missing = [], [], []
    for rid, values in imported.items():
        row = current.get(rid)
        if row is None:
            added.append({"ID": rid, "values": {k: v for k, v in values.items() if not k.startswith("\0")}})
            continue
        changes = []
        for col in compared:
            if col == "ID":
                continue
            old, new = row.get_str(col), values.get(col, "")
            if _norm_ws(old) != _norm_ws(new):
                changes.append({"column": col, "old": old, "new": new})
        if changes:
            changed.append({"ID": rid, "changes": changes})
    for rid in current:
        if rid not in imported:
            missing.append(rid)
    unchanged = len(imported) - len(added) - len(changed)
    return {"added": added, "changed": changed, "missing": missing, "unchanged": unchanged}


def render_diff(diff: Dict, fmt: str, unknown: Sequence[str], skipped: int, source: str) -> str:
    if fmt == "json":
        return json.dumps({"source": source, **diff, "ignored_attributes": list(unknown),
                           "skipped_objects": skipped}, indent=2, ensure_ascii=False) + "\n"
    if fmt == "md":
        out = [f"# ReqIF import diff: `{source}`", "",
               f"Added {len(diff['added'])}, changed {len(diff['changed'])}, unchanged {diff['unchanged']}, "
               f"missing from the import {len(diff['missing'])}.", ""]
        out += ["## Added", ""]
        if diff["added"]:
            out += ["| ID | Text |", "| --- | --- |"]
            out += [f"| {a['ID']} | {_md_cell(a['values'].get('Text', ''))} |" for a in diff["added"]]
        else:
            out.append("None.")
        out += ["", "## Changed", ""]
        if diff["changed"]:
            out += ["| ID | Column | Workspace | Import |", "| --- | --- | --- | --- |"]
            for c in diff["changed"]:
                for ch in c["changes"]:
                    out.append(f"| {c['ID']} | {ch['column']} | {_md_cell(ch['old'])} | {_md_cell(ch['new'])} |")
        else:
            out.append("None.")
        out += ["", "## Missing from the import (kept in the register)", ""]
        out.append(", ".join(diff["missing"]) if diff["missing"] else "None.")
        if unknown:
            out += ["", f"Ignored attributes (not register columns): {', '.join(unknown)}."]
        if skipped:
            out += ["", f"Skipped {skipped} object(s) without a requirement ID (headings, notes)."]
        return "\n".join(out) + "\n"
    out = [f"ReqIF import {source}: added {len(diff['added'])}, changed {len(diff['changed'])}, "
           f"unchanged {diff['unchanged']}, missing from import {len(diff['missing'])}"]
    for a in diff["added"]:
        out.append(f"  + {a['ID']}  {_norm_ws(a['values'].get('Text', ''))[:100]}")
    for c in diff["changed"]:
        out.append(f"  ~ {c['ID']}")
        for ch in c["changes"]:
            out.append(f"      {ch['column']}: {_norm_ws(ch['old'])[:80]!r} -> {_norm_ws(ch['new'])[:80]!r}")
    for rid in diff["missing"]:
        out.append(f"  ? {rid}  not in the import (kept; rows are never deleted)")
    if unknown:
        out.append(f"  ignored attributes (not register columns): {', '.join(unknown)}")
    if skipped:
        out.append(f"  skipped {skipped} object(s) without a requirement ID")
    return "\n".join(out) + "\n"


def cmd_import(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    source = Path(args.file)
    parsed = parse_reqif(_read_reqif_bytes(source))
    columns, register = _read_register(ws, schema)
    base_columns = list(columns) or reqio.ordered_columns([], schema)
    imported, compared, unknown, skipped, warnings = import_rows(parsed, base_columns, schema)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    if not imported:
        raise UsageError(f"{source}: no SPEC-OBJECT carries a requirement ID")
    write_columns = list(base_columns)
    if args.add_columns and unknown:
        write_columns += [u for u in unknown if u not in write_columns]
        compared = list(compared) + [u for u in unknown if u not in compared]
        for values in imported.values():
            for u in unknown:
                if f"\0{u}" in values:
                    values[u] = values[f"\0{u}"]
        unknown = []
    diff = diff_import(imported, compared, register)
    print(render_diff(diff, args.format, unknown, skipped, str(source)), end="")
    if not args.apply:
        return 0
    if not diff["added"] and not diff["changed"]:
        print("nothing to apply")
        return 0
    rows = [dict(r) for r in register]
    by_id = {r.get("ID", ""): r for r in rows}
    for change in diff["changed"]:
        for ch in change["changes"]:
            by_id[change["ID"]][ch["column"]] = ch["new"]
    for add in diff["added"]:
        values = imported[add["ID"]]
        rows.append({c: values.get(c, "") for c in write_columns})
    target = ws / "requirements.csv"
    reqio.write_csv(target, rows, write_columns)
    print(f"wrote {target}: {len(diff['changed'])} changed, {len(diff['added'])} added, no row deleted")
    return 0


# --------------------------------------------------------------------------- CLI


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", metavar="DIR", help="workspace folder (default: <repo root>/requirements)")
    parser.add_argument("--schema", metavar="FILE", help="schema.json to use (default: <workspace>/schema.json)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reqif_bridge.py",
        description="Exchange requirements with DOORS, Polarion, Jama and other ReqIF tools: export "
                    "requirements.csv as ReqIF 1.2, import a ReqIF file and diff or merge it.",
        epilog="Exit codes: 0 ok, 2 usage or parse error. Full-fidelity exchange (relations, nested "
               "hierarchies) can use the strictdoc 'reqif' library instead.",
    )
    sub = parser.add_subparsers(dest="action", metavar="{export,import}")
    sub.required = True
    e = sub.add_parser("export", help="write requirements.csv as ReqIF 1.2",
                       description="One SPEC-OBJECT per requirement (IDENTIFIER = requirement ID), one "
                                   "ATTRIBUTE-DEFINITION-STRING per CSV column.")
    e.add_argument("--out", metavar="FILE", help="output file (default <workspace>/exports/requirements.reqif; '-' = stdout)")
    e.add_argument("--ids", metavar="ID", nargs="+", action="extend", help="export only these IDs (comma lists allowed)")
    e.add_argument("--title", metavar="TEXT", help="document and specification title (default '<repo> requirements')")
    e.add_argument("--timestamp", metavar="ISO", help="CREATION-TIME and LAST-CHANGE (default now, UTC); "
                                                       "fix it for reproducible files")
    _common(e)
    i = sub.add_parser("import", help="diff a ReqIF file against requirements.csv, optionally apply it",
                       description="Map attribute LONG-NAMEs back to columns and compare requirement by "
                                   "requirement. --apply writes added rows and changed cells; it never deletes.")
    i.add_argument("file", metavar="FILE", help=".reqif or .reqifz file")
    i.add_argument("--diff", action="store_true", help="print the requirement-level diff (the default)")
    i.add_argument("--apply", action="store_true", help="write the changes into requirements.csv")
    i.add_argument("--add-columns", action="store_true",
                   help="with --apply, add attributes that are not register columns as new columns")
    i.add_argument("--format", choices=("text", "json", "md"), default="text", help="diff format")
    _common(i)
    return parser


def run(args: argparse.Namespace) -> int:
    handlers = {"export": cmd_export, "import": cmd_import}
    try:
        return handlers[args.action](args)
    except (UsageError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
