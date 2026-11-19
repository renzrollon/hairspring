from __future__ import annotations

import ast
import re
import subprocess
import sys

import pytest

from relint_helpers import PACKAGE_ROOT, REPO_ROOT, SRC, make_row, run_cli
import re_lint
from re_lint import cli, reqio


def test_version(capsys):
    result = run_cli(cli, ["--version"], capsys)
    assert (result.code, result.out) == (0, f"re-lint {re_lint.__version__}\n")


def test_help_lists_every_command(capsys):
    result = run_cli(cli, ["--help"], capsys)
    assert result.code == 0
    for name in cli.COMMANDS:
        assert re.search(rf"^  {name}\s", result.out, re.M)
    assert "Exit codes" in result.out


def test_no_arguments_prints_help_and_exits_2(capsys):
    result = run_cli(cli, [], capsys)
    assert result.code == 2 and "commands:" in result.err


def test_unknown_command_suggests(capsys):
    result = run_cli(cli, ["chek"], capsys)
    assert result.code == 2 and "did you mean 'check'" in result.err


def test_options_before_command(capsys):
    assert run_cli(cli, ["--format", "json"], capsys).code == 2


def test_missing_module_gives_a_clear_message(monkeypatch, capsys):
    monkeypatch.setitem(cli.COMMANDS, "ghost", ("does_not_exist", "A command that is not installed."))
    result = run_cli(cli, ["ghost"], capsys)
    assert result.code == 2
    assert "the 'ghost' command is not available" in result.err and "Traceback" not in result.err
    help_text = run_cli(cli, ["--help"], capsys).out
    assert re.search(r"ghost .*not available in this installation", help_text)


def test_broken_module_does_not_crash(monkeypatch, capsys):
    monkeypatch.setitem(cli.COMMANDS, "broken", ("_broken_for_test", "Broken."))

    def explode(name):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "_load", explode)
    monkeypatch.delenv("RE_LINT_DEBUG", raising=False)
    result = run_cli(cli, ["broken"], capsys)
    assert result.code == 2 and "could not load the 'broken' command: RuntimeError: boom" in result.err


def test_dispatch_check_and_ids(workspace, capsys):
    workspace.register([make_row(), make_row("R-002", text="The app shall be fast.")])
    result = run_cli(cli, ["check", "--format", "json"], capsys)
    assert result.code == 1 and result.json()["summary"]["error"] == 1
    assert run_cli(cli, ["ids", "next", "--no-git"], capsys).out == "R-003\n"


def test_subcommand_help_and_usage_errors(capsys):
    result = run_cli(cli, ["check", "--help"], capsys)
    assert result.code == 0 and result.out.startswith("usage: re-lint check")
    assert run_cli(cli, ["check", "--fail-on", "nope"], capsys).code == 2
    assert run_cli(cli, ["help", "ids"], capsys).out.startswith("usage: re-lint ids")


def test_python_dash_m(workspace):
    workspace.register([make_row()])
    proc = subprocess.run([sys.executable, "-m", "re_lint", "check"], cwd=workspace.root,
                          capture_output=True, text=True, env={"PYTHONPATH": str(SRC), "PATH": ""})
    assert proc.returncode == 0, proc.stderr
    assert "no findings" in proc.stdout


# ---------------------------------------------------------------- packaging guards

def _modules():
    return sorted((SRC / "re_lint").glob("*.py"))


@pytest.mark.parametrize("path", _modules(), ids=lambda p: p.name)
def test_modules_parse_as_python_3_9(path):
    source = path.read_text(encoding="utf-8")
    ast.parse(source, filename=str(path), feature_version=(3, 9))


@pytest.mark.parametrize("name", ["lint.py", "ids.py", "reqio.py"])
def test_command_modules_import_only_stdlib_and_reqio(name):
    tree = ast.parse((SRC / "re_lint" / name).read_text(encoding="utf-8"))
    stdlib = set(getattr(sys, "stdlib_module_names", ())) or {
        "argparse", "copy", "csv", "dataclasses", "hashlib", "io", "json", "os", "re",
        "subprocess", "sys", "pathlib", "typing", "__future__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in stdlib | {"reqio"}, alias.name
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            assert node.module.split(".")[0] in stdlib, node.module


def test_versions_agree():
    pyproject = (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.M).group(1)
    assert re_lint.__version__ == version == reqio.__version__


def test_readme_documents_every_rule():
    readme = PACKAGE_ROOT / "README.md"
    if not readme.is_file():
        pytest.skip("README not written yet")
    text = readme.read_text(encoding="utf-8")
    from re_lint import lint
    for rule in lint.RULES:
        assert f"`{rule}`" in text, rule


def test_contract_documents_every_rule():
    contract = REPO_ROOT / "docs" / "tooling-contract.md"
    if not contract.is_file():
        pytest.skip("contract not present")
    text = contract.read_text(encoding="utf-8")
    from re_lint import lint
    for rule in lint.RULES:
        assert f"| `{rule}` |" in text, rule
