# Stories: Redeem points at checkout

| Field | Value |
| --- | --- |
| Epic | LOY-210 Redeem points at checkout |
| Source | S-06 (LOY-210, Mei Tan 2026-10-29); answers SH-01 2026-11-03 |
| Refined | 2026-11-03, Mei Tan (SH-01), user-story-refiner |
| Schema | requirements/schema.json |
| Definition of Ready | schema.json `definition_of_ready` (default items) |

## Summary

| Story | Title | Priority | INVEST | DoR | Acceptance criteria | Flags |
| --- | --- | --- | --- | --- | --- | --- |
| R-040 | Spend 500 points as an SGD 5 voucher at the till | must | 5/6 pass | not ready | 5 (2 unwanted behavior) | R-040.AC4 blocked (Q2); R-040.AC5 untestable |
| R-041 | Choose how many points to turn into a voucher | could | 5/6 pass | not ready | 4 (2 unwanted behavior) | R-041.AC2 blocked (Q1) |
| R-042 | Cancel an unused voucher | should | 5/6 pass | not ready | 3 (2 unwanted behavior) | R-042.AC1 blocked (Q5) |

## Slicing

| Order | Slice | Pattern | Valuable on its own because |
| --- | --- | --- | --- |
| 1 | R-040 Spend 500 points as an SGD 5 voucher at the till | Workflow steps (thinnest end-to-end path), business rule variation (one fixed value) | A member can spend points at the till for the first time; converting without spending would not be valuable alone |
| 2 | R-042 Cancel an unused voucher | Workflow steps (cancel) | Support resolves voucher complaints without a manual points adjustment |
| 3 | R-041 Choose how many points to turn into a voucher | Business rule variation (any amount from 500 points) | Members with large balances use more points per visit |
| later | Campaign vouchers | Data variation (voucher origin), after the spike | Waits for the spike "Campaign vouchers" |
| later | Voucher validation time at the till | Defer performance | Becomes a quality requirement via `/quality-requirements` (Q3) |

## R-040: Spend 500 points as an SGD 5 voucher at the till

<!-- paste-start R-040 -->
**Story:** As a member, I want to spend 500 of my posted points as an SGD 5 voucher at the till, so that my points reduce what I pay.

**Acceptance criteria**

**R-040.AC1: Convert 500 points** _(happy path)_
- **Given** a member with 1,200 posted points
- **When** the member asks the app for an SGD 5 voucher
- **Then** the app shows an SGD 5 voucher with a scannable code
- **And** the app shows a posted balance of 700 points

**R-040.AC2: Apply the voucher at the till** _(happy path)_
- **Given** a member holds an issued SGD 5 voucher
- **When** the cashier scans the voucher code at the POS
- **Then** the POS deducts SGD 5 from the purchase total
- **And** the voucher status becomes Applied

**R-040.AC3: Not enough posted points** _(unwanted behavior)_
- **Given** a member with 300 posted points and 400 pending points
- **When** the member asks the app for an SGD 5 voucher
- **Then** the app refuses the voucher
- **And** the app shows the posted balance of 300 points, the 500-point minimum and when the pending points post

**R-040.AC4: Loyalty service does not answer** _(unwanted behavior)_
- **Given** the loyalty service is not reachable from the POS
- **When** the cashier scans an issued voucher
- **Then** after TBD seconds the POS tells the cashier the voucher cannot be checked
- **And** the POS completes the sale without the voucher discount
- **And** the voucher stays Issued
- **Flag:** blocked by Q2 (POS timeout)

**R-040.AC5: First voucher for a new cashier** _(alternative)_
- **Given** a cashier who has not applied a voucher before
- **When** the cashier applies a member's voucher
- **Then** the cashier completes the checkout without asking for help
- **Flag:** untestable: "without asking for help" has no test setting or pass threshold; routed to testability-check

**Notes:** Source S-06 (LOY-210) · Priority must · Depends on none · Constraints TillPoint POS loyalty interface spec v2.1 (S-02) · Open questions Q2, Q4
<!-- paste-end R-040 -->

**INVEST**

