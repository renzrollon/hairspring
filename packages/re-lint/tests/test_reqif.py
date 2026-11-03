from __future__ import annotations

import csv
import io
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import pytest

from relint_helpers import SRC, make_row, run_cli
from re_lint import reqif_io

NS = {"r": "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"}
HEADER = ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale", "Title"]
STAMP = "2026-11-03T10:00:00Z"


@pytest.fixture
def register(workspace):
    workspace.register([
        make_row("R-001", Status="agreed", Title="Earn points"),
        make_row("R-002", text='The receipt shall show "Points: <balance>" & the date.\nSecond line.',
                 Rationale="Members ask at the till; ünïcödé ok."),
        make_row("R-003", text="The app shall show expiring points.", Title=""),
        make_row("R-004", text="The POS shall print vouchers.", Status="withdrawn"),
    ], header=HEADER)
    return workspace


def _export(ws, capsys, *extra):
    out = ws.root / "out.reqif"
    result = run_cli(reqif_io, ["export", "--out", str(out), "--timestamp", STAMP, *extra], capsys)
    assert result.code == 0, result.err
    return out


def test_export_structure(register, capsys):
    root = ET.parse(_export(register, capsys)).getroot()
    assert root.tag == "{%s}REQ-IF" % NS["r"]
    header = root.find("r:THE-HEADER/r:REQ-IF-HEADER", NS)
    assert [c.tag.split("}")[1] for c in header] == ["COMMENT", "CREATION-TIME", "REQ-IF-TOOL-ID", "REQ-IF-VERSION",
                                                     "SOURCE-TOOL-ID", "TITLE"]
    assert header.find("r:CREATION-TIME", NS).text == STAMP and header.find("r:REQ-IF-VERSION", NS).text == "1.0"
    content = root.find("r:CORE-CONTENT/r:REQ-IF-CONTENT", NS)
    assert [c.tag.split("}")[1] for c in content] == ["DATATYPES", "SPEC-TYPES", "SPEC-OBJECTS", "SPECIFICATIONS"]
    assert content.find("r:DATATYPES/r:DATATYPE-DEFINITION-STRING", NS).get("MAX-LENGTH")
    attrs = content.findall("r:SPEC-TYPES/r:SPEC-OBJECT-TYPE/r:SPEC-ATTRIBUTES/r:ATTRIBUTE-DEFINITION-STRING", NS)
    assert [a.get("LONG-NAME") for a in attrs] == HEADER
    assert [a.get("IDENTIFIER") for a in attrs][:2] == ["rs-ad-ID", "rs-ad-Type"]
    assert content.find("r:SPEC-TYPES/r:SPECIFICATION-TYPE", NS) is not None
    objects = content.findall("r:SPEC-OBJECTS/r:SPEC-OBJECT", NS)
    assert [o.get("IDENTIFIER") for o in objects] == ["R-001", "R-002", "R-003"]
    assert all(o.get("LAST-CHANGE") == STAMP for o in objects)
    first = objects[0]
    assert first.find("r:TYPE/r:SPEC-OBJECT-TYPE-REF", NS).text == "rs-sot-requirement"
    values = {v.find("r:DEFINITION/r:ATTRIBUTE-DEFINITION-STRING-REF", NS).text: v.get("THE-VALUE")
              for v in first.findall("r:VALUES/r:ATTRIBUTE-VALUE-STRING", NS)}
    assert values["rs-ad-ID"] == "R-001" and values["rs-ad-Title"] == "Earn points"
    third_refs = [v.find("r:DEFINITION/r:ATTRIBUTE-DEFINITION-STRING-REF", NS).text
                  for v in objects[2].findall("r:VALUES/r:ATTRIBUTE-VALUE-STRING", NS)]
    assert "rs-ad-Title" not in third_refs  # empty cells are not written
    spec = content.find("r:SPECIFICATIONS/r:SPECIFICATION", NS)
    assert spec.find("r:TYPE/r:SPECIFICATION-TYPE-REF", NS).text == "rs-st-specification"
    refs = [h.find("r:OBJECT/r:SPEC-OBJECT-REF", NS).text for h in spec.findall("r:CHILDREN/r:SPEC-HIERARCHY", NS)]
    assert refs == ["R-001", "R-002", "R-003"]
    identifiers = [e.get("IDENTIFIER") for e in root.iter() if e.get("IDENTIFIER")]
    assert len(identifiers) == len(set(identifiers))


