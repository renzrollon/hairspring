# Input: epic LOY-210 (loyalty-points sample)

Command: `/user-story-refiner` with the ticket below.

> **LOY-210 (epic): Redeem points at checkout**
>
> As a member I want to use my points at the till. Members turn points into vouchers in the app and the cashier scans the voucher at checkout. 100 points = SGD 1, minimum 500 points. The POS checks the voucher with us. If the member doesn't have enough points the app should show a nice error. Cashiers should find it easy. Support needs to be able to cancel a voucher when a member complains. Campaign vouchers from marketing should work too. Make it fast.
>
> Must-have for launch: members redeeming at the till. Support cancel: should. Choosing the amount: could.
>
> Reporter: Mei Tan (Head of Loyalty), 2026-10-29. Source in the inventory: S-06.

Workspace state: `requirements.csv` holds R-001 to R-039 (earning, balance and history). `requirements/schema.json` exists with the default `definition_of_ready`. `stakeholders.md` names the roles member, cashier and support agent. Business rules from the brief: points are pending for 24 hours, then posted; 100 points = SGD 1 voucher; minimum redemption 500 points.

## Question batch and answers (Mei Tan, SH-01, 2026-11-03)

| # | Question | Recommended answer | Answer |
| --- | --- | --- | --- |
| 1 | What is the smallest thing a member must be able to do at the till in the first release? | Spend one voucher of a fixed value | Spend one SGD 5 voucher (500 points). Other amounts later. |
| 2 | May members convert amounts that are not multiples of 100 points? | Only multiples of 100 | Don't know; ask Finance (Grace). |
| 3 | How long does the POS wait for our voucher answer before it gives up? | Use the timeout in the TillPoint spec (S-02) | Ask the TillPoint integration manager. |
| 4 | When do vouchers expire? | Same as points (12 months) | Not decided yet; I will decide before the campaign work. Defer it. |
| 5 | How are campaign vouchers issued today? | Through the legacy module (S-04) | Through the legacy module; nobody on the team knows the details. |
