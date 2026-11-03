"""re-lint check: formats, exit codes, configuration, --only-ids, --changed-only, fixtures."""
from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest

from relint_helpers import REPO_ROOT, SRC, make_row, run_cli
from re_lint import lint

BAD = make_row("R-002", text="The app shall show the balance quickly.")
WARN = make_row("R-003", text="The POS shall always print a receipt.")
INFO = make_row("R-004", text="The app shall show the balance within TBD ms.")
FIXTURE = REPO_ROOT / "skills/specification/requirement-phrasing/examples/expected-output.csv"


def check(argv, capsys):
    return run_cli(lint, argv, capsys)


# ---------------------------------------------------------------- exit codes and --fail-on

def test_workspace_option_lints_a_nested_workspace(workspace, capsys):
    workspace.write("examples/demo/requirements/requirements.csv",
                    "ID,Type,Text,Source,Priority,Status,Rationale\n"
                    "R-001,F,The app shall show the balance quickly.,PO,must,draft,Why.\n")
    workspace.register([make_row()])  # the root workspace is clean
    assert check([], capsys).code == 0
    nested = check(["--workspace", str(workspace.root / "examples/demo/requirements")], capsys)
    assert nested.code == 1 and "weak-word" in nested.out
    missing = check(["--workspace", str(workspace.root / "nope")], capsys)
    assert missing.code == 2 and "--workspace" in missing.err


def test_clean_register_exits_0(workspace, capsys):
    workspace.register([make_row()])
    result = check([], capsys)
    assert result.code == 0
    assert result.out.strip() == "re-lint: no findings in 1 row (1 file)"


def test_error_exits_1(workspace, capsys):
    workspace.register([make_row(), BAD])
    assert check([], capsys).code == 1


@pytest.mark.parametrize("fail_on,rows,code", [
    ("error", [WARN, INFO], 0),
    ("warning", [WARN], 1),
    ("warning", [INFO], 0),
    ("info", [INFO], 1),
])
def test_fail_on_threshold(workspace, capsys, fail_on, rows, code):
    workspace.register(rows)
    assert check(["--fail-on", fail_on], capsys).code == code


def test_missing_register_is_usage_error(workspace, capsys):
    result = check([], capsys)
    assert result.code == 2 and "no requirement register found" in result.err


def test_missing_file_and_bad_suffix_are_usage_errors(workspace, capsys):
    assert check(["nope.csv"], capsys).code == 2
    workspace.write("notes.txt", "x")
    result = check(["notes.txt"], capsys)
    assert result.code == 2 and "unsupported file type" in result.err


def test_csv_without_id_column_is_a_usage_error(workspace, capsys):
    path = workspace.write("requirements/requirements.csv", "Name,Text\nx,y\n")
    result = check([str(path)], capsys)
    assert result.code == 2 and "no 'ID' column" in result.err


def test_invalid_schema_json_is_exit_2(workspace, capsys):
    workspace.register([make_row()])
    workspace.write("requirements/schema.json", "{broken")
    result = check([], capsys)
    assert result.code == 2 and "invalid JSON" in result.err


def test_unknown_rule_on_cli_is_exit_2(workspace, capsys):
    workspace.register([make_row()])
    result = check(["--disable", "weak-words"], capsys)
    assert result.code == 2 and "unknown rule" in result.err


def test_argparse_usage_error_exits_2(capsys):
    with pytest.raises(SystemExit) as exc:
        lint.main(["--format", "xml"])
    assert exc.value.code == 2


# ---------------------------------------------------------------- formats

def test_text_format(workspace, capsys):
    workspace.register([make_row(), BAD])
    out = check([], capsys).out.splitlines()
    assert out[0] == ('requirements/requirements.csv:3: error weak-word R-002: '
                      'weak word "quickly" has no measurable meaning')
    assert out[1] == "    hint: Replace with a measurable criterion or a reference to a defined term"
    assert out[-1] == "re-lint: 1 error, 0 warnings, 0 info in 2 rows (1 file)"


def test_json_format(workspace, capsys):
    workspace.register([BAD, INFO])
    doc = check(["--format", "json"], capsys).json()
    assert doc["summary"] == {"error": 1, "warning": 0, "info": 1}
    assert doc["rows_checked"] == 2 and doc["files"] == ["requirements/requirements.csv"]
    first = doc["findings"][0]
    assert set(first) == {"rule", "severity", "id", "file", "line", "column", "match", "message", "hint"}
    assert (first["rule"], first["id"], first["line"], first["match"]) == ("weak-word", "R-002", 2, "quickly")
    # column points at the word inside the raw CSV line
    line = (workspace.ws / "requirements.csv").read_text().splitlines()[1]
    assert line[first["column"] - 1:].startswith("quickly")


