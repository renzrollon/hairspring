from __future__ import annotations

import csv
import io
import shutil
import subprocess
import sys

import pytest

from relint_helpers import SRC, run_cli
from re_lint import prioritize

TIE = "tie, do not over-interpret"


def _write(tmp_path, text, name="items.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _csv(path):
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


WIEGERS = (
    "ID,Title,Benefit,Penalty,Cost,Risk\n"
    "R-040,Spend points at the till,5,3,2,1\n"
    "R-041,Choose voucher amount,9,7,5,3\n"
    "R-042,Cancel a voucher,1,1,1,1\n"
)


def test_wiegers_matches_the_hand_calculation(tmp_path, capsys):
    out = tmp_path / "priorities.csv"
    result = run_cli(prioritize, [str(_write(tmp_path, WIEGERS)), "--out", str(out)], capsys)
    assert result.code == 0, result.err
    # value = 2*benefit + penalty -> 13, 25, 3 (total 41); cost total 8; risk total 5.
    expected = {
        "R-040": (13 / 41 * 100) / (2 / 8 * 100 + 0.5 * 1 / 5 * 100),
        "R-041": (25 / 41 * 100) / (5 / 8 * 100 + 0.5 * 3 / 5 * 100),
        "R-042": (3 / 41 * 100) / (1 / 8 * 100 + 0.5 * 1 / 5 * 100),
    }
    rows = _csv(out)
    assert list(rows[0]) == ["ID", "Title", "Benefit", "Penalty", "Cost", "Risk", "Score", "Rank", "Tie"]
    assert [r["ID"] for r in rows] == ["R-040", "R-041", "R-042"]
    for row in rows:
        assert row["Score"] == f"{expected[row['ID']]:.3f}"
    assert [r["Rank"] for r in rows] == ["1", "2", "3"] and all(r["Tie"] == "" for r in rows)
    assert "| 1 | R-040 | Spend points at the till | 0.906 |" in result.out
    assert "benefit=2, penalty=1, cost=1, risk=0.5" in result.out


def test_weights_option_and_weights_row(tmp_path, capsys):
    path = _write(tmp_path, WIEGERS)
    flat = run_cli(prioritize, [str(path), "--weights", "Benefit=1, penalty=1,cost=1,risk=0", "--format", "json"],
                   capsys).json()
    assert flat["weights"] == {"benefit": 1.0, "penalty": 1.0, "cost": 1.0, "risk": 0.0}
    by_id = {i["id"]: i["score"] for i in flat["items"]}
    assert by_id["R-040"] == round((8 / 26 * 100) / (2 / 8 * 100), 3)  # values 8, 16, 2
    with_row = _write(tmp_path, WIEGERS.replace("ID,Title,Benefit,Penalty,Cost,Risk\n",
                                                "ID,Title,Benefit,Penalty,Cost,Risk\nWeights,,1,1,1,0\n"), "w.csv")
    out = tmp_path / "out.csv"
    from_row = run_cli(prioritize, [str(with_row), "--format", "json", "--out", str(out)], capsys).json()
    assert from_row["weights"] == flat["weights"] and from_row["items"] == flat["items"]
    assert _csv(out)[0]["ID"] == "Weights" and _csv(out)[0]["Score"] == ""
    override = run_cli(prioritize, [str(with_row), "--weights", "risk=0.5", "--format", "json"], capsys).json()
    assert override["weights"]["risk"] == 0.5 and override["weights"]["benefit"] == 1.0


def test_wsjf_with_spelled_out_headers_and_tie_chain(tmp_path, capsys):
    path = _write(tmp_path, (
        "id,title,Business Value,time_criticality,RR|OE,Job-Size\n"
        "R-001,A,300,10,10,100\n"   # 3.20
        "R-002,B,290,10,10,100\n"   # 3.10 (3.1% below A)
        "R-003,C,276,10,10,100\n"   # 2.96 (4.5% below B): chained into the same tie group
        "R-004,D,180,10,10,100\n"   # 2.00
    ))
    out = tmp_path / "ranked.csv"
    result = run_cli(prioritize, [str(path), "--method", "wsjf", "--out", str(out)], capsys)
    assert result.code == 0, result.err
    rows = _csv(out)
    assert [(r["id"], r["Score"], r["Tie"]) for r in rows] == [
        ("R-001", "3.20", TIE), ("R-002", "3.10", TIE), ("R-003", "2.96", TIE), ("R-004", "2.00", "")]
    assert "Tie groups" in result.out and "- R-001, R-002, R-003" in result.out
    narrow = run_cli(prioritize, [str(path), "--method", "wsjf", "--tie-band", "0.04", "--format", "json"], capsys).json()
    assert [i["tie"] for i in narrow["items"]] == [True, True, False, False]


def test_equal_scores_share_a_rank(tmp_path, capsys):
    path = _write(tmp_path, "ID,BusinessValue,TimeCriticality,RiskReduction,JobSize\nA,5,3,2,5\nB,5,3,2,5\nC,1,1,1,5\n")
    result = run_cli(prioritize, [str(path), "--method", "wsjf", "--format", "csv"], capsys)
    rows = list(csv.DictReader(io.StringIO(result.out)))
    assert [(r["ID"], r["Rank"]) for r in rows] == [("A", "1"), ("B", "1"), ("C", "3")]
    assert rows[0]["Tie"] == rows[1]["Tie"] == TIE and rows[2]["Tie"] == ""


def test_rerun_on_its_own_output_replaces_score_columns(tmp_path, capsys):
    out = tmp_path / "priorities.csv"
    run_cli(prioritize, [str(_write(tmp_path, WIEGERS)), "--out", str(out)], capsys)
    first = out.read_text(encoding="utf-8")
    run_cli(prioritize, [str(out), "--out", str(out)], capsys)
    assert out.read_text(encoding="utf-8") == first


def test_markdown_table_input(tmp_path, capsys):
    path = _write(tmp_path, "| ID | Benefit | Penalty | Cost | Risk |\n| --- | --- | --- | --- | --- |\n"
                            "| R-1 | 2 | 2 | 2 | 2 |\n| R-2 | 4 | 4 | 2 | 2 |\n", "items.md")
    result = run_cli(prioritize, [str(path), "--format", "json"], capsys)
    assert [i["id"] for i in result.json()["items"]] == ["R-2", "R-1"]


@pytest.mark.parametrize("content, args, message", [
    ("ID,Title,Benefit,Penalty\nR-1,x,1,1\n", [], "missing column(s) for wiegers: Cost, Risk"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,high,1,1,1\n", [], "R-1 (line 2): Benefit 'high' is not a number"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,1,1,0,1\n", [], "Cost must be greater than 0"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,1,,1,1\n", [], "Penalty is empty"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,1,-2,1,1\n", [], "is negative"),
    ("ID,BusinessValue,TimeCriticality,RiskReduction,JobSize\nR-1,1,1,1,0\n", ["--method", "wsjf"],
     "JobSize must be greater than 0"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,1,1,1,1\n", ["--weights", "value=2"], "unknown key 'value'"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,1,1,1,1\n", ["--weights", "benefit"], "is not key=value"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,1,1,1,1\n", ["--tie-band", "1.5"], "--tie-band"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,0,0,1,1\n", [], "sum to 0"),
    ("ID,Benefit,Penalty,Cost,Risk\nR-1,1,1,1,1\n", ["--weights", "cost=0,risk=0"], "divide by zero"),
    ("Title,Benefit,Penalty,Cost,Risk\nx,1,1,1,1\n", [], "missing column(s) for wiegers: ID"),
    ("", [], "is empty"),
])
def test_input_errors_exit_2(tmp_path, capsys, content, args, message):
    result = run_cli(prioritize, [str(_write(tmp_path, content)), *args], capsys)
    assert result.code == 2 and message in result.err, result.err


def test_missing_file_and_scale_warning(tmp_path, capsys):
    assert run_cli(prioritize, [str(tmp_path / "nope.csv")], capsys).code == 2
    result = run_cli(prioritize, [str(_write(tmp_path, "ID,Benefit,Penalty,Cost,Risk\nR-1,20,1,1,1\nR-1,2,1,1,1\n"))], capsys)
    assert result.code == 0 and "outside the usual 1-9" in result.err and "appears twice" in result.err


def test_runs_standalone_next_to_reqio(tmp_path):
    shutil.copy(SRC / "re_lint" / "reqio.py", tmp_path / "reqio.py")
    shutil.copy(SRC / "re_lint" / "prioritize.py", tmp_path / "prioritize.py")
    items = _write(tmp_path, WIEGERS)
    proc = subprocess.run([sys.executable, str(tmp_path / "prioritize.py"), str(items), "--format", "csv"],
                          cwd=tmp_path, capture_output=True, text=True)
    assert proc.returncode == 0 and proc.stdout.startswith("ID,Title,Benefit"), proc.stderr
