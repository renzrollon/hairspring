"""Tests for skills/specification/user-story-refiner/scripts/check_stories.py."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "specification" / "user-story-refiner"
SCRIPT = SKILL / "scripts" / "check_stories.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_stories", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cs = _load()

STORY = """# Stories: Test

## R-050: Spend a voucher

<!-- paste-start R-050 -->
**Story:** As a member, I want to spend a voucher at the till, so that my points reduce what I pay.

**Acceptance criteria**

**R-050.AC1: Apply** _(happy path)_
- **Given** an issued SGD 5 voucher
- **When** the cashier scans the voucher
- **Then** the POS deducts SGD 5

**R-050.AC2: Already used** _(unwanted behavior)_
- **Given** an applied voucher
- **When** the cashier scans the voucher
- **Then** the POS refuses the voucher

**Notes:** Source S-06 · Priority must · Depends on none · Constraints none · Open questions none
<!-- paste-end R-050 -->

**INVEST**

| Criterion | Result | Evidence |
| --- | --- | --- |
| Independent | pass | none needed |
| Negotiable | pass | no solution |
| Valuable | pass | benefit differs |
| Estimable | pass | clear |
| Small | pass | one step |
| Testable | pass | all testable |

**Definition of Ready**

| Item | Result | Evidence |
| --- | --- | --- |
| Has an ID, type, source, priority and rationale | pass | row complete |
"""

CSV = (
    "ID,Type,Text,Source,Priority,Status,Rationale\n"
    'R-050,F,"As a member, I want to spend a voucher at the till, so that my points reduce what I pay.",S-06,must,draft,Test.\n'
)


def _write(tmp_path: Path, story: str = STORY, csv_text: str = CSV):
    md = tmp_path / "stories.md"
    md.write_text(story, encoding="utf-8")
    req = tmp_path / "requirements.csv"
    req.write_text(csv_text, encoding="utf-8")
    return md, req


def _rules(findings):
    return {f["rule"] for f in findings}


def test_example_output_is_clean():
    assert cs.main([str(SKILL / "examples" / "expected-output.md"),
                    "--requirements", str(SKILL / "examples" / "expected-output.csv")]) == 0


def test_minimal_story_is_clean(tmp_path):
    md, req = _write(tmp_path)
    assert cs.check_file(md, cs._read_requirements(req)) == []


def test_missing_unwanted_behavior(tmp_path):
    md, _ = _write(tmp_path, STORY.replace("_(unwanted behavior)_", "_(alternative)_"))
    assert "unwanted-missing" in _rules(cs.check_file(md))


def test_story_template(tmp_path):
    md, _ = _write(tmp_path, STORY.replace("so that my points", "because my points"))
    assert "story-template" in _rules(cs.check_file(md))


def test_generic_role_warns(tmp_path):
    story = STORY.replace("As a member,", "As a user,")
    md, _ = _write(tmp_path, story)
    findings = cs.check_file(md)
    assert any(f["rule"] == "role-generic" and f["severity"] == "warning" for f in findings)


def test_duplicate_ac_and_prefix(tmp_path):
    md, _ = _write(tmp_path, STORY.replace("**R-050.AC2: Already used**", "**R-050.AC1: Already used**"))
    assert "ac-duplicate" in _rules(cs.check_file(md))
    md, _ = _write(tmp_path, STORY.replace("**R-050.AC2: Already used**", "**R-051.AC2: Already used**"))
    assert "ac-prefix" in _rules(cs.check_file(md))


def test_two_whens(tmp_path):
    story = STORY.replace("- **When** the cashier scans the voucher\n- **Then** the POS deducts SGD 5",
                          "- **When** the cashier scans the voucher\n- **When** the member pays\n- **Then** the POS deducts SGD 5")
    md, _ = _write(tmp_path, story)
    assert "ac-gwt" in _rules(cs.check_file(md))


def test_untestable_flag_must_route(tmp_path):
    story = STORY.replace("- **Then** the POS refuses the voucher",
                          "- **Then** the POS refuses the voucher\n- **Flag:** untestable: \"nice\" has no measure")
    md, _ = _write(tmp_path, story)
    assert "flag-route" in _rules(cs.check_file(md))
    md, _ = _write(tmp_path, story.replace("no measure", "no measure; routed to testability-check"))
    assert "flag-route" not in _rules(cs.check_file(md))


def test_invest_rows_and_results(tmp_path):
    md, _ = _write(tmp_path, STORY.replace("| Small | pass | one step |\n", ""))
    assert "invest-table" in _rules(cs.check_file(md))
    md, _ = _write(tmp_path, STORY.replace("| Small | pass |", "| Small | partly |"))
    assert "invest-table" in _rules(cs.check_file(md))


def test_paste_block_rules(tmp_path):
    md, _ = _write(tmp_path, STORY.replace("<!-- paste-end R-050 -->\n", ""))
    assert "paste-block" in _rules(cs.check_file(md))
    md, _ = _write(tmp_path, STORY.replace("**Acceptance criteria**", "| a | b |\n| --- | --- |\n| 1 | 2 |"))
    assert "paste-format" in _rules(cs.check_file(md))


def test_register_cross_check(tmp_path):
    md, req = _write(tmp_path, csv_text=CSV.replace("reduce what I pay.", "pay less."))
    assert "csv-drift" in _rules(cs.check_file(md, cs._read_requirements(req)))
    md, req = _write(tmp_path, csv_text=CSV.replace(",F,", ",Q,"))
    assert "csv-type" in _rules(cs.check_file(md, cs._read_requirements(req)))
    md, req = _write(tmp_path, csv_text="ID,Type,Text,Source,Priority,Status,Rationale\n")
    assert "csv-missing" in _rules(cs.check_file(md, cs._read_requirements(req)))


def test_exit_codes_and_json(tmp_path, capsys):
    md, req = _write(tmp_path, STORY.replace("_(unwanted behavior)_", "_(alternative)_"))
    assert cs.main([str(md), "--format", "json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert any(f["rule"] == "unwanted-missing" for f in data)
    assert cs.main([str(tmp_path / "missing.md")]) == 2
    md, _ = _write(tmp_path, STORY.replace("As a member,", "As a user,"))
    assert cs.main([str(md)]) == 0
    assert cs.main([str(md), "--fail-on", "warning"]) == 1


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        cs.main(["--help"])
    assert exc.value.code == 0
