"""Tests for skills/specification/domain-model/scripts/check_glossary.py (stdlib + pytest)."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "specification" / "domain-model"
SCRIPT = SKILL / "scripts" / "check_glossary.py"

_spec = importlib.util.spec_from_file_location("check_glossary", SCRIPT)
check_glossary = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(check_glossary)

GLOSSARY = """# Glossary

| Term | Definition | Synonyms | Abbreviation | Owner |
| --- | --- | --- | --- | --- |
| Member | A person in the programme. | Customer; Account holder | — | SH-01 |
| Points transaction | Points for one purchase. | — | PT | SH-01 |
| **Voucher** | A single-use discount. | | | SH-01 |
| Points balance | The points a member holds. | Balance | | SH-01 |
| Cashier | Operates the POS. | | | SH-02 |
"""

MODEL = """# Domain model

```mermaid
classDiagram
  direction LR
  class Member {
    pointsBalance: Points
  }
  class PointsTransaction {
    +Points points
  }
  class Voucher["Voucher"]
  Member "1" --> "0..*" PointsTransaction : holds
  Member "1" --> "0..*" Voucher : redeems
```
"""


def make(tmp_path: Path, model: str = MODEL, glossary: str = GLOSSARY) -> Path:
    ws = tmp_path / "requirements"
    (ws / "models").mkdir(parents=True)
    (ws / "glossary.md").write_text(glossary, encoding="utf-8")
    path = ws / "models" / "domain-model.md"
    path.write_text(model, encoding="utf-8")
    return path


def run_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8", cwd=cwd
    )


def findings(path: Path, *extra: str) -> list:
    proc = run_cli(str(path), "--format", "json", *extra)
    assert proc.returncode in (0, 1), proc.stderr
    return [(f["kind"], f["name"]) for f in json.loads(proc.stdout)["findings"]]


def test_help_exits_zero():
    proc = run_cli("--help")
    assert proc.returncode == 0
    assert "--glossary" in proc.stdout and "--ignore" in proc.stdout


def test_default_glossary_next_to_models_and_term_as_attribute(tmp_path):
    path = make(tmp_path)
    proc = run_cli(str(path), "--format", "json")
    data = json.loads(proc.stdout)
    assert data["classes"] == ["Member", "PointsTransaction", "Voucher"]
    assert "Points balance -> Member.pointsBalance" in data["terms_as_attributes"]
    assert [(f["kind"], f["name"]) for f in data["findings"]] == [("term-without-class", "Cashier")]
    assert proc.returncode == 1


def test_ignore_makes_it_clean(tmp_path):
    proc = run_cli(str(make(tmp_path)), "--ignore", "Cashier")
    assert proc.returncode == 0, proc.stdout
    assert "0 finding(s)" in proc.stdout


def test_class_without_term(tmp_path):
    model = MODEL.replace("  Member \"1\" --> \"0..*\" Voucher : redeems\n",
                          "  Member \"1\" --> \"0..*\" Voucher : redeems\n  Store \"1\" --> \"0..*\" PointsTransaction : records\n")
    assert ("class-without-term", "Store") in findings(make(tmp_path, model), "--ignore", "Cashier")


def test_synonym_class_and_duplicate_concept(tmp_path):
    model = MODEL.replace("  class Voucher", "  class Customer\n  class AccountHolder\n  class Voucher")
    found = findings(make(tmp_path, model), "--ignore", "Cashier")
    assert ("class-named-after-synonym", "Customer") in found
    assert ("class-named-after-synonym", "AccountHolder") in found
    assert ("duplicate-concept", "Member") in found


def test_abbreviation_counts_as_alternative_name(tmp_path):
    model = MODEL.replace("class PointsTransaction {", "class PT {").replace(
        "Member \"1\" --> \"0..*\" PointsTransaction : holds", "Member \"1\" --> \"0..*\" PT : holds")
    assert ("class-named-after-synonym", "PT") in findings(make(tmp_path, model), "--ignore", "Cashier")


def test_enumerations_are_not_checked(tmp_path):
    model = MODEL.replace("  class Voucher", "  class PointsTransactionState {\n    <<enumeration>>\n    Pending\n  }\n  class Voucher")
    assert findings(make(tmp_path, model), "--ignore", "Cashier") == []


def test_plural_and_case_insensitive_matching(tmp_path):
    glossary = GLOSSARY.replace("| **Voucher** |", "| vouchers |")
    assert findings(make(tmp_path, glossary=glossary), "--ignore", "Cashier") == []


def test_er_diagram(tmp_path):
    model = """```mermaid
erDiagram
  MEMBER ||--o{ POINTS_TRANSACTION : holds
  MEMBER ||--o{ VOUCHER : redeems
  VOUCHER }o--|{ POINTS_TRANSACTION : "uses points of (TBD)"
  MEMBER {
    Points pointsBalance
  }
  STORE {
    Text name
  }
```
"""
    found = findings(make(tmp_path, model), "--ignore", "Cashier")
    assert found == [("class-without-term", "STORE")]


def test_csv_glossary(tmp_path):
    path = make(tmp_path)
    csv_glossary = tmp_path / "glossary.csv"
    csv_glossary.write_text(
        "Term,Definition,Synonyms\nMember,x,Customer\nPoints transaction,x,\nVoucher,x,\nPoints balance,x,\n",
        encoding="utf-8",
    )
    proc = run_cli(str(path), "--glossary", str(csv_glossary))
    assert proc.returncode == 0, proc.stdout


def test_other_mermaid_blocks_and_relationship_kinds(tmp_path):
    model = """```mermaid
flowchart LR
  a --> b
```

