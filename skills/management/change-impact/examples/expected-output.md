# CR-001: Lower the minimum redemption from 500 to 300 points

| Field | Value |
| --- | --- |
| ID | CR-001 |
| Status | draft |
| Requested by | Priya Raman (SH-07), 2026-11-02 |
| Source | Email to the loyalty team, 2026-11-02 |
| Change authority | product-owner (default; no `schema.json`): Mei Tan (SH-01) |
| Route | Backlog item for the product owner |
| Trace coverage | trace matrix: requirements/trace/trace.csv, built 2026-11-03 |
| Links | R-041 |

## 1. Requested change

> For the year-end campaign we want members to redeem from 300 points instead of 500. Many members sit between 300 and 500 points and never redeem. The redeem screen in the app says "Redeem from 500 points". Can we have it live by 1 December?

| Statement | Before | After |
| --- | --- | --- |
| R-041 | IF a member requests a redemption of fewer than 500 posted points, THEN the loyalty service shall reject the redemption with the reason "below minimum". | IF a member requests a redemption of fewer than 300 posted points, THEN the loyalty service shall reject the redemption with the reason "below minimum". |
| Duration | Permanent rule | TBD: permanent, or only for the year-end campaign (Q3) |
| Wanted by | n/a | 2026-12-01 (requester's date) |

## 2. Reason

Many members hold between 300 and 499 posted points and never redeem (Priya Raman, SH-07, 2026-11-02). The size of that group is not stated (Q5).

## 3. Impact set

| # | Item | Kind | Impact | Evidence | Found by |
| --- | --- | --- | --- | --- | --- |
| 1 | R-041 | requirement | text change | requirements/requirements.csv:7 | trace |
| 2 | S-01 programme terms, draft v3 | source | update document: the terms state the 500-point minimum | trace.csv: R-041 derives-from S-01 (requirements/requirements.csv:7) | trace |
| 3 | src/loyalty/redeem.py | code | re-implement: `MIN_REDEMPTION_POINTS` | src/loyalty/redeem.py:12, src/loyalty/redeem.py:13 | trace, search |
| 4 | tests/test_redeem.py::test_r_041_rejects_below_minimum | test | re-test: new boundary values (299 rejected, 300 accepted) | tests/test_redeem.py:9 | trace |
| 5 | Customer mobile app, redeem screen copy | interface | update: "Redeem from 500 points" | requirements/context.md (customer mobile app); requester's email | user |
| 6 | POS voucher validation | interface | review: voucher value per 100 points is unchanged, so no interface change is expected | requirements/context.md (POS) | user |
| 7 | Grace Lim (SH-03), Finance | stakeholder | inform: earlier redemptions change the points-liability run-off | requirements/requirements.csv:7 (source S-01, programme terms) | user |

## 4. Conflicts and dependencies

| Item | Conflicts with or depends on | Note | Next step |
| --- | --- | --- | --- |
| Option B | R-004 (bonus campaigns), status proposed | A campaign-only minimum needs campaign rules that are not agreed yet | Decide on R-004 first if option B is chosen |
| Finance position | not stated | No conflict is registered yet. If Finance objects (Q1), register it with `conflict-detector` | Ask Q1 before the decision |

## 5. Options

| Option | What changes | Effort (relative) | Risk | Assumptions |
| --- | --- | --- | --- | --- |
| 0 | No change (reject or defer) | n/a | low: no factor applies | Members with 300–499 points keep not redeeming; the campaign goal is not met |
| A | R-041: minimum 300, permanent. Terms S-01, the constant in `redeem.py`, the test and the app copy change | M (proposed by the agent) | medium: source document S-01 must be updated; reopens implemented R-041 | The minimum is one constant (`src/loyalty/redeem.py:13`); the app reads the minimum from the API (Q2); someone outside the team updates the terms (Q4) |
| B | R-041 keeps 500; new requirement: WHERE a campaign with a lowered minimum is active, the lower minimum applies | M (proposed by the agent) | medium: as A, plus a dependency on R-004, which is still proposed | Campaign configuration exists by 2026-12-01 (not today: R-004 is proposed) |

## 6. Recommendation

Option A, if Finance accepts the liability effect (Q1). It is one rule change with a clear test, and it does not depend on the unagreed campaign requirement R-004. Choose B only if the requester answers Q3 with "campaign only". This is the agent's recommendation; Mei Tan (SH-01) decides.

## 7. Draft for the change authority

**Backlog item for Mei Tan (SH-01)**

- **Title:** CR-001: Lower the minimum redemption from 500 to 300 points
- **Problem:** Members with 300–499 posted points never redeem (SH-07, 2026-11-02).
- **Change:** R-041 minimum from 500 to 300 posted points (option A).
- **Acceptance criteria:**
  - Given a member with 350 posted points, when the member redeems 300 points, then a SGD 3 voucher is issued.
  - Given a member with 350 posted points, when the member redeems 299 points, then the redemption is rejected with the reason "below minimum".
- **Impacted:** R-041, S-01 terms, `src/loyalty/redeem.py`, `tests/test_redeem.py`, app redeem screen copy.
- **Size:** M (proposed by the agent; to be confirmed by the platform team, SH-08).
- **Wanted by:** 2026-12-01 (requester).
- **Links:** `requirements/changes/CR-001-lower-minimum-redemption.md`

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

| ID | Change | Text before | Text after | Version | Status |
| --- | --- | --- | --- | --- | --- |
| R-041 | text change (option A, proposed) | IF a member requests a redemption of fewer than 500 posted points, THEN the loyalty service shall reject the redemption with the reason "below minimum". | IF a member requests a redemption of fewer than 300 posted points, THEN the loyalty service shall reject the redemption with the reason "below minimum". | 1 → 2 (column to be added) | implemented → agreed (re-implement and re-verify) |

## 10. Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| Q1 | Is the effect of earlier redemptions on the points liability acceptable? | SH-03 Grace Lim | Options A and B |
| Q2 | Does the app read the minimum from the API, or is "500" hard-coded in the redeem screen copy? | App team (owner TBD) | Effort of A and B |
| Q3 | Should the lower minimum be permanent, or only for the year-end campaign? | SH-07 Priya Raman | Choice between A and B |
| Q4 | Who updates the programme terms (S-01), and by when? | SH-01 Mei Tan | Release date |
| Q5 | How many members hold between 300 and 499 posted points? | SH-07 Priya Raman | Reason, value of the change |
