# Stories: Redeem points at checkout

| Field | Value |
| --- | --- |
| Epic | Redeem points at checkout (no tracker key) |
| Source | S-14 (PRD excerpt, `inputs/prd-redeem-at-checkout.md`), `requirements/classification.md` batch 2026-11-03, BRIEF.md:61 and BRIEF.md:70 |
| Refined | 2026-11-03, platform-team engineer (non-interactive; nobody answered), user-story-refiner |
| Schema | requirements/schema.json |
| Definition of Ready | schema.json `definition_of_ready` (10 items: base, iterative, explorative, customer-specific, criticality) |

## Summary

| Story | Title | Priority | INVEST | DoR | Acceptance criteria | Flags |
| --- | --- | --- | --- | --- | --- | --- |
| R-024 | Spend 500 points as an SGD 5 voucher at the till | TBD | 5/6 pass | not ready | 7 (5 unwanted behavior) | R-024.AC7 blocked (Q1) |
| R-025 | Choose how many points to turn into a voucher | TBD | 4/6 pass | not ready | 3 (1 unwanted behavior) | R-025.AC2 blocked (Q2) |
| R-026 | Push notification when a voucher is issued | should | 3/6 pass | not ready | 2 (1 unwanted behavior) | R-026.AC1 blocked (Q3); R-026.AC2 blocked (Q4) |

## Slicing

| Order | Slice | Pattern | Valuable on its own because |
| --- | --- | --- | --- |
| 1 | R-024 Spend 500 points as an SGD 5 voucher at the till | Workflow steps (thinnest end-to-end path), business rule variation (one fixed value) | A member can spend points at the till for the first time; converting without spending would not be valuable alone |
| 2 | R-025 Choose how many points to turn into a voucher | Business rule variation (any amount from 500 points) | Members with more than 500 posted points use more of them in one voucher |
| 3 | R-026 Push notification when a voucher is issued | Workflow steps (confirmation) | Members learn that the voucher exists without opening the app; the benefit is still TBD (Q5) |
| later | Voucher validation time at the till | Defer performance | A quality requirement via `/quality-requirements`, not an acceptance criterion |
| later | Expired vouchers at the till | Business rule variation | Waits for the voucher expiry period (glossary open question 3) |

## R-024: Spend 500 points as an SGD 5 voucher at the till

<!-- paste-start R-024 -->
**Story:** As a member, I want to spend 500 of my posted points as an SGD 5 voucher at the till, so that my points reduce what I pay.

**Acceptance criteria**

**R-024.AC1: Convert 500 points** _(happy path)_
- **Given** a member with 800 posted points
- **When** the member asks the app for an SGD 5 voucher
- **Then** the service issues a voucher worth SGD 5
- **And** the member's points balance shows 300 posted points

**R-024.AC2: Apply the voucher at the till** _(happy path)_
- **Given** an issued voucher worth SGD 5
- **When** the TillPoint POS requests validation of the voucher
- **Then** the service returns the voucher as valid with a value of SGD 5
- **And** the voucher's state is Applied

**R-024.AC3: Fewer than 500 posted points** _(unwanted behavior)_
- **Given** a member with 450 posted points
- **When** the member asks the app for an SGD 5 voucher
- **Then** the service issues no voucher
- **And** the member's points balance still shows 450 posted points

**R-024.AC4: Pending points do not count** _(unwanted behavior)_
- **Given** a member with 300 posted points and 400 pending points
- **When** the member asks the app for an SGD 5 voucher
- **Then** the service issues no voucher
- **And** the member's points balance still shows 300 posted points

**R-024.AC5: Voucher already applied** _(unwanted behavior)_
- **Given** a voucher in state Applied
- **When** the TillPoint POS requests validation of the same voucher
- **Then** the service rejects the validation request

**R-024.AC6: Unknown voucher code** _(unwanted behavior)_
- **Given** no voucher exists with the scanned code
- **When** the TillPoint POS requests validation of that code
- **Then** the service rejects the validation request as not found

**R-024.AC7: Service does not answer the till** _(unwanted behavior)_
- **Given** an issued voucher worth SGD 5
- **When** the service does not answer the validation request within the POS timeout
- **Then** TBD (Q1: the sale completes without the discount and the voucher stays Issued, or the cashier retries)
- **Flag:** blocked by Q1 (behavior at the till when the service is slow or down)

**Notes:** Source S-14 · Priority TBD · Depends on none · Constraints S-02 (TillPoint POS loyalty interface spec v2.1), S-05 · Open questions Q1, Q6 · Business rules R-013, R-014, R-015, R-016
<!-- paste-end R-024 -->

**INVEST**

