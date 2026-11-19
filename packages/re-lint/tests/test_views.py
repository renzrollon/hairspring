from __future__ import annotations

import csv
import io
import shutil
import subprocess
import sys

import pytest

from relint_helpers import SRC, make_row, run_cli
from re_lint import views

HEADER = ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale", "Title", "Verification", "Tags", "Owner"]


@pytest.fixture
def register(workspace):
    workspace.register([
        make_row("R-001", Status="agreed", Title="Earn points", Verification="test", Tags="earning"),
        make_row("R-002", text="The app shall show the balance.", Status="draft", Priority="could"),
        make_row("R-080", text="The service shall post points within 2 seconds.", Type="Q", Status="agreed",
                 Priority="should", Tags="performance security"),
        make_row("R-081", text="The service shall encrypt tokens.", Type="Q", Status="proposed", Verification="TBD",
                 Tags="security", Owner="SH-05"),
        make_row("R-100", text="The service shall run on the Kubernetes platform.", Type="C", Status="draft",
                 Verification="inspection"),
        make_row("R-019", text="The POS shall print vouchers.", Status="withdrawn"),
    ], header=HEADER)
    workspace.write("requirements/stories/redeem.md", (
        "# Stories\n\n| ID | Title | Status | Priority |\n| --- | --- | --- | --- |\n"
        "| R-040 | Spend points at the till | draft | must |\n"
        "| R-001 | duplicate of the register row | draft | must |\n"
    ))
    return workspace


def _table(md: str, heading: str = "## Requirements"):
    section = md.split(heading, 1)[1].strip().splitlines()
    rows = [line for line in section if line.startswith("|")]
    return [[c.strip() for c in line.strip("|").split("|")] for line in rows[2:]]


def test_builtin_views_are_written(register, capsys):
    result = run_cli(views, [], capsys)
    assert result.code == 0, result.err
    for name in ("po", "architect", "qa"):
        assert (register.ws / "views" / f"{name}.md").is_file()
    po = (register.ws / "views" / "po.md").read_text(encoding="utf-8")
    assert po.startswith("# Product owner view")
    assert _table(po)[0] == ["R-001", "Earn points", "agreed", "must"]          # Title wins
    assert ["R-002", "The app shall show the balance.", "draft", "could"] in _table(po)  # Text fallback
    assert ["R-040", "Spend points at the till", "draft", "must"] in _table(po)  # story row, no Type
    assert "| draft | 2 |" in po and "| withdrawn | 1 |" in po  # aggregating counts by Status
    architect = (register.ws / "views" / "architect.md").read_text(encoding="utf-8")
    assert [r[0] for r in _table(architect)] == ["R-080", "R-081"]
    assert "| Q | 2 |" in architect
    qa = (register.ws / "views" / "qa.md").read_text(encoding="utf-8")
    assert [r[0] for r in _table(qa)] == ["R-002", "R-040", "R-080", "R-081"]  # TBD counts as empty, R-019 excluded


def test_custom_view_filters_columns_grouping_and_sort(register, capsys):
    register.schema({"views": {
        "security": {
            "title": "Security-relevant requirements",
            "filter": {"Tags": {"has": "security"}, "Status": {"not": ["withdrawn"]}, "Text": {"contains": "SHALL"}},
            "columns": ["ID", "Title|Text", "Owner|Source", "Status"],
            "group_by": ["Type", "Status"],
            "sort_by": "Priority",
        },
        "unverified-drafts": {"filter": {"Status": "draft", "Verification": {"empty": False}}},
    }})
    result = run_cli(views, ["--view", "security", "unverified-drafts", "--stdout"], capsys)
    assert result.code == 0, result.err
    security, drafts = result.out.split("# View: unverified-drafts")
    assert security.startswith("# Security-relevant requirements")
    assert _table(security) == [  # sorted by Priority in schema enum order: must before should
        ["R-081", "The service shall encrypt tokens.", "SH-05", "proposed"],
        ["R-080", "The service shall post points within 2 seconds.", "S-01", "agreed"],
    ]
    assert "| Type | Status | Count |" in security and "| Q | agreed | 1 |" in security
    assert "Filter: Tags has security; Status not in withdrawn; Text contains SHALL" in security
    assert [r[0] for r in _table(drafts)] == ["R-100"]
    header = [line for line in drafts.splitlines() if line.startswith("| ID")][0]
    assert header.startswith("| ID | Type | Text | Source")  # default: every register column


def test_custom_view_replaces_builtin(register, capsys):
    register.schema({"views": {"qa": {"title": "QA (team)", "filter": {"Type": "C"}, "columns": ["ID"]}}})
    run_cli(views, ["--view", "qa"], capsys)
    qa = (register.ws / "views" / "qa.md").read_text(encoding="utf-8")
    assert qa.startswith("# QA (team)") and _table(qa) == [["R-100"]]
    listing = run_cli(views, ["--list"], capsys).out
    assert "qa           custom" in listing and "po           built-in" in listing


@pytest.mark.parametrize("definition, message", [
    ({"filter": []}, "'filter' must be an object"),
    ({"filter": {"Type": {"in": ["Q"]}}}, "conditions are a value list"),
    ({"filter": {"Type": {"empty": "yes"}}}, "'empty' must be true or false"),
    ({"columns": "ID"}, "'columns' must be a non-empty list"),
    ({"group_by": 3}, "'group_by' must be a column name"),
    ({"sorted": "ID"}, "unknown key(s) sorted"),
])
def test_invalid_view_definitions(register, capsys, definition, message):
    register.schema({"views": {"bad": definition}})
    result = run_cli(views, ["--view", "bad"], capsys)
    assert result.code == 2 and message in result.err


def test_unknown_view_and_bad_names(register, capsys):
    result = run_cli(views, ["--view", "nope"], capsys)
    assert result.code == 2 and "available: po, architect, qa" in result.err
    register.schema({"views": {"../x": {}}})
    assert run_cli(views, [], capsys).code == 2


def test_csv_format_and_out_dir(register, capsys):
    out = register.root / "out"
    result = run_cli(views, ["--view", "architect", "--format", "csv", "--out", str(out)], capsys)
    assert result.code == 0
    rows = list(csv.reader(io.StringIO((out / "architect.csv").read_text(encoding="utf-8"))))
    assert rows[0] == ["ID", "Type", "Text", "Status", "Priority", "Rationale"]
    assert [r[0] for r in rows[1:]] == ["R-080", "R-081"]
    printed = run_cli(views, ["--view", "po", "--format", "csv", "--stdout"], capsys).out
    assert printed.splitlines()[0] == "ID,Title,Status,Priority"


def test_typo_in_a_column_warns(register, capsys):
    register.schema({"views": {"x": {"filter": {"Stauts": "agreed"}}}})
    result = run_cli(views, ["--view", "x", "--stdout"], capsys)
    assert result.code == 0 and "Stauts" in result.err and "None." in result.out


def test_empty_workspace_is_a_usage_error(workspace, capsys):
    assert run_cli(views, [], capsys).code == 2


def test_runs_standalone_next_to_reqio(tmp_path):
    shutil.copy(SRC / "re_lint" / "reqio.py", tmp_path / "reqio.py")
    shutil.copy(SRC / "re_lint" / "views.py", tmp_path / "views.py")
    proc = subprocess.run([sys.executable, str(tmp_path / "views.py"), "--help"], cwd=tmp_path,
                          capture_output=True, text=True)
    assert proc.returncode == 0 and '"views"' in proc.stdout and "group_by" in proc.stdout, proc.stderr
