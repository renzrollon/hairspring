"""One positive and one negative case (at least) per lint rule."""
from __future__ import annotations

import pytest

from relint_helpers import csv_text, make_row
from re_lint import lint, reqio


@pytest.fixture(scope="module")
def config():
    return lint.build_config(reqio.DEFAULT_SCHEMA)


def rules_for(text, config):
    return [rule for rule, _, _, _ in lint.check_text(text, config)]


def matches_for(text, rule, config):
    return [match for r, _, match, _ in lint.check_text(text, config) if r == rule]


CLEAN = [
    "WHEN the POS sends a completed purchase event, the loyalty service shall create a pending points transaction.",
    "WHILE a member account is on fraud hold, the loyalty service shall reject redemption requests for that account.",
    "WHERE a bonus campaign is active for the store, the loyalty service shall apply the campaign multiplier to earned points.",
    "IF the fraud engine places a hold on a purchase, THEN the loyalty service shall keep the points of that purchase in pending state until the fraud engine releases the hold.",
    "WHILE the POS is in offline mode, WHEN the cashier scans a member QR code, the POS shall queue the purchase event for later delivery.",
    "The updated balance shall be available to the customer mobile app within 2 seconds.",
    "The loyalty service shall back up the ledger every 24 hours.",
    "As a member, I want to see my balance so that I can plan a redemption.",
]


@pytest.mark.parametrize("text", CLEAN)
def test_clean_requirements_have_no_findings(text, config):
    assert lint.check_text(text, config) == []


# ---------------------------------------------------------------- weak-word

@pytest.mark.parametrize("text,word", [
    ("The app shall show the balance quickly.", "quickly"),
    ("The checkout shall be user-friendly.", "user-friendly"),
    ("The POS shall print the receipt as soon as possible.", "as soon as possible"),
    ("The POS shall accept card, QR, etc.", "etc."),
    ("The app shall send a push and/or an email.", "and/or"),
    ("The service shall be ROBUST.", "ROBUST"),
    ("The service shall retry some requests.", "some"),
])
def test_weak_word_fires(text, word, config):
    assert matches_for(text, "weak-word", config) == [word]


@pytest.mark.parametrize("text", [
    "The POS shall serve breakfast orders.",          # word boundary: breakfast is not fast
    "The service shall log something to the audit trail.",  # something is not some
    'The banner shall read "Earn points fast".',     # quoted text is not linted
    "The POS shall fast-track VIP members.",          # hyphenated compound is not the weak word
])
def test_weak_word_does_not_fire(text, config):
    assert "weak-word" not in rules_for(text, config)


def test_weak_word_reported_once_per_row(config):
    assert matches_for("The app shall be fast and the API shall be fast.", "weak-word", config) == ["fast"]


# ---------------------------------------------------------------- universal-quantifier

@pytest.mark.parametrize("text,word", [
    ("The loyalty service shall notify all members.", "all"),
    ("The POS shall always print a receipt.", "always"),
    ("The POS shall accept any card.", "any"),
    ("The loyalty service shall be available at any time.", "any"),
    ("Any member shall be able to redeem points.", "Any"),
    ("The service shall log each and every refund.", "each and every"),
    ("The app shall show everything about the account.", "everything"),
])
def test_universal_quantifier_fires(text, word, config):
    assert matches_for(text, "universal-quantifier", config) == [word]


@pytest.mark.parametrize("text", [
    "IF any payment fails, THEN the POS shall retry the payment.",   # existential, in a condition
    "WHEN all items are scanned, the POS shall show the total.",     # condition clause
    "The loyalty service shall back up the ledger every 24 hours.",  # frequency
    "The loyalty service shall recalculate tiers every night.",
    "The POS shall allow the cashier to scan items.",                # allow is not all
    "The POS shall not charge the member at all.",
    "The POS shall reject the voucher without any delay.",
])
def test_universal_quantifier_does_not_fire(text, config):
    assert "universal-quantifier" not in rules_for(text, config)


# ---------------------------------------------------------------- passive-voice

@pytest.mark.parametrize("text,phrase", [
    ("The voucher shall be validated.", "be validated"),
    ("Member data shall be stored in the EU.", "be stored"),
    ("Members are notified by email.", "are notified"),            # "by email" is not an actor
    ("The receipt shall be automatically printed.", "be automatically printed"),
    ("The export shall be written to the archive.", "be written"),  # irregular participle
    ("The balance shall be being recalculated.", "be being recalculated"),
])
def test_passive_voice_fires(text, phrase, config):
    assert matches_for(text, "passive-voice", config) == [phrase]


