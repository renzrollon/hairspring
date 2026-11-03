# Prioritization: January release (app and admin console)

| Field | Value |
| --- | --- |
| Date | 2026-11-03 |
| Decision this serves | Scope of the January app and admin console release |
| Decision-maker | Mei Tan (SH-01) |
| Technique | Wiegers, because several stakeholders must accept the result and cost differs a lot between items |
| Matrix | requirements/priorities.csv |
| Command | `python3 <skill-dir>/scripts/prioritize.py requirements/priorities.csv --method wiegers --weights benefit=2,penalty=1,cost=1,risk=0.5 --out requirements/priorities.csv` |

## 1. Goals and constraints

| Kind | Statement | Source |
| --- | --- | --- |
| Goal | Pick the requirements for the January release | SH-01 Mei Tan, 2026-10-30 |
| Constraint | Capacity: "about four of these in January" (team's own unit) | SH-08 Wei Jie Chua, 2026-11-02 |
| Fixed item | R-100: must without scoring, because the retention policy requires it | S-05 |

## 2. Criteria

| Criterion | Meaning in this run | Scale |
| --- | --- | --- |
| Benefit | Value to members, stores or support if the item ships in January | 1–9, relative |
| Penalty | Harm (complaints, fraud exposure, lost trust) if it does not ship in January | 1–9, relative |
| Cost | Effort for the platform and app teams | 1–9, relative |
| Risk | Technical or delivery risk of building it in January | 1–9, relative |

## 3. Stakeholders

| ID | Name / role | Scores | Decides |
| --- | --- | --- | --- |
| SH-01 | Mei Tan, Head of Loyalty | Benefit, Penalty (joint session) | yes |
| SH-07 | Priya Raman, Marketing manager | Benefit, Penalty (joint session) | no |
| SH-06 | Daniel Ng, Customer support lead | Benefit, Penalty (joint session) | no |
| SH-08 | Wei Jie Chua, Platform team tech lead | Cost, Risk | no |

## 4. Items

Level of abstraction: requirements (feature-sized). Items: 6 from the command line, all in `requirements/requirements.csv`.

| Excluded item | Reason |
| --- | --- |
| R-100 | Fixed must (retention policy S-05); not ranked |

## 5. Weights

Agreed before scoring: yes

| Weight | Value | Agreed by | Date |
| --- | --- | --- | --- |
| benefit | 2 | Mei Tan (SH-01) | 2026-10-30 |
| penalty | 1 | Mei Tan (SH-01) | 2026-10-30 |
| cost | 1 | Mei Tan (SH-01) | 2026-10-30 |
| risk | 0.5 | Mei Tan (SH-01) | 2026-10-30 |

## 6. Result

| Band | Rank | ID | Title | Score | Tie |
| --- | --- | --- | --- | --- | --- |
| top | 1 | R-063 | Second approver for large adjustments | 1.043 | |
| top | 2 | R-021 | Points history in the app | 0.856 | |
| middle | 3 | R-026 | Push notification when points are posted | 0.697 | |
| middle | 4 | R-061 | Expiry reminder before points expire | 0.642 | tie, do not over-interpret |
| middle | 5 | R-043 | Redeem a voucher in the app | 0.622 | tie, do not over-interpret |
| bottom | 6 | R-004 | Bonus campaign multiplier | 0.484 | |

Reading the result: scores rest on ordinal judgments, so read the bands, not the decimals. Items marked `tie, do not over-interpret` are equal for this decision.

- The capacity of about four items puts the cut line inside the R-061 / R-043 tie. The 0.020 difference must not decide it. Choose between them on other grounds, for example the year-end expiry wave (R-061) against the redemption volume in the app (R-043).
- R-043 has the highest benefit and penalty of all the items, but also the highest cost and risk. A smaller first slice of R-043 could move it up. That is a scope question for `/user-story-refiner`, not a reason to change the scores.

## Disputed items

None.

## Decision

| Field | Value |
| --- | --- |
| Cut line | Proposed: R-063, R-021, R-026 in; fourth slot R-061 or R-043 (tie); R-004 out |
| Decided by | pending: Mei Tan (SH-01) |
| Date | |
| Priority attribute updated | no |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| Q1 | Which of the tied R-061 and R-043 takes the fourth January slot? | SH-01 Mei Tan | Cut line |
| Q2 | After the cut, should the `Priority` of these items in `requirements.csv` change (for example, in-scope items to `must`)? | SH-01 Mei Tan | `Priority` attribute |
