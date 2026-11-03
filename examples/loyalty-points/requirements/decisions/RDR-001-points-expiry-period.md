# RDR-001: Points expiry period

- Status: proposed
- Date: 2026-11-03
- Decision-makers: Mei Tan (SH-01, Head of Loyalty, product owner and change authority)
- Consulted: Grace Lim (SH-03, Finance controller); Priya Raman (SH-07, Marketing manager)
- Informed: Customer support lead (SH-06); data platform team lead (SH-13, while D-01 is open)
- Conflict: CF-01 (interest)
- Technique: compromise (recommended by conflict-detector; not yet confirmed by the decision-maker); analysis aid: decision matrix
- Affected requirements: R-019
- Supersedes: none

## Context and Problem Statement

The programme terms draft v3 (S-01) and Finance (SH-03) set points to expire 12 months after posting, and R-019 is written that way; Marketing (SH-07) would like 18 months (BRIEF.md:60). One period applies to the same posted points, so both cannot hold, and the expiry rule must be settled before the terms are published and before expiry is built (open decision D-01 decides who builds it). How many months after posting do posted points expire?

## Decision Drivers

### Constraints

| Constraint | Source |
| --- | --- |
| The period becomes part of the programme terms that members are bound by once published | S-01 (draft v3) |
| Transaction data, including expiry transactions, is kept 7 years for audit (a separate subject, not the period itself) | R-036; S-05 (DRP-2024) |

### Criteria

| Criterion | Weight | Agreed by | Agreed on |
| --- | --- | --- | --- |
| Effect on the points liability Finance accounts for (BRIEF.md:35) | TBD | pending | pending |
| Effect on campaigns and member engagement (BRIEF.md:39) | TBD | pending | pending |
| Consistency with the programme terms that members read (S-01) | TBD | pending | pending |

The criteria are the drivers the two positions name; the decision-maker has not confirmed them, and no weight may be set or score given before she and the consulted parties agree them.

### Facts and assumptions

| # | Statement | Kind | Source or owner to verify |
| --- | --- | --- | --- |
| 1 | The programme terms draft v3 sets expiry at 12 months after posting | fact | S-01 via BRIEF.md:60 |
| 2 | Finance wants 12 months; Marketing would like 18 months | fact | BRIEF.md:60 |
| 3 | The legacy module expires points 12 months after posting, in a nightly job | fact | CAN-012, CAN-013 (inputs/legacy/sp_redeem_points.sql:35-37) |
| 4 | 2 of 12 tickets in the S-03 excerpt complain that points expired without warning | fact | CAN-018 (inputs/support-tickets-excerpt.csv:5, :11) |
| 5 | Whether the service or the data platform team runs expiry is not decided | fact | D-01 in `context.md` |
| 6 | A longer period increases the points that stay in the points liability | assumption | SH-03 Grace Lim to verify |
| 7 | A longer period helps campaigns and member engagement | assumption | SH-07 Priya Raman to verify |

## Considered Options

1. **12 months**: Finance's position and the S-01 draft. Requirement changes: R-019 kept as written.
2. **18 months**: Marketing's position. Requirement changes: R-019 rewritten to 18 months (same ID, through `requirement-phrasing`).
3. **Compromise period**: a period between the two positions, TBD from the parties (neither side has offered one). Requirement changes: R-019 rewritten to the agreed period.
4. **Variants**: different periods for different scopes; no scope has been named by anyone (TBD). Requirement changes: R-019 narrowed, plus one new `WHERE` requirement per variant.
5. **Defer**: keep R-019 at 12 months as a draft until the published terms (after draft v3) settle the period. Requirement changes: none now.

## Decision Outcome

Pending: decision by the product owner, Mei Tan (SH-01). The brief records the two positions but no decision; this run was non-interactive, so no option is chosen.

| Decision-maker | Confirmed | Date |
| --- | --- | --- |
| Mei Tan (SH-01) | pending | pending |

Dissent: none recorded (no decision yet)

### Consequences

- Good, because the conflict, both positions and the options are on record before the terms are published.
- Bad, because R-019 and the expiry notice (R-020) cannot become `agreed` and expiry cannot be built until the period is decided.

### Confirmation

- R-019 shows the chosen period, `Links` holds `RDR-001 CF-01`, and `conflicts.md` shows CF-01 `resolved` with `RDR-001`.
- `re-lint check --only-ids R-019` reports no errors after the update.

## Pros and Cons of the Options

### 12 months

- Plus: matches the S-01 draft and the legacy behavior, so nothing changes for members (facts 1, 3)
- Minus: Marketing's goal is not met (fact 2)
- Interesting: the expiry complaints in S-03 (fact 4) are about missing warnings, which R-020 addresses whatever the period

### 18 months

- Plus: Marketing's position (fact 2)
- Minus: the S-01 draft must change; the points liability effect is unverified (assumption 6)
- Interesting: members holding points longer may change the redemption pattern (not sourced)

### Compromise period

- Plus: both sides can give some
- Minus: no value has been offered; the requirements engineer must not propose one
- Interesting: needs the decision matrix weights agreed first

### Variants

- Plus: could serve both needs if a scope exists
- Minus: no scope has been named; adds configuration and member communication
- Interesting: would become `WHERE` requirements

### Defer

- Plus: no rework if the published terms differ from draft v3
- Minus: expiry stays unbuildable; Marketing's request stays open

### Decision matrix

Not used yet: criteria and weights are not agreed (see Criteria). Scoring before that would make the matrix invalid.

## Requirement Updates

| Requirement | Change | Before | After | Applied |
| --- | --- | --- | --- | --- |
| R-019 | keep (option 1 or 5) or rewrite (option 2, 3 or 4), depending on the outcome | Status draft; no Links column; Text "WHEN 12 months have passed since points were posted, the loyalty service shall expire those points." | Status `agreed` once the RDR is accepted; `Links` `RDR-001 CF-01` (needs a `Links` column, see More Information); Text with the chosen period | no |

## More Information

- Open questions: Which option does Mei Tan choose, and does she accept the decision matrix as the aid? (SH-01); Do Grace Lim and Priya Raman agree the criteria and weights before scoring? (SH-03, SH-07); Who runs expiry after go-live, D-01? (SH-01)
- Follow-ups: when the RDR is accepted, add a `Links` column to `requirements.csv` (optional attribute in `schema.json`) to record `RDR-001 CF-01` on R-019 (engineer); update R-020 if the expiry notice period depends on the outcome (engineer)
- Review trigger: publication of the programme terms after draft v3 (S-01)
- Related: CF-01 in `requirements/conflicts.md`; D-01 in `requirements/context.md`; CAN-012, CAN-013, CAN-018 in `requirements/candidates.csv`
