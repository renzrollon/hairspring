# Everything about returns (brain dump, Arjun Pillai SH-02 and Daniel Ng SH-06, 2026-11-01)

- Customer brings goods and receipt; cashier scans receipt and processes the return at the till.
- Refund goes back to the card or as cash. Loyalty must not hold up the refund.
- POS sends the return to the loyalty service. If the POS is offline it queues the return and sends it later (no idea for how long it can queue).
- Loyalty finds the original points transaction. Pending points are reversed, posted points are deducted.
- Partial returns: only the returned items' points come off. Nobody knows how rounding works for partial returns.
- If the points were already used for a voucher, we haven't decided what happens.
- If the fraud engine had a hold on the purchase, the return still goes through.
- No receipt: the cashier can look up the purchase by card; if not found, no points change and support gets a ticket.
- Card chargebacks: the bank tells finance up to 120 days later; finance tells support; support reverses the points with a reason code; above 5,000 points a second agent approves.
- If loyalty can't match the return, support reviews it, looks up the member and enters an adjustment, same 5,000 rule.