def test_export_skips_retired_rows_and_refuses_non_ncname_ids(register, capsys):
    root = ET.parse(_export(register, capsys)).getroot()
    assert "R-004" not in [o.get("IDENTIFIER") for o in root.iter("{%s}SPEC-OBJECT" % NS["r"])]
    named = ET.parse(_export(register, capsys, "--ids", "R-004")).getroot()
    assert [o.get("IDENTIFIER") for o in named.iter("{%s}SPEC-OBJECT" % NS["r"])] == ["R-004"]
    register.schema({"ids": {"requirement": {"prefix": "9-", "digits": 3}}})
    register.register([make_row("9-001")], header=HEADER)
    result = run_cli(reqif_io, ["export", "--out", str(register.root / "x.reqif")], capsys)
    assert result.code == 2 and "NCName" in result.err


def test_export_is_deterministic_and_selectable(register, capsys):
    first = _export(register, capsys).read_bytes()
    assert _export(register, capsys).read_bytes() == first
    subset = ET.parse(_export(register, capsys, "--ids", "R-003,R-001", "--title", "Tender")).getroot()
    assert [o.get("IDENTIFIER") for o in subset.iter("{%s}SPEC-OBJECT" % NS["r"])] == ["R-001", "R-003"]
    assert subset.find("r:THE-HEADER/r:REQ-IF-HEADER/r:TITLE", NS).text == "Tender"
    assert run_cli(reqif_io, ["export", "--ids", "R-404"], capsys).code == 2
    assert run_cli(reqif_io, ["export", "--timestamp", "yesterday"], capsys).code == 2
    default = run_cli(reqif_io, ["export"], capsys)
    assert default.code == 0 and (register.ws / "exports" / "requirements.reqif").is_file()
    stdout = run_cli(reqif_io, ["export", "--out", "-", "--timestamp", "2026-11-03"], capsys)
    assert stdout.out.startswith('<?xml version="1.0" encoding="UTF-8"?>') and "2026-11-03T00:00:00Z" in stdout.out


def _default_export(ws, capsys):
    result = run_cli(reqif_io, ["export", "--timestamp", STAMP], capsys)
    assert result.code == 0 and "agreed 1, draft 2" in result.out
    return ws.ws / "exports" / "requirements.reqif"


def _csv_rows(ws):
    return list(csv.DictReader(io.StringIO((ws.ws / "requirements.csv").read_text(encoding="utf-8"))))


def test_round_trip_has_no_changes(register, capsys):
    out = _default_export(register, capsys)
    result = run_cli(reqif_io, ["import", str(out), "--format", "json"], capsys)
    assert result.code == 0, result.out
    diff = result.json()
    assert diff["changes"] == [] and diff["counts"]["unchanged"] == 3
    assert [r["id"] for r in diff["readonly"]] == ["R-004"] and diff["readonly"][0]["class"] == "not exported"
    before = (register.ws / "requirements.csv").read_bytes()
    applied = run_cli(reqif_io, ["import", str(out), "--apply"], capsys)
    assert applied.code == 0 and "nothing to apply" in applied.out
    assert (register.ws / "requirements.csv").read_bytes() == before


