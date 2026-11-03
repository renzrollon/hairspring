#!/usr/bin/env python3
# VENDORED from packages/re-lint/src/re_lint/reqif_io.py by tools/vendor_scripts.py; do not edit.
# Change the package module, then run `python3 tools/vendor_scripts.py` to refresh this copy.
"""Export the requirement register to ReqIF 1.2 and import a ReqIF file back.

Usage::

    re-lint reqif export [--out FILE] [--ids R-001,R-002 ...] [--title TEXT] [--timestamp ISO]
    re-lint reqif import FILE [--diff] [--apply] [--add-columns] [--allow-invalid] [--cr CR-nnn]
                         [--format md|json]

``export`` writes a minimal, valid ReqIF 1.2 document (namespace
``http://www.omg.org/spec/ReqIF/20110401/reqif.xsd``) from ``<workspace>/requirements.csv``:
one ``DATATYPE-DEFINITION-STRING``, one ``SPEC-OBJECT-TYPE`` with an
``ATTRIBUTE-DEFINITION-STRING`` per CSV column (``LONG-NAME`` = column name), one
``SPEC-OBJECT`` per requirement whose ``IDENTIFIER`` is the requirement ID, and one
``SPECIFICATION`` whose ``SPEC-HIERARCHY`` children reference every object in register order.
Identifiers of types and attribute definitions are derived from the column names, so two
exports of the same register are identical apart from ``--timestamp`` (default: now, UTC), which
sets ``CREATION-TIME`` and every ``LAST-CHANGE``. Empty cells are not written. Without ``--ids``,
withdrawn and rejected rows are left out. An ID that is not an XML NCName is refused (exit 2).
Default ``--out``: ``<workspace>/exports/requirements.reqif`` (``-`` for stdout).

``import`` reads ``.reqif`` files and the ``.reqif`` inside a ``.reqifz``; files with a
``<!DOCTYPE`` are refused. Values of type STRING, XHTML (flattened to one line of text),
ENUMERATION (enum value names), INTEGER, REAL, BOOLEAN and DATE map to columns by the attribute
definition's ``LONG-NAME`` (case-insensitive; ``ReqIF.ForeignID`` -> ID, ``ReqIF.Text`` -> Text,
``ReqIF.Name`` -> Title). An object is a requirement when its ``IDENTIFIER`` or its ``ID`` /
``ReqIF.ForeignID`` value is a requirement ID; an object with Text but no requirement ID is a
``new-object``; one with neither is skipped (heading, note).

The diff (Markdown in the shape of the reqif-bridge ``import-diff.md`` template, or ``--format
json``) uses these classes: ``changed-text``, ``changed-attribute``, ``invalid-value`` (outside
``schema.attributes.enums``; ``TBD`` is allowed), ``new-object``, ``missing-object`` (in the newest
``<workspace>/exports/*.reqif`` with the same ``SPECIFICATION`` identifier, or in the register
when no export matches, but not in the file), ``unmapped-attribute``, ``xhtml-flattened`` and
``unchanged``. A column is compared only when the file defines that attribute.

``--apply`` writes ``changed-text``, ``changed-attribute`` and ``new-object`` (next free ID unless
the object carries one, ``Status=draft``, ``Source=reqif:<file>#<IDENTIFIER>``, empty required
cells ``TBD``) into ``requirements.csv``. It never deletes a row and never writes an
``invalid-value`` unless ``--allow-invalid``. A Text change increments ``Version`` when that column
exists (empty counts as 1); on an ``agreed``, ``implemented`` or ``verified`` row it also sets
``Status=proposed``, unless ``--cr CR-nnn`` names the approved change request (then the row is or
goes back to ``agreed`` and the CR is added to ``Links``). Every written cell is printed.

Exit codes: 0 ok (import: no difference, or applied), 1 import found differences, 2 usage or
parse error.
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
RETIRED = {"withdrawn", "rejected"}
COMMITTED = {"agreed", "implemented", "verified"}
MAX_IMPORT_BYTES = 200_000_000
_BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "tr", "td", "th", "table", "h1", "h2", "h3", "h4",
               "h5", "h6", "blockquote", "pre"}


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
    else:
        rows = [r for r in rows if r.get_str("Status").lower() not in RETIRED]
    bad = [r.get_str("ID") for r in rows if not _NCNAME.match(r.get_str("ID"))]
    if bad:
        raise UsageError(f"requirement ID(s) {', '.join(bad)} are not XML NCNames (ReqIF IDENTIFIER needs a letter "
                         "or '_' first); the bridge does not invent other identifiers")
    if not rows:
        raise UsageError("nothing to export (every row is withdrawn or rejected; name rows with --ids)")
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
    counts: Dict[str, int] = OrderedDict()
    for r in rows:
        counts[r.get_str("Status") or "(empty)"] = counts.get(r.get_str("Status") or "(empty)", 0) + 1
    print(f"wrote {out} ({len(rows)} requirements, {len(columns)} attributes; "
          + ", ".join(f"{k} {v}" for k, v in counts.items()) + ")")
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
            if archive.getinfo(members[0]).file_size > MAX_IMPORT_BYTES:
                raise UsageError(f"{path}: {members[0]} is larger than {MAX_IMPORT_BYTES} bytes")
            data = archive.read(members[0])
    if re.search(rb"<!DOCTYPE|<!ENTITY", data[:65536], re.I):
        raise UsageError(f"{path}: documents with a <!DOCTYPE> are not accepted (entity-expansion risk)")
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
    """Header, attribute names, specification identifiers and objects of a ReqIF document."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise UsageError(f"not well-formed XML: {exc}") from exc
    if _local(root.tag) != "REQ-IF":
        raise UsageError(f"not a ReqIF document (root element is {_local(root.tag)!r})")
    header: Dict[str, str] = {}
    attr_names: Dict[str, str] = {}
    enum_names: Dict[str, str] = {}
    spec_ids: List[str] = []
    for el in root.iter():
        tag = _local(el.tag)
        if tag in ("SOURCE-TOOL-ID", "REQ-IF-TOOL-ID", "CREATION-TIME", "TITLE") and tag not in header:
            header[tag] = (el.text or "").strip()
        elif tag.startswith("ATTRIBUTE-DEFINITION-") and el.get("IDENTIFIER"):
            attr_names[el.get("IDENTIFIER", "")] = el.get("LONG-NAME") or el.get("IDENTIFIER", "")
        elif tag == "ENUM-VALUE" and el.get("IDENTIFIER"):
            enum_names[el.get("IDENTIFIER", "")] = el.get("LONG-NAME") or el.get("IDENTIFIER", "")
        elif tag == "SPECIFICATION" and el.get("IDENTIFIER"):
            spec_ids.append(el.get("IDENTIFIER", ""))
    objects: List[Dict] = []
    for obj in root.iter():
        if _local(obj.tag) != "SPEC-OBJECT":
            continue
        values: Dict[str, str] = {}
        xhtml: List[str] = []
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
                    xhtml.append(name)
                elif tag == "ATTRIBUTE-VALUE-ENUMERATION":
                    refs = [(r.text or "").strip() for c in av if _local(c.tag) == "VALUES" for r in c]
                    values[name] = " ".join(enum_names.get(r, r) for r in refs if r)
                else:
                    values[name] = av.get("THE-VALUE", "")
        objects.append({"identifier": obj.get("IDENTIFIER", ""), "values": values, "xhtml": xhtml})
    return {"header": header, "objects": objects, "attributes": sorted(set(attr_names.values())),
            "specifications": spec_ids}