| Criterion | Result | Evidence |
| --- | --- | --- |
| Independent | pass | Needs earning and posting (R-001, R-004) only, which are separate requirements, not unbuilt stories of this epic |
| Negotiable | pass | No UI element or technology in the goal; the Redis idea is under *Not stories* |
| Valuable | pass | Benefit (points reduce what the member pays) differs from the goal |
| Estimable | fail | Q1 (behavior when the service does not answer the till) changes what is built at the POS interface |
| Small | pass | No sizing rule is set; splitting the conversion from the till step leaves no slice valuable on its own |
| Testable | pass | Every criterion is testable or blocked (AC7 by Q1) |

**Definition of Ready**

| Item | Result | Evidence |
| --- | --- | --- |
| Has an ID, type, source, priority and rationale | fail | Priority is TBD (Q6) |
| Passes re-lint check with no errors | pass | `re-lint check --only-ids R-024`: no errors |
| Has a verification method and a measurable acceptance criterion | fail | `Verification` not set yet; testability-check runs later |
| Open questions are resolved or explicitly deferred with an owner | fail | Q1 and Q6 open |
| Dependencies and constraints are named | pass | Notes name dependencies (none) and constraints (S-02, S-05) |
| Is written as a story with a benefit and acceptance criteria, one of them for unwanted behavior | pass | 5 unwanted-behavior criteria |
| States the assumption it tests and how the team will learn whether the assumption holds | fail | No assumption stated; the product owner keeps none in this workspace |
| Is agreed by a named customer representative | fail | Status draft; Mei Tan (SH-01) has not agreed it |
| Cites the regulation, policy or contract clause in Source or Links where one applies | n/a | No regulation applies to the story text; PDPA handling goes to `constraints-register` |
| Requirements touching personal data or audit evidence are reviewed by the compliance or data protection role | n/a | The story stores no new personal data |

## R-025: Choose how many points to turn into a voucher

<!-- paste-start R-025 -->
**Story:** As a member, I want to choose how many of my posted points, from 500 upward, to turn into a voucher, so that my points reduce more of what I pay.

**Acceptance criteria**

**R-025.AC1: Convert a chosen amount** _(happy path)_
- **Given** a member with 1,250 posted points
- **When** the member asks the app to turn 1,200 points into a voucher
- **Then** the service issues a voucher worth SGD 12
- **And** the member's points balance shows 50 posted points

**R-025.AC2: Amount not a multiple of 100** _(alternative)_
- **Given** a member with 800 posted points
- **When** the member asks the app to turn 550 points into a voucher
- **Then** TBD (Q2: a voucher worth SGD 5 and 50 points stay in the balance, as the legacy module does (CAN-003), or the request is rejected)
- **Flag:** blocked by Q2 (rule for points below the next 100)

**R-025.AC3: More points than posted** _(unwanted behavior)_
- **Given** a member with 1,250 posted points
- **When** the member asks the app to turn 2,000 points into a voucher
- **Then** the service issues no voucher
- **And** the member's points balance still shows 1,250 posted points

**Notes:** Source S-14 · Priority TBD · Depends on R-024 · Constraints S-02 · Open questions Q2, Q6 · Business rules R-013, R-014
<!-- paste-end R-025 -->

**INVEST**

| Criterion | Result | Evidence |
| --- | --- | --- |
| Independent | fail | Builds on R-024 (normal for a later slice) |
| Negotiable | pass | No UI element or technology in the goal |
| Valuable | pass | Benefit differs from the goal |
| Estimable | fail | Q2 changes the conversion rule |
| Small | pass | One rule variation |
| Testable | pass | AC2 blocked by Q2; the rest testable |

**Definition of Ready**

| Item | Result | Evidence |
| --- | --- | --- |
| Has an ID, type, source, priority and rationale | fail | Priority is TBD (Q6) |
| Passes re-lint check with no errors | pass | `re-lint check --only-ids R-025`: no errors |
| Has a verification method and a measurable acceptance criterion | fail | `Verification` not set yet |
| Open questions are resolved or explicitly deferred with an owner | fail | Q2 and Q6 open |
| Dependencies and constraints are named | pass | Depends on R-024; constraint S-02 |
| Is written as a story with a benefit and acceptance criteria, one of them for unwanted behavior | pass | AC3 |
| States the assumption it tests and how the team will learn whether the assumption holds | fail | No assumption stated |
| Is agreed by a named customer representative | fail | Status draft |
| Cites the regulation, policy or contract clause in Source or Links where one applies | n/a | None applies |
| Requirements touching personal data or audit evidence are reviewed by the compliance or data protection role | n/a | No personal data |

## R-026: Push notification when a voucher is issued

<!-- paste-start R-026 -->
**Story:** As a member, I want a push notification when a voucher is issued to me, so that TBD.

**Acceptance criteria**

**R-026.AC1: Push on issue** _(happy path)_
- **Given** a member who agreed to receive push notifications
- **When** the service issues a voucher worth SGD 5 to that member
- **Then** the member receives a push notification that names the SGD 5 voucher
- **Flag:** blocked by Q3 (whether agreement to push notifications is needed)

