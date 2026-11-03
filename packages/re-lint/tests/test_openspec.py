from __future__ import annotations

import shutil
import subprocess
import sys

import pytest

from relint_helpers import SRC, make_row, run_cli
from re_lint import openspec

HEADER = ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale", "Title", "Verification", "Tags"]
DATE = "2026-11-03"

STORIES = """# Stories: Redeem points at checkout

## R-040: Issue voucher

**R-040.AC1: Convert 1,000 points** _(happy path)_
- **Given** a member with 1,250 posted points
- **When** the member requests a voucher for 1,000 points in the customer mobile app
- **Then** the loyalty service issues a voucher worth SGD 10
- **And** the member's posted balance is 250 points

**Notes:** Source S-01

| ID | Acceptance criterion |
| --- | --- |
| R-042.AC1 | Given a member with 480 posted points, when the member requests a voucher, then the loyalty service rejects the request and the response states the 500-point minimum. |

- R-044.AC1: Given a voucher in state Issued, when the cashier scans it, then the POS shows TBD seconds of wait.
"""


@pytest.fixture
def ws(workspace):
    workspace.register([
        make_row("R-040", text="WHEN a member with at least 500 posted points requests a voucher in the customer "
                 "mobile app, the loyalty service shall issue a voucher worth SGD 1 per 100 points redeemed.",
                 Status="agreed", Title="Issue voucher on redemption request", Verification="test",
                 Rationale="Redemption is why members collect points."),
        make_row("R-041", text="WHEN the POS sends a voucher validation request for a voucher in state Issued, the "
                 "loyalty service shall return the voucher value to the POS.", Status="agreed",
                 Title="Validate voucher at checkout", Tags="cap:checkout"),
        make_row("R-042", text="IF a member with fewer than 500 posted points requests a voucher, THEN the loyalty "
                 "service shall reject the request with a response that states the 500-point minimum.",
                 Status="agreed", Title="Reject redemption below minimum", Priority="should"),
        make_row("R-043", text="WHEN the POS applies a voucher, the POS should print the remaining balance.",
                 Status="draft", Title="Print remaining balance", Priority="could"),
        make_row("R-044", text="WHEN the cashier scans a voucher, the POS shall confirm it.", Status="agreed",
                 Title="Confirm scanned voucher"),
        make_row("R-045", text="The loyalty service shall keep an audit log of redemptions.", Status="proposed"),
        make_row("R-085", text="WHILE the POS load is at most 9000 purchases per minute, the loyalty service shall "
                 "answer 95% of voucher validation requests within 300 ms.", Type="Q", Status="agreed",
                 Title="Validation response time", Verification="test"),
        make_row("R-100", text="The loyalty service shall implement the TillPoint interface v2.1.", Type="C",
                 Status="agreed", Title="TillPoint interface", Verification="inspection"),
        make_row("R-019", text="The POS shall print vouchers.", Status="withdrawn"),
        make_row("R-060", text="WHEN points expire, the service shall notify the member.", Status="agreed",
                 Priority="wont"),
    ], header=HEADER)
    workspace.write("requirements/stories/redeem.md", STORIES)
    return workspace


def _change(ws, name="add-voucher-redemption"):
    return ws.root / "openspec" / "changes" / name


