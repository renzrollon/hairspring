# Input: loyalty-points repo snapshot (nightly trace run)

Prompt: "Build the trace matrix and tell me what is missing before the January release."

The workspace has no `schema.json`, so the default trace globs apply. `requirements/sources.csv` registers S-01, S-02, S-05 and S-06. `requirements/stakeholders.md` registers SH-02.

## `requirements/requirements.csv`

```csv
ID,Type,Text,Source,Priority,Status,Rationale,Verification,Links
R-001,F,"WHEN the POS sends a completed purchase event, the loyalty service shall create a pending points transaction for the member.",S-02,must,verified,Core earning flow.,test,
R-002,F,"WHEN the loyalty service creates a pending points transaction, the loyalty service shall award 1 point per SGD 1 of the purchase amount, rounded down per transaction.",S-01,must,implemented,Earning rule in the programme terms.,test,
R-003,F,"WHEN 24 hours have passed since the purchase, the loyalty service shall post the pending points to the member's balance.",S-01,must,agreed,Return window before points become usable.,test,
R-005,F,"IF the POS reports a return within 24 hours of the purchase, THEN the loyalty service shall reverse the pending points of the original transaction.",S-01,must,agreed,Points must not survive a returned purchase.,test,
R-022,F,"WHEN the loyalty service posts points, the loyalty service shall send the member an SMS with the new balance.",S-06,could,withdrawn,Replaced by the push notification (RDR-002).,,RDR-002
R-041,F,"IF a member requests a redemption of fewer than 500 posted points, THEN the loyalty service shall reject the redemption with the reason ""below minimum"".",S-01,must,implemented,Minimum redemption in the programme terms.,test,
R-080,Q,"WHEN the POS requests voucher validation, the loyalty service shall respond within TBD ms at the 95th percentile under year-end peak load.",SH-02,must,proposed,Checkout must not get slower (I-02).,test,
R-100,C,The loyalty service shall retain points transaction records for 7 years.,S-05,must,agreed,Audit retention under DRP-2024.,inspection,RDR-001
```

## Citations elsewhere in the repo

| File | Line | Text |
| --- | --- | --- |
| `requirements/decisions/RDR-001-retention-vs-pdpa.md` | 3 | `Requirements: R-100` |
| `requirements/decisions/RDR-002-notification-channel.md` | 3 | `Requirements: R-022` |
| `docs/adr/0003-voucher-validation-cache.md` | 7 | `Drivers: R-080` |
| `src/loyalty/earn.py` | 8 | `# @req R-001` |
| `src/loyalty/earn.py` | 21 | `# @req R-002` |
| `src/loyalty/redeem.py` | 12 | `# @req R-041` |
| `src/loyalty/notify.py` | 5 | `# @req R-022` |
| `tests/test_earn.py` | 6 | `def test_r_001_creates_pending_transaction():` |
| `tests/test_earn.py` | 14 | `def test_r_002_rounds_down_per_transaction():` |
| `tests/test_redeem.py` | 9 | `def test_r_041_rejects_below_minimum():` |
| `tests/test_redeem.py` | 18 | `def test_r_045_partial_redemption():` |
| `tests/test_notify.py` | 4 | `def test_r_022_sms_after_posting():` |
| `tests/test_redeem.py` | 24 | `def test_redeem_issues_voucher():` (no requirement ID) |
| `src/loyalty/history.py` | n/a | No requirement ID in the file |

## `git log --oneline`

```text
3f9c2ab feat(redeem): reject redemptions below the minimum (R-041) (#212)
a7d01e4 feat(earn): create a pending transaction per purchase event (R-001)
9e41b70 chore: bump dependencies
```

## Command run

```sh
python3 <skill-dir>/scripts/trace_matrix.py build
python3 <skill-dir>/scripts/trace_matrix.py gaps --format json
```

Outputs: `expected-output.csv` (`requirements/trace/trace.csv`), `expected-output.md` (`requirements/trace/trace.md`), `expected-message.md` (the final message, with triage and issue drafts). The `change-impact` example reads this `trace.csv`; that is the hand-off this example demonstrates.