| Criterion | Result | Evidence |
| --- | --- | --- |
| Independent | pass | First slice; needs no other story in this set |
| Negotiable | pass | States what the member gets; how the code is shown and scanned is left to the team |
| Valuable | pass | Benefit (points reduce what the member pays) differs from the goal |
| Estimable | pass | Q2 changes a timeout value, not what is built |
| Small | pass | Converting alone or applying alone would not be valuable; no pattern yields two valuable slices (team sizing rule not stated) |
| Testable | fail | R-040.AC5 is untestable as written |

**Definition of Ready**

| Item | Result | Evidence |
| --- | --- | --- |
| Has an ID, type, source, priority and rationale | pass | R-040, F, S-06 (LOY-210), must, rationale set |
| Passes re-lint check with no errors | pass | `re-lint check --only-ids R-040`: 0 errors |
| Has a verification method and a measurable acceptance criterion | fail | `Verification` empty until `testability-check` runs; R-040.AC5 untestable |
| Open questions are resolved or explicitly deferred with an owner | fail | Q2 open (SH-09); Q4 deferred with owner SH-01 |
| Dependencies and constraints are named | pass | Depends on none; constraint S-02 named |

## R-041: Choose how many points to turn into a voucher

<!-- paste-start R-041 -->
**Story:** As a member, I want to choose how many of my posted points to turn into a voucher, so that I can use more of my balance in one purchase.

**Acceptance criteria**

**R-041.AC1: Convert a larger amount** _(happy path)_
- **Given** a member with 2,000 posted points
- **When** the member asks the app for a voucher worth 1,500 points
- **Then** the app shows an SGD 15 voucher with a scannable code
- **And** the app shows a posted balance of 500 points

**R-041.AC2: Amount that is not a multiple of 100** _(alternative)_
- **Given** a member with 1,250 posted points
- **When** the member asks the app for a voucher worth 1,250 points
- **Then** TBD (Q1: an SGD 12.50 voucher, or a refusal of amounts that are not multiples of 100 points)
- **Flag:** blocked by Q1 (rounding rule)

**R-041.AC3: More points than posted** _(unwanted behavior)_
- **Given** a member with 2,000 posted points
- **When** the member asks the app for a voucher worth 2,500 points
- **Then** the app refuses the voucher
- **And** the app shows the posted balance of 2,000 points

**R-041.AC4: Below the minimum** _(unwanted behavior)_
- **Given** a member with 2,000 posted points
- **When** the member asks the app for a voucher worth 400 points
- **Then** the app refuses the voucher
- **And** the app shows the 500-point minimum

**Notes:** Source S-06 (LOY-210) · Priority could · Depends on R-040 · Constraints none · Open questions Q1
<!-- paste-end R-041 -->

**INVEST**

| Criterion | Result | Evidence |
| --- | --- | --- |
| Independent | fail | Needs the voucher flow of R-040; ordered after it |
| Negotiable | pass | No UI or technology prescribed |
| Valuable | pass | Benefit (more of the balance in one purchase) differs from the goal |
| Estimable | pass | Q1 decides one rule; both options are small and known |
| Small | pass | One rule variation; no further split yields value |
| Testable | pass | AC2 is blocked by Q1, not untestable |

**Definition of Ready**

| Item | Result | Evidence |
| --- | --- | --- |
| Has an ID, type, source, priority and rationale | pass | R-041, F, S-06 (LOY-210), could, rationale set |
| Passes re-lint check with no errors | pass | `re-lint check --only-ids R-041`: 0 errors |
| Has a verification method and a measurable acceptance criterion | fail | `Verification` empty until `testability-check` runs |
| Open questions are resolved or explicitly deferred with an owner | fail | Q1 open (SH-03) |
| Dependencies and constraints are named | pass | Depends on R-040; no constraints |

## R-042: Cancel an unused voucher

<!-- paste-start R-042 -->
**Story:** As a support agent, I want to cancel a member's unused voucher, so that the member gets the points back without a manual points adjustment.

**Acceptance criteria**

**R-042.AC1: Cancel an issued voucher** _(happy path)_
- **Given** a member's SGD 5 voucher with status Issued
- **When** the support agent cancels the voucher in the admin console
- **Then** the voucher status becomes Cancelled
- **And** the member's posted balance increases by 500 points
- **And** the returned points expire on TBD (Q5: their original expiry date or a new one)
- **Flag:** blocked by Q5 (expiry of returned points)

