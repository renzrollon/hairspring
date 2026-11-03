# Stories: Redeem points at checkout

| Field | Value |
| --- | --- |
| Epic | LOY-210 Redeem points at checkout |
| Refined | 2026-11-03, Mei Tan (SH-01), user-story-refiner |

## R-040: Spend 500 points as an SGD 5 voucher at the till

<!-- paste-start R-040 -->
**Story:** As a member, I want to spend 500 of my posted points as an SGD 5 voucher at the till, so that my points reduce what I pay.

**Acceptance criteria**

**R-040.AC1: Convert 500 points** _(happy path)_
- **Given** a member with 1,200 posted points
- **When** the member asks the app for an SGD 5 voucher
- **Then** the app shows an SGD 5 voucher with a scannable code
- **And** the app shows a posted balance of 700 points

**R-040.AC2: Not enough posted points** _(unwanted behavior)_
- **Given** a member with 300 posted points and 400 pending points
- **When** the member asks the app for an SGD 5 voucher
- **Then** the app refuses the voucher

**Notes:** Source S-06 (LOY-210) · Priority must · Depends on none · Constraints R-100 · Open questions none
<!-- paste-end R-040 -->

## R-042: Cancel an unused voucher

<!-- paste-start R-042 -->
**Story:** As a support agent, I want to cancel a member's unused voucher, so that the member gets the points back without a manual points adjustment.

**Acceptance criteria**

**R-042.AC1: Cancel an issued voucher** _(happy path)_
- **Given** a member's SGD 5 voucher with status Issued
- **When** the support agent cancels the voucher in the admin console
- **Then** the voucher status becomes Cancelled

**R-042.AC2: Voucher already applied** _(unwanted behavior)_
- **Given** a member's voucher with status Applied
- **When** the support agent tries to cancel the voucher
- **Then** the admin console refuses the cancellation

**Notes:** Source S-06 (LOY-210) · Priority should · Depends on R-040 · Constraints none · Open questions none
<!-- paste-end R-042 -->
