# Input: `/use-case-spec redeem voucher` (loyalty-points sample)

## Material in the workspace

`requirements/context.md` (excerpt): the system under development is the loyalty-points service. External: Customer (member) through the customer mobile app; Cashier through the TillPoint POS; fraud engine (scores redeem events, places and releases holds); POS to service: voucher validation. Grey zone: voucher printing at the POS, vendor or us, open decision `D-02`.

Kick-off interview `I-01`, Mei Tan (SH-01, Head of Loyalty), 2026-10-27, notes on redemption:

> "Members pick how many points to redeem in the app and get a voucher QR they show at the till. The cashier scans it, the POS checks it with us, and the discount goes on the bill. Fraud wants to see every redemption before a voucher is issued. A voucher can be used once. Unused vouchers expire; I don't know after how long yet. Everything here is a must for launch."

Programme terms and conditions draft v3 (`S-01`): 100 points = SGD 1 voucher value; minimum redemption 500 points; points become redeemable once posted, 24 hours after purchase.

Store operations lead (SH-02) on record: "Checkout must not get slower."

`requirements/requirements.csv` already holds, among others:

| ID | Type | Text | Source |
| --- | --- | --- | --- |
| R-040 | F | IF a redemption request asks for fewer than 500 points, THEN the loyalty service shall reject the request. | S-01 |
| R-041 | F | WHEN the loyalty service issues a voucher, the loyalty service shall set the voucher value to SGD 1 per 100 redeemed points. | S-01 |
| R-042 | F | The loyalty service shall issue each voucher with a unique voucher code. | S-02 |

## Answers given during the run (via `re-interview`)

1. Q: "Does the use case end when the voucher is issued, or when the discount is on the bill? Recommended: on the bill, because that is what the member wants." A (Mei Tan, SH-01, 2026-11-03): "On the bill."
2. Q: "Who is the primary actor: the member or the cashier? Recommended: the member, the cashier supports." A (Mei Tan, 2026-11-03): "The member."
3. The user then said: "That's all I know today. Write it and list what's open."