@pytest.mark.parametrize("text", [
    "Member data shall be stored by the loyalty service in the EU.",           # actor named
    "The updated balance shall be available to the app within TBD seconds.",   # adjective
    "The member shall be able to redeem points.",
    "The loyalty service shall create a transaction when the purchase is completed.",  # condition
    "The loyalty service shall reverse points that were earned on a refunded purchase.",  # relative
    "WHILE the account is locked, the app shall hide the redeem button.",      # condition region
    "The cut-off date shall be the date to be confirmed by finance.",          # placeholder
    "The POS shall keep the drawer open.",
    "As a cashier, I want the receipt to be printed so that the member has proof.",  # story form
    "WHEN the POS sends a voucher, the loyalty service shall return whether the voucher can be applied.",
])
def test_passive_voice_does_not_fire(text, config):
    assert "passive-voice" not in rules_for(text, config)


# ---------------------------------------------------------------- nominalization

@pytest.mark.parametrize("text,phrase", [
    ("The loyalty service shall support the validation of vouchers.", "the validation of"),
    ("The service shall perform processing of refunds.", "processing of"),
    ("The service shall start the processing.", "processing"),
    ("The tool shall provide management of tiers.", "management of"),
])
def test_nominalization_fires(text, phrase, config):
    assert matches_for(text, "nominalization", config) == [phrase]


@pytest.mark.parametrize("text", [
    "The loyalty service shall validate the voucher code.",
    "IF the service stops processing, THEN the service shall resume processing within 5 minutes.",
])
def test_nominalization_does_not_fire(text, config):
    assert "nominalization" not in rules_for(text, config)


# ---------------------------------------------------------------- incomplete-condition

@pytest.mark.parametrize("text", [
    "WHEN the user logs in, the balance",
    "WHILE the POS is offline.",
    "IF the card is declined, the POS shall display an error.",   # IF without THEN
    "IF the card is declined, THEN the balance",                   # THEN without a response
    "WHILE offline, IF the card is declined, the POS shall queue the sale.",  # inner IF needs THEN
])
def test_incomplete_condition_fires(text, config):
    assert "incomplete-condition" in rules_for(text, config)


@pytest.mark.parametrize("text", [
    "If the card is declined, the POS shall display an error.",  # prose "If" is not the EARS keyword
    "WHEN the member opens the app and scans the code, the POS shall show the balance.",
    "The POS shall print a receipt when the sale completes.",
])
def test_incomplete_condition_does_not_fire(text, config):
    assert "incomplete-condition" not in rules_for(text, config)


def test_incomplete_condition_replaces_missing_obligation(config):
    rules = rules_for("WHEN the user logs in, the balance", config)
    assert "missing-obligation" not in rules


# ---------------------------------------------------------------- missing-obligation

@pytest.mark.parametrize("text", [
    "The system displays the balance.",
    "The member can redeem points.",
    'The banner shows "you shall pass".',  # the only "shall" is quoted
])
def test_missing_obligation_fires(text, config):
    assert "missing-obligation" in rules_for(text, config)


@pytest.mark.parametrize("text", [
    "The system shall display the balance.",
    "The system should display the balance.",
    "The system may display the balance.",
    "The system must display the balance.",
    "As a member, I want to see my balance.",
    "As an operator I need an export of the ledger.",
])
def test_missing_obligation_does_not_fire(text, config):
    assert "missing-obligation" not in rules_for(text, config)


def test_can_gets_a_specific_message(config):
    messages = [m for r, _, _, m in lint.check_text("The member can redeem points.", config) if r == "missing-obligation"]
    assert '"can"' in messages[0]


# ---------------------------------------------------------------- future-tense

def test_future_tense_fires(config):
    assert matches_for("The system will log every refund.", "future-tense", config) == ["will"]
    assert matches_for("The POS won't store card numbers.", "future-tense", config) == ["won't"]


@pytest.mark.parametrize("text", [
    "The loyalty service shall notify the member who will lose points.",  # will is not the obligation
    "As a member, I want points that will not expire.",
    "The member may cancel the subscription at will.",
])
def test_future_tense_does_not_fire(text, config):
    assert "future-tense" not in rules_for(text, config)


# ---------------------------------------------------------------- compound-requirement

@pytest.mark.parametrize("text", [
    "The system shall export the file and email the user.",
    "The system shall export the file. The system shall email the user.",
    "The POS shall print the receipt and shall open the drawer.",
    "The system shall create the invoice or send it to the member.",
])
def test_compound_fires(text, config):
    assert "compound-requirement" in rules_for(text, config)


