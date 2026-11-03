# Glossary: loyalty-points

Terms the team uses with one meaning. Write requirements, stories, code and docs with the spelling in **Term**. Status: `candidate` (found, not defined yet), `proposed` (definition drafted, waiting for the owner), `agreed` (confirmed by the named owner), `deprecated` (do not use; the row names the replacement).

## Terms

| Term | Definition | Synonyms | Homonym notes | Abbreviation | Owner | Status | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Admin console | The loyalty-points service's interface in which support agents look up members and adjust points. | | | | SH-06 | proposed | docs/team.md:5; tickets/support-export.csv:4 |
| Adjustment | A manual change to a member's points that a support agent makes in the admin console. | | | | SH-06 | proposed | tickets/support-export.csv:4; tickets/support-export.csv:5 |
| Bonus campaign | A promotion that multiplies the points a member earns on a purchase. | | | | SH-07 | proposed | docs/programme-notes.md:6 |
| Cashier | A store employee who operates the POS and scans the member QR code. | | | | SH-02 | proposed | docs/programme-notes.md:10 |
| Liability account | The finance general-ledger account in which unredeemed posted points are booked. | | One of three senses of "account" (see Member app account, Staff account); never write "account" alone. | | SH-03 | proposed | docs/programme-notes.md:9; src/loyalty/models.py:16 |
| Member | A person registered in the Harbourline Rewards programme who earns and redeems points. | customer (code: `Customer` class, `customer_id`; tickets LOY-204, LOY-205), account holder (ticket LOY-202): avoid | | | SH-01 | proposed | docs/programme-notes.md:3 |
| Member app account | The sign-in identity a member uses for the customer mobile app. | | One of three senses of "account" (see Liability account, Staff account); never write "account" alone. | | SH-05 | proposed | tickets/support-export.csv:2 |
| Member QR code | The code shown in the customer mobile app that identifies a member at the POS. | | | QR | SH-02 | proposed | docs/programme-notes.md:10 |
| Pending points | Points from a purchase that is still inside its return window and cannot yet be redeemed. | | | | SH-01 | proposed | docs/programme-notes.md:4; tickets/support-export.csv:3 |
| Point of sale | The system in a Harbourline store on which cashiers record purchases and scan member QR codes. | | The POS calls a sale a "transaction"; in requirements say Purchase. | POS | SH-02 | proposed | docs/programme-notes.md:10; tickets/support-export.csv:5 |
| Points | The unit of a member's reward balance in the programme. | | | | SH-01 | proposed | docs/programme-notes.md:3; docs/programme-notes.md:5 |
| Points expiry | The moment posted points stop being redeemable. | | | | SH-01 | proposed | docs/programme-notes.md:7 |
| Points liability | The value of posted points that members have not redeemed, which Finance books as a liability. | | | | SH-03 | proposed | docs/programme-notes.md:9; src/loyalty/models.py:17 |
| Points transaction | One entry in a member's points ledger that adds or removes points. | | Not the POS sale: the POS calls a sale a "transaction" (LOY-204); say Purchase for the sale. | | SH-01 | proposed | src/loyalty/models.py:8; tickets/support-export.csv:6 |
| Posted points | Points whose return window has ended and that a member can redeem. | | | | SH-01 | proposed | docs/programme-notes.md:4; docs/programme-notes.md:5 |
| Product owner | The person who decides the content and priority of the loyalty-points backlog. | | "PO" also means Purchase order in store operations; write both out. | PO | SH-01 | proposed | docs/team.md:3 |
| Purchase | A completed sale to a member, at the POS or in the app, that can earn points. | transaction (POS staff, ticket LOY-204): avoid | "Transaction" also names a Points transaction; say Purchase for the sale. | | SH-02 | proposed | docs/programme-notes.md:3; tickets/support-export.csv:5 |
| Purchase order | A store's order for supplies, raised through the store portal. | | "PO" also means Product owner; write both out. | PO | SH-02 | proposed | docs/team.md:4 |
| Redemption | The exchange of posted points for a voucher. | | | | SH-01 | proposed | docs/programme-notes.md:5 |
| Return window | The period after a purchase in which a return reverses its points; points stay pending until it ends. | | | | SH-01 | proposed | docs/programme-notes.md:4 |
| Singapore dollar | The currency of purchases and of voucher values in the programme. | | | SGD | SH-03 | proposed | docs/programme-notes.md:3; docs/programme-notes.md:5 |
| Staff account | The sign-in identity a Harbourline employee uses for the admin console. | | One of three senses of "account" (see Liability account, Member app account); never write "account" alone. | | SH-05 | proposed | docs/team.md:5; tickets/support-export.csv:4 |
| Support agent | A Harbourline support employee who looks up members and makes adjustments in the admin console. | | | | SH-06 | proposed | docs/team.md:5; tickets/support-export.csv:4 |
| Tier | TBD | | | | SH-01 | candidate | docs/programme-notes.md:8; src/loyalty/models.py:5 |
| Voucher | A code with a value in SGD that a member receives in exchange for posted points. | | | | SH-01 | proposed | docs/programme-notes.md:5 |

## Findings

| # | Kind | Words | Evidence | Proposed resolution | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | homonym | account | tickets/support-export.csv:2 (app sign-in); docs/team.md:5, tickets/support-export.csv:4 (staff sign-in); docs/programme-notes.md:9, src/loyalty/models.py:17 (ledger) | Three qualified terms: Member app account, Staff account, Liability account; "account" alone is not used in requirements | SH-01 | open |
| 2 | synonym | member, customer, account holder | docs/programme-notes.md:3 (member, from the T&C draft S-01); src/loyalty/models.py:1 (`Customer`); tickets/support-export.csv:3 (account holder) | Preferred term Member, because the T&C draft uses it; renaming the `Customer` class is a code change for the tech lead | SH-01 (term), SH-08 (code) | open |
| 3 | homonym | transaction | tickets/support-export.csv:5 (POS sale); src/loyalty/models.py:8 (ledger entry) | Purchase for the sale, Points transaction for the ledger entry | SH-01 | open |
| 4 | abbreviation clash | PO | docs/team.md:3 (product owner); docs/team.md:4 (purchase order) | Write Product owner and Purchase order out in requirements and stories | SH-01 | open |
| 5 | undefined | tier | docs/programme-notes.md:8 ("tier rules are not final"); src/loyalty/models.py:5 | Keep Tier as a candidate until tiers are defined | SH-01 | open |
| 6 | rule in definition | points expiry | docs/programme-notes.md:7 | The expiry period is a business rule, not part of the definition; route it to `requirement-classifier` | SH-01 | open |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | Which tiers exist, and what moves a member from one tier to another? | SH-01 | Tier |
| 2 | Should one sense keep the bare word "account", or is "account" always qualified? | SH-01 | Liability account, Member app account, Staff account |
| 3 | Should the code follow the glossary and rename `Customer` to `Member`? | SH-08 | Member |