def test_github_format(workspace, capsys):
    workspace.register([BAD, WARN, INFO])
    lines = check(["--format", "github"], capsys).out.splitlines()
    assert lines[0] == ("::error file=requirements/requirements.csv,line=2,title=re-lint weak-word::"
                        'R-002: weak word "quickly" has no measurable meaning')
    assert lines[1].startswith("::warning file=requirements/requirements.csv,line=3,title=re-lint universal-quantifier::R-003: ")
    assert lines[2].startswith("::notice file=requirements/requirements.csv,line=4,title=re-lint open-tbd::R-004: ")


def test_github_escapes_properties_and_data():
    assert lint._gh_prop("a,b:c%") == "a%2Cb%3Ac%25"
    assert lint._gh_data("50%\nnext") == "50%25%0Anext"


def test_sarif_format_shape(workspace, capsys):
    workspace.register([BAD, WARN, INFO])
    doc = check(["--format", "sarif"], capsys).json()
    assert doc["version"] == "2.1.0" and doc["$schema"].endswith("sarif-2.1.0.json")
    run = doc["runs"][0]
    driver = run["tool"]["driver"]
    assert driver["name"] == "re-lint" and [r["id"] for r in driver["rules"]] == list(lint.RULES)
    for rule in driver["rules"]:
        assert rule["shortDescription"]["text"] and rule["help"]["text"]
        assert rule["defaultConfiguration"]["level"] in ("error", "warning", "note")
    levels = [r["level"] for r in run["results"]]
    assert levels == ["error", "warning", "note"]
    for result in run["results"]:
        assert driver["rules"][result["ruleIndex"]]["id"] == result["ruleId"]
        loc = result["locations"][0]["physicalLocation"]
        assert loc["artifactLocation"]["uri"] == "requirements/requirements.csv"
        assert loc["region"]["startLine"] >= 2 and loc["region"]["startColumn"] >= 1
        assert result["message"]["text"] and result["partialFingerprints"]
    assert run["results"][0]["properties"]["requirementId"] == "R-002"


def test_list_rules(capsys):
    result = check(["--list-rules"], capsys)
    assert result.code == 0 and all(rid in result.out for rid in lint.RULES)


# ---------------------------------------------------------------- configuration

def test_schema_disable_and_cli_enable(workspace, capsys):
    workspace.register([BAD])
    workspace.schema({"lint": {"disable": ["weak-word"]}})
    assert check([], capsys).code == 0
    assert check(["--enable", "weak-word"], capsys).code == 1


def test_cli_disable_comma_separated(workspace, capsys):
    workspace.register([BAD, WARN])
    result = check(["--disable", "weak-word,universal-quantifier", "--fail-on", "info"], capsys)
    assert result.code == 0


def test_schema_severity_override_and_off(workspace, capsys):
    workspace.register([WARN, INFO])
    workspace.schema({"lint": {"severity": {"universal-quantifier": "error", "open-tbd": "off"}}})
    doc = check(["--format", "json"], capsys).json()
    assert [(f["rule"], f["severity"]) for f in doc["findings"]] == [("universal-quantifier", "error")]


def test_schema_bad_severity_is_exit_2(workspace, capsys):
    workspace.register([WARN])
    workspace.schema({"lint": {"severity": {"universal-quantifier": "fatal"}}})
    assert check([], capsys).code == 2


def test_schema_unknown_rule_is_a_warning(workspace, capsys):
    workspace.register([make_row()])
    workspace.schema({"lint": {"disable": ["not-a-rule"]}})
    result = check([], capsys)
    assert result.code == 0 and "unknown rule 'not-a-rule'" in result.err


def test_extra_weak_words_and_allow_words(workspace, capsys):
    workspace.register([make_row(text="The app shall show a blazing balance for the Flexible Spending Account.")])
    workspace.schema({"lint": {"extra_weak_words": ["blazing"], "allow_words": ["Flexible Spending Account"]}})
    doc = check(["--format", "json"], capsys).json()
    assert [f["match"] for f in doc["findings"]] == ["blazing"]