@pytest.mark.parametrize("text", [
    "The system shall display the balance and the points history.",
    "The loyalty service shall record the member ID and store ID.",
    "The system shall flag transactions that may be fraudulent.",          # epistemic may
    "The loyalty service shall create a transaction when the member pays and leaves the store.",
    "IF the payment should fail, THEN the POS shall retry the payment.",   # should in the condition
    "The campaign shall start on 1 May 2027.",
])
def test_compound_does_not_fire(text, config):
    assert "compound-requirement" not in rules_for(text, config)


# ---------------------------------------------------------------- open-tbd

@pytest.mark.parametrize("text,marker", [
    ("The app shall show the balance within TBD ms.", "TBD"),
    ("The app shall show the balance within tbc ms.", "tbc"),
    ("The app shall show the balance within ?? ms.", "??"),
    ("The app shall show XXX.", "XXX"),
])
def test_open_tbd_fires(text, marker, config):
    assert matches_for(text, "open-tbd", config) == [marker]


def test_open_tbd_does_not_fire(config):
    assert "open-tbd" not in rules_for("The app shall show the TBDX code within 2 s.", config)


def test_text_that_is_only_a_placeholder_gets_only_open_tbd(config):
    assert rules_for("TBD", config) == ["open-tbd"]


# ---------------------------------------------------------------- structural rules (workspace runs)

def findings(workspace, rows=None, header=None, args=()):
    if rows is not None:
        workspace.register(rows, header)
    found, _ = lint.lint(paths=list(args))
    return found


def test_duplicate_id(workspace):
    found = findings(workspace, [make_row("R-001"), make_row("R-002"), make_row("R-001")])
    dupes = [f for f in found if f.rule == "duplicate-id"]
    assert len(dupes) == 1 and dupes[0].line == 4 and "requirements/requirements.csv:2" in dupes[0].message
    assert not [f for f in findings(workspace, [make_row("R-001"), make_row("R-002")]) if f.rule == "duplicate-id"]


def test_duplicate_id_across_registers_in_one_run(workspace):
    a = workspace.register([make_row("R-001")], name="a/requirements.csv")
    b = workspace.register([make_row("R-001")], name="b/requirements.csv")
    found, _ = lint.lint(paths=[str(a), str(b)])
    assert [f.rule for f in found] == ["duplicate-id"]


def test_invalid_id(workspace):
    found = findings(workspace, [make_row("REQ12"), make_row("R-01"), make_row("R-001")])
    assert sorted(f.id for f in found if f.rule == "invalid-id") == ["R-01", "REQ12"]


def test_invalid_id_honors_schema_pattern(workspace):
    workspace.schema({"ids": {"requirement": {"prefix": "REQ-", "digits": 4}}})
    found = findings(workspace, [make_row("REQ-0001"), make_row("R-001")])
    assert [f.id for f in found if f.rule == "invalid-id"] == ["R-001"]


def test_missing_attribute_row_and_header(workspace):
    found = findings(workspace, [make_row(Source="")])
    assert [(f.rule, f.match) for f in found] == [("missing-attribute", "Source")]
    header = [c for c in ["ID", "Type", "Text", "Source", "Priority", "Status"]]
    found = findings(workspace, [make_row()], header=header)
    assert [(f.rule, f.match, f.line, f.id) for f in found] == [("missing-attribute", "Rationale", 1, "")]


def test_invalid_enum(workspace):
    found = findings(workspace, [make_row(Type="NFR", Priority="Must")])
    messages = {f.match: f.message for f in found if f.rule == "invalid-enum"}
    assert set(messages) == {"NFR", "Must"}
    assert 'did you mean "must"' in messages["Must"]
    assert not findings(workspace, [make_row(Type="Q", Priority="could", Status="verified")])


def test_tbd_is_never_missing_attribute_or_invalid_enum(workspace):
    found = findings(workspace, [make_row(Priority="TBD", Rationale="TBD", Source="tbd")])
    assert {f.rule for f in found} == {"open-tbd"}
    assert sorted(f.message for f in found) == [
        'open placeholder "TBD" in Priority', 'open placeholder "TBD" in Rationale',
        'open placeholder "tbd" in Source']


def test_unregistered_source(workspace):
    workspace.write("requirements/sources.csv", "ID,Name\nS-01,Ticket\n")
    workspace.write("requirements/stakeholders.md", "| ID | Name |\n| --- | --- |\n| SH-01 | Mei |\n")
    found = findings(workspace, [make_row("R-001", Source="S-01, SH-01"), make_row("R-002", Source="S-19 (SH-04)")])
    assert sorted(f.match for f in found if f.rule == "unregistered-source") == ["S-19", "SH-04"]


def test_unregistered_source_needs_a_source_register(workspace):
    assert not findings(workspace, [make_row(Source="S-19")])


