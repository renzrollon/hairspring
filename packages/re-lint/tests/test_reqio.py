from __future__ import annotations

import json
from pathlib import Path

import pytest

from re_lint import reqio


def test_csv_rows_keep_their_first_line_even_when_a_field_spans_lines(tmp_path):
    path = tmp_path / "requirements.csv"
    path.write_text('ID,Text\nR-001,"first\nsecond"\n\nR-002,plain\n', encoding="utf-8")
    table = reqio.read_table(path)
    assert [(r["ID"], r.line, r.end_line) for r in table] == [("R-001", 2, 3), ("R-002", 5, 5)]
    assert table.rows[0]["Text"] == "first\nsecond"
    assert table.rows[0].file == str(path)


def test_csv_bom_crlf_and_short_rows(tmp_path):
    path = tmp_path / "r.csv"
    path.write_bytes("﻿ID,Type,Text\r\nR-001,F\r\n".encode("utf-8"))
    table = reqio.read_table(path)
    assert table.columns == ["ID", "Type", "Text"]
    assert table.rows[0]["Text"] == "" and table.rows[0].line == 2


def test_empty_csv_has_no_columns(tmp_path):
    path = tmp_path / "r.csv"
    path.write_text("", encoding="utf-8")
    assert reqio.read_table(path).columns == []


def test_markdown_tables_with_code_spans_escaped_pipes_and_fences(tmp_path):
    path = tmp_path / "story.md"
    path.write_text(
        "# Stories\n\n"
        "```\n| ID | Text |\n| --- | --- |\n| R-999 | inside a fence |\n```\n\n"
        "| **ID** | Text |\n"
        "| :--- | ---: |\n"
        "| R-001 | uses `a|b` and a \\| pipe |\n"
        "| R-002 | second |\n\n"
        "| Name | Value |\n| --- | --- |\n| x | y |\n",
        encoding="utf-8")
    tables = reqio.read_tables(path)
    assert len(tables) == 2
    first = tables[0]
    assert first.columns == ["ID", "Text"] and first.header_line == 9
    assert [r["ID"] for r in first] == ["R-001", "R-002"]
    assert first.rows[0]["Text"] == "uses `a|b` and a | pipe"
    assert first.rows[0].line == 11
    assert reqio.read_table(path).columns == ["ID", "Text"]


def test_unsupported_suffix(tmp_path):
    path = tmp_path / "r.txt"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        reqio.read_tables(path)


def test_read_requirements_filters_by_id_pattern(tmp_path):
    path = tmp_path / "requirements.csv"
    path.write_text("ID,Text\nR-001,a\nREQ2,b\nS-01,c\n", encoding="utf-8")
    assert [r["ID"] for r in reqio.read_requirements([path])] == ["R-001"]


def test_load_schema_merges_over_defaults(tmp_path):
    (tmp_path / "schema.json").write_text(json.dumps({
        "ids": {"requirement": {"prefix": "REQ-", "digits": 4}},
        "lint": {"disable": ["nominalization"]},
    }), encoding="utf-8")
    schema = reqio.load_schema(workspace=tmp_path)
    assert schema["ids"]["requirement"] == {"prefix": "REQ-", "digits": 4}
    assert schema["ids"]["source"] == {"prefix": "S-", "digits": 2}
    assert schema["lint"]["disable"] == ["nominalization"]
    assert schema["lint"]["allow_words"] == []
    assert schema["_path"].endswith("schema.json")
    assert reqio.DEFAULT_SCHEMA["ids"]["requirement"]["prefix"] == "R-"  # defaults untouched


def test_load_schema_missing_file_and_bad_json(tmp_path):
    assert reqio.load_schema(path=tmp_path / "nope.json")["workspace"] == "requirements"
    bad = tmp_path / "schema.json"
    bad.write_text("{nope", encoding="utf-8")
    with pytest.raises(ValueError):
        reqio.load_schema(path=bad)
    bad.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        reqio.load_schema(path=bad)


def test_default_schema_matches_the_template_asset():
    asset = Path(__file__).resolve().parents[3] / "skills/_primitives/re-templates/assets/schema.json"
    if not asset.is_file():
        pytest.skip("template asset not present")
    assert json.loads(asset.read_text(encoding="utf-8")) == reqio.DEFAULT_SCHEMA


def test_find_workspace_honors_custom_workspace(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / "requirements").mkdir()
    (tmp_path / "requirements" / "schema.json").write_text('{"workspace": "reqs"}', encoding="utf-8")
    nested = tmp_path / "src" / "deep"
    nested.mkdir(parents=True)
    assert reqio.find_repo_root(nested) == tmp_path
    assert reqio.find_workspace(nested) == tmp_path / "reqs"


def test_id_helpers():
    pattern = reqio.id_regex("requirement")
    assert pattern.match("R-001") and pattern.match("R-1234")
    assert not pattern.match("R-01") and not pattern.match("REQ-001")
    finder = reqio.id_prefix_regex("requirement")
    assert [m.group(1) for m in finder.finditer("R-012, CR-013, PR-14, R-015.AC2, xR-016")] == ["012", "015"]
    assert reqio.format_id("source", 7) == "S-07"
    assert reqio.format_id("requirement", 1234) == "R-1234"
    assert reqio.parse_id_number("see R-041 here") == 41
    assert reqio.parse_id_number("nothing") is None
    custom = {"ids": {"requirement": {"pattern": r"^REQ-[A-Z]{2}-\d+$"}}}
    assert reqio.id_regex("requirement", custom).match("REQ-AB-1")
    with pytest.raises(KeyError):
        reqio.id_regex("bogus")


def test_id_in_text():
    found = reqio.ID_IN_TEXT.findall("feat: export (R-041); see R-012.AC2, not CR-013 or PR-12")
    assert found == ["R-041", "R-012"]


def test_write_csv_is_lf_minimal_quoting_trailing_newline(tmp_path):
    path = tmp_path / "out" / "requirements.csv"
    reqio.write_csv(path, [{"ID": "R-001", "Text": 'say "hi", then go'}, {"ID": "R-002"}], ["ID", "Text"])
    data = path.read_bytes()
    assert data == b'ID,Text\nR-001,"say ""hi"", then go"\nR-002,\n'


def test_ordered_columns():
    assert reqio.ordered_columns(["Tags", "ID", "Custom", "Owner"]) == (
        reqio.DEFAULT_SCHEMA["attributes"]["columns"] + ["Owner", "Tags", "Custom"])


def test_row_get_str():
    row = reqio.Row({"A": "  x ", "B": None}, file="f", line=3)
    assert row.get_str("A") == "x" and row.get_str("B") == "" and row.get_str("C") == ""
    assert (row.file, row.line, row.end_line) == ("f", 3, 3)
