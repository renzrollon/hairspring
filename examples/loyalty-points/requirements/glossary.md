# Glossary: loyalty-points

Terms the team uses with one meaning. Write requirements, stories, code and docs with the spelling in **Term**. Status: `candidate` (found, not defined yet), `proposed` (definition drafted, waiting for the owner), `agreed` (confirmed by the named owner), `deprecated` (do not use; the row names the replacement).

## Terms

| Term | Definition | Synonyms | Homonym notes | Abbreviation | Owner | Status | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Adjustment | A manual change to a member's points by a support agent, recorded with a reason code. | | Not a reversal: the legacy module records both as `ADJ` (inputs/legacy/sp_redeem_points.sql:27); finding 5 | | SH-06 | proposed | BRIEF.md:63; inputs/legacy/sp_redeem_points.sql:27 |
| Applying a voucher | The cashier's use of an issued voucher at checkout after the service has validated it. | "redeem" at the till: avoid (inputs/support-tickets-excerpt.csv:4) | Not a redemption; finding 3 | | SH-02 | proposed | BRIEF.md:18; BRIEF.md:70 |
| Bonus campaign | A promotion that multiplies the points members earn on purchases. | | | | SH-07 | proposed | BRIEF.md:58 |
| Cashier | Store staff member who scans the member QR token and applies vouchers at the POS. | | | | SH-02 | proposed | BRIEF.md:18 |
| Data retention policy DRP-2024 | Harbourline's company policy on how long data is kept. | | | DRP-2024 | SH-04 | proposed | BRIEF.md:52 (S-05) |
| Fraud engine | The external system that scores earn and redeem events and sends back hold or release decisions. | | | | TBD | proposed | BRIEF.md:22 |
| Fraud hold | A fraud engine decision that keeps points or a redemption from being used until the fraud engine releases it. | held | | | SH-05 | proposed | BRIEF.md:22; inputs/LOY-118.md:5 |
| Maker-checker | A control in which a second person approves an adjustment that one support agent made. | second approver (inputs/legacy/sp_redeem_points.sql:24) | | | SH-06 | proposed | BRIEF.md:63 |
| Member | A person registered in the Harbourline Rewards programme who earns and redeems points. | customer: avoid (BRIEF.md:17, inputs/support-tickets-excerpt.csv:3); `cust_id`, `loy_customer` in legacy code (inputs/legacy/sp_redeem_points.sql:3, :13) | "Customer mobile app" stays the external system's name | | SH-01 | proposed | BRIEF.md:7; BRIEF.md:58 |
| Member QR token | The code on a member's card or app that the cashier scans to identify the member at the POS. | card, QR | | QR | SH-01 | proposed | BRIEF.md:18; BRIEF.md:68 |
| Pending points | Points from a purchase that are recorded in a points transaction but not yet posted. | | | | SH-01 | proposed | BRIEF.md:69; inputs/support-tickets-excerpt.csv:7 |
| Personal Data Protection Act | Singapore's law on the collection, use and retention of personal data. | | | PDPA | SH-04 | proposed | BRIEF.md:52 (S-05) |
| Points | The unit of the programme's reward balance that members earn on purchases and redeem for vouchers. | | | | SH-01 | proposed | BRIEF.md:58; BRIEF.md:61 |
| Points balance | TBD | balance | Unclear whether pending points are included (finding 6, open question 1) | | SH-01 | candidate | BRIEF.md:7; inputs/support-tickets-excerpt.csv:2; inputs/support-tickets-excerpt.csv:12; inputs/LOY-118.md:5 |
| Points expiry | The end of the period in which posted points can be redeemed, after which they no longer count towards the points balance. | | Not voucher expiry; finding 4 | | SH-01 | proposed | BRIEF.md:60; BRIEF.md:69 |
| Points liability | The value of the points members hold, which Finance accounts for as an amount Harbourline owes. | | | | SH-03 | proposed | BRIEF.md:24; BRIEF.md:35 |
| Points transaction | One entry in a member's points history that adds or removes points, linked to the purchase, redemption, expiry, reversal or adjustment that caused it. | | Not the purchase itself; see Purchase | | SH-01 | proposed | BRIEF.md:68; BRIEF.md:69 |
| Posting | The change of a points transaction from pending to posted, after which its points count towards the points balance and can be redeemed. | | The brief also says "available" (BRIEF.md:59); finding 7 | | SH-01 | proposed | BRIEF.md:59; BRIEF.md:69 |
| Purchase | A paid sale to a member at the POS or in the app that can earn points. | | Not the points transaction it creates | | SH-01 | proposed | BRIEF.md:19; BRIEF.md:68 |
| Reason code | A code that states why a support agent made an adjustment. | | | | SH-06 | proposed | BRIEF.md:63; inputs/legacy/sp_redeem_points.sql:21 |
| Redemption | A member's exchange of posted points for a voucher. | "redeem" for using a voucher at the till: avoid (inputs/support-tickets-excerpt.csv:4) | Using the voucher at checkout is Applying a voucher; finding 3 | | SH-01 | proposed | BRIEF.md:7; BRIEF.md:61; inputs/prd-redeem-at-checkout.md:12 |
| Relay CRM | The customer relationship management system that receives member tier and points summaries. | | | CRM | TBD | proposed | BRIEF.md:21 |
| Return window | The period after a purchase during which a return reverses its points before they are posted. | | | | SH-01 | proposed | BRIEF.md:59 |
| Reversal | A points transaction that removes the points of a returned purchase. | | Not an adjustment; finding 5 | | SH-01 | proposed | BRIEF.md:62; BRIEF.md:69 |
| Singapore dollar | The currency in which purchases and voucher values are counted. | | | SGD | SH-03 | proposed | BRIEF.md:58; BRIEF.md:61 |
| Support agent | Customer support staff member who looks up members and makes adjustments in the admin console. | support console agent (BRIEF.md:25) | | | SH-06 | proposed | BRIEF.md:25 |
| Tier | TBD | | | | SH-01 | candidate | BRIEF.md:21; BRIEF.md:68 |
| TillPoint POS | The vendor's point-of-sale system in Harbourline stores that sends purchase events and asks the service to validate vouchers. | till (inputs/support-tickets-excerpt.csv:4) | | POS | SH-09 | proposed | BRIEF.md:19 (S-02) |
| Voucher | A code worth a fixed amount in Singapore dollars that a member receives for a redemption and applies at checkout. | coupon, e-voucher: avoid (inputs/support-tickets-excerpt.csv:4, inputs/support-tickets-excerpt.csv:9) | | | SH-01 | proposed | BRIEF.md:61; BRIEF.md:70 |
| Voucher expiry | The end of the period in which an issued voucher can be applied. | | Not points expiry; finding 4 | | SH-01 | proposed | BRIEF.md:70 |
| Voucher validation | The POS's call to the service that checks whether a voucher can be applied. | | | | SH-09 | proposed | BRIEF.md:19; BRIEF.md:74 |

