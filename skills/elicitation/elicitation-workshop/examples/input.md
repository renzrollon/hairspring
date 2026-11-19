# Input: redemption delighters workshop (loyalty-points sample)

## Run 1 (phase A), 2026-11-05

> `/elicitation-workshop 90-minute remote workshop on 2026-11-12 to find delighters for redeeming points in the member app. Mei Tan decides. Invite Priya Raman, Daniel Ng, Arjun Pillai and two app members Priya recruits. I facilitate.`

The facilitator is Wei Jie Chua (SH-08). `requirements/stakeholders.md` lists SH-01 Mei Tan, SH-02 Arjun Pillai, SH-06 Daniel Ng, SH-07 Priya Raman. `requirements/context.md` has open decision D-02 (voucher printing at the POS: vendor or us?). `requirements/candidates.csv` holds CAN-001 to CAN-014; R-063 sets expiry at 12 months after posting.

## Run 2 (phase B), 2026-11-12

> `/elicitation-workshop capture the board export below for workshop-redemption-delighters`

Board export (one line per sticky note: technique, round or sheet, note text, cluster, dots, Kano agreed in the room):

```text
paradox,-,"voucher only works in the store where it was issued",Where it works,2,dissatisfier
paradox,-,"make people print the voucher at a kiosk first",At the till,3,dissatisfier
paradox,-,"hide how many points you still need",Progress,1,satisfier
paradox,-,"cashier has to type a 16-digit code",At the till,0,
635,sheet1-r1,"pay part of the bill with points right at checkout, no voucher",At the till,5,delighter
635,sheet2-r1,"donate points to a charity",Giving,2,delighter
635,sheet2-r3,"birthday bonus surprise",Earning,3,
635,sheet3-r2,"share points with my family",Family,6,delighter
635,sheet5-r4,"family pool: partner and kids add to one balance",Family,0,delighter
635,sheet4-r2,"vouchers in steps of 100 points instead of 500",Flexibility,1,satisfier
635,sheet4-r5,"pay with points for online orders",Online,1,
635,sheet6-r2,"tell me before my voucher expires",Progress,2,satisfier
635,sheet6-r4,"points never expire!!",Progress,3,delighter
635,sheet1-r6,"put the voucher in Apple Wallet",At the till,1,satisfier
635,sheet3-r6,"free unicorn rides lol",-,0,
```

The expected output is the workshop file after run 2 (`expected-output.md`) and the rows appended to `requirements/candidates.csv` (`expected-candidates.csv`).
