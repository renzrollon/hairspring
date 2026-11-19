"""Tests for skills/specification/spec-assembler/scripts/spec_tool.py."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "specification" / "spec-assembler"
SCRIPT = SKILL / "scripts" / "spec_tool.py"
EXAMPLE_WS = SKILL / "examples" / "input"
EXAMPLE_SPEC = SKILL / "examples" / "expected-output.md"


def _load():
    spec = importlib.util.spec_from_file_location("spec_tool", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


st = _load()

CSV = (
    "ID,Type,Text,Source,Priority,Status,Rationale\n"
    "R-001,F,The loyalty service shall record each points transaction.,S-02,must,agreed,Core.\n"
    "R-002,Q,The loyalty service shall answer within TBD ms.,SH-02,should,draft,Speed.\n"
    "R-003,F,The loyalty service shall send a push message.,S-06,could,withdrawn,Dropped.\n"
)

SPEC = """# Spec

- [3 Requirements](#3-requirements)

## 3 Requirements

#### R-001

The loyalty service shall record each points transaction.

Type F · Priority must · Status agreed · Source S-02

#### R-002

The loyalty service shall answer within TBD ms.

See [R-001](#r-001).
"""


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    req = tmp_path / "requirements"
    req.mkdir()
    (req / "requirements.csv").write_text(CSV, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _check(path: Path, capsys, *extra) -> tuple:
    code = st.main(["check", str(path), "--format", "json", *extra])
    return code, {f["rule"] for f in json.loads(capsys.readouterr().out)}


def test_example_spec_is_clean(monkeypatch, capsys):
    monkeypatch.chdir(EXAMPLE_WS)
    assert st.main(["check", str(EXAMPLE_SPEC)]) == 0
    assert "0 error(s), 0 warning(s); 10 requirement block(s)" in capsys.readouterr().out


def test_clean_spec(ws, capsys):
    spec = ws / "spec.md"
    spec.write_text(SPEC, encoding="utf-8")
    assert _check(spec, capsys) == (0, set())


def test_drift_missing_excluded_duplicate_links(ws, capsys):
    spec = ws / "spec.md"
    spec.write_text(SPEC.replace("within TBD ms", "within 2 s"), encoding="utf-8")
    assert "text-drift" in _check(spec, capsys)[1]
    spec.write_text(SPEC.split("#### R-002")[0], encoding="utf-8")
    assert "missing-requirement" in _check(spec, capsys)[1]
    spec.write_text(SPEC + "\n#### R-003\n\nThe loyalty service shall send a push message.\n", encoding="utf-8")
    assert "excluded-requirement" in _check(spec, capsys)[1]
    spec.write_text(SPEC + "\n#### R-001\n\nThe loyalty service shall record each points transaction.\n", encoding="utf-8")
    assert "duplicate-block" in _check(spec, capsys)[1]
    spec.write_text(SPEC + "\nSee [R-009](#r-009) and [x](#no-such-heading).\n", encoding="utf-8")
    code, rules = _check(spec, capsys)
    assert code == 1 and {"broken-link", "unknown-reference"} <= rules


def test_status_filter_and_id_column(ws, capsys):
    spec = ws / "spec.md"
    spec.write_text(SPEC.split("#### R-002")[0], encoding="utf-8")
    assert _check(spec, capsys, "--status-in", "agreed") == (0, set())
    spec.write_text(SPEC + "\n| ID | Note |\n| --- | --- |\n| R-001 | x |\n", encoding="utf-8")
    code, rules = _check(spec, capsys)
    assert code == 0 and "id-column" in rules
    assert st.main(["check", str(spec), "--fail-on", "warning"]) == 1


def test_links_inside_code_fences_are_ignored(ws, capsys):
    spec = ws / "spec.md"
    spec.write_text(SPEC + "\n```text\n[x](#nowhere)\n#### R-009\n```\n", encoding="utf-8")
    assert _check(spec, capsys) == (0, set())


def test_blocks_verbatim_and_criteria(monkeypatch, capsys):
    monkeypatch.chdir(EXAMPLE_WS)
    assert st.main(["blocks", "--ids", "R-040", "--stories", "requirements/stories"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("#### R-040\n\nAs a member, I want to spend 500 of my posted points")
    assert "Type F · Priority must · Status draft · Source S-06 (LOY-210)" in out
    assert "**R-040.AC2: Not enough posted points** _(unwanted behavior)_" in out
    assert "**Notes:**" not in out


def test_blocks_by_type_skips_excluded(ws, capsys):
    assert st.main(["blocks", "--type", "F"]) == 0
    out = capsys.readouterr().out
    assert "#### R-001" in out and "R-003" not in out and "R-002" not in out
    assert st.main(["blocks", "--ids", "R-404"]) == 2


def test_summary_counts(ws, capsys):
    assert st.main(["summary"]) == 0
    out = capsys.readouterr().out
    assert "| F (functional) | 0 | 1 | 1 |" in out
    assert "| Total | 1 | 1 | 2 |" in out
    assert "Excluded from this document: 1 (withdrawn: 1)." in out


def test_trace_fallback_and_matrix(ws, capsys):
    assert st.main(["trace"]) == 0
    out = capsys.readouterr().out
    assert "not found" in out and "| [R-001](#r-001) | S-02 | none |" in out
    trace = ws / "requirements" / "trace"
    trace.mkdir()
    (trace / "trace.csv").write_text(
        "From,FromType,To,ToType,Relation,Evidence\n"
        "S-02,source,R-001,requirement,derives,sources.csv\n"
        "R-001,requirement,tests/test_points.py::test_r_001,test,verifies,name\n",
        encoding="utf-8",
    )
    assert st.main(["trace"]) == 0
    out = capsys.readouterr().out
    assert "| [R-001](#r-001) | S-02 | none | none | `tests/test_points.py::test_r_001` | none |" in out


def test_usage_errors(tmp_path, monkeypatch, capsys):
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    assert st.main(["summary"]) == 2
    assert st.main(["check", "missing.md", "--requirements", "nope.csv"]) == 2
    with pytest.raises(SystemExit) as exc:
        st.main(["--help"])
    assert exc.value.code == 0
    with pytest.raises(SystemExit) as exc:
        st.main([])
    assert exc.value.code == 2


def test_example_workspace_copy_roundtrip(tmp_path, monkeypatch, capsys):
    """The example spec stays valid when the workspace is copied elsewhere."""
    shutil.copytree(EXAMPLE_WS, tmp_path / "ws")
    monkeypatch.chdir(tmp_path / "ws")
    assert st.main(["check", str(EXAMPLE_SPEC), "--requirements", "requirements/requirements.csv"]) == 0