def test_unregistered_interview_needs_elicitation_folder(workspace):
    workspace.write("requirements/sources.csv", "ID,Name\nS-01,Ticket\n")
    assert not findings(workspace, [make_row(Source="I-02")])
    workspace.write("requirements/elicitation/interview-ops.md", "# Interview I-01\n")
    found = findings(workspace, [make_row(Source="I-02"), make_row("R-002", Source="I-01")])
    assert [(f.id, f.match) for f in found] == [("R-001", "I-02")]


def test_register_drift_markdown_and_detail_csv(workspace):
    workspace.register([make_row("R-001"), make_row("R-002", text="The POS shall print a receipt.")])
    workspace.write("requirements/stories/earn.md",
                    "| ID | Text |\n| --- | --- |\n"
                    f"| R-001 | {make_row()['Text']} |\n"
                    "| R-002 | The POS shall print two receipts. |\n")
    workspace.write("requirements/verification.csv",
                    "ID,Text,Method\nR-001,The old text,test\nR-002,The POS shall print a ...,test\n")
    found = findings(workspace)
    drift = sorted((f.file, f.id) for f in found if f.rule == "register-drift")
    assert drift == [("requirements/stories/earn.md", "R-002"), ("requirements/verification.csv", "R-001")]


def test_markdown_partial_views_get_only_text_rules(workspace):
    path = workspace.write("requirements/stories/earn.md",
                           "| ID | Text | Status | Risk |\n| --- | --- | --- | --- |\n"
                           "| R-031 | The app displays the balance. | agreed -> To Do | 4 |\n"
                           "| R-031 | dup in a report | draft | 2 |\n| R-031.AC1 | Given ... | | |\n"
                           "| R-040 (line 11) | not an ID | | |\n")
    found, _ = lint.lint(paths=[str(path)])
    assert sorted((f.rule, f.id) for f in found) == [("missing-obligation", "R-031")]


def test_markdown_register_gets_every_rule(workspace):
    path = workspace.write("requirements/register.md",
                           "| ID | Type | Text | Source | Priority | Status | Rationale |\n"
                           "| --- | --- | --- | --- | --- | --- | --- |\n"
                           "| R-001 | F | The POS shall print a receipt. | S-01 | must | draft | x |\n"
                           "| R-001 | F | The POS shall print a receipt. | S-01 | high | draft | x |\n"
                           "| REQ9 | F | The POS shall print a receipt. |  | must | draft | x |\n")
    found, _ = lint.lint(paths=[str(path)])
    assert sorted((f.rule, f.id) for f in found) == [
        ("duplicate-id", "R-001"), ("invalid-enum", "R-001"), ("invalid-id", "REQ9"), ("missing-attribute", "REQ9")]


def test_default_scan_skips_historical_records(workspace):
    workspace.register([make_row("R-001")])
    workspace.write("requirements/changes/CR-001-x.md", "| ID | Text |\n| --- | --- |\n| R-001 | The old text. |\n")
    workspace.write("requirements/decisions/RDR-001-x.md", "| ID | Text |\n| --- | --- |\n| R-001 | Older text. |\n")
    assert findings(workspace) == []


def test_withdrawn_rows_only_get_structural_rules(workspace):
    found = findings(workspace, [make_row("R-001", text="The app is fast.", Status="withdrawn", Priority="high")])
    assert [f.rule for f in found] == ["invalid-enum"]


def test_story_form_skips_obligation_future_and_passive(workspace):
    story = "As a member, I want my points to be shown quickly so that I will trust the app."
    found = findings(workspace, [make_row(text=story)])
    assert [f.rule for f in found] == ["weak-word"]


def test_registry_is_complete_and_stable():
    assert list(lint.RULES) == [
        "weak-word", "universal-quantifier", "passive-voice", "nominalization", "incomplete-condition",
        "missing-obligation", "future-tense", "compound-requirement", "open-tbd", "duplicate-id",
        "invalid-id", "missing-attribute", "invalid-enum", "unregistered-source", "register-drift"]
    defaults = {r.id: r.severity for r in lint.RULES.values()}
    assert defaults["weak-word"] == "error" and defaults["nominalization"] == "info"
    assert defaults["passive-voice"] == "warning" and defaults["register-drift"] == "warning"
    for rule in lint.RULES.values():
        assert rule.summary and rule.example and rule.hint and rule.kind in ("text", "structure")
    assert lint.TEXT_RULES == tuple(list(lint.RULES)[:9])


def test_csv_text_helper_roundtrip():
    assert csv_text([make_row()]).splitlines()[0] == "ID,Type,Text,Source,Priority,Status,Rationale"
