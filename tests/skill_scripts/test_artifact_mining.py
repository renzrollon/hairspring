"""Tests for skills/elicitation/artifact-mining/scripts/check_candidates.py."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[2] / "skills" / "elicitation" / "artifact-mining"
SCRIPT = SKILL / "scripts" / "check_candidates.py"
HEADER = "ID,Statement,Type,Technique,Source,Location,Quote,Disposition,Reason,Owner,Kano,Requirement\n"


def _load():
    spec = importlib.util.spec_from_file_location("check_candidates", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cc = _load()


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "legacy").mkdir()
    (tmp_path / "legacy" / "post.sql").write_text(
        "-- header\n"
        "v_points := FLOOR(r.amount_cents / 100);    -- 1 point per SGD 1, rounded down\n"
        "IF v_points > 5000 THEN\n"
        "  v_points := 5000;  -- cap\n"
        "END IF;\n",
        encoding="utf-8",
    )
    (tmp_path / "support.csv").write_text(
        "id,body\n1,Hi I am Tan Wei Ling and my points from Tampines are missing\n", encoding="utf-8"
    )
    (tmp_path / "requirements").mkdir()
    return tmp_path


def _write(repo: Path, rows: str, header: str = HEADER) -> Path:
    path = repo / "requirements" / "candidates.csv"
    path.write_text(header + rows, encoding="utf-8")
    return path


def test_header_matches_asset():
    asset = (SKILL / "assets" / "candidates.csv").read_text(encoding="utf-8")
    assert asset == HEADER
    assert ",".join(cc.COLUMNS) + "\n" == HEADER


def test_example_is_valid():
    code = cc.main([str(SKILL / "examples" / "expected-output.csv"), "--root", str(SKILL / "examples" / "input")])
    assert code == 0


@pytest.mark.parametrize(
    "skill, target",
    [
        ("interview-guide", "interview-support-lead.md"),
        ("elicitation-workshop", "workshop-redemption-delighters.md"),
        ("observation-protocol", "observation-tampines-evening-checkout.md"),
    ],
)
def test_capture_examples_land_valid_candidates(tmp_path: Path, skill: str, target: str):
    """The skills that append to candidates.csv use the same header, and their quotes are real."""
    examples = SKILL.parent / skill / "examples"
    assert (SKILL.parent / skill / "assets" / "candidates.csv").read_text(encoding="utf-8") == HEADER
    elicitation = tmp_path / "requirements" / "elicitation"
    elicitation.mkdir(parents=True)
    (elicitation / target).write_text((examples / "expected-output.md").read_text(encoding="utf-8"), encoding="utf-8")
    assert cc.main([str(examples / "expected-candidates.csv"), "--root", str(tmp_path)]) == 0


def test_valid_row_with_whitespace_and_gap(repo: Path):
    _write(repo, 'CAN-001,Earning is capped at 5000 points.,F,system-archaeology,S-04,legacy/post.sql:3-4,'
                 '"IF v_points > 5000 THEN ... v_points := 5000;",confirm,Legacy-only rule.,Mei Tan (SH-01),,\n')
    assert cc.main(["--root", str(repo)]) == 0


def test_fabricated_quote_is_an_error(repo: Path, capsys):
    _write(repo, 'CAN-001,Points are rounded up.,F,system-archaeology,S-04,legacy/post.sql:2,'
                 'CEIL(r.amount_cents / 100),keep,Backed by S-01 4.1.,,,\n')
    assert cc.main(["--root", str(repo)]) == 1
    assert "quote-not-found" in capsys.readouterr().out


def test_quote_outside_window_is_an_error(repo: Path):
    _write(repo, 'CAN-001,Earning is capped.,F,system-archaeology,S-04,legacy/post.sql:5,'
                 'FLOOR(r.amount_cents / 100),confirm,Legacy-only.,Mei Tan (SH-01),,\n')
    assert cc.main(["--root", str(repo), "--window", "1"]) == 1
    assert cc.main(["--root", str(repo), "--window", "3"]) == 0


def test_masked_personal_data_matches(repo: Path):
    _write(repo, 'CAN-001,Members see missing points.,F,feedback-analysis,S-03,support.csv:2,'
                 '"Hi I am [name] and my points from Tampines are missing",confirm,1 of 1 tickets.,PO,dissatisfier,\n')
    assert cc.main(["--root", str(repo)]) == 0


def test_structural_errors(repo: Path, capsys):
    _write(repo,
           'CAN-001,A.,F,system-archaeology,S-04,legacy/post.sql:2,FLOOR,confirm,Legacy-only.,,,\n'
           'CAN-001,B.,X,guessing,S-04,legacy/post.sql:2,FLOOR,maybe,,,,REQ12\n'
           'CAN-2,C.,F,system-archaeology,S-04,legacy/missing.sql:1,FLOOR,drop,Gone.,,,\n')
    assert cc.main(["--root", str(repo), "--format", "json"]) == 1
    report = json.loads(capsys.readouterr().out)
    rules = {f["rule"] for f in report["findings"]}
    assert {"missing-owner", "duplicate-id", "invalid-enum", "missing-field",
            "invalid-requirement-ref", "invalid-id", "location-not-found"} <= rules


def test_wrong_header_is_an_error(repo: Path):
    _write(repo, "CAN-001,A\n", header="ID,Text\n")
    assert cc.main(["--root", str(repo)]) == 1


def test_external_source_location_is_info_only(repo: Path, capsys):
    _write(repo, 'CAN-001,Members get an expiry reminder.,F,feedback-analysis,S-03,S-03 ticket 48851,'
                 'nobody told me,confirm,4 of 18 tickets.,Mei Tan (SH-01),dissatisfier,\n')
    assert cc.main(["--root", str(repo)]) == 0
    assert "unverified-location" in capsys.readouterr().out


def test_schema_prefix_override(repo: Path):
    (repo / "requirements" / "schema.json").write_text(
        json.dumps({"ids": {"candidate": {"prefix": "CND-", "digits": 2}}}), encoding="utf-8")
    _write(repo, 'CND-01,A.,F,system-archaeology,S-04,legacy/post.sql:2,FLOOR,confirm,Legacy-only.,PO,,\n')
    assert cc.main(["--root", str(repo)]) == 0


def test_usage_errors(tmp_path: Path):
    assert cc.main([str(tmp_path / "nope.csv")]) == 2
    with pytest.raises(SystemExit) as exc:
        cc.main(["--help"])
    assert exc.value.code == 0
