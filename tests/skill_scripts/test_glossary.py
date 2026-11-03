"""Tests for skills/foundations/glossary/scripts/mine_terms.py (stdlib + pytest only)."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "foundations" / "glossary" / "scripts" / "mine_terms.py"


def _load():
    spec = importlib.util.spec_from_file_location("mine_terms", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


mine_terms = _load()


def run_json(capsys, *argv):
    code = mine_terms.main([*argv, "--format", "json"])
    out = capsys.readouterr().out
    return code, {row["Term"]: row for row in json.loads(out)["candidates"]}


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "docs" / "notes.md").write_text(
        "# Notes\n"
        "A points transaction is created for every purchase.\n"
        "Each points transaction belongs to one member.\n"
        "WHEN the POS sends a purchase, the CRM gets a summary. TBD: the POS retry rule.\n"
        "The point of sale prints a receipt. See SH-01 and R-012.\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "models.py").write_text(
        "class PointsTransaction:\n"
        "    points_transaction_id: str\n"
        "    member_id: str\n"
        "\n"
        "def getPointsTransaction(member_id):\n"
        "    return PointsTransaction()\n",
        encoding="utf-8",
    )
    return tmp_path


def test_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        mine_terms.main(["--help"])
    assert exc.value.code == 0
    assert "Exit codes" in capsys.readouterr().out


def test_script_runs_as_cli(repo: Path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo / "docs"), "--format", "csv"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert proc.stdout.splitlines()[0] == "Term,Kind,Count,Files,Variants,In glossary,Locations"


def test_identifier_and_prose_forms_merge(repo: Path, capsys):
    code, rows = run_json(capsys, str(repo / "docs"), str(repo / "src"))
    assert code == 0
    row = rows["points transaction"]
    assert set(row["Kind"].split("+")) == {"identifier", "phrase"}
    assert int(row["Count"]) >= 5
    assert row["Files"] == "2"
    assert "PointsTransaction" in row["Variants"]
    assert "docs/notes.md:2" in row["Locations"]


def test_accessor_verbs_and_id_suffixes_are_stripped(repo: Path, capsys):
    _, rows = run_json(capsys, str(repo / "src"), "--min-count", "1")
    assert "member" in rows  # member_id -> member
    assert "get points transaction" not in rows
    assert "points transaction id" not in rows


def test_acronyms_counted_and_keywords_ignored(repo: Path, capsys):
    _, rows = run_json(capsys, str(repo / "docs"), "--min-count", "1")
    assert rows["POS"]["Kind"] == "acronym"
    assert rows["POS"]["Count"] == "2"
    assert "CRM" in rows
    for noise in ("WHEN", "TBD", "SH", "R"):
        assert noise not in rows


def test_of_joins_multiword_terms(repo: Path, capsys):
    _, rows = run_json(capsys, str(repo / "docs"), "--min-count", "1")
    assert "point of sale" in rows
    assert "point of" not in rows


def test_glossary_marks_and_exit_code(repo: Path, capsys):
    glossary = repo / "glossary.md"
    glossary.write_text(
        "| Term | Definition | Synonyms | Homonym notes | Abbreviation | Owner | Status | Source |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| Member | A person in the programme. | customer (code, tickets), account holder | | | SH-01 | agreed | S-01 |\n"
        "| Point of sale | The till system. | | | POS | SH-02 | proposed | S-02 |\n"
        "| Points transaction | One ledger entry. | | | | SH-01 | proposed | S-01 |\n",
        encoding="utf-8",
    )
    code, rows = run_json(capsys, str(repo / "docs"), "--glossary", str(glossary), "--min-count", "1")
    assert code == 1  # "purchase", "receipt", ... are not in the glossary
    assert rows["member"]["In glossary"] == "term"
    assert rows["POS"]["In glossary"] == "abbreviation"
    assert rows["points transaction"]["In glossary"] == "term"
    assert rows["purchase"]["In glossary"] == "no"

    code, rows = run_json(
        capsys, str(repo / "docs"), "--glossary", str(glossary), "--kinds", "acronym", "--only-new", "--min-count", "1"
    )
    assert code == 1
    assert set(rows) == {"CRM"}


def test_exit_zero_when_everything_is_known(repo: Path, capsys):
    glossary = repo / "glossary.md"
    glossary.write_text(
        "| Term | Definition | Synonyms | Homonym notes | Abbreviation | Owner | Status | Source |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| Point of sale | The till system. | | | POS | SH-02 | proposed | S-02 |\n"
        "| Customer relationship management | The CRM system. | | | CRM | SH-01 | proposed | S-01 |\n",
        encoding="utf-8",
    )
    code, rows = run_json(capsys, str(repo / "docs"), "--glossary", str(glossary), "--kinds", "acronym", "--min-count", "1")
    assert code == 0
    assert {r["In glossary"] for r in rows.values()} == {"abbreviation"}


def test_glossary_file_is_not_counted_as_usage(repo: Path, capsys):
    glossary = repo / "docs" / "glossary.md"
    glossary.write_text(
        "| Term | Definition | Synonyms | Homonym notes | Abbreviation | Owner | Status | Source |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| Voucher | A code worth money. Voucher voucher voucher. | | | | SH-01 | proposed | S-01 |\n",
        encoding="utf-8",
    )
    _, rows = run_json(capsys, str(repo / "docs"), "--glossary", str(glossary), "--min-count", "1")
    assert "voucher" not in rows


def test_min_count_and_top(repo: Path, capsys):
    _, rows = run_json(capsys, str(repo / "docs"), "--min-count", "3")
    assert all(int(r["Count"]) >= 3 for r in rows.values())
    _, rows = run_json(capsys, str(repo / "docs"), "--min-count", "1", "--top", "2")
    assert len(rows) == 2


def test_skips_vendor_and_git_directories(repo: Path, capsys):
    hidden = repo / "node_modules" / "pkg"
    hidden.mkdir(parents=True)
    (hidden / "readme.md").write_text("Zebracorn zebracorn zebracorn.\n", encoding="utf-8")
    _, rows = run_json(capsys, str(repo), "--min-count", "1")
    assert "zebracorn" not in rows


@pytest.mark.parametrize(
    "argv",
    [
        ["does-not-exist"],
        ["{repo}", "--glossary", "{repo}/missing.md"],
        ["{repo}", "--only-new"],
        ["{repo}", "--max-words", "9"],
        ["{repo}", "--kinds", "nouns"],
    ],
)
def test_usage_errors_exit_two(repo: Path, capsys, argv):
    args = [a.replace("{repo}", str(repo)) for a in argv]
    assert mine_terms.main(args) == 2
    assert "error" in capsys.readouterr().err


def test_glossary_without_term_table_exits_two(repo: Path, capsys):
    bad = repo / "bad.md"
    bad.write_text("# Glossary\n\nNo table here.\n", encoding="utf-8")
    assert mine_terms.main([str(repo / "docs"), "--glossary", str(bad)]) == 2


def test_no_readable_files_exits_two(tmp_path: Path, capsys):
    (tmp_path / "image.png").write_bytes(b"\x89PNG\x00\x00")
    assert mine_terms.main([str(tmp_path)]) == 2