## Findings

| # | Kind | Words | Evidence | Proposed resolution | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | synonym | member, customer, cust | BRIEF.md:17; BRIEF.md:58; inputs/support-tickets-excerpt.csv:3; inputs/legacy/sp_redeem_points.sql:3; inputs/legacy/sp_redeem_points.sql:13 | Use "Member" (the programme's own word, BRIEF.md:58); "customer" only in the name "Customer mobile app"; legacy column names are not renamed because the module is replaced | SH-01 | open |
| 2 | synonym | voucher, coupon, e-voucher | BRIEF.md:61; inputs/support-tickets-excerpt.csv:4; inputs/support-tickets-excerpt.csv:9 | Use "Voucher"; members' words stay in tickets but not in requirements | SH-01 | open |
| 3 | homonym | redeem (points for a voucher; using the voucher at the till) | BRIEF.md:7; BRIEF.md:18; inputs/support-tickets-excerpt.csv:4; inputs/support-tickets-excerpt.csv:9 | "Redemption" keeps the bare word (points to voucher); the till step is "Applying a voucher" (Voucher state Applied, BRIEF.md:70) | SH-01 | open |
| 4 | homonym | expiry, expired (points; vouchers) | BRIEF.md:60; BRIEF.md:69; BRIEF.md:70; inputs/support-tickets-excerpt.csv:5 | Always qualify: "Points expiry", "Voucher expiry"; the voucher expiry period is open question 3 | SH-01 | open |
| 5 | homonym | adjustment (support correction; legacy `ADJ` for return reversals) | BRIEF.md:63; inputs/legacy/sp_redeem_points.sql:27 | "Adjustment" is the manual correction with a reason code; a return creates a "Reversal" | SH-06 | open |
| 6 | undefined | points balance | BRIEF.md:7; BRIEF.md:59; inputs/support-tickets-excerpt.csv:7; inputs/support-tickets-excerpt.csv:12; inputs/LOY-118.md:5 | Ask whether the balance members see includes pending points (open question 1); LOY-118 depends on it | SH-01 | open |
| 7 | rule in definition | posting, available | BRIEF.md:59 | The brief defines posting with a rule ("24 hours after purchase"); the 24-hour rule goes to a requirement candidate, and whether "available" and "posted" are one moment is open question 5 | SH-01 | open |
| 8 | undefined | tier | BRIEF.md:21; BRIEF.md:68 | No source defines tiers; definition stays `TBD` (open question 4) | SH-01 | open |
| 9 | undefined | processed (in "points will be added once the purchase is processed") | inputs/LOY-118.md:5 | Ask whether "processed" means the purchase event is received (pending) or posted; handed to `clarifying-questions` for LOY-118 | SH-01 | open |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | Does the points balance a member sees include pending points, or only posted points? | SH-01 | Points balance, Pending points |
| 2 | Do you agree that "redeem" means exchanging points for a voucher, and that using the voucher at the till is "applying" it? | SH-01 | Redemption, Applying a voucher |
| 3 | Do vouchers expire, and if so after how long? | SH-01 | Voucher expiry |
| 4 | What tiers exist and what decides a member's tier? | SH-01 | Tier |
| 5 | Are "available" and "posted" the same moment, 24 hours after purchase (BRIEF.md:59)? | SH-01 | Posting |
| 6 | Is a return after posting recorded as a reversal or as an adjustment, and who approves it? | SH-06 | Reversal, Adjustment |
| 7 | Do you confirm "Member" as the preferred term over "customer"? | SH-01 | Member |