def test_openspec_change_folder(ws, capsys):
    result = run_cli(openspec, ["add-voucher-redemption", "--ids", "R-040,R-041,R-042,R-085,R-100", "--date", DATE],
                     capsys)
    assert result.code == 0, result.err
    change = _change(ws)
    files = sorted(p.relative_to(change).as_posix() for p in change.rglob("*") if p.is_file())
    assert files == [".openspec.yaml", "proposal.md", "specs/checkout/spec.md", "specs/voucher-redemption/spec.md",
                     "tasks.md"]
    meta = (change / ".openspec.yaml").read_text(encoding="utf-8")
    assert meta == ("schema: spec-driven\ncreated: 2026-11-03\nx-re-skills-source: requirements/requirements.csv\n"
                    "x-re-skills-ids: [R-040, R-041, R-042, R-085, R-100]\n")
    spec = (change / "specs" / "voucher-redemption" / "spec.md").read_text(encoding="utf-8")
    lines = spec.splitlines()
    assert lines[0] == "# Spec Delta: voucher-redemption" and "## Purpose" in spec and "## ADDED Requirements" in spec
    i = lines.index("### Requirement: R-040 Issue voucher on redemption request")
    assert lines[i + 1] == "<!-- R-040 -->" and "the loyalty service SHALL issue a voucher" in lines[i + 2]
    assert ("#### Scenario: R-040.AC1 Convert 1,000 points\n- **GIVEN** a member with 1,250 posted points\n"
            "- **WHEN** the member requests a voucher for 1,000 points in the customer mobile app\n"
            "- **THEN** the loyalty service issues a voucher worth SGD 10\n"
            "- **AND** the member's posted balance is 250 points\n") in spec
    assert ("#### Scenario: R-042.AC1 Member requests a voucher\n- **GIVEN** a member with 480 posted points\n"
            "- **WHEN** the member requests a voucher\n"
            "- **THEN** the loyalty service rejects the request and the response states the 500-point minimum\n"
            ) in spec  # an "and" inside a clause never splits it
    assert "Voucher Redemption: Issue voucher on redemption request; Reject redemption below minimum" in spec
    assert "R-085" not in spec and "R-100" not in spec  # quality requirements and constraints stay in the proposal
    checkout = (change / "specs" / "checkout" / "spec.md").read_text(encoding="utf-8")
    assert ("#### Scenario: R-041 main case (derived from the requirement text)\n"
            "- **WHEN** the POS sends a voucher validation request for a voucher in state Issued\n"
            "- **THEN** the loyalty service SHALL return the voucher value to the POS.\n") in checkout
    proposal = (change / "proposal.md").read_text(encoding="utf-8")
    for heading in ("# Proposal: add-voucher-redemption", "## Why", "## What Changes", "## Capabilities",
                    "### New Capabilities", "### Modified Capabilities", "## Constraints and Quality Requirements",
                    "## Impact", "## Not in this change", "## Traceability"):
        assert heading in proposal, heading
    why = proposal.split("## Why\n\n", 1)[1].split("\n", 1)[0]
    assert 50 <= len(why) <= 1000 and "(R-040)" in why
    assert "- R-042 Reject redemption below minimum (should)" in proposal
    assert "| R-100 | C | The loyalty service shall implement the TillPoint interface v2.1. |" in proposal
    assert "| R-041 | F | must | agreed | S-01 | specs/checkout/spec.md; tasks 2.1 |" in proposal
    assert "## Impact\n\n- Register: `requirements/requirements.csv`\n" in proposal
    assert "## Not in this change\n\nNone." in proposal
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    assert "## 1. voucher-redemption" in tasks and "## 3. Quality requirements and constraints" in tasks
    assert ("- [ ] 1.1 Implement R-040 Issue voucher on redemption request; verify by an automated test for "
            "scenario R-040.AC1 (R-040)") in tasks
    assert "- [ ] 3.2 Verify R-100 TillPoint interface by inspection against proposal.md (R-100)" in tasks
    assert all(line.rstrip().endswith(")") for line in tasks.splitlines() if line.startswith("- [ ]"))
    assert "next: openspec validate add-voucher-redemption --strict" in result.out


def test_default_selection_is_agreed_and_blocked_rows_can_be_left_out(ws, capsys):
    refused = run_cli(openspec, ["add-voucher-redemption", "--date", DATE], capsys)
    assert refused.code == 1 and "| R-044 | G2 | open-tbd in R-044.AC1 |" in refused.out
    assert not _change(ws).exists()
    result = run_cli(openspec, ["add-voucher-redemption", "--date", DATE, "--skip-blocked"], capsys)
    assert result.code == 0, result.err
    assert "handed off: R-040, R-041, R-042, R-085, R-100" in result.out
    proposal = (_change(ws) / "proposal.md").read_text(encoding="utf-8")
    assert "| R-044 | open-tbd in R-044.AC1 |" in proposal
    assert "R-043" not in proposal and "R-045" not in proposal  # never selected: not listed


def test_named_rows_never_selectable_and_approved_exceptions(ws, capsys):
    draft = run_cli(openspec, ["fix-voucher", "--ids", "R-019", "R-060", "R-043", "--date", DATE], capsys)
    assert draft.code == 1 and "not-agreed (Status=draft)" in draft.out and "--allow-draft" in draft.out
    named = run_cli(openspec, ["fix-voucher", "--ids", "R-019", "R-060", "R-043", "--date", DATE, "--allow-draft"],
                    capsys)
    assert named.code == 0, named.err
    proposal = (_change(ws, "fix-voucher") / "proposal.md").read_text(encoding="utf-8")
    not_in = proposal.split("## Not in this change", 1)[1].split("## Traceability", 1)[0]
    assert "| R-019 | Status=withdrawn |" in not_in and "| R-060 | Priority=wont |" in not_in
    assert "R-043" not in not_in  # handed off: never listed under "Not in this change"
    assert "| R-043 | F | could | draft; exception: not-agreed |" in proposal
    spec = (_change(ws, "fix-voucher") / "specs" / "voucher" / "spec.md").read_text(encoding="utf-8")
    assert "the POS SHOULD print" in spec  # no shall/must: should is upper-cased
    assert "R-043: strict-keyword" in named.out and "exception: R-043: not-agreed" in named.out
    nothing = run_cli(openspec, ["add-x", "--ids", "R-019"], capsys)
    assert nothing.code == 1 and "nothing to hand off" in nothing.err