def test_allow_word_removes_a_builtin_weak_word(workspace, capsys):
    workspace.register([make_row(text="The POS shall accept the Fast Lane card.")])
    workspace.schema({"lint": {"allow_words": ["fast"]}})
    assert check([], capsys).code == 0


def test_explicit_schema_flag(workspace, capsys, tmp_path):
    workspace.register([BAD])
    other = tmp_path / "strict.json"
    other.write_text(json.dumps({"lint": {"disable": ["weak-word"]}}), encoding="utf-8")
    assert check(["--schema", str(other)], capsys).code == 0
    assert check(["--schema", str(tmp_path / "missing.json")], capsys).code == 2


def test_custom_workspace_and_required_columns(workspace, capsys):
    workspace.schema({"workspace": "reqs", "attributes": {"required": ["ID", "Text", "Owner"]}})
    workspace.write("reqs/requirements.csv", "ID,Text,Owner\nR-001,The POS shall print a receipt.,\n")
    doc = check(["--format", "json"], capsys).json()
    assert [(f["rule"], f["match"], f["file"]) for f in doc["findings"]] == [
        ("missing-attribute", "Owner", "reqs/requirements.csv")]


# ---------------------------------------------------------------- TBD semantics

def test_tbd_blocks_only_with_fail_on_info(workspace, capsys):
    workspace.register([make_row(text="The app shall show the balance within TBD ms.", Priority="TBD")])
    assert check([], capsys).code == 0
    result = check(["--fail-on", "info", "--format", "json"], capsys)
    assert result.code == 1
    assert [f["rule"] for f in result.json()["findings"]] == ["open-tbd", "open-tbd"]


# ---------------------------------------------------------------- --only-ids

def test_only_ids(workspace, capsys):
    workspace.register([BAD, make_row("R-005", text="The app shall be fast.")])
    doc = check(["--only-ids", "R-005", "--format", "json"], capsys).json()
    assert {f["id"] for f in doc["findings"]} == {"R-005"}
    result = check(["--only-ids", "R-099"], capsys)
    assert result.code == 0 and "R-099 not found" in result.err


def test_only_ids_keeps_header_findings(workspace, capsys):
    workspace.register([make_row()], header=["ID", "Type", "Text", "Source", "Priority", "Status"])
    doc = check(["--only-ids", "R-001", "--format", "json"], capsys).json()
    assert [f["rule"] for f in doc["findings"]] == ["missing-attribute"]


# ---------------------------------------------------------------- --changed-only

def test_changed_only_reports_only_changed_rows(workspace, capsys, git_available):
    workspace.register([BAD, make_row("R-005", text="The app shall be fast.")])
    workspace.git("init", "-q", "-b", "main")
    workspace.git("add", ".")
    workspace.git("commit", "-q", "-m", "baseline")
    workspace.register([BAD, make_row("R-005", text="The app shall be fast."),
                        make_row("R-006", text="The app shall be easy.")])
    doc = check(["--changed-only", "main", "--format", "json"], capsys).json()
    assert [f["id"] for f in doc["findings"]] == ["R-006"]
    # a modified existing row counts too
    workspace.register([BAD, make_row("R-005", text="The app shall be robust.")])
    doc = check(["--changed-only", "main", "--format", "json"], capsys).json()
    assert [(f["id"], f["match"]) for f in doc["findings"]] == [("R-005", "robust")]


def test_changed_only_duplicate_reported_when_either_row_changed(workspace, capsys, git_available):
    workspace.register([make_row("R-001"), make_row("R-002")])
    workspace.git("init", "-q", "-b", "main")
    workspace.git("add", ".")
    workspace.git("commit", "-q", "-m", "baseline")
    workspace.register([make_row("R-002"), make_row("R-001"), make_row("R-002")])  # new first row
    doc = check(["--changed-only", "main", "--format", "json"], capsys).json()
    assert [f["rule"] for f in doc["findings"]] == ["duplicate-id"]


def test_changed_only_untracked_file_counts_as_changed(workspace, capsys, git_available):
    workspace.write("README.md", "x\n")
    workspace.git("init", "-q", "-b", "main")
    workspace.git("add", ".")
    workspace.git("commit", "-q", "-m", "init")
    workspace.register([BAD])
    doc = check(["--changed-only", "main", "--format", "json"], capsys).json()
    assert [f["id"] for f in doc["findings"]] == ["R-002"]


