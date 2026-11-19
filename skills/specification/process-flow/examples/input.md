# Input: the purchase-return process (loyalty-points sample)

Prompt: "Draw the return process for purchases that earned points, from the till to the member's points."

## Notes the agent was given

Interview I-02, Arjun Pillai (SH-02, store operations lead), 2026-10-30:

> "At the till the cashier scans the receipt and processes the return. The refund to the customer must not wait for loyalty: the POS sends the return to the loyalty service in the background and the customer leaves with the refund."

Daniel Ng (SH-06, customer support lead), 2026-10-31:

> "If loyalty can't match the return to a points transaction, it lands in our review queue. An agent looks up the member and the purchase in the admin console. If it wasn't a loyalty purchase, the agent closes the case. Otherwise the agent enters a points adjustment with a reason code. Anything above 5,000 points needs a second agent to approve it."

## What the agent found in the workspace

- `requirements/context.md`: Customer (member), Cashier at the TillPoint POS, Support console agents, loyalty-points service.
- `requirements/models/state-points-transaction.md`: a return reverses Pending or OnHold points without touching the redeemable balance, deducts Posted points, leaves Expired points unchanged, is impossible for Reversed (the POS blocks a second return, SH-01 2026-11-02), and is open for Redeemed (Q1 there).
- `requirements/requirements.csv` rows that apply (R-062 to R-068 come from the state model and the support policy):

| ID | Type | Text | Source |
| --- | --- | --- | --- |
| R-062 | F | WHILE a points transaction is Pending, WHEN the POS sends a return for its purchase, the loyalty service shall reverse the transaction without changing the member's redeemable balance. | S-01 |
| R-063 | F | WHILE a points transaction is Posted, WHEN the POS sends a return for its purchase, the loyalty service shall deduct the transaction's points from the member's redeemable balance. | S-01 |
| R-068 | F | WHILE a points transaction is OnHold, WHEN the POS sends a return for its purchase, the loyalty service shall reverse the transaction without changing the member's redeemable balance. | S-01 |
| R-064 | F | WHILE a points transaction is Expired, WHEN the POS sends a return for its purchase, the loyalty service shall leave the member's points balance unchanged. | SH-01 2026-11-02 |
| R-065 | F | WHEN a support agent submits an adjustment, the loyalty service shall require a reason code. | SH-06 2026-10-29 |
| R-066 | F | IF an adjustment exceeds 5,000 points, THEN the loyalty service shall hold it until a second support agent approves it. | SH-06 2026-10-29 |
