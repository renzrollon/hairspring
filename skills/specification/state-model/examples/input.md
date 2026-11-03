# Input: the PointsTransaction lifecycle (loyalty-points sample)

Prompt: "Model the states of a points transaction and tell me what we have missed."

## What the agent found in the workspace

Business rules from the programme terms and conditions, draft v3 (`S-01`), as listed in `examples/loyalty-points/BRIEF.md`:

- Points become available 24 hours after purchase (return window), then are posted.
- Points expire 12 months after posting (Finance wants this; Marketing would like 18 months: an open conflict).
- Returns reverse the points of the original transaction; if they were already redeemed, the balance may go negative (open question).
- States named in the brief: Pending, Posted, then Redeemed, Expired or Reversed; Pending goes to Reversed on a return within 24 hours.

Existing rows in `requirements/requirements.csv` that touch the lifecycle:

| ID | Type | Text | Source |
| --- | --- | --- | --- |
| R-001 | F | WHEN the POS sends a completed purchase event, the loyalty service shall create a pending points transaction for the member. | S-02 |
| R-002 | F | WHEN the return window of a pending points transaction ends, the loyalty service shall post the transaction. | S-01 |
| R-025 | F | IF the fraud engine places a hold on a purchase, THEN the loyalty service shall keep the points of that purchase in pending state until the fraud engine releases the hold. | S-06 (LOY-118) |

The glossary defines Points transaction, Member, Purchase, Return window, Redeemable balance (posted points only) and Fraud hold.

## Answers recorded on 2026-11-02 (via `clarifying-questions`)

- Lena Koh (SH-05, security architect): "The fraud engine only places holds on pending points. Once points are posted we never hold them. A purchase has at most one hold at a time."
- Mei Tan (SH-01, Head of Loyalty): "A receipt can be returned only once; the POS blocks a second return."
- Mei Tan (SH-01): "If a purchase is returned after its points expired, nothing happens to the balance."

## ID ranges

The register holds R-001 to R-027, R-040 to R-042, and R-065 to R-066 (support adjustments). Lifecycle requirements use the free IDs in the R-060 to R-079 range (expiry, reversal, adjustments).