**R-042.AC2: Voucher already applied** _(unwanted behavior)_
- **Given** a member's voucher with status Applied
- **When** the support agent tries to cancel the voucher
- **Then** the admin console refuses the cancellation
- **And** the voucher stays Applied

**R-042.AC3: Cancelled voucher scanned at the till** _(unwanted behavior)_
- **Given** a voucher with status Cancelled
- **When** the cashier scans the voucher code at the POS
- **Then** the POS shows that the voucher is cancelled
- **And** the POS deducts nothing from the purchase total

**Notes:** Source S-06 (LOY-210) · Priority should · Depends on R-040 · Constraints none · Open questions Q5, Q6
<!-- paste-end R-042 -->

**INVEST**

| Criterion | Result | Evidence |
| --- | --- | --- |
| Independent | fail | Needs issued vouchers from R-040; ordered after it |
| Negotiable | pass | No UI or technology prescribed |
| Valuable | pass | Benefit (no manual adjustment) differs from the goal |
| Estimable | pass | Q5 and Q6 change details, not scope |
| Small | pass | One workflow step |
| Testable | pass | AC1 is blocked by Q5, not untestable |

**Definition of Ready**

| Item | Result | Evidence |
| --- | --- | --- |
| Has an ID, type, source, priority and rationale | pass | R-042, F, S-06 (LOY-210), should, rationale set |
| Passes re-lint check with no errors | pass | `re-lint check --only-ids R-042`: 0 errors |
| Has a verification method and a measurable acceptance criterion | fail | `Verification` empty until `testability-check` runs |
| Open questions are resolved or explicitly deferred with an owner | fail | Q5 open (SH-03); Q6 open (SH-06) |
| Dependencies and constraints are named | pass | Depends on R-040; no constraints |

## Spikes

| Spike | Question to answer | Output | Time box | Owner |
| --- | --- | --- | --- | --- |
| Campaign vouchers | How are campaign vouchers issued and validated in the legacy module (S-04), and which rules differ from member vouchers? | Note in `requirements/elicitation/` and a story draft for campaign vouchers | TBD (team decides) | Priya Raman (SH-07) with the loyalty squad |

## Not stories

| Statement | Source | It is | Routed to |
| --- | --- | --- | --- |
| "Make it fast." | S-06 (LOY-210) | Quality requirement without a target (voucher validation time at the till) | Q3; suggest `/quality-requirements` |
| "The POS checks the voucher with us." | S-06 (LOY-210) | Constraint: the voucher validation call is defined by the TillPoint POS loyalty interface spec v2.1 (S-02) | `constraints-register`; named in R-040 Notes |
| "If the member doesn't have enough points the app should show a nice error." | S-06 (LOY-210) | Not a story on its own; "nice" is a weak word | Rewritten as R-040.AC3 with the content the app shows |

## Open questions

| # | Question | Recommended answer | Owner | Affects | Status |
| --- | --- | --- | --- | --- | --- |
| Q1 | May members convert amounts that are not multiples of 100 points (for example 1,250 points into SGD 12.50)? | Only multiples of 100 | SH-03 Grace Lim | R-041.AC2 | open |
| Q2 | How many seconds does the POS wait for the voucher validation answer before it completes the sale without the voucher? | Use the timeout in the TillPoint spec (S-02) | SH-09 TillPoint integration manager | R-040.AC4 | open |
| Q3 | What voucher validation time at the till keeps checkout from getting slower at peak? | Measure today's checkout time first; run `/quality-requirements` | SH-02 Arjun Pillai | quality requirement, not yet written | open |
| Q4 | When do vouchers expire, and what happens to the points of an expired voucher? | Same as points (12 months, S-01 draft) | SH-01 Mei Tan | expiry criteria, not yet written | deferred |
| Q5 | Do points returned by a cancelled voucher keep their original expiry date? | Keep the original date | SH-03 Grace Lim | R-042.AC1 | open |
| Q6 | Must a support agent give a reason code when canceling a voucher, as for points adjustments? | Yes, the same reason codes | SH-06 Daniel Ng | R-042 | open |