def _column_for(name: str, columns: Sequence[str]) -> Optional[str]:
    low = name.strip().lower()
    if low in STANDARD_NAMES:
        low = STANDARD_NAMES[low].lower()
    for col in columns:
        if col.lower() == low:
            return col
    return None


def _enums(schema: Dict) -> Dict[str, List[str]]:
    enums = ((schema.get("attributes") or {}).get("enums") or {})
    return {str(k): [str(v) for v in vals] for k, vals in enums.items() if isinstance(vals, list)}


def _valid(column: str, value: str, enums: Dict[str, List[str]]) -> bool:
    if column not in enums or value.strip() == "" or value.strip().upper() == "TBD":
        return True
    return value.strip().lower() in {v.lower() for v in enums[column]}


def _canonical_enum(column: str, value: str, enums: Dict[str, List[str]]) -> str:
    for allowed in enums.get(column, []):
        if allowed.lower() == value.strip().lower():
            return allowed
    return value


def _newest_export(ws: Path, spec_ids: Sequence[str], source: Path) -> Optional[Tuple[Path, List[str]]]:
    """The newest ``<workspace>/exports/*.reqif`` with one of ``spec_ids``, and its requirement IDs."""
    folder = ws / "exports"
    if not folder.is_dir() or not spec_ids:
        return None
    candidates = sorted(folder.glob("*.reqif"), key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
    for path in candidates:
        try:
            parsed = parse_reqif(_read_reqif_bytes(path))
        except (UsageError, OSError):
            continue
        if set(parsed["specifications"]) & set(spec_ids):
            ids = [o["values"].get("ID") or o["identifier"] for o in parsed["objects"]]
            return path, [i for i in ids if i]
    return None


def classify(parsed: Dict, columns: Sequence[str], register: Sequence[reqio.Row], schema: Dict,
             export: Optional[Tuple[Path, List[str]]]) -> Dict:
    """Import findings by class (the classes of the reqif-bridge skill)."""
    pattern = reqio.id_regex("requirement", schema)
    enums = _enums(schema)
    mapping: Dict[str, str] = {}
    for name in parsed["attributes"]:
        col = _column_for(name, columns)
        if col:
            mapping[name] = col
        elif name.lower() == "reqif.foreignid":
            mapping[name] = "ID"
    defined = [c for c in columns if c in set(mapping.values()) and c != "ID"]
    current = OrderedDict((r.get_str("ID"), r) for r in register)
    changes: List[Dict] = []
    readonly: List[Dict] = []
    objects: List[Dict] = []
    seen: set = set()
    unchanged = 0
    for obj in parsed["objects"]:
        values = {mapping[n]: v for n, v in obj["values"].items() if n in mapping}
        extras = [(n, v) for n, v in obj["values"].items() if n not in mapping and v.strip()]
        ident = obj["identifier"]
        rid = ident if pattern.match(ident) else (values.get("ID", "").strip() if pattern.match(values.get("ID", "").strip()) else "")
        label = rid or ident
        if rid in seen:
            readonly.append({"id": label, "class": "duplicate-object", "detail": "appears twice; the first one is used"})
            continue
        if rid:
            seen.add(rid)
        for name, value in extras:
            readonly.append({"id": label, "class": "unmapped-attribute", "detail": f"`{name}`: \"{_norm_ws(value)}\""})
        if obj["xhtml"]:
            readonly.append({"id": label, "class": "xhtml-flattened",
                             "detail": f"{', '.join(mapping.get(n, n) for n in obj['xhtml'])} arrived as XHTML; "
                                       "formatting dropped"})
        if rid and rid in current:
            row = current[rid]
            found = False
            for col in defined:
                old, new = row.get_str(col), values.get(col, "")
                if _norm_ws(old) == _norm_ws(new):
                    continue
                found = True
                if not _valid(col, new, enums):
                    cls = "invalid-value"
                else:
                    cls = "changed-text" if col == "Text" else "changed-attribute"
                changes.append({"id": rid, "class": cls, "column": col, "old": old, "new": new})
            if not found:
                unchanged += 1
            continue
        if not rid and not values.get("Text", "").strip():
            readonly.append({"id": ident, "class": "skipped", "detail": "no requirement ID and no Text (heading or note)"})
            continue
        new_values = {c: v for c, v in values.items() if c != "ID"}
        invalid = [c for c, v in new_values.items() if not _valid(c, v, enums)]
        entry = {"id": rid or ident, "class": "new-object", "identifier": ident, "rid": rid,
                 "values": new_values, "invalid": invalid}
        changes.append(entry)
        objects.append(entry)
    imported = seen
    if export is not None:
        exported = set(export[1])
        missing = [rid for rid in current if rid in exported and rid not in imported]
        never = [rid for rid in current if rid not in exported and rid not in imported]
    else:
        missing = [rid for rid in current if rid not in imported]
        never = []
    for rid in missing:
        changes.append({"id": rid, "class": "missing-object", "column": "-",
                        "old": "exported" if export else "in the register", "new": "not in the file"})
    for rid in never:
        readonly.append({"id": rid, "class": "not exported",
                         "detail": f"Status={current[rid].get_str('Status')}; never sent, absent as expected"})
    counts = OrderedDict((c, 0) for c in ("changed-text", "changed-attribute", "invalid-value", "new-object",
                                          "missing-object", "unmapped-attribute", "xhtml-flattened"))
    for item in changes + readonly:
        if item["class"] in counts:
            counts[item["class"]] += 1
    counts["unchanged"] = unchanged
    return {"changes": changes, "readonly": readonly, "counts": counts, "defined": defined,
            "unmapped": sorted({n for n in parsed["attributes"] if n not in mapping})}


def _recommendation(item: Dict, register: Dict[str, reqio.Row], next_id: str, source_name: str = "<file>") -> str:
    cls = item["class"]
    if cls == "changed-text":
        status = register[item["id"]].get_str("Status").lower() if item["id"] in register else ""
        if status in COMMITTED:
            return (f"Change request: {item['id']} is {status}. If accepted, --apply sets Status=proposed and "
                    "increments Version (or pass --cr CR-nnn for an approved change request)")
        return "Review; if accepted, --apply writes it and increments Version when the column exists"
    if cls == "changed-attribute":
        return "Review; if accepted, --apply writes it"
    if cls == "invalid-value":
        return f"Not written: {item['new']!r} is not a {item['column']} value; ask the sender what it means"
    if cls == "new-object":
        rid = item["rid"] or next_id
        return f"Candidate requirement. If accepted: new row {rid}, Status=draft, Source reqif:{source_name}#{item['identifier']}"
    if cls == "missing-object":
        return "Never deleted. Ask the sender whether they left it out on purpose"
    return ""


def render_import_md(result: Dict, source: Path, header: Dict[str, str], compared_with: str,
                     register: Dict[str, reqio.Row], next_id: str, today: str) -> str:
    out = [f"# ReqIF import diff: {source.name}", "",
           f"Reviewed: {today} · File: `{source}` · From: {header.get('SOURCE-TOOL-ID') or '?'} / "
           f"{header.get('REQ-IF-TOOL-ID') or '?'}, created {header.get('CREATION-TIME') or '?'} · "
           f"Compared with: {compared_with}", "",
           f"Command: `reqif_bridge.py import {source.name} --diff` · Nothing has been written to the register.", "",
           "## Summary", "", "| Class | Count |", "| --- | --- |"]
    out += [f"| {cls} | {n} |" for cls, n in result["counts"].items()]
    out += ["", "## Changes to decide", ""]
    if result["changes"]:
        out += ["| # | ID or object | Class | Attribute | Register value | File value | Recommendation | Decision (who, date) |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for n, item in enumerate(result["changes"], 1):
            if item["class"] == "new-object":
                cols = ", ".join(item["values"]) or "-"
                value = "; ".join(f'"{_norm_ws(v)}"' if " " in v else _norm_ws(v) for v in item["values"].values())
                ident = item["id"] if item["rid"] else f"`{item['id']}`"
                out.append(f"| {n} | {ident} | new-object | {cols} | - | {_md_cell(value)} | "
                           f"{_md_cell(_recommendation(item, register, next_id, source.name))} | open |")
            else:
                out.append(f"| {n} | {item['id']} | {item['class']} | {item['column']} | {_md_cell(item['old'])} | "
                           f"{_md_cell(item['new'])} | {_md_cell(_recommendation(item, register, next_id, source.name))} | open |")
    else:
        out.append("None.")
    out += ["", "## Read only (not imported)", ""]
    if result["readonly"]:
        out += ["| # | ID or object | Class | Detail |", "| --- | --- | --- | --- |"]
        out += [f"| {n} | {item['id']} | {item['class']} | {_md_cell(item['detail'])} |"
                for n, item in enumerate(result["readonly"], 1)]
    else:
        out.append("None.")
    out += ["", "## Next", "",
            "- [ ] A decision is recorded for every row in \"Changes to decide\".",
            f"- [ ] Accepted changes applied: `import {source.name} --apply` only if every applicable change was "
            "accepted; otherwise by hand. `invalid-value` and `missing-object` rows are never written.",
            "- [ ] Accepted text changes on agreed rows: `Version` + 1 and `Status=proposed`, or the change request "
            "is cited (`--cr CR-nnn`).",
            "- [ ] `requirement-linter` run on the changed and new rows."]
    return "\n".join(out) + "\n"


def _next_free_id(ws: Path, schema: Dict, taken: Sequence[str]) -> int:
    """Highest requirement number in the workspace files (withdrawn ones included), plus one."""
    pattern = reqio.id_prefix_regex("requirement", schema)
    highest = 0
    for rid in taken:
        number = reqio.parse_id_number(rid, "requirement", schema)
        highest = max(highest, number or 0)
    for path in ws.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in (".csv", ".md", ".json", ".txt", ".yaml", ".yml"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in pattern.finditer(text):
            highest = max(highest, int(match.group(1)))
    return highest + 1


def cmd_import(args: argparse.Namespace) -> int:
    ws, schema = _workspace(args)
    source = Path(args.file)
    parsed = parse_reqif(_read_reqif_bytes(source))
    if not parsed["objects"]:
        raise UsageError(f"{source}: no SPEC-OBJECT found")
    if args.cr and not reqio.id_regex("change", schema).match(args.cr):
        raise UsageError(f"--cr {args.cr!r} is not a change request ID (e.g. CR-014)")
    columns, register_rows = _read_register(ws, schema)
    columns = list(columns) or reqio.ordered_columns([], schema)
    if args.add_columns:
        for name in parsed["attributes"]:
            if _column_for(name, columns) is None and name.lower() not in STANDARD_NAMES:
                columns.append(name)
    export = _newest_export(ws, parsed["specifications"], source)
    result = classify(parsed, columns, register_rows, schema, export)
    register = OrderedDict((r.get_str("ID"), r) for r in register_rows)
    first_free = _next_free_id(ws, schema, list(register))
    next_id = reqio.format_id("requirement", first_free, schema)
    root = reqio.find_repo_root(ws)
    reg_name = os.path.relpath(ws / "requirements.csv", root).replace(os.sep, "/")
    compared_with = f"`{reg_name}`" + (
        f" and the export `{os.path.relpath(export[0], root).replace(os.sep, '/')}`" if export
        else " (no matching export found)")
    if args.format == "json":
        print(json.dumps({"source": str(source), "header": parsed["header"], "compared_with": compared_with,
                          **{k: v for k, v in result.items()}}, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_import_md(result, source, parsed["header"], compared_with, register, next_id,
                              _dt.date.today().isoformat()), end="")
    findings = any(item["class"] not in ("not exported", "skipped") for item in result["changes"] + result["readonly"])
    if not args.apply:
        return 1 if findings else 0
    return _apply(args, ws, schema, columns, register_rows, result, source, first_free)


def _apply(args: argparse.Namespace, ws: Path, schema: Dict, columns: List[str], register_rows: Sequence[reqio.Row],
           result: Dict, source: Path, first_free: int) -> int:
    enums = _enums(schema)
    rows = [dict(r) for r in register_rows]
    by_id = {r.get("ID", ""): r for r in rows}
    log: List[str] = []
    held: List[str] = []
    text_changed: List[str] = []
    for item in result["changes"]:
        cls = item["class"]
        if cls in ("changed-text", "changed-attribute") or (cls == "invalid-value" and args.allow_invalid):
            row = by_id[item["id"]]
            row[item["column"]] = _canonical_enum(item["column"], item["new"], enums)
            log.append(f"{item['id']} {item['column']}: {_norm_ws(item['old'])!r} -> {_norm_ws(item['new'])!r}")
            if item["column"] == "Text" and item["id"] not in text_changed:
                text_changed.append(item["id"])
        elif cls == "invalid-value":
            held.append(f"{item['id']} {item['column']}={item['new']!r} (invalid-value; --allow-invalid overrides)")
    for rid in text_changed:
        row = by_id[rid]
        old_status = next((r.get_str("Status") for r in register_rows if r.get_str("ID") == rid), "").lower()
        if "Version" in columns:
            old = (row.get("Version") or "").strip() or "1"
            if old.isdigit():
                row["Version"] = str(int(old) + 1)
                log.append(f"{rid} Version: {old!r} -> {row['Version']!r} (text changed)")
            else:
                held.append(f"{rid} Version {old!r} is not an integer; increment it by hand")
        if old_status in COMMITTED:
            if args.cr:
                target = "agreed"
                if "Links" in columns and args.cr not in (row.get("Links") or "").split():
                    row["Links"] = ((row.get("Links") or "") + " " + args.cr).strip()
                    log.append(f"{rid} Links: + {args.cr}")
                reason = f"text change approved by {args.cr}"
            else:
                target = "proposed"
                reason = f"text changed while Status={old_status}; pass --cr CR-nnn if a change request approved it"
            if (row.get("Status") or "").lower() != target:
                log.append(f"{rid} Status: {row.get('Status')!r} -> {target!r} ({reason})")
                row["Status"] = target
    required = list((schema.get("attributes") or {}).get("required") or [])
    number = first_free
    added = 0
    for item in result["changes"]:
        if item["class"] != "new-object":
            continue
        rid = item["rid"]
        if not rid:
            rid = reqio.format_id("requirement", number, schema)
            number += 1
        new = {c: "" for c in columns}
        for col, value in item["values"].items():
            if col in new:
                new[col] = "" if col in item["invalid"] else _canonical_enum(col, value, enums)
        new.update({"ID": rid, "Status": "draft", "Source": f"reqif:{source.name}#{item['identifier']}"})
        for col in required:
            if col in new and not new[col].strip():
                new[col] = "TBD"
        if item["invalid"]:
            held.append(f"{rid}: invalid {', '.join(item['invalid'])} not written (set to TBD or empty)")
        rows.append(new)
        added += 1
        log.append(f"{rid} added from {item['identifier']} (Status=draft)")
    if not log:
        print("nothing to apply")
        for line in held:
            print(f"held back: {line}")
        return 1 if held else 0
    target = ws / "requirements.csv"
    reqio.write_csv(target, rows, columns)
    print(f"wrote {target}: {len(log) - added} cell change(s), {added} row(s) added, no row deleted")
    for line in log:
        print(f"  {line}")
    for line in held:
        print(f"held back: {line}")
    return 0


# --------------------------------------------------------------------------- CLI


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", metavar="DIR", help="workspace folder (default: <repo root>/requirements)")
    parser.add_argument("--schema", metavar="FILE", help="schema.json to use (default: <workspace>/schema.json)")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
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
    e.add_argument("--ids", metavar="ID", nargs="+", action="extend",
                   help="export only these IDs (comma lists allowed; default: every row except withdrawn and rejected)")
    e.add_argument("--title", metavar="TEXT", help="document and specification title (default '<repo> requirements')")
    e.add_argument("--timestamp", metavar="ISO", help="CREATION-TIME and LAST-CHANGE (default now, UTC); "
                                                       "fix it for reproducible files")
    _common(e)
    i = sub.add_parser("import", help="diff a ReqIF file against requirements.csv, optionally apply it",
                       description="Map attribute LONG-NAMEs back to columns and compare requirement by "
                                   "requirement. Exit 1 when the file differs from the register. --apply writes "
                                   "changed-text, changed-attribute and new-object rows; it never deletes a row and "
                                   "never writes an invalid-value without --allow-invalid.")
    i.add_argument("file", metavar="FILE", help=".reqif or .reqifz file")
    i.add_argument("--diff", action="store_true", help="print the requirement-level diff (the default)")
    i.add_argument("--apply", action="store_true", help="write the changes into requirements.csv")
    i.add_argument("--add-columns", action="store_true",
                   help="with --apply, add attributes that are not register columns as new columns")
    i.add_argument("--allow-invalid", action="store_true",
                   help="with --apply, also write values outside schema.attributes.enums (normally held back)")
    i.add_argument("--cr", metavar="CR-nnn",
                   help="with --apply, the approved change request for text changes on agreed rows: Status stays "
                        "(implemented/verified go back to agreed) and the CR is added to Links")
    i.add_argument("--format", choices=("md", "json"), default="md",
                   help="diff format (default md, in the shape of the reqif-bridge import-diff template)")
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
