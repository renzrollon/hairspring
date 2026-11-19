"""Tests for skills/elicitation/questionnaire-builder/scripts/analyze_responses.py."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[2] / "skills" / "elicitation" / "questionnaire-builder"
SCRIPT = SKILL / "scripts" / "analyze_responses.py"
EXAMPLES = SKILL / "examples"


def _load():
    spec = importlib.util.spec_from_file_location("analyze_responses", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ar = _load()

FORM_HEADER = "ID,Type,Title,HelpText,Required,Options,ScaleMin,ScaleMax,MinLabel,MaxLabel\n"
PLAN_HEADER = "Item,Hypothesis,Metric,Threshold,MinN,N,Missing,Distribution,Value,Result,Notes\n"


def _rows(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_asset_headers_match_script():
    assert (SKILL / "assets" / "form-import.csv").read_text(encoding="utf-8") == FORM_HEADER
    assert (SKILL / "assets" / "analysis.csv").read_text(encoding="utf-8") == PLAN_HEADER
    assert ",".join(ar.FORM_COLUMNS) + "\n" == FORM_HEADER
    assert ",".join(ar.ANALYSIS_COLUMNS) + "\n" == PLAN_HEADER


def test_example_reproduces_expected_results(tmp_path: Path):
    out = tmp_path / "analysis.csv"
    code = ar.main([
        "--items", str(EXAMPLES / "expected-output-form-import.csv"),
        "--analysis", str(EXAMPLES / "expected-output-analysis.csv"),
        "--responses", str(EXAMPLES / "responses.csv"),
        "--out", str(out),
    ])
    assert code == 0
    assert out.read_text(encoding="utf-8") == (EXAMPLES / "expected-output-analysis-results.csv").read_text(encoding="utf-8")


def test_example_values_by_hand():
    rows = {r["Item"]: r for r in _rows(EXAMPLES / "expected-output-analysis-results.csv")}
    assert rows["Q01"]["Value"] == "33.3%" and rows["Q01"]["Result"] == "supported"      # 16 of 48
    assert rows["Q02"]["N"] == "47" and rows["Q02"]["Missing"] == "1"
    assert rows["Q03"]["Result"] == "not supported"                                        # 26 of 48 < 60%
    assert rows["Q05"]["Result"] == "inconclusive" and "threshold not agreed" in rows["Q05"]["Notes"]
    assert rows["Q06"]["Result"] == "manual" and rows["Q06"]["N"] == "30"


@pytest.fixture()
def folder(tmp_path: Path) -> Path:
    (tmp_path / "form-import.csv").write_text(
        FORM_HEADER
        + "Q01,scale,How often does it fail?,,yes,,1,5,Never,Very often\n"
        + "Q02,multi,What do you do?,,no,Retry|Ask for card|Give up,,,,\n"
        + "Q03,single,Which store type?,,yes,Mall|Street,,,,\n"
        + "Q04,paragraph,Anything else?,,no,,,,,\n",
        encoding="utf-8",
    )
    (tmp_path / "responses.csv").write_text(
        "Timestamp,How often does it fail?,What do you do?,Which store type?,Anything else?\n"
        "t1,5,Retry;Give up,Mall,slow\n"
        "t2,4,\"Retry, Ask for card\",Mall,\n"
        "t3,2,Ask for card,Street,\n"
        "t4,,Give up,Mall,queue\n",
        encoding="utf-8",
    )
    return tmp_path


def _plan(folder: Path, rows: str) -> Path:
    path = folder / "analysis.csv"
    path.write_text(PLAN_HEADER + rows, encoding="utf-8")
    return path


def test_metrics_and_results(folder: Path):
    _plan(folder,
          "Q01,H1,top2,>=60%,3,,,,,,\n"
          "Q01,H1,median,>=4,2,,,,,,\n"
          "Q02,H2,share:Give up,>=0.5,3,,,,,,\n"
          "Q03,H3,share:Mall,>75%,4,,,,,,\n"
          "Q04,H4,themes,,,,,,,,\n")
    assert ar.main([str(folder), "--responses", str(folder / "responses.csv")]) == 0
    rows = _rows(folder / "analysis.csv")
    top2, median, share_multi, share_single, themes = rows
    assert (top2["N"], top2["Missing"], top2["Value"], top2["Result"]) == ("3", "1", "66.7%", "supported")
    assert top2["Distribution"] == "1=0; 2=1; 3=0; 4=1; 5=1"
    assert (median["Value"], median["Result"]) == ("4", "supported")
    assert share_multi["Value"] == "50.0%" and share_multi["Result"] == "supported"
    assert "Retry=2" in share_multi["Distribution"] and "Ask for card=2" in share_multi["Distribution"]
    assert share_single["Value"] == "75.0%" and share_single["Result"] == "not supported"
    assert themes["Result"] == "manual" and themes["N"] == "2"


def test_tbd_and_small_n_are_inconclusive(folder: Path):
    _plan(folder, "Q01,H1,top2,TBD,3,,,,,,\nQ01,H1,top2,>=50%,TBD,,,,,,\nQ01,H1,top2,>=50%,10,,,,,,\n")
    assert ar.main([str(folder), "--responses", str(folder / "responses.csv")]) == 0
    rows = _rows(folder / "analysis.csv")
    assert [r["Result"] for r in rows] == ["inconclusive"] * 3
    assert "threshold not agreed" in rows[0]["Notes"]
    assert "MinN not agreed" in rows[1]["Notes"]
    assert "N below MinN" in rows[2]["Notes"]


def test_findings_exit_1(folder: Path, capsys):
    _plan(folder,
          "Q09,H1,top2,>=50%,1,,,,,,\n"          # unknown item
          "Q01,H1,share:Retry,>=50%,1,,,,,,\n"   # not a scale point
          "Q02,H2,top2,>=50%,1,,,,,,\n"          # top2 on a multi item
          "Q01,H1,top2,>=60,1,,,,,,\n")          # share threshold without %
    assert ar.main([str(folder), "--responses", str(folder / "responses.csv"), "--format", "json"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert len(report["findings"]) == 4


def test_unmatched_column_is_a_finding(folder: Path):
    (folder / "responses.csv").write_text("Timestamp,Other question\nt1,3\n", encoding="utf-8")
    _plan(folder, "Q01,H1,top2,>=50%,1,,,,,,\n")
    assert ar.main([str(folder), "--responses", str(folder / "responses.csv")]) == 1
    assert _rows(folder / "analysis.csv")[0]["Notes"] == "response column not found"


def test_id_prefix_header_matches(folder: Path):
    (folder / "responses.csv").write_text("Timestamp,Q01. How often (renamed)?\nt1,5\nt2,1\n", encoding="utf-8")
    _plan(folder, "Q01,H1,top2,>=50%,2,,,,,,\n")
    assert ar.main([str(folder), "--responses", str(folder / "responses.csv")]) == 0
    assert _rows(folder / "analysis.csv")[0]["Result"] == "supported"


def test_usage_errors(tmp_path: Path):
    assert ar.main([str(tmp_path), "--responses", str(tmp_path / "missing.csv")]) == 2
    (tmp_path / "form-import.csv").write_text("ID,Title\n", encoding="utf-8")
    (tmp_path / "analysis.csv").write_text(PLAN_HEADER, encoding="utf-8")
    (tmp_path / "r.csv").write_text("a\n", encoding="utf-8")
    assert ar.main([str(tmp_path), "--responses", str(tmp_path / "r.csv")]) == 2
    with pytest.raises(SystemExit) as exc:
        ar.main(["--help"])
    assert exc.value.code == 0