def test_gate_refuses_tbd_and_missing_scenarios(ws, capsys):
    tbd = run_cli(openspec, ["add-confirm", "--ids", "R-044"], capsys)
    assert tbd.code == 1 and "| R-044 | G2 | open-tbd in R-044.AC1 |" in tbd.out and "--allow-tbd" in tbd.out
    assert not _change(ws, "add-confirm").exists()
    allowed = run_cli(openspec, ["add-confirm", "--ids", "R-044", "--allow-tbd", "--date", DATE], capsys)
    assert allowed.code == 0
    proposal = (_change(ws, "add-confirm") / "proposal.md").read_text(encoding="utf-8")
    assert "| R-044 | F | must | agreed; exception: open-tbd |" in proposal
    assert "## Not in this change\n\nNone." in proposal
    ubiquitous = run_cli(openspec, ["add-audit", "--ids", "R-045", "--allow-draft"], capsys)
    assert ubiquitous.code == 1 and "| R-045 | G4 | no-scenario-source" in ubiquitous.out
    assert run_cli(openspec, ["add-audit", "--ids", "R-045", "--allow-draft", "--skip-blocked"], capsys).code == 1


def test_existing_change_needs_force(ws, capsys):
    args = ["add-voucher-redemption", "--ids", "R-040", "R-041", "--date", DATE]
    assert run_cli(openspec, args, capsys).code == 0
    again = run_cli(openspec, args, capsys)
    assert again.code == 1 and "already exists" in again.err
    notes = _change(ws) / "design.md"
    notes.write_text("# Design\n", encoding="utf-8")
    forced = run_cli(openspec, ["add-voucher-redemption", "--ids", "R-040", "--date", DATE, "--force"], capsys)
    assert forced.code == 0
    assert not (_change(ws) / "specs" / "checkout" / "spec.md").exists()  # stale generated spec removed
    assert notes.read_text(encoding="utf-8") == "# Design\n"  # hand-written files kept


def test_capability_option_and_modified_requirements(ws, capsys):
    ws.write("openspec/specs/checkout/spec.md", (
        "# checkout Specification\n\n## Purpose\nCheckout behavior for vouchers at the till, from the POS.\n\n"
        "## Requirements\n\n### Requirement: R-041 Voucher validation\n<!-- R-041 -->\nThe service SHALL validate.\n\n"
        "#### Scenario: R-041 main case\n- **WHEN** x\n- **THEN** y\n"
    ))
    result = run_cli(openspec, ["update-redemption", "--ids", "R-040,R-041", "--capability", "redemption",
                                "--date", DATE], capsys)
    assert result.code == 0, result.err
    change = _change(ws, "update-redemption")
    checkout = (change / "specs" / "checkout" / "spec.md").read_text(encoding="utf-8")
    assert "## MODIFIED Requirements\n\n### Requirement: R-041 Voucher validation\n<!-- R-041 -->" in checkout
    assert "## Purpose" not in checkout and "## ADDED" not in checkout
    assert (change / "specs" / "redemption" / "spec.md").is_file()
    proposal = (change / "proposal.md").read_text(encoding="utf-8")
    assert "### Modified Capabilities\n\n- `checkout`: Validate voucher at checkout (R-041)" in proposal
    assert "already in openspec/specs/checkout" in result.out


