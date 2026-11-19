"""Tests for skills/specification/state-model/scripts/check_states.py (stdlib + pytest)."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "specification" / "state-model"
SCRIPT = SKILL / "scripts" / "check_states.py"

_spec = importlib.util.spec_from_file_location("check_states", SCRIPT)
check_states = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(check_states)

CLEAN = """# State model: Voucher

```mermaid
stateDiagram-v2
  [*] --> Issued : redemptionApproved / create voucher
  Issued --> Applied : voucherValidated [not expired] / mark applied
  Issued --> Expired : voucherValidated [else] / reject
  Issued --> Expired : expiryDateReached
  Applied --> [*]
  Expired --> [*]
```

| State / event | voucherValidated | expiryDateReached |
| --- | --- | --- |
| Issued | → Applied [not expired]; else → Expired | → Expired |
| Applied | impossible (POS rejects applied codes, SH-02) | ignored (already used, SH-01) |
| Expired | impossible (code is invalid, S-02) | impossible (fires once) |
"""


def write(tmp_path: Path, text: str, name: str = "state.md") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8"
    )


def kinds(path: Path) -> list:
    proc = run_cli(str(path), "--format", "json")
    assert proc.returncode in (0, 1), proc.stderr
    return [(f["kind"], f["state"], f["event"]) for f in json.loads(proc.stdout)["findings"]]


def test_help_exits_zero():
    proc = run_cli("--help")
    assert proc.returncode == 0
    assert "--print-matrix" in proc.stdout and "--block" in proc.stdout


def test_clean_machine_exits_zero(tmp_path):
    proc = run_cli(str(write(tmp_path, CLEAN)))
    assert proc.returncode == 0, proc.stdout
    assert "0 finding(s)" in proc.stdout


def test_parses_events_guards_actions(tmp_path):
    proc = run_cli(str(write(tmp_path, CLEAN)), "--format", "json")
    data = json.loads(proc.stdout)
    assert data["states"] == ["Issued", "Applied", "Expired"]
    assert data["events"] == ["voucherValidated", "expiryDateReached"]
    assert data["initial"] == ["Issued"]
    assert data["final"] == ["Applied", "Expired"]
    first = data["transitions"][1]
    assert (first["event"], first["guard"], first["action"]) == ("voucherValidated", "not expired", "mark applied")


def test_unreachable_state(tmp_path):
    text = CLEAN.replace("  Applied --> [*]\n", "  Applied --> [*]\n  Reissued --> Issued : supportReissued\n")
    found = kinds(write(tmp_path, text))
    assert ("unreachable-state", "Reissued", "") in found


def test_dead_end_and_self_loop_is_not_an_exit(tmp_path):
    text = CLEAN.replace(
        "  Applied --> [*]\n",
        "  Applied --> [*]\n  Issued --> Suspended : fraudFlagRaised\n  Suspended --> Suspended : reminderSent\n",
    )
    found = kinds(write(tmp_path, text))
    assert ("dead-end", "Suspended", "") in found


def test_multiple_self_transitions_on_one_state(tmp_path):
    text = CLEAN.replace(
        "  Applied --> [*]\n",
        "  Applied --> [*]\n  Issued --> Issued : reminderSent / send reminder\n"
        "  Issued --> Issued : fraudFlagRaised / flag voucher\n",
    )
    found = kinds(write(tmp_path, text))
    assert ("multiple-self-transitions", "Issued", "") in found


def test_no_initial_state(tmp_path):
    text = "```mermaid\nstateDiagram-v2\n  A --> B : go\n  B --> [*]\n```\n"
    found = kinds(write(tmp_path, text))
    assert ("no-initial-state", "", "") in found


def test_missing_matrix_reports_every_gap(tmp_path):
    text = CLEAN.split("| State / event")[0]
    found = kinds(write(tmp_path, text))
    assert ("no-matrix", "", "") in found
    gaps = {(s, e) for k, s, e in found if k == "matrix-gap"}
    assert gaps == {
        ("Applied", "voucherValidated"), ("Applied", "expiryDateReached"),
        ("Expired", "voucherValidated"), ("Expired", "expiryDateReached"),
    }


def test_tbd_dash_and_blank_cells_are_gaps(tmp_path):
    text = CLEAN.replace(
        "| Applied | impossible (POS rejects applied codes, SH-02) | ignored (already used, SH-01) |",
        "| Applied | TBD (Q1) | - |",
    ).replace("| Expired | impossible (code is invalid, S-02) | impossible (fires once) |", "| Expired |  | ? |")
    found = kinds(write(tmp_path, text))
    gaps = {(s, e) for k, s, e in found if k == "matrix-gap"}
    assert len(gaps) == 4


def test_matrix_mismatch_when_cell_contradicts_diagram(tmp_path):
    text = CLEAN.replace("| Issued | → Applied [not expired]; else → Expired | → Expired |",
                         "| Issued | → Applied [not expired]; else → Expired | ignored (SH-01) |")
    found = kinds(write(tmp_path, text))
    assert ("matrix-mismatch", "Issued", "expiryDateReached") in found


def test_matrix_mismatch_when_cell_names_missing_transition(tmp_path):
    text = CLEAN.replace("| Applied | impossible (POS rejects applied codes, SH-02) |", "| Applied | → Issued |")
    found = kinds(write(tmp_path, text))
    assert ("matrix-mismatch", "Applied", "voucherValidated") in found


def test_guard_without_else(tmp_path):
    text = CLEAN.replace("  Issued --> Expired : voucherValidated [else] / reject\n", "").replace(
        "→ Applied [not expired]; else → Expired", "→ Applied [not expired]")
    found = kinds(write(tmp_path, text))
    assert ("guard-without-else", "Issued", "voucherValidated") in found
    fixed = text.replace("→ Applied [not expired] |", "→ Applied [not expired]; else impossible (S-02) |")
    assert ("guard-without-else", "Issued", "voucherValidated") not in kinds(write(tmp_path, fixed))


def test_ambiguous_transition(tmp_path):
    text = CLEAN.replace("Issued --> Expired : voucherValidated [else] / reject",
                         "Issued --> Expired : voucherValidated / reject")
    found = kinds(write(tmp_path, text))
    assert ("ambiguous-transition", "Issued", "voucherValidated") in found


def test_unknown_matrix_row_and_unclear_cell(tmp_path):
    text = CLEAN + "| Archived | ignored (x) | ignored (x) |\n"
    text = text.replace("| Applied | impossible (POS rejects applied codes, SH-02) |", "| Applied | nothing |")
    found = kinds(write(tmp_path, text))
    assert ("matrix-unknown-state", "Archived", "") in found
    assert ("matrix-unclear-cell", "Applied", "voucherValidated") in found


def test_states_table_is_not_mistaken_for_matrix(tmp_path):
    text = CLEAN.replace("| State / event |", "| State |  # not a matrix\n| --- |\n| Issued |\n\n| State / event |", 1)
    assert kinds(write(tmp_path, text)) == []


def test_display_names_notes_and_style_lines_are_accepted(tmp_path):
    text = CLEAN.replace(
        "  [*] --> Issued : redemptionApproved / create voucher\n",
        '  direction LR\n  %% comment\n  state "Issued voucher" as Issued\n'
        "  [*] --> Issued : redemptionApproved / create voucher\n"
        "  note right of Issued : a note\n  note left of Applied\n    multi-line\n  end note\n"
        "  classDef done fill:#eee\n  class Applied done\n",
    )
    assert kinds(write(tmp_path, text)) == []


@pytest.mark.parametrize("construct", [
    "  state Active {\n    A --> B\n  }\n",
    "  state check <<choice>>\n",
    "  state f <<fork>>\n",
])
def test_unsupported_constructs_exit_2(tmp_path, construct):
    text = CLEAN.replace("  Applied --> [*]\n", "  Applied --> [*]\n" + construct)
    proc = run_cli(str(write(tmp_path, text)))
    assert proc.returncode == 2
    assert "not supported" in proc.stderr


def test_unparseable_transition_exits_2(tmp_path):
    text = CLEAN.replace("  Applied --> [*]\n", "  Applied state --> [*]\n")
    assert run_cli(str(write(tmp_path, text))).returncode == 2


def test_no_state_block_and_missing_file_exit_2(tmp_path):
    assert run_cli(str(write(tmp_path, "# nothing\n\n```mermaid\nflowchart LR\n  a --> b\n```\n"))).returncode == 2
    assert run_cli(str(tmp_path / "missing.md")).returncode == 2


def test_block_option_and_raw_mmd_file(tmp_path):
    second = "```mermaid\nstateDiagram-v2\n  [*] --> A : make\n  A --> [*]\n```\n"
    path = write(tmp_path, CLEAN + "\n" + second)
    assert run_cli(str(path), "--block", "1").returncode == 0
    assert run_cli(str(path), "--block", "3").returncode == 2
    raw = write(tmp_path, "stateDiagram-v2\n  [*] --> A : make\n  A --> [*]\n", "machine.mmd")
    assert run_cli(str(raw)).returncode == 0


def test_print_matrix_keeps_explicit_cells_and_marks_unknown_tbd(tmp_path):
    text = CLEAN.replace("| Expired | impossible (code is invalid, S-02) | impossible (fires once) |",
                         "| Expired | impossible (code is invalid, S-02) | |")
    proc = run_cli(str(write(tmp_path, text)), "--print-matrix")
    assert proc.returncode == 0
    lines = proc.stdout.strip().splitlines()
    assert lines[0] == "| State / event | voucherValidated | expiryDateReached |"
    assert "| Issued | → Applied [not expired]; else → Expired | → Expired |" in lines
    assert "| Expired | impossible (code is invalid, S-02) | TBD |" in lines


def test_print_matrix_appends_else_tbd_for_guarded_cells(tmp_path):
    text = "```mermaid\nstateDiagram-v2\n  [*] --> A : make\n  A --> B : go [ready]\n  B --> [*]\n```\n"
    proc = run_cli(str(write(tmp_path, text)), "--print-matrix")
    assert "| A | → B [ready]; else TBD |" in proc.stdout


def test_skill_example_has_exactly_the_documented_gaps():
    found = kinds(SKILL / "examples" / "expected-output.md")
    assert found == [
        ("matrix-gap", "Reversed", "fraudHoldReleased"),
        ("matrix-gap", "Redeemed", "returnReceived"),
    ]


def test_asset_template_parses_and_has_one_placeholder_gap():
    found = kinds(SKILL / "assets" / "state-model.md")
    assert found == [("matrix-gap", "SecondState", "someEvent")]


def test_module_api_classify_cell():
    assert check_states.classify_cell("→ Posted") == check_states.TRANSITION
    assert check_states.classify_cell("-> Posted") == check_states.TRANSITION
    assert check_states.classify_cell("`ignored` (SH-01)") == check_states.IGNORED
    assert check_states.classify_cell("Impossible (x)") == check_states.IMPOSSIBLE
    assert check_states.classify_cell("TBD (Q1)") == check_states.GAP
    assert check_states.classify_cell(None) == check_states.GAP
    assert check_states.classify_cell("maybe") == check_states.UNCLEAR