def test_changed_only_falls_back_without_git_repo(workspace, capsys):
    workspace.register([BAD])
    result = check(["--changed-only", "origin/main"], capsys)
    assert result.code == 1 and "checking all rows" in result.err


def test_changed_only_unknown_ref_falls_back(workspace, capsys, git_available):
    workspace.register([BAD])
    workspace.git("init", "-q", "-b", "main")
    workspace.git("add", ".")
    workspace.git("commit", "-q", "-m", "init")
    result = check(["--changed-only", "origin/nope"], capsys)
    assert result.code == 1 and "unknown base ref" in result.err


def test_changed_lines_parses_hunks(workspace, git_available):
    path = workspace.write("requirements/requirements.csv", "a\nb\nc\nd\n")
    workspace.git("init", "-q", "-b", "main")
    workspace.git("add", ".")
    workspace.git("commit", "-q", "-m", "init")
    path.write_text("a\nB\nc\nd\nE\nF\n", encoding="utf-8")
    assert lint.changed_lines(str(path), "main") == {2, 5, 6}


# ---------------------------------------------------------------- multi-file runs and Markdown

def test_directory_argument_is_a_workspace(workspace, capsys, tmp_path):
    other = tmp_path / "other" / "requirements"
    other.mkdir(parents=True)
    (other / "requirements.csv").write_text(
        "ID,Type,Text,Source,Priority,Status,Rationale\nR-001,F,The POS is fast.,S-01,must,draft,x\n",
        encoding="utf-8")
    doc = check([str(other), "--format", "json"], capsys).json()
    assert sorted(f["rule"] for f in doc["findings"]) == ["missing-obligation", "weak-word"]


def test_multiline_csv_text_reports_physical_line(workspace, capsys):
    path = workspace.write("requirements/requirements.csv",
                           'ID,Type,Text,Source,Priority,Status,Rationale\n'
                           'R-001,F,"The POS shall print\na receipt quickly.",S-01,must,draft,x\n')
    doc = check([str(path), "--format", "json"], capsys).json()
    finding = doc["findings"][0]
    assert (finding["line"], finding["column"]) == (3, 11)


def test_markdown_definitions_without_register(workspace, capsys):
    path = workspace.write("requirements/stories/earn.md",
                           "# Earn\n\n| ID | Text | Status |\n| --- | --- | --- |\n"
                           "| R-031 | As a member, I want quick points. | draft |\n")
    doc = check([str(path), "--format", "json"], capsys).json()
    assert [(f["rule"], f["line"]) for f in doc["findings"]] == [("weak-word", 5)]


# ---------------------------------------------------------------- the exemplar fixture

def test_requirement_phrasing_fixture(capsys, monkeypatch):
    if not FIXTURE.is_file():
        pytest.skip("exemplar fixture not present")
    monkeypatch.chdir(REPO_ROOT)
    result = check([str(FIXTURE), "--format", "json"], capsys)
    doc = result.json()
    assert result.code == 0
    assert doc["summary"] == {"error": 0, "warning": 0, "info": 1}
    assert [(f["rule"], f["id"]) for f in doc["findings"]] == [("open-tbd", "R-024")]


def test_python_dash_m_and_script_mode(tmp_path):
    """The module runs as a script from any cwd (the vendored layout) and under ``python -m``."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "lint_requirements.py").write_text((SRC / "re_lint/lint.py").read_text(encoding="utf-8"))
    (scripts / "reqio.py").write_text((SRC / "re_lint/reqio.py").read_text(encoding="utf-8"))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    proc = subprocess.run([sys.executable, str(scripts / "lint_requirements.py"), "--help"],
                          cwd=elsewhere, capture_output=True, text=True)
    assert proc.returncode == 0 and "--changed-only" in proc.stdout
    proc = subprocess.run([sys.executable, "-I", str(scripts / "lint_requirements.py"), "--list-rules"],
                          cwd=elsewhere, capture_output=True, text=True)
    assert proc.returncode == 0 and "weak-word" in proc.stdout
    if FIXTURE.is_file():
        proc = subprocess.run([sys.executable, str(scripts / "lint_requirements.py"), str(FIXTURE)],
                              cwd=elsewhere, capture_output=True, text=True)
        assert proc.returncode == 0 and re.search(r"0 errors, 0 warnings, 1 info", proc.stdout)
