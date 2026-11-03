# Requirement classification: loyalty-points

Each batch sorts statements as they were given; nothing here is a requirement yet. Rows with Verdict `requirement` go to the skill in Next. The Kano column is a first guess from wording and domain; confirm it with stakeholders before it influences priority.

## Batch 2026-11-03: PRD excerpt "Redeem points at checkout"

Input: `inputs/prd-redeem-at-checkout.md` (draft, not reviewed by SH-01).

| # | Statement | Source | Ref | Verdict | Type | Concern | Kano (guess) | Flags | Next |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | "Today about 600,000 members are registered in the app." | inputs/prd-redeem-at-checkout.md:11 | - | fact | - | Describes today's member base (BRIEF.md:7); volume context for quality requirements | - | current-state | none |
| 2 | "Members can redeem points for a voucher in the app." | inputs/prd-redeem-at-checkout.md:12 | CAN-005 | requirement | F | F: redemption behavior offered through the app's API | dissatisfier | no-obligation | user-story-refiner |
| 3 | "A redemption needs at least 500 points." | inputs/prd-redeem-at-checkout.md:13 | CAN-001 | requirement | F | F: programme rule the service must enforce | indifferent | rule, no-obligation, duplicate:CAN-001 | user-story-refiner |
| 4 | "Every 100 points are worth SGD 1 of voucher value." | inputs/prd-redeem-at-checkout.md:14 | CAN-002 | requirement | F | F: programme rule for the voucher value | dissatisfier | rule, no-obligation, duplicate:CAN-002 | user-story-refiner |
| 5 | "The cashier scans the voucher at the POS" | inputs/prd-redeem-at-checkout.md:15 | - | fact | - | Describes what the cashier and the POS do, outside the system (`context.md` row 17) | - | - | system-context |
| 6 | "the POS asks our service to validate it." | inputs/prd-redeem-at-checkout.md:15 | - | requirement | F | F: the service answers voucher validation requests (`context.md` rows 2 and 3) | dissatisfier | no-obligation | user-story-refiner |
| 7 | "A voucher can be applied only once." | inputs/prd-redeem-at-checkout.md:16 | - | requirement | F | F: voucher state rule (Issued to Applied, BRIEF.md:70) | dissatisfier | rule, no-obligation | user-story-refiner |
| 8 | "Voucher validation must not make checkout slower." | inputs/prd-redeem-at-checkout.md:17 | - | requirement | Q | Q: performance efficiency, time behavior of voucher validation (SH-02, BRIEF.md:74) | dissatisfier | missing-value | quality-requirements |
| 9 | "The redemption screen should be easy to use." | inputs/prd-redeem-at-checkout.md:18 | - | unclear | - | The redemption screen belongs to the customer mobile app (`context.md` row 4), an external system; unclear whether this is a requirement on the service at all | - | weak-word, missing-value | clarifying-questions |
| 10 | "Keep issued vouchers in a Redis cluster so the POS gets an answer fast." | inputs/prd-redeem-at-checkout.md:19 | - | solution | Q | A storage technology nobody outside the team mandated; the need behind it is the response time of voucher validation | - | weak-word, missing-value | SH-08 (platform team tech lead); clarifying-questions |
| 11 | "The vouchers will be printed on the receipt by TillPoint." | inputs/prd-redeem-at-checkout.md:20 | CAN-006 | fact | - | Another party's intention; who prints vouchers is open decision D-02, and the legacy module prints a slip at the service desk (CAN-006) | - | will, dependency, conflict? | system-context; conflict-detector |
| 12 | "Redemptions are sent to the fraud engine, and a held redemption issues no voucher until it is released." | inputs/prd-redeem-at-checkout.md:21 | - | requirement | F | F: fraud scoring of redemptions and the effect of a fraud hold (`context.md` rows 7 and 8) | dissatisfier | compound, no-obligation | user-story-refiner |
| 13 | "Redemption data must be handled in line with the PDPA and policy DRP-2024." | inputs/prd-redeem-at-checkout.md:22 | - | requirement | C | C: Singapore law (PDPA) and company policy DRP-2024 restrict how redemption data is handled (S-05) | - | - | constraints-register |
| 14 | "The service runs on the platform team's Kubernetes platform." | inputs/prd-redeem-at-checkout.md:23 | - | requirement | C | C: an organizational platform restriction; the brief names the Kubernetes platform only as SH-08's interest (BRIEF.md:40) | - | rule, mandate-unconfirmed | constraints-register |
| 15 | "Members should get a push notification when a voucher is issued." | inputs/prd-redeem-at-checkout.md:24 | - | requirement | F | F: notification on voucher issue, sent through the notification provider (`context.md` row 9) | satisfier | - | user-story-refiner |

Summary: 15 statements: 7 F, 1 Q, 2 C requirements; 1 solution; 3 fact; 0 goal; 1 unclear.

### Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | Is the redemption screen part of the loyalty-points service or of the customer mobile app; if the app's, who owns its usability requirement? | SH-01 | 9 |
| 2 | How much time may voucher validation add to a checkout, at which percentile? | SH-02 | 8 |
| 3 | What response time must voucher validation meet, and does any platform policy mandate Redis? | SH-08 | 10 |
| 4 | Is printing by TillPoint decided and binding, or is it still open decision D-02? | SH-01, with SH-09 | 11 |
| 5 | Who mandates the Kubernetes platform, and in which policy or standard? | SH-08 | 14 |
