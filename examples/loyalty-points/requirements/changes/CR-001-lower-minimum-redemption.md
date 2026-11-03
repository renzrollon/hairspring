# CR-001: Lower the minimum redemption from 500 to 300 points

| Field | Value |
| --- | --- |
| ID | CR-001 |
| Status | draft |
| Requested by | Priya Raman (SH-07, Marketing manager), 2026-11-03 |
| Source | Change request in the sample loop's scenario script (no ticket key) |
| Change authority | product-owner: Mei Tan (SH-01) |
| Route | backlog item for the product owner |
| Trace coverage | trace matrix: requirements/trace/trace.csv, built 2026-11-03 |
| Links | R-013, R-024, R-025 |

## 1. Requested change

> Lower the minimum redemption from 500 to 300 points.

| Statement | Before | After |
| --- | --- | --- |
| R-013 | IF a member requests a redemption of fewer than 500 points, THEN the loyalty service shall reject the redemption request. | IF a member requests a redemption of fewer than 300 points, THEN the loyalty service shall reject the redemption request. |
| R-024 | As a member, I want to spend 500 of my posted points as an SGD 5 voucher at the till, so that my points reduce what I pay. | TBD: keep the first slice at 500 points as an SGD 5 voucher, or rewrite it to 300 points as an SGD 3 voucher (Q2) |
| R-025 | As a member, I want to choose how many of my posted points, from 500 upward, to turn into a voucher, so that my points reduce more of what I pay. | As a member, I want to choose how many of my posted points, from 300 upward, to turn into a voucher, so that my points reduce more of what I pay. |
| Programme rule | Minimum redemption 500 points (BRIEF.md:61) | Minimum redemption 300 points in the programme terms (S-01) |

## 2. Reason

TBD: the request gives no reason. Priya Raman's stated interests are campaigns and bonus-point promotions (BRIEF.md:39); whether the change serves a campaign or the whole programme is open question 1.

## 3. Impact set

| # | Item | Kind | Impact | Evidence | Found by |
| --- | --- | --- | --- | --- | --- |
| 1 | R-013 | requirement | text change | `requirements/requirements.csv:14`; `re-lint trace impact` hop 0 | trace |
| 2 | R-024 | requirement | text change or review (Q2) | `requirements/requirements.csv:25`; hop 0 | trace |
| 3 | R-025 | requirement | text change | `requirements/requirements.csv:26`; hop 0 | trace |
| 4 | R-014 | requirement | review: no text change (300 points give an SGD 3 voucher under the same rate) | hop 2 via `src/loyalty/redemption.py` | trace |
| 5 | R-038 | requirement | review: no text change | hop 2 via `src/loyalty/redemption.py` | trace |
| 6 | `src/loyalty/redemption.py` | code | re-implement: `MIN_REDEMPTION_POINTS` | `src/loyalty/redemption.py:5` (`# @req R-013`), value at :6 | trace |
| 7 | `tests/test_redemption.py::test_r_013_rejects_fewer_than_500_points` | test | re-test: boundary moves to 299 and 300 | `tests/test_redemption.py:6` | trace |
| 8 | `tests/test_redemption.py::test_r_024_ac1_convert_500_points`, `::test_r_024_ac3_fewer_than_500_posted_points`, `::test_r_024_ac4_pending_points_do_not_count` | test | re-test if R-024 is rewritten (Q2) | `tests/test_redemption.py:24`, `:29`, `:35` | trace |
| 9 | `tests/test_redemption.py::test_r_025_ac1_convert_a_chosen_amount`, `::test_r_025_ac3_more_points_than_posted` | test | review: values above 500 still pass; add a 300-point case | `tests/test_redemption.py:41`, `:46` | trace |
| 10 | `requirements/stories/redeem-points-at-checkout.md` (R-024.AC1, R-024.AC3, R-024.AC4, R-025 story sentence, Summary and Slicing rows) | work product | update document through `/user-story-refiner` | lines 15, 23, 24, 29, 32, 36, 48, 108 | search |
| 11 | `requirements/verification.csv` rows R-013, R-024, R-025 | work product | update: R-013 criterion uses 499 and 500 | `requirements/verification.csv:14`, `:25`, `:26` | search |
| 12 | S-01 programme terms and conditions, draft v3 | source | update document: the minimum is a programme rule members read | BRIEF.md:61; `requirements/sources.csv` S-01 | user |
| 13 | S-14 PRD excerpt, line 13 ("at least 500 points") | source | update document | `inputs/prd-redeem-at-checkout.md:13` | search |
| 14 | Customer mobile app (`context.md` rows 4 and 5) | interface | inform the app team: any text or check that shows the minimum must change (open question 4) | `requirements/context.md` rows 4, 5 | user |
| 15 | SH-01 Mei Tan (decides), SH-03 Grace Lim (points liability), SH-06 Daniel Ng (member questions), SH-12 legal counsel (terms) | stakeholder | inform | `requirements/stakeholders.md` | user |

