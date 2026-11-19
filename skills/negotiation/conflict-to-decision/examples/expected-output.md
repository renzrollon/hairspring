# RDR-001: Points expiry period

- Status: accepted
- Date: 2026-11-05
- Decision-makers: Mei Tan (SH-01, product owner)
- Consulted: Grace Lim (SH-03, Finance controller); Priya Raman (SH-07, Marketing manager)
- Informed: Daniel Ng (SH-06, Customer support lead); Wei Jie Chua (SH-08, Platform team tech lead)
- Conflict: CF-01 (interest)
- Technique: overruling; analysis aid: decision matrix
- Affected requirements: R-060, R-061
- Supersedes: none

## Context and Problem Statement

R-060 (from the programme terms draft, S-01) expires posted points 12 months after posting to limit the points liability; R-061 (Marketing, SH-07) asks for 18 months so occasional shoppers can reach the redemption minimum. Both are `must` and cannot hold for the same members. The period is printed in the programme terms, which must be final before launch. Which expiry period applies to posted points?

## Decision Drivers

### Constraints

| Constraint | Source |
| --- | --- |
| The expiry period is published in the programme terms, which must be final before launch | S-01 |

### Criteria

| Criterion | Weight | Agreed by | Agreed on |
| --- | --- | --- | --- |
| Points liability | 3 | Mei Tan, Grace Lim, Priya Raman | 2026-11-05 |
| Member engagement | 2 | Mei Tan, Grace Lim, Priya Raman | 2026-11-05 |
| Implementation effort | 1 | Mei Tan, Grace Lim, Priya Raman | 2026-11-05 |

### Facts and assumptions

| # | Statement | Kind | Source or owner to verify |
| --- | --- | --- | --- |
| 1 | Expiry counts from posting; points post 24 hours after purchase | fact | S-01 |
| 2 | The minimum redemption is 500 points | fact | S-01 |
| 3 | A longer expiry period raises the outstanding points liability | fact | SH-03 Grace Lim 2026-11-05 |
| 4 | Occasional shoppers do not reach 500 points within 12 months | assumption | SH-07 Priya Raman, from data warehouse figures |

## Considered Options

1. **A: 12 months**: one period for all members. Requirement changes: keep R-060, reject R-061.
2. **B: 18 months**: one period for all members. Requirement changes: keep R-061, reject R-060.
3. **C: 12 months, 18 months for Gold tier**: a variant by tier. Requirement changes: rewrite R-060 for non-Gold members, new `WHERE` requirement for Gold, reject R-061.

## Decision Outcome

Chosen option: "A: 12 months", because points liability carries the highest agreed weight and A scores best on it, while C adds a tier rule to expiry, member communication and the liability report for a small group of members.

| Decision-maker | Confirmed | Date |
| --- | --- | --- |
| Mei Tan (SH-01) | yes (session, then by email) | 2026-11-05 |

Dissent: Priya Raman (SH-07): occasional shoppers will lose points before reaching the redemption minimum; asks for an expiry reminder.

### Consequences

- Good, because the points liability stays bounded at the period Finance plans with (S-01).
- Good, because one rule applies to every member, so terms, app copy and support answers stay simple.
- Bad, because occasional shoppers may lose points before reaching 500 (assumption 4, to be verified).
- Bad, because Marketing's engagement goal is not met by this decision; the follow-up below addresses part of it.

### Confirmation

- R-060 is `agreed` and R-061 `rejected` in `requirements/requirements.csv`, both linked to RDR-001.
- `requirement-linter` reports no errors on R-060 and R-061.
- `testability-check` adds a verification row for R-060 in `requirements/verification.csv`.

## Pros and Cons of the Options

### A: 12 months

- Plus: lowest liability; matches the draft terms; no new rule.
- Minus: occasional shoppers may lose points.
- Interesting: an expiry reminder could soften the minus without changing the period.

### B: 18 months

- Plus: best for member engagement.
- Minus: highest liability; terms draft must change.
- Interesting: Finance would need a new liability forecast.

### C: 12 months, 18 months for Gold tier

- Plus: rewards the most loyal members; liability rises only for Gold.
- Minus: tier-dependent expiry in the service, the app and the liability report.
- Interesting: tier changes during the 12 months would need their own rule.

### Decision matrix

| Criterion | Weight | A: 12 months | B: 18 months | C: 12 months, 18 for Gold |
| --- | --- | --- | --- | --- |
| Points liability | 3 | 5 (15) | 2 (6) | 4 (12) |
| Member engagement | 2 | 2 (4) | 5 (10) | 4 (8) |
| Implementation effort | 1 | 5 (5) | 5 (5) | 2 (2) |
| **Weighted total** (max 30) | | **24** | **21** | **22** |

Scale: 1 to 5, 5 = best on the criterion. Scored by: Mei Tan, Grace Lim, Priya Raman, 2026-11-05.

## Requirement Updates

| Requirement | Change | Before | After | Applied |
| --- | --- | --- | --- | --- |
| R-060 | keep | Status proposed; Links empty | Status agreed; Links RDR-001 CF-01 | yes (2026-11-05) |
| R-061 | reject | Status draft; Links empty | Status rejected; Links RDR-001 CF-01 | yes (2026-11-05) |

## More Information

- Open questions: Do occasional shoppers reach 500 points within 12 months? (owner: SH-07, data warehouse figures)
- Follow-ups: Priya Raman to propose an expiry reminder requirement for `requirement-phrasing` (owner: SH-07)
- Review trigger: the data on assumption 4 contradicts it
- Related: CF-01 in `requirements/conflicts.md` (Status resolved, Decision RDR-001)