def test_spec_kit_target(ws, capsys):
    result = run_cli(openspec, ["004-voucher-redemption", "--target", "spec-kit", "--ids",
                                "R-040,R-042,R-043,R-044,R-085,R-100", "--allow-tbd", "--allow-draft", "--date", DATE],
                     capsys)
    assert result.code == 0, result.err
    spec = (ws.root / "specs" / "004-voucher-redemption" / "spec.md").read_text(encoding="utf-8")
    assert spec.startswith("# Feature Specification: Voucher redemption\n\n**Feature Branch**: `004-voucher-redemption`")
    for heading in ("## User Scenarios & Testing *(mandatory)*", "### Edge Cases", "## Requirements *(mandatory)*",
                    "### Functional Requirements", "### Constraints", "## Success Criteria *(mandatory)*",
                    "### Measurable Outcomes", "## Assumptions"):
        assert heading in spec, heading
    order = [line for line in spec.splitlines() if line.startswith("### User Story")]
    assert order == ["### User Story 1 - Issue voucher on redemption request (Priority: P1)",
                     "### User Story 2 - Confirm scanned voucher (Priority: P1)",
                     "### User Story 3 - Reject redemption below minimum (Priority: P2)",
                     "### User Story 4 - Print remaining balance (Priority: P3)"]
    assert ("1. **Given** a member with 1,250 posted points, **When** the member requests a voucher for 1,000 points "
            "in the customer mobile app, **Then** the loyalty service issues a voucher worth SGD 10, **And** the "
            "member's posted balance is 250 points (R-040.AC1)") in spec
    assert "the loyalty service SHALL issue a voucher worth SGD 1 per 100 points redeemed. (R-040)" in spec
    assert "- R-042: Reject redemption below minimum (see User Story 3)" in spec
    assert "- **R-085**: WHILE the POS load" in spec.split("### Measurable Outcomes")[1] and "SHALL answer" in spec
    assert "- **R-100**: The loyalty service SHALL implement" in spec.split("### Constraints")[1]
    assert "[NEEDS CLARIFICATION: value is TBD in requirements/requirements.csv]" in spec
    assert "Not in this feature" not in spec  # every named row crossed
    assert " shall " not in spec.split("## Requirements")[0].split("## User Scenarios")[1].replace("Given", "")
    assert not (ws.root / "openspec").exists()
    again = run_cli(openspec, ["004-voucher-redemption", "--target", "spec-kit", "--ids", "R-040"], capsys)
    assert again.code == 1


@pytest.mark.parametrize("args", [
    ["Add Voucher"], ["add-x", "--ids", "R-404"], ["add-x", "--date", "03/11/2026"], ["add-x", "--capability", "Bad Cap"],
])
def test_usage_errors(ws, capsys, args):
    assert run_cli(openspec, args, capsys).code == 2


@pytest.mark.parametrize("text, steps", [
    ("WHEN a member logs in, the app shall show the balance.",
     [("WHEN", "a member logs in"), ("THEN", "the app SHALL show the balance.")]),
    ("IF the fraud engine holds a purchase, THEN the service shall keep the points pending.",
     [("WHEN", "the fraud engine holds a purchase"), ("THEN", "the service SHALL keep the points pending.")]),
    ("WHILE the POS is offline, WHEN a voucher is scanned, the POS shall queue it.",
     [("GIVEN", "the POS is offline"), ("WHEN", "a voucher is scanned"), ("THEN", "the POS SHALL queue it.")]),
    ("WHERE campaigns are enabled, the service shall multiply points.",
     [("GIVEN", "campaigns are enabled"), ("THEN", "the service SHALL multiply points.")]),
    ("The service shall log every redemption.", None),
    ("The service, on startup, shall load the rules.", None),
    ("As a member, I want to see my balance, so that I can plan.", None),
])
def test_ears_steps(text, steps):
    assert openspec.ears_steps(text) == steps


def test_inline_steps_and_names():
    label, steps = openspec.inline_steps("Given a member with 300 posted points and 400 pending points, when the "
                                         "member asks for a voucher, then the app refuses it and the app shows the "
                                         "minimum, and the balance stays 300; but no voucher is issued.")
    assert label == "" and steps == [("GIVEN", "a member with 300 posted points and 400 pending points"),
                                     ("WHEN", "the member asks for a voucher"),
                                     ("THEN", "the app refuses it and the app shows the minimum"),
                                     ("AND", "the balance stays 300"), ("AND", "no voucher is issued")]
    assert openspec.when_name(steps) == "Member asks for a voucher"
    assert openspec.upcase_obligation("The app shall show it and must not crash.") == "The app SHALL show it and MUST not crash."
    assert openspec.upcase_obligation("The app should show it; users may skip.") == "The app SHOULD show it; users MAY skip."
    assert openspec.upcase_obligation("The app shall show what users may skip.") == "The app SHALL show what users may skip."


def test_runs_standalone_next_to_reqio(tmp_path):
    shutil.copy(SRC / "re_lint" / "reqio.py", tmp_path / "reqio.py")
    shutil.copy(SRC / "re_lint" / "openspec.py", tmp_path / "to_openspec.py")
    proc = subprocess.run([sys.executable, str(tmp_path / "to_openspec.py"), "--help"], cwd=tmp_path,
                          capture_output=True, text=True)
    assert proc.returncode == 0 and "CHANGE_NAME" in proc.stdout, proc.stderr