Not impacted, checked: CAN-001 and the legacy rule at `inputs/legacy/sp_redeem_points.sql:6` (the module is being replaced; the candidate stays as history); classification batch 2026-11-03 row 3 (historical batch, never edited); R-018 (5,000-point adjustment threshold, a different rule that a search for "500" also hits).

## 4. Conflicts and dependencies

| Item | Conflicts with or depends on | Note | Next step |
| --- | --- | --- | --- |
| Programme rule (BRIEF.md:61) | S-01 programme terms | The terms must change before or with the requirement; whoever owns the terms (SH-12, not yet named) must agree | Open question 3 |
| Points liability | SH-03 Grace Lim | No stated position on the minimum; a lower minimum may change the redemption pattern Finance accounts for (unverified) | Open question 5; register with `conflict-detector` only if Finance objects |
| R-024 first slice | stories Q6 (priority) | If R-024 stays at 500, the first slice and the rule disagree on the minimum shown to members | Decide Q2 together with this CR |

No stakeholder position in `stakeholders.md`, `conflicts.md` or `decisions/` contradicts the request today, so no conflict was registered.

## 5. Options

| Option | What changes | Effort (relative) | Risk | Assumptions |
| --- | --- | --- | --- | --- |
| 0 | No change (reject or defer) | n/a | low: none of the risk factors apply | Marketing's request stays open; members still need 500 points for a first voucher |
| A | Minimum 300 points for every redemption: R-013 and R-025 rewritten, R-024 reviewed (Q2), constant and tests changed, stories and verification rows updated, S-01 and S-14 updated, the app team informed | M (proposed by the agent) | medium: a source document (S-01) must be updated | The minimum lives in one constant (`src/loyalty/redemption.py:6`); the customer mobile app reads the minimum from the service and does not hard-code it (open question 4) |
| B | Minimum 300 points only while a campaign named by Marketing runs: R-013 kept, a new `WHERE` requirement for the campaign minimum, campaign set-up defined first | M (proposed by the agent) | medium: S-01 must describe the campaign rule; campaign set-up is undefined (review F-03) | Marketing's reason is a campaign (open question 1); the campaign set-up requirements exist before this is built |

## 6. Recommendation

Decide after open questions 1 and 5 are answered: if the reason is a campaign, option B keeps the programme rule stable; if Marketing wants the change for every member, option A is the smaller change (one rule row, one constant, two story rows). This is the agent's recommendation; Mei Tan (SH-01) decides.

## 7. Draft for the change authority

**CR-001: Lower the minimum redemption from 500 to 300 points**

- **Problem:** Marketing (SH-07) asks to lower the minimum redemption from 500 to 300 points; the reason is not stated yet.
- **Change:** option A (minimum 300 for every redemption) or option B (300 only during a named campaign); see section 5.
- **Acceptance criteria:** a redemption request of 299 points is rejected and one of 300 points is accepted when the member has at least 300 posted points; the app and the programme terms show the same minimum.
- **Impacted IDs:** R-013, R-024, R-025 (text); R-014, R-038 (review).
- **Size:** M (proposed by the agent, both options).
- **Links:** `requirements/changes/CR-001-lower-minimum-redemption.md`, `requirements/trace/trace.csv`.

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

| Requirement | Change | Text before | Text after | Version | Status |
| --- | --- | --- | --- | --- | --- |
| R-013 | text change (option A) | IF a member requests a redemption of fewer than 500 points, THEN the loyalty service shall reject the redemption request. | IF a member requests a redemption of fewer than 300 points, THEN the loyalty service shall reject the redemption request. | 2 (needs a `Version` column, not in the schema yet) | unchanged while draft |
| R-025 | text change (option A) | ... from 500 upward ... | ... from 300 upward ... | 2 | unchanged while draft |
| R-024 | TBD (Q2) | | | | |

## 10. Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | Why does Marketing want the lower minimum: for a campaign, or for every member? | SH-07 Priya Raman | Option A or B |
| 2 | Does the first slice R-024 stay at 500 points as an SGD 5 voucher, or become 300 points as an SGD 3 voucher? | SH-01 Mei Tan | R-024 and its acceptance criteria |
| 3 | Who updates the programme terms (S-01), and must the change be announced to members before it applies? | SH-01 Mei Tan, with legal counsel (SH-12, not yet named) | S-01 |
| 4 | Does the customer mobile app show or check the minimum itself? | App team owner (not yet named; `stakeholders.md` open question 6) | Customer mobile app interface |
| 5 | Does a lower minimum change how Finance accounts for the points liability? | SH-03 Grace Lim | Option A, B |
