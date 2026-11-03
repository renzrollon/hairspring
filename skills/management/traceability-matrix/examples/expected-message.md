# Expected final message

Trace matrix rebuilt with `re-lint trace build`: `requirements/trace/trace.csv` (22 links), `requirements/trace/trace.md` and `requirements/trace/gaps.json`. No `schema.json` was found, so the default trace globs were used.

**Coverage:** 7 requirements in scope. All 7 have a source, 3 have code and a test, and 2 have a decision or ADR. The tracer reports 8 gaps.

## Triage

| Severity | Item | Why | Next step | Owner |
| --- | --- | --- | --- | --- |
| fix first | none | Every `implemented` or `verified` requirement (R-001, R-002, R-041) has a test | none | none |
| real gap | R-003 | Agreed, verification `test`, no test and no implementation reference | Write the posting test. Cite R-003 in the posting job once it exists | QA, tech lead |
| real gap | R-005 | Agreed, verification `test`, no test and no implementation reference | Same as R-003, for the return reversal | QA, tech lead |
| real gap | R-100 | Agreed, no implementation reference. Verification is `inspection`, so this is not a test gap | Link the retention configuration or the inspection record in `Links` | SH-03 Grace Lim |
| stale citation | R-022 in `src/loyalty/notify.py:5` and `tests/test_notify.py:4` | R-022 was withdrawn by RDR-002 (SMS replaced by push) | Remove the SMS sender and its test, or confirm with SH-01 that they serve another requirement | developer, SH-01 Mei Tan |
| stale citation | R-045 in `tests/test_redeem.py:18` | R-045 is not registered | If partial redemption is wanted, register it with `requirement-phrasing`; otherwise fix the ID | SH-01 Mei Tan |
| informational | R-080 | Proposed, target still `TBD`; no test expected yet | Suggest `/quality-requirements` to resolve the TBD | SH-02 Arjun Pillai |
| informational | `tests/test_redeem.py::test_redeem_issues_voucher` | The test cites no requirement. It checks voucher issuing, which has no registered requirement in this register | Ask SH-01 whether a voucher-issuing requirement is missing (then `requirement-phrasing`) before citing anything | SH-01 Mei Tan |
| informational | `src/loyalty/history.py` | The file cites no requirement. It probably serves the points history, which has no requirement here | Same question as above | tech lead |

The last two rows come from comparing the files under the globs with `trace.csv`; the tracer does not report unlinked files.

## Draft issues (for `/issue-sync` or your tracker)

| Title | Evidence | Owner role |
| --- | --- | --- |
| R-003: no test and no implementation reference (trace gap) | requirements/requirements.csv:4 | QA |
| R-005: no test and no implementation reference (trace gap) | requirements/requirements.csv:5 | QA |
| R-100: link the retention evidence (trace gap) | requirements/requirements.csv:9 | requirement owner |
| R-022: withdrawn but still implemented and tested | src/loyalty/notify.py:5, tests/test_notify.py:4 | developer |
| R-045: test cites an unregistered requirement | tests/test_redeem.py:18 | product owner |

No tests, code or requirement statuses were changed.
