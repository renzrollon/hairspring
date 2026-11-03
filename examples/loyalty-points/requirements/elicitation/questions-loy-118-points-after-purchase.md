# Clarifying questions: LOY-118 points after purchase

| Field | Value |
| --- | --- |
| Task | LOY-118: Show points after purchase (`inputs/LOY-118.md`) |
| Asked | 2026-11-03 |
| Asked of | Mei Tan (SH-01), the ticket's reporter; other owners per question in Source |
| Mode | non-interactive |
| Status | open |

## Already answered (not asked)

| Topic | Answer | Where |
| --- | --- | --- |
| When purchased points become usable | 24 hours after purchase (the return window), then they are posted | BRIEF.md:59 |
| How many points a purchase earns | 1 point per SGD 1, rounded down per transaction; bonus campaigns can multiply this | BRIEF.md:58 |
| Who decides a fraud hold | The fraud engine scores earn events and sends back hold or release | BRIEF.md:22; `context.md` rows 7 and 8 |
| Which channels the notification provider offers | SMS and push | BRIEF.md:23; `context.md` row 9 |
| Load the balance path must survive | Year-end sale peak, last year about 9,000 purchases per minute across stores | BRIEF.md:76 |
| Whether "Use Redis to cache balances" is a requirement | No: a design decision without a stated need; the need behind it is the freshness target in question 6 | `inputs/LOY-118.md:5`; `requirement-phrasing` example routes it to SH-08 |

## Questions

| # | Group | Question | Why it matters | Recommended answer | Answer | Source | Becomes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Boundary | The ticket asks for an email when points are added, but the notification provider sends only SMS and push (`context.md` row 9). Should we add an email provider, or send push only? | Email adds a new external system and interface to the context | Push only for LOY-118: it needs no new external system | TBD | owner: Mei Tan (SH-01) | open |
| 2 | Functional | Between purchase and posting (24 hours), what does the app show: (a) pending points listed apart from the points balance, (b) a points balance that includes pending points, or (c) nothing until posting? | Decides the balance API's fields and whether pending points count in the points balance (glossary open question 1) | (a): only posted points can be redeemed, and 4 of 12 tickets in the S-03 excerpt ask where pending points are (CAN-015) | TBD | owner: Mei Tan (SH-01) | open |
| 3 | Functional | When does the "points added" push go out: when the purchase is recorded as pending, or when the points are posted? | Decides which event triggers the notification and whether a reversal must send a correction | At posting: a return within 24 hours reverses pending points (BRIEF.md:59), so a push at purchase could announce points that disappear | TBD | owner: Mei Tan (SH-01) | open |
| 4 | Functional | If the fraud engine does not answer for a purchase, are its points held as for a fraud hold, or posted as normal? | Decides the failure path of the fraud call and whether points can leak to fraudsters while the engine is down | Held until the fraud engine answers: the most restrictive option for points that convert to money | TBD | owner: Lena Koh (SH-05) | open (blocking) |
| 5 | Functional | What does the app show for points on fraud hold: (a) pending, with no reason, (b) a "held" status, or (c) nothing? | Decides the member-facing states and what the app reveals about fraud checks | (a): it reveals nothing about the fraud check | TBD | owner: Lena Koh (SH-05), with Mei Tan (SH-01) | open |
| 6 | Quality | How many seconds after the POS sends the purchase event may it take until the app shows the pending points, at which percentile, during the year-end peak? | Decides whether a synchronous read path is enough or a cache or projection is needed (the Redis idea) | No recommendation: needs a business value ("quickly", BRIEF.md:75) | TBD | owner: Mei Tan (SH-01) | open |
| 7 | Constraint | Does every member get the "points added" push, or only members who agreed to receive push notifications? | Decides whether a consent check is needed before sending, under PDPA (S-05) | Only members who agreed to push notifications; the data protection officer decides whether this message needs consent | TBD | owner: Farid Osman (SH-04) | open (blocking) |

Group: `Boundary`, `Functional`, `Quality`, `Constraint`, in that order; at most 7 rows per batch, and a follow-up batch continues the numbering.
Answer: the confirmed answer, `Accepted` (the person said "ok" to the recommended answer), or `TBD`.
Source: `<name> (SH-nn) YYYY-MM-DD` or `<role> YYYY-MM-DD` once answered; `owner: <person or role>` while open.
Becomes: `R-nnn` (requirement written), `R-nnn (existing)` (answer confirms it), `R-nnn (open)` (row written with a `TBD` this question resolves), `D-nn` (open boundary decision), `open`, or `open (blocking)`.

## Assumptions

Only when work proceeds before an answer. A blocking question takes the most restrictive option.

| # | Assumption | For question | Reverse by |
| --- | --- | --- | --- |
| A1 | No email is sent; only the push channel is used | 1 | Add an email requirement and an email provider row in `context.md` |
| A2 | The balance response shows posted points as the points balance and pending points as a separate figure | 2 | Merge the two figures in the balance response |
| A3 | The "points added" push is sent when points are posted | 3 | Move the trigger to the purchase event and add a reversal notice |
| A4 | When the fraud engine does not answer, the points stay pending and are not posted | 4 (blocking) | Post on timeout instead |
| A5 | Points on fraud hold are shown as pending, with no reason | 5 | Add a "held" state to the balance response |
| A6 | The push goes only to members who agreed to push notifications | 7 (blocking) | Drop the consent check |
