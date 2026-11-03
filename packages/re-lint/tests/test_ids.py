from __future__ import annotations

import pytest

from relint_helpers import make_row, run_cli
from re_lint import ids


def ids_cli(argv, capsys):
    return run_cli(ids, argv, capsys)


def test_next_on_empty_workspace_starts_at_one(workspace, capsys):
    result = ids_cli(["next", "--no-git"], capsys)
    assert (result.code, result.out) == (0, "R-001\n")


def test_next_counts_withdrawn_and_mentions_anywhere_in_the_workspace(workspace, capsys):
    workspace.register([make_row("R-001"), make_row("R-007", Status="withdrawn")])
    workspace.write("requirements/decisions/RDR-001-x.md", "Supersedes R-012 (rejected).\n")
    result = ids_cli(["next", "--count", "3", "--no-git"], capsys)
    assert result.out.split() == ["R-013", "R-014", "R-015"]


def test_next_ignores_lookalike_prefixes(workspace, capsys):
    workspace.write("requirements/changes/CR-090-x.md", "CR-090 touches R-002; PR-50 merged.\n")
    assert ids_cli(["next", "--no-git"], capsys).out == "R-003\n"
    assert ids_cli(["next", "--kind", "change", "--no-git"], capsys).out == "CR-091\n"


def test_next_other_kinds_zero_pad(workspace, capsys):
    workspace.write("requirements/sources.csv", "ID,Name\nS-01,a\nS-09,b\n")
    assert ids_cli(["next", "--kind", "source", "--no-git"], capsys).out == "S-10\n"
    assert ids_cli(["next", "--kind", "stakeholder", "--no-git"], capsys).out == "SH-01\n"


def test_next_uses_schema_prefix_and_digits(workspace, capsys):
    workspace.schema({"ids": {"requirement": {"prefix": "REQ-", "digits": 4}}})
    workspace.register([make_row("REQ-0041")])
    assert ids_cli(["next", "--no-git"], capsys).out == "REQ-0042\n"


def test_next_scans_git_log_messages(workspace, capsys, git_available):
    workspace.register([make_row("R-001")])
    workspace.git("init", "-q", "-b", "main")
    workspace.git("add", ".")
    workspace.git("commit", "-q", "-m", "feat: export CSV (R-044)")
    assert ids_cli(["next"], capsys).out == "R-045\n"
    assert ids_cli(["next", "--no-git"], capsys).out == "R-002\n"


def test_next_with_explicit_workspace(tmp_path, capsys):
    ws = tmp_path / "elsewhere"
    ws.mkdir()
    (ws / "requirements.csv").write_text("ID\nR-020\n", encoding="utf-8")
    assert ids_cli(["next", "--workspace", str(ws), "--no-git"], capsys).out == "R-021\n"


def test_next_usage_errors(workspace, capsys):
    result = ids_cli(["next", "--kind", "bogus"], capsys)
    assert result.code == 2 and "unknown ID kind" in result.err
    assert ids_cli(["next", "--count", "0"], capsys).code == 2


def test_check_clean_and_findings(workspace, capsys):
    workspace.register([make_row("R-001"), make_row("R-002")])
    result = ids_cli(["check"], capsys)
    assert result.code == 0 and "no findings in 2 rows" in result.out
    workspace.register([make_row("R-001"), make_row("R-001"), make_row("R12"), make_row("R-003", Source="")])
    result = ids_cli(["check"], capsys)
    assert result.code == 1
    lines = result.out.splitlines()
    assert lines[0].startswith("requirements/requirements.csv:3: error duplicate-id R-001: R-001 is already defined at")
    assert any("invalid-id R12" in line for line in lines)
    assert any('missing-attribute R-003: required attribute "Source" is empty' in line for line in lines)


def test_check_tbd_counts_as_filled_and_header_columns(workspace, capsys):
    workspace.register([make_row(Priority="TBD")])
    assert ids_cli(["check"], capsys).code == 0
    workspace.register([make_row()], header=["ID", "Type", "Text"])
    result = ids_cli(["check", "--format", "json"], capsys)
    messages = [f["message"] for f in result.json()["findings"]]
    assert 'required column "Source" is missing from the header' in messages


def test_check_detects_kind_of_explicit_register(workspace, capsys):
    path = workspace.write("requirements/sources.csv", "ID,Name\nS-01,a\nS-01,b\nS-2,c\n")
    result = ids_cli(["check", str(path)], capsys)
    assert result.code == 1
    assert "duplicate-id S-01" in result.out and "invalid-id S-2" in result.out


def test_check_stakeholders_markdown_uses_first_table(workspace, capsys):
    workspace.write("requirements/stakeholders.md",
                    "| ID | Name |\n| --- | --- |\n| SH-01 | Mei |\n| SH-02 | Arjun |\n\n"
                    "## Quadrant\n\n| ID | Quadrant |\n| --- | --- |\n| SH-01 | manage closely |\n")
    assert ids_cli(["check"], capsys).code == 0


def test_check_decision_file_names(workspace, capsys):
    workspace.register([make_row()])
    workspace.write("requirements/decisions/RDR-001-points-expiry.md", "x")
    workspace.write("requirements/decisions/RDR-001-other.md", "y")
    result = ids_cli(["check", "--format", "github"], capsys)
    assert result.code == 1
    assert result.out.startswith("::error file=requirements/decisions/RDR-001-points-expiry.md,line=1,title=re-lint duplicate-id::RDR-001")


def test_check_usage_errors(workspace, capsys):
    assert ids_cli(["check"], capsys).code == 2  # nothing to check
    assert ids_cli(["check", "missing.csv"], capsys).code == 2
    path = workspace.write("requirements/notes.md", "# no tables\n")
    assert ids_cli(["check", str(path)], capsys).code == 2


def test_list(workspace, capsys):
    workspace.register([make_row("R-002"), make_row("R-010", Status="withdrawn")])
    workspace.write("requirements/stories/earn.md", "Covers R-002 and R-010.\n")
    result = ids_cli(["list", "--kind", "requirement"], capsys)
    assert result.out.splitlines() == [
        "R-002\trequirements/requirements.csv:2\t(+1 reference)",
        "R-010\trequirements/requirements.csv:3\t(+1 reference)",
    ]
    result = ids_cli(["list", "--kind", "requirement", "--all"], capsys)
    assert "R-002\trequirements/stories/earn.md:1" in result.out.splitlines()
    doc = ids_cli(["list", "--format", "json"], capsys).json()
    kinds = {(e["id"], e["kind"]) for e in doc}
    assert ("R-002", "requirement") in kinds and ("S-01", "source") in kinds


def test_parser_requires_an_action(capsys):
    with pytest.raises(SystemExit) as exc:
        ids.main([])
    assert exc.value.code == 2