def _edit(path, old, new):
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def _vendor_copy(ws, source, edits=(), drop=(), add=()):
    """A copy of an export as a vendor would send it back: edited values, dropped and added objects."""
    target = ws.root / "vendor.reqif"
    text = source.read_text(encoding="utf-8")
    for old, new in edits:
        assert old in text, old
        text = text.replace(old, new)
    root = ET.fromstring(text)
    objects = root.find("r:CORE-CONTENT/r:REQ-IF-CONTENT/r:SPEC-OBJECTS", NS)
    for obj in list(objects):
        if obj.get("IDENTIFIER") in drop:
            objects.remove(obj)
    template = objects.findall("r:SPEC-OBJECT", NS)[0]
    for identifier, rid, value in add:
        clone = ET.fromstring(ET.tostring(template))
        clone.set("IDENTIFIER", identifier)
        for av in list(clone.iter("{%s}ATTRIBUTE-VALUE-STRING" % NS["r"])):
            ref = av.find("r:DEFINITION/r:ATTRIBUTE-DEFINITION-STRING-REF", NS).text
            if ref == "rs-ad-ID":
                av.set("THE-VALUE", rid)
            elif ref == "rs-ad-Text":
                av.set("THE-VALUE", value)
        if not rid:
            values = clone.find("r:VALUES", NS)
            for av in list(values):
                if av.find("r:DEFINITION/r:ATTRIBUTE-DEFINITION-STRING-REF", NS).text in ("rs-ad-ID", "rs-ad-Rationale"):
                    values.remove(av)
        objects.append(clone)
    ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
    return target


def test_import_classes_and_apply_never_delete(register, capsys):
    out = _default_export(register, capsys)
    vendor = _vendor_copy(register, out, edits=[('THE-VALUE="Earn points"', 'THE-VALUE="Earn loyalty points"')],
                          drop=["R-003"],
                          add=[("R-050", "R-050", "The vendor portal shall export the register."),
                               ("_vendor-7", "", "The loyalty service shall log each validation request.")])
    result = run_cli(reqif_io, ["import", str(vendor), "--format", "json"], capsys)
    assert result.code == 1  # differences found
    diff = result.json()
    found = [(c["class"], c["id"]) for c in diff["changes"]]
    assert found == [("changed-attribute", "R-001"), ("new-object", "R-050"), ("new-object", "_vendor-7"),
                     ("missing-object", "R-003")]
    assert diff["counts"]["unchanged"] == 1  # R-002
    md = run_cli(reqif_io, ["import", str(vendor)], capsys).out
    assert md.startswith("# ReqIF import diff: vendor.reqif")
    for heading in ("## Summary", "## Changes to decide", "## Read only (not imported)", "## Next"):
        assert heading in md
    assert "| changed-attribute | 1 |" in md and "| new-object | 2 |" in md and "| missing-object | 1 |" in md
    assert "If accepted: new row R-005" in md  # next free ID after R-004 (withdrawn IDs are never reused)
    applied = run_cli(reqif_io, ["import", str(vendor), "--apply"], capsys)
    assert applied.code == 0 and "1 cell change(s), 2 row(s) added, no row deleted" in applied.out
    rows = _csv_rows(register)
    assert [r["ID"] for r in rows] == ["R-001", "R-002", "R-003", "R-004", "R-050", "R-005"]
    assert rows[0]["Title"] == "Earn loyalty points" and rows[0]["Status"] == "agreed"  # not a text change
    new = rows[5]
    assert (new["Status"], new["Source"], new["Rationale"]) == ("draft", "reqif:vendor.reqif#_vendor-7", "TBD")
    assert rows[1]["Text"].endswith("Second line.") and "ünïcödé" in rows[1]["Rationale"]


def test_invalid_enum_values_are_never_applied_without_override(register, capsys):
    out = _default_export(register, capsys)
    vendor = _vendor_copy(register, out, edits=[('THE-VALUE="agreed"', 'THE-VALUE="Accepted"'),
                                                ('THE-VALUE="F"', 'THE-VALUE="TBD"')])
    diff = run_cli(reqif_io, ["import", str(vendor), "--format", "json"], capsys).json()
    classes = {(c["id"], c["column"]): c["class"] for c in diff["changes"]}
    assert classes[("R-001", "Status")] == "invalid-value"
    assert classes[("R-001", "Type")] == "changed-attribute"  # TBD is a valid placeholder
    held = run_cli(reqif_io, ["import", str(vendor), "--apply"], capsys)
    assert held.code == 0 and "held back: R-001 Status='Accepted'" in held.out
    assert _csv_rows(register)[0]["Status"] == "agreed"
    forced = run_cli(reqif_io, ["import", str(vendor), "--apply", "--allow-invalid"], capsys)
    assert forced.code == 0 and _csv_rows(register)[0]["Status"] == "Accepted"


