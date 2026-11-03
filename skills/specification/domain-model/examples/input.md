# Input: domain model for the loyalty-points service (loyalty-points sample)

Prompt: "Draw the domain model for the loyalty service from our requirements and glossary."

## `requirements/glossary.md` (as the agent found it)

| Term | Definition | Synonyms | Owner |
| --- | --- | --- | --- |
| Member | A person registered in Harbourline Rewards who earns and redeems points. | — | SH-01 |
| Member QR code | The code shown in the customer mobile app that identifies a member at the POS. | QR token | SH-02 |
| Purchase | A completed sale at a Harbourline till that the POS reports to the loyalty service. | Sale | SH-02 |
| Points transaction | The points earned for one purchase, from pending until redeemed, expired or reversed. | — | SH-01 |
| Points balance | The points a member holds. | Balance | SH-01 |
| Return window | The 24 hours after a purchase during which its points stay pending. | — | SH-01 |
| Voucher | A single-use discount issued in exchange for points. | — | SH-01 |
| Campaign | A time-limited promotion that multiplies the points earned. | Bonus campaign | SH-07 |
| Adjustment | A manual change to a member's points made by a support agent. | — | SH-06 |
| Reason code | The code a support agent must give for an adjustment. | — | SH-06 |
| Cashier | The store employee who operates the POS. | — | SH-02 |

## `requirements/requirements.csv` (excerpt, columns ID, Type, Text, Source)

| ID | Type | Text | Source |
| --- | --- | --- | --- |
| R-001 | F | WHEN the POS sends a completed purchase event, the loyalty service shall create a pending points transaction for the member. | S-02 |
| R-003 | F | The loyalty service shall award 1 point per SGD 1 of the purchase amount, rounded down per purchase. | S-01 |
| R-004 | F | WHERE a campaign is active for the store of a purchase, the loyalty service shall multiply the points earned by the campaign multiplier. | S-01 |
| R-005 | F | The loyalty service shall record the member, the store and the time of each points transaction. | S-04 |
| R-020 | F | WHEN the customer mobile app requests a balance, the loyalty service shall return the customer's points balance and redeemable balance. | S-06 |
| R-021 | F | The loyalty service shall send each customer's tier and points summary to the CRM once per night. | S-04 |
| R-041 | F | WHEN the loyalty service issues a voucher, the loyalty service shall set the voucher value to SGD 1 per 100 redeemed points. | S-01 |
| R-042 | F | The loyalty service shall issue each voucher with a unique voucher code. | S-02 |
| R-065 | F | WHEN a support agent submits an adjustment, the loyalty service shall require a reason code. | SH-06 2026-10-29 |
| R-066 | F | IF an adjustment exceeds 5,000 points, THEN the loyalty service shall hold it until a second support agent approves it. | SH-06 2026-10-29 |

No `context.md` and no `schema.json` yet: the agent uses the default schema and says so.