```mermaid
classDiagram
  class Member
  class Voucher
  class PointsTransaction
  Member <|-- Cashier
  Voucher *-- PointsTransaction
  Voucher o-- Member
  Voucher ..> Member
  Member : +pointsBalance
  note for Member "a note"
```
"""
    assert findings(make(tmp_path, model)) == []


def test_parse_errors_exit_2(tmp_path):
    bad = make(tmp_path, "```mermaid\nclassDiagram\n  this is not mermaid ???\n```\n")
    assert run_cli(str(bad)).returncode == 2
    assert run_cli(str(tmp_path / "missing.md")).returncode == 2


def test_no_diagram_or_no_glossary_table_exit_2(tmp_path):
    path = make(tmp_path, "# nothing here\n")
    assert run_cli(str(path)).returncode == 2
    path2 = tmp_path / "other" / "requirements" / "models" / "domain-model.md"
    path2.parent.mkdir(parents=True)
    path2.write_text(MODEL, encoding="utf-8")
    (path2.parent.parent / "glossary.md").write_text("# Glossary\n\nNo table yet.\n", encoding="utf-8")
    assert run_cli(str(path2)).returncode == 2


def test_missing_glossary_exits_2(tmp_path):
    path = tmp_path / "solo" / "domain-model.md"
    path.parent.mkdir(parents=True)
    path.write_text(MODEL, encoding="utf-8")
    assert run_cli(str(path), cwd=tmp_path).returncode == 2


def test_skill_example_reports_documented_findings():
    model = SKILL / "examples" / "expected-output.md"
    glossary = SKILL / "examples" / "input.md"
    first = findings(model, "--glossary", str(glossary))
    assert first == [
        ("class-without-term", "Store"),
        ("class-without-term", "Tier"),
        ("term-without-class", "Return window"),
        ("term-without-class", "Cashier"),
    ]
    second = findings(model, "--glossary", str(glossary), "--ignore", "Return window,Cashier")
    assert second == [("class-without-term", "Store"), ("class-without-term", "Tier")]


GLOSSARY_SKILL_FORMAT = """# Glossary: loyalty-points

## Terms

| Term | Definition | Synonyms | Homonym notes | Abbreviation | Owner | Status | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Member | A person in the programme. | customer (code: `Customer` class, `customer_id`; tickets LOY-204, LOY-205), account holder (ticket LOY-202): avoid | | | SH-01 | proposed | x |
| Points transaction | One ledger entry. | | Not the POS sale: say Purchase. | | SH-01 | proposed | x |
| Voucher | A discount. | | | | SH-01 | agreed | x |
| Loyalty card | The old plastic card. | | | | SH-02 | deprecated | x |
| Point of sale | The till system. | | | POS | SH-02 | proposed | x |

## Findings

| # | Kind | Words | Evidence | Proposed resolution | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | synonym | customer | x | y | SH-01 | open |
"""


def test_glossary_skill_format_notes_and_deprecated(tmp_path):
    model = MODEL.replace("  class Voucher", "  class Customer\n  class LoyaltyCard\n  class POS\n  class Voucher")
    found = findings(make(tmp_path, model, GLOSSARY_SKILL_FORMAT))
    assert ("class-named-after-synonym", "Customer") in found
    assert ("class-named-after-synonym", "LoyaltyCard") in found
    assert ("class-named-after-synonym", "POS") in found
    assert ("duplicate-concept", "Member") in found
    assert not any(kind == "term-without-class" for kind, _ in found)


def test_split_list_drops_notes():
    cell = "customer (code: `Customer` class, `customer_id`; tickets LOY-204), account holder (LOY-202): avoid"
    assert check_glossary._split_list(cell) == ["customer", "account holder"]
    assert check_glossary._split_list("—") == []
    assert check_glossary._split_list("Sale; Bonus campaign") == ["Sale", "Bonus campaign"]


def test_norm_helper():
    assert check_glossary.norm("Points transaction") == check_glossary.norm("POINTS_TRANSACTION")
    assert check_glossary.norm("PointsTransaction") == "pointstransaction"
    assert check_glossary.norm("Balance (redeemable)") == "balance"
