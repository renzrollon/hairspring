# Input: scan the loyalty-points register for conflicts

Request (Wei Jie Chua, platform tech lead, 2026-11-03): "Before Thursday's refinement, check the redemption, expiry, adjustment and retention requirements for conflicts."

## `requirements/requirements.csv` (excerpt)

```csv
ID,Type,Text,Source,Priority,Status,Rationale
R-008,F,"IF the POS cannot read the member QR code, THEN the POS shall let the cashier enter the member number manually.",I-02 (SH-02 Arjun Pillai 2026-10-30),must,draft,Cashiers need a fallback when the app screen is too dark to scan.
R-020,F,"WHEN the member opens the balance screen, the customer mobile app shall display the posted points balance.",S-06,must,agreed,Members check their balance after paying.
R-041,F,"IF a member requests a voucher with fewer than 500 posted points, THEN the loyalty service shall reject the request.",S-01,must,proposed,Minimum redemption in the programme terms.
R-045,F,"WHEN a member has more than 500 posted points, the customer mobile app shall show the Redeem button.",SH-07 Priya Raman 2026-10-29,should,draft,Prompts members to redeem as soon as they can.
R-060,F,"The loyalty service shall expire posted points 12 months after posting.",S-01,must,proposed,Limits the points liability on the balance sheet (SH-03).
R-061,F,"The loyalty service shall expire posted points 18 months after posting.",SH-07 Priya Raman 2026-10-29,must,draft,Occasional shoppers lose points before they reach the redemption minimum.
R-064,F,"The support console shall let support agents adjust a member's points with a reason code.",S-03,should,draft,Support resolves complaints about missing points.
R-065,F,"WHEN a support agent submits an adjustment above 5,000 points, the admin console shall require approval by a second support agent before posting it.",S-01,must,proposed,Maker-checker control against insider fraud.
R-100,C,"The loyalty service shall retain points transaction records for 7 years after the transaction date.",S-05 (DRP-2024),must,proposed,Audit retention required by Finance (SH-03).
R-101,C,"WHEN a member closes their account, the loyalty service shall delete the member's personal data within 30 days.",S-05 (PDPA) SH-04 Farid Osman 2026-10-31,must,draft,Personal data must not be kept longer than needed.
```

## Refinement notes, 2026-10-30 (excerpt)

- R-008 manual member-number entry: Arjun Pillai (SH-02) wants it as `must` ("queues build up when the QR fails"). Lena Koh (SH-05) rates it `wont`: typed member numbers let staff earn points on other members' purchases.

## Context

`requirements/stakeholders.md` holds SH-01 to SH-09 as in the sample brief. `requirements/schema.json` is the default (change authority: product owner, SH-01 Mei Tan). No `conflicts.md` exists yet.

## Expected final message (summary)

5 conflicts registered (CF-01 to CF-05), none escalated, no requirement changed. Next: suggest `/conflict-to-decision CF-01` (expiry, two `must` rows) and `/conflict-to-decision CF-02` (retention constraints). Open questions: 4, listed in the register.