**R-026.AC2: Notification provider rejects the message** _(unwanted behavior)_
- **Given** the notification provider rejects push messages
- **When** the service issues a voucher to a member
- **Then** TBD (Q4: retry later, or no message); the voucher itself stays issued
- **Flag:** blocked by Q4 (delivery failure handling)

**Notes:** Source S-14 · Priority should (PRD line 24 says "should") · Depends on R-024 · Constraints S-05 (PDPA, consent) · Open questions Q3, Q4, Q5
<!-- paste-end R-026 -->

**INVEST**

| Criterion | Result | Evidence |
| --- | --- | --- |
| Independent | fail | Needs R-024 to issue vouchers |
| Negotiable | pass | Channel named by the PRD; no technology prescribed |
| Valuable | fail | Benefit is TBD (Q5) |
| Estimable | fail | Q3 (consent) changes whether a consent check is built |
| Small | pass | One trigger, one message |
| Testable | pass | Both criteria blocked, none untestable |

**Definition of Ready**

| Item | Result | Evidence |
| --- | --- | --- |
| Has an ID, type, source, priority and rationale | pass | Priority should from the PRD wording |
| Passes re-lint check with no errors | pass | `re-lint check --only-ids R-026`: no errors |
| Has a verification method and a measurable acceptance criterion | fail | `Verification` not set yet |
| Open questions are resolved or explicitly deferred with an owner | fail | Q3, Q4, Q5 open |
| Dependencies and constraints are named | pass | Depends on R-024; constraint S-05 |
| Is written as a story with a benefit and acceptance criteria, one of them for unwanted behavior | fail | Benefit TBD |
| States the assumption it tests and how the team will learn whether the assumption holds | fail | No assumption stated |
| Is agreed by a named customer representative | fail | Status draft |
| Cites the regulation, policy or contract clause in Source or Links where one applies | fail | Consent rules under PDPA (S-05) may apply; not cited until Q3 is answered |
| Requirements touching personal data or audit evidence are reviewed by the compliance or data protection role | fail | Push messages use member contact data; not reviewed by SH-04 |

## Spikes

| Spike | Question to answer | Output | Time box | Owner |
| --- | --- | --- | --- | --- |
| none | | | | |

## Not stories

| Statement | Source | It is | Routed to |
| --- | --- | --- | --- |
| "Voucher validation must not make checkout slower." | inputs/prd-redeem-at-checkout.md:17 (SH-02, BRIEF.md:74) | quality requirement | `/quality-requirements` |
| "Keep issued vouchers in a Redis cluster so the POS gets an answer fast." | inputs/prd-redeem-at-checkout.md:19 | design decision | SH-08 Wei Jie Chua (ADR candidate); need behind it goes to `/quality-requirements` |
| "The vouchers will be printed on the receipt by TillPoint." | inputs/prd-redeem-at-checkout.md:20 | fact | none; open decision D-02 in `context.md` |
| "Redemption data must be handled in line with the PDPA and policy DRP-2024." | inputs/prd-redeem-at-checkout.md:22 | constraint | `constraints-register` |
| "The service runs on the platform team's Kubernetes platform." | inputs/prd-redeem-at-checkout.md:23 | constraint | `constraints-register` (mandator unconfirmed) |
| "The redemption screen should be easy to use." | inputs/prd-redeem-at-checkout.md:18 | quality requirement of the customer mobile app, an external system | `classification.md` open question 1 (SH-01) |

## Open questions

| # | Question | Recommended answer | Owner | Affects | Status |
| --- | --- | --- | --- | --- | --- |
| Q1 | What happens at the till when the service does not answer a voucher validation request within the POS timeout? | The sale completes without the discount and the voucher stays Issued, so checkout never waits; confirm with the POS vendor | SH-02 Arjun Pillai, with SH-09 | R-024.AC7 | open |
| Q2 | When a member turns a number of points that is not a multiple of 100 into a voucher, is the remainder kept or the request rejected? | Keep the remainder, as the legacy module does (CAN-003) | SH-01 Mei Tan | R-025.AC2 | open |
| Q3 | Does a voucher push need the member's agreement to push notifications under PDPA? | Ask the data protection officer; same question as LOY-118 question 7 | SH-04 Farid Osman | R-026.AC1 | open |
| Q4 | If the notification provider rejects the push, is it retried, and for how long? | No recommendation: needs a business decision | SH-01 Mei Tan | R-026.AC2 | open |
| Q5 | What does a member gain from a push when the voucher is issued, given that they asked for it in the app a moment before? | Ask SH-01; without a benefit, consider dropping R-026 | SH-01 Mei Tan | R-026 | open |
| Q6 | What priority do R-024 and R-025 have for the next iteration? | No recommendation: the product owner decides | SH-01 Mei Tan | R-024, R-025 | open |