def test_text_change_on_agreed_rows_follows_the_lifecycle(workspace, capsys):
    header = HEADER + ["Version", "Links"]
    workspace.register([
        make_row("R-001", Status="agreed", Version=""),
        make_row("R-002", Status="implemented", Version="3", Links="RDR-001"),
        make_row("R-003", Status="draft", Version="1"),
    ], header=header)
    run_cli(reqif_io, ["export", "--timestamp", STAMP], capsys)
    out = workspace.ws / "exports" / "requirements.reqif"
    changed = make_row()["Text"].replace("pending", "posted")
    vendor = _vendor_copy(workspace, out, edits=[(make_row()["Text"].replace("&", "&amp;"), changed)])
    diff = run_cli(reqif_io, ["import", str(vendor), "--format", "json"], capsys).json()
    assert [(c["id"], c["class"]) for c in diff["changes"]] == [("R-001", "changed-text"), ("R-002", "changed-text"),
                                                                ("R-003", "changed-text")]
    assert run_cli(reqif_io, ["import", str(vendor), "--apply"], capsys).code == 0
    rows = {r["ID"]: r for r in _csv_rows(workspace)}
    assert (rows["R-001"]["Status"], rows["R-001"]["Version"]) == ("proposed", "2")  # empty Version counts as 1
    assert (rows["R-002"]["Status"], rows["R-002"]["Version"]) == ("proposed", "4")
    assert (rows["R-003"]["Status"], rows["R-003"]["Version"]) == ("draft", "2")
    assert all(r["Text"] == changed for r in rows.values())


def test_change_request_keeps_agreed_and_is_recorded(workspace, capsys):
    workspace.register([make_row("R-001", Status="agreed", Version="1", Links="RDR-001"),
                        make_row("R-002", Status="verified", Version="2", Links="")],
                       header=HEADER + ["Version", "Links"])
    run_cli(reqif_io, ["export", "--timestamp", STAMP], capsys)
    changed = make_row()["Text"].replace("pending", "posted")
    vendor = _vendor_copy(workspace, workspace.ws / "exports" / "requirements.reqif",
                          edits=[(make_row()["Text"], changed)])
    assert run_cli(reqif_io, ["import", str(vendor), "--apply", "--cr", "nope"], capsys).code == 2
    result = run_cli(reqif_io, ["import", str(vendor), "--apply", "--cr", "CR-014"], capsys)
    assert result.code == 0, result.out
    rows = {r["ID"]: r for r in _csv_rows(workspace)}
    assert (rows["R-001"]["Status"], rows["R-001"]["Version"], rows["R-001"]["Links"]) == ("agreed", "2", "RDR-001 CR-014")
    assert (rows["R-002"]["Status"], rows["R-002"]["Links"]) == ("agreed", "CR-014")  # verified goes back to agreed


