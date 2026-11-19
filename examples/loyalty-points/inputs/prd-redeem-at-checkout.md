# PRD excerpt: Redeem points at checkout (draft)

Written for the sample loop by the platform-team engineer from the brief (`BRIEF.md`) and ticket LOY-118, as the kind of PRD section a team receives. Not yet reviewed by the product owner (SH-01). Line numbers are cited by `requirements/classification.md`.

## Goal

Members can turn points into vouchers and use them at the till.

## Statements

1. Today about 600,000 members are registered in the app.
2. Members can redeem points for a voucher in the app.
3. A redemption needs at least 500 points.
4. Every 100 points are worth SGD 1 of voucher value.
5. The cashier scans the voucher at the POS and the POS asks our service to validate it.
6. A voucher can be applied only once.
7. Voucher validation must not make checkout slower.
8. The redemption screen should be easy to use.
9. Keep issued vouchers in a Redis cluster so the POS gets an answer fast.
10. The vouchers will be printed on the receipt by TillPoint.
11. Redemptions are sent to the fraud engine, and a held redemption issues no voucher until it is released.
12. Redemption data must be handled in line with the PDPA and policy DRP-2024.
13. The service runs on the platform team's Kubernetes platform.
14. Members should get a push notification when a voucher is issued.
