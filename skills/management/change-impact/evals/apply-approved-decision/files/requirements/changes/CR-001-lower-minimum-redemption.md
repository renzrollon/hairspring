# CR-001: Lower the minimum redemption from 500 to 300 points

| Field | Value |
| --- | --- |
| ID | CR-001 |
| Status | submitted |
| Requested by | Priya Raman (SH-07), 2026-11-02 |
| Source | Email to the loyalty team, 2026-11-02 |
| Change authority | product-owner: Mei Tan (SH-01) |
| Route | Backlog item for the product owner |
| Trace coverage | trace matrix: requirements/trace/trace.csv, built 2026-11-03 |
| Links | R-041 |

## 1. Requested change

> For the year-end campaign we want members to redeem from 300 points instead of 500.

| Statement | Before | After |
| --- | --- | --- |
| R-041 | IF a member requests a redemption of fewer than 500 posted points, THEN the loyalty service shall reject the redemption with the reason "below minimum". | IF a member requests a redemption of fewer than 300 posted points, THEN the loyalty service shall reject the redemption with the reason "below minimum". |

## 3. Impact set

| # | Item | Kind | Impact | Evidence | Found by |
| --- | --- | --- | --- | --- | --- |
| 1 | R-041 | requirement | text change | requirements/requirements.csv:3 | trace |
| 2 | src/loyalty/redeem.py | code | re-implement | src/loyalty/redeem.py:3 | trace |
| 3 | tests/test_redeem.py::test_r_041_rejects_below_minimum | test | re-test | tests/test_redeem.py:4 | trace |

## 5. Options

| Option | What changes | Effort (relative) | Risk | Assumptions |
| --- | --- | --- | --- | --- |
| 0 | No change | n/a | low | Campaign goal not met |
| A | R-041 minimum 300, permanent | M (confirmed by platform team, 2026-11-03) | medium: terms S-01 must change; reopens implemented R-041 | One constant in redeem.py |

## 8. Decision

| Field | Value |
| --- | --- |
| Decision | pending |
| Option | |
| Decided by | |
| Date | |
| Conditions | |
| Decision record | none |

## 9. Requirement updates

Applied: no (requirement rows are changed only after an approved decision)

## 10. Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
