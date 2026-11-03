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


def test_round_trip_has_no_changes(register, capsys):
    out = _export(register, capsys)
    result = run_cli(reqif_io, ["import", str(out), "--format", "json"], capsys)
    assert result.code == 0, result.err
    diff = result.json()
    assert (diff["added"], diff["changed"], diff["missing"], diff["unchanged"]) == ([], [], [], 3)
    before = (register.ws / "requirements.csv").read_bytes()
    applied = run_cli(reqif_io, ["import", str(out), "--apply"], capsys)
    assert applied.code == 0 and "nothing to apply" in applied.out
    assert (register.ws / "requirements.csv").read_bytes() == before


def _edit(path, old, new):
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def test_import_diff_and_apply_never_delete(register, capsys):
    out = _export(register, capsys)
    _edit(out, 'THE-VALUE="Earn points"', 'THE-VALUE="Earn loyalty points"')
    _edit(out, 'THE-VALUE="draft"', 'THE-VALUE="proposed"')
    root = ET.parse(out).getroot()
    objects = root.find("r:CORE-CONTENT/r:REQ-IF-CONTENT/r:SPEC-OBJECTS", NS)
    gone = objects.findall("r:SPEC-OBJECT", NS)[2]
    objects.remove(gone)  # R-003 missing from the vendor's file
    clone = ET.fromstring(ET.tostring(objects.findall("r:SPEC-OBJECT", NS)[0]))
    clone.set("IDENTIFIER", "R-050")
    for value in clone.iter("{%s}ATTRIBUTE-VALUE-STRING" % NS["r"]):
        ref = value.find("r:DEFINITION/r:ATTRIBUTE-DEFINITION-STRING-REF", NS).text
        if ref == "rs-ad-ID":
            value.set("THE-VALUE", "R-050")
        if ref == "rs-ad-Text":
            value.set("THE-VALUE", "The vendor portal shall export the register.")
    objects.append(clone)
    ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)
    diff = run_cli(reqif_io, ["import", str(out), "--diff", "--format", "json"], capsys).json()
    assert [a["ID"] for a in diff["added"]] == ["R-050"]
    changed = {c["ID"]: {ch["column"]: (ch["old"], ch["new"]) for ch in c["changes"]} for c in diff["changed"]}
    assert changed == {"R-001": {"Title": ("Earn points", "Earn loyalty points")},
                       "R-002": {"Status": ("draft", "proposed")}}
    assert diff["missing"] == ["R-003"]
    text = run_cli(reqif_io, ["import", str(out)], capsys).out
    assert "+ R-050" in text and "~ R-001" in text and "? R-003  not in the import (kept" in text
    md = run_cli(reqif_io, ["import", str(out), "--format", "md"], capsys).out
    assert "| R-001 | Title | Earn points | Earn loyalty points |" in md
    applied = run_cli(reqif_io, ["import", str(out), "--apply"], capsys)
    assert applied.code == 0 and "2 changed, 1 added, no row deleted" in applied.out
    rows = list(csv.DictReader(io.StringIO((register.ws / "requirements.csv").read_text(encoding="utf-8"))))
    assert [r["ID"] for r in rows] == ["R-001", "R-002", "R-003", "R-050"]
    assert rows[0]["Title"] == "Earn loyalty points" and rows[1]["Status"] == "proposed"
    assert rows[1]["Text"].endswith("Second line.") and "ünïcödé" in rows[1]["Rationale"]
    assert rows[3]["Text"] == "The vendor portal shall export the register."


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
    diff = run_cli(reqif_io, ["import", str(path), "--format", "json"], capsys).json()
    assert diff["skipped_objects"] == 1 and diff["ignored_attributes"] == ["Vendor comment"]
    changes = {ch["column"]: ch["new"] for ch in diff["changed"][0]["changes"]}
    assert changes == {"Priority": "should"}  # XHTML text equals the register after whitespace normalization
    assert sorted(diff["missing"]) == ["R-002", "R-003"]
    run_cli(reqif_io, ["import", str(path), "--apply", "--add-columns"], capsys)
    rows = list(csv.DictReader(io.StringIO((register.ws / "requirements.csv").read_text(encoding="utf-8"))))
    assert list(rows[0])[-1] == "Vendor comment" and rows[0]["Vendor comment"] == "Please confirm"
    assert rows[0]["Priority"] == "should" and rows[0]["Title"] == "Earn points"  # Title not defined: untouched
    assert len(rows) == 3


def test_reqifz_archive(register, capsys):
    out = _export(register, capsys)
    archive = register.root / "bundle.reqifz"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.write(out, "requirements.reqif")
    result = run_cli(reqif_io, ["import", str(archive), "--format", "json"], capsys)
    assert result.code == 0 and result.json()["unchanged"] == 3


@pytest.mark.parametrize("content, message", [
    ('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x "y">]><REQ-IF/>', "entity declarations"),
    ("<REQ-IF><broken></REQ-IF>", "not well-formed"),
    ("<SPEC/>", "not a ReqIF document"),
    ('<REQ-IF xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"/>', "no SPEC-OBJECT"),
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