VENDOR = """<?xml version="1.0" encoding="UTF-8"?>
<REQ-IF xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <THE-HEADER><REQ-IF-HEADER IDENTIFIER="h"><CREATION-TIME>2026-11-01T00:00:00Z</CREATION-TIME>
    <REQ-IF-TOOL-ID>Polarion</REQ-IF-TOOL-ID><REQ-IF-VERSION>1.0</REQ-IF-VERSION>
    <SOURCE-TOOL-ID>Polarion</SOURCE-TOOL-ID><TITLE>Vendor</TITLE></REQ-IF-HEADER></THE-HEADER>
  <CORE-CONTENT><REQ-IF-CONTENT>
    <DATATYPES>
      <DATATYPE-DEFINITION-XHTML IDENTIFIER="dx" LAST-CHANGE="2026-11-01T00:00:00Z"/>
      <DATATYPE-DEFINITION-STRING IDENTIFIER="ds" LAST-CHANGE="2026-11-01T00:00:00Z" MAX-LENGTH="255"/>
      <DATATYPE-DEFINITION-ENUMERATION IDENTIFIER="de" LAST-CHANGE="2026-11-01T00:00:00Z">
        <SPECIFIED-VALUES>
          <ENUM-VALUE IDENTIFIER="ev-must" LAST-CHANGE="2026-11-01T00:00:00Z" LONG-NAME="must"/>
          <ENUM-VALUE IDENTIFIER="ev-should" LAST-CHANGE="2026-11-01T00:00:00Z" LONG-NAME="should"/>
        </SPECIFIED-VALUES>
      </DATATYPE-DEFINITION-ENUMERATION>
    </DATATYPES>
    <SPEC-TYPES><SPEC-OBJECT-TYPE IDENTIFIER="t" LAST-CHANGE="2026-11-01T00:00:00Z"><SPEC-ATTRIBUTES>
      <ATTRIBUTE-DEFINITION-STRING IDENTIFIER="a-id" LAST-CHANGE="2026-11-01T00:00:00Z" LONG-NAME="ReqIF.ForeignID"/>
      <ATTRIBUTE-DEFINITION-XHTML IDENTIFIER="a-text" LAST-CHANGE="2026-11-01T00:00:00Z" LONG-NAME="ReqIF.Text"/>
      <ATTRIBUTE-DEFINITION-ENUMERATION IDENTIFIER="a-prio" LAST-CHANGE="2026-11-01T00:00:00Z" LONG-NAME="priority"/>
      <ATTRIBUTE-DEFINITION-STRING IDENTIFIER="a-note" LAST-CHANGE="2026-11-01T00:00:00Z" LONG-NAME="Vendor comment"/>
    </SPEC-ATTRIBUTES></SPEC-OBJECT-TYPE></SPEC-TYPES>
    <SPEC-OBJECTS>
      <SPEC-OBJECT IDENTIFIER="_poly-1" LAST-CHANGE="2026-11-01T00:00:00Z"><TYPE><SPEC-OBJECT-TYPE-REF>t</SPEC-OBJECT-TYPE-REF></TYPE>
        <VALUES>
          <ATTRIBUTE-VALUE-STRING THE-VALUE="R-001"><DEFINITION><ATTRIBUTE-DEFINITION-STRING-REF>a-id</ATTRIBUTE-DEFINITION-STRING-REF></DEFINITION></ATTRIBUTE-VALUE-STRING>
          <ATTRIBUTE-VALUE-XHTML><DEFINITION><ATTRIBUTE-DEFINITION-XHTML-REF>a-text</ATTRIBUTE-DEFINITION-XHTML-REF></DEFINITION>
            <THE-VALUE><xhtml:div><xhtml:p>WHEN the POS sends a <xhtml:b>completed</xhtml:b> purchase event,</xhtml:p><xhtml:p>the loyalty service shall create a pending points transaction.</xhtml:p></xhtml:div></THE-VALUE>
          </ATTRIBUTE-VALUE-XHTML>
          <ATTRIBUTE-VALUE-ENUMERATION><DEFINITION><ATTRIBUTE-DEFINITION-ENUMERATION-REF>a-prio</ATTRIBUTE-DEFINITION-ENUMERATION-REF></DEFINITION>
            <VALUES><ENUM-VALUE-REF>ev-should</ENUM-VALUE-REF></VALUES></ATTRIBUTE-VALUE-ENUMERATION>
          <ATTRIBUTE-VALUE-STRING THE-VALUE="Please confirm"><DEFINITION><ATTRIBUTE-DEFINITION-STRING-REF>a-note</ATTRIBUTE-DEFINITION-STRING-REF></DEFINITION></ATTRIBUTE-VALUE-STRING>
        </VALUES></SPEC-OBJECT>
      <SPEC-OBJECT IDENTIFIER="_heading" LAST-CHANGE="2026-11-01T00:00:00Z"><TYPE><SPEC-OBJECT-TYPE-REF>t</SPEC-OBJECT-TYPE-REF></TYPE>
        <VALUES><ATTRIBUTE-VALUE-STRING THE-VALUE="Chapter 1"><DEFINITION><ATTRIBUTE-DEFINITION-STRING-REF>a-note</ATTRIBUTE-DEFINITION-STRING-REF></DEFINITION></ATTRIBUTE-VALUE-STRING></VALUES>
      </SPEC-OBJECT>
    </SPEC-OBJECTS>
  </REQ-IF-CONTENT></CORE-CONTENT>
</REQ-IF>
"""


