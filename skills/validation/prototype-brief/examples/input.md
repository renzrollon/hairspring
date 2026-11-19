# Input: `/prototype-brief R-044 R-048 R-049 R-050 R-051` (loyalty-points sample)

## Plan request (Mei Tan, SH-01, 2026-11-04)

"Before the app team builds voucher redemption, I want members to try it. Marketing can get six members from the app beta list, a mix of frequent and occasional shoppers. Two weeks, starting 10 November. I decide what we build."

Thresholds Mei agreed on 2026-11-04, before any session: H1, H2 and H3 are validated when at least 5 of the 6 participants succeed; R-051 is kept only if at least 3 of 6 would use it in the next month, and dropped if at most 1 of 6 would.

## `requirements/requirements.csv` (excerpt)

```csv
ID,Type,Text,Source,Priority,Status,Rationale
R-044,F,"WHEN the member opens the vouchers screen, the customer mobile app shall list the member's unused vouchers with their value and expiry date.",SH-01 Mei Tan 2026-10-28,could,draft,Members want to find their vouchers at the till.
R-048,F,"WHEN the member selects an unused voucher, the customer mobile app shall display the voucher as a QR code for the POS to scan.",S-02,must,draft,The POS reads vouchers by QR code.
R-049,F,"WHEN a member redeems points in the customer mobile app, the customer mobile app shall let the member choose the number of points to redeem in steps of 100 points.",SH-01 Mei Tan 2026-10-28,should,draft,100 points = SGD 1 (S-01).
R-050,F,"WHERE the member has fewer than 500 posted points, the customer mobile app shall show how many points are missing to reach the redemption minimum.",SH-07 Priya Raman 2026-10-29,could,draft,Motivates members to come back.
R-051,F,"The customer mobile app shall let a member send an unused voucher to another member.",SH-07 Priya Raman 2026-10-29,could,draft,Gifting could bring in new members.
```

## Record request (Mei Tan, 2026-11-14): "/prototype-brief record voucher-redemption"

Session notes, 2026-11-12 and 2026-11-13, six members (P1 to P6), clickable mock-up:

- T1 (get a voucher with 1,240 points): P2 and P6 chose an amount without help. P1, P3, P4 and P5 looked for fixed values; P4: "Just give me 5, 10 or 20 dollars, like a gift card."
- T2 (show the voucher at the till): P1 to P5 opened the voucher from the home screen. P6 looked under History first, then found it.
- T3 (account with 320 points): all six restated the message correctly. P3: "I'm 180 short, so I'll come back on Saturday."
- Closing question on sending vouchers: nobody would use it in the next month. P5: "If someone sends me a voucher I'd think it's a scam."