def test_import_vendor_file_with_xhtml_enumeration_and_standard_names(register, capsys):
    path = register.root / "vendor.reqif"
    path.write_text(VENDOR, encoding="utf-8")
    result = run_cli(reqif_io, ["import", str(path), "--format", "json"], capsys)
    assert result.code == 1
    diff = result.json()
    assert diff["unmapped"] == ["Vendor comment"]
    readonly = {(r["id"], r["class"]) for r in diff["readonly"]}
    assert {("R-001", "unmapped-attribute"), ("R-001", "xhtml-flattened"), ("_heading", "skipped")} <= readonly
    changes = [(c["id"], c["class"], c.get("column"), c.get("new")) for c in diff["changes"]]
    assert ("R-001", "changed-attribute", "Priority", "should") in changes  # XHTML text equals the register
    assert {c[0] for c in changes if c[1] == "missing-object"} == {"R-002", "R-003", "R-004"}  # no export to compare
    run_cli(reqif_io, ["import", str(path), "--apply", "--add-columns"], capsys)
    rows = _csv_rows(register)
    assert list(rows[0])[-1] == "Vendor comment" and rows[0]["Vendor comment"] == "Please confirm"
    assert rows[0]["Priority"] == "should" and rows[0]["Title"] == "Earn points"  # Title not defined: untouched
    assert len(rows) == 4


def test_reqifz_archive(register, capsys):
    out = _default_export(register, capsys)
    archive = register.root / "bundle.reqifz"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.write(out, "requirements.reqif")
    result = run_cli(reqif_io, ["import", str(archive), "--format", "json"], capsys)
    assert result.code == 0 and result.json()["counts"]["unchanged"] == 3


@pytest.mark.parametrize("content, message", [
    ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x "y">]><REQ-IF/>', "<!DOCTYPE"),
    ('<?xml version="1.0"?><!DOCTYPE REQ-IF><REQ-IF/>', "<!DOCTYPE"),
    ("<REQ-IF><broken></REQ-IF>", "not well-formed"),
    ("<SPEC/>", "not a ReqIF document"),
    ('<REQ-IF xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"/>', "no SPEC-OBJECT found"),
])
def test_bad_imports_exit_2(register, capsys, content, message):
    path = register.root / "bad.reqif"
    path.write_text(content, encoding="utf-8")
    result = run_cli(reqif_io, ["import", str(path)], capsys)
    assert result.code == 2 and message in result.err
    assert run_cli(reqif_io, ["import", str(register.root / "missing.reqif")], capsys).code == 2


def test_xhtml_flattening():
    element = ET.fromstring('<v xmlns:x="http://www.w3.org/1999/xhtml"><x:div>A<x:br/>B <x:ul><x:li>c</x:li>'
                            '<x:li>d</x:li></x:ul>  e</x:div></v>')
    assert reqif_io._flatten_xhtml(element) == "A B c d e"


def test_runs_standalone_next_to_reqio(tmp_path):
    shutil.copy(SRC / "re_lint" / "reqio.py", tmp_path / "reqio.py")
    shutil.copy(SRC / "re_lint" / "reqif_io.py", tmp_path / "reqif_bridge.py")
    proc = subprocess.run([sys.executable, str(tmp_path / "reqif_bridge.py"), "--help"], cwd=tmp_path,
                          capture_output=True, text=True)
    assert proc.returncode == 0 and "export" in proc.stdout, proc.stderr
