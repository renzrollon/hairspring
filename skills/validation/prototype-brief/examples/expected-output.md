# Prototype brief: voucher redemption in the app

| Field | Value |
| --- | --- |
| File | requirements/elicitation/prototype-voucher-redemption.md |
| Status | done |
| Owner | Mei Tan (SH-01, Head of Loyalty) |
| Decision-maker | Mei Tan (SH-01, product owner) |
| Decision it informs | Which redemption requirements the app team builds in the first release |
| Decision needed by | TBD |
| Requirements under validation | R-044, R-049, R-050, R-051 (R-048 moved out, see below) |
| Kind | throwaway |
| Fidelity | mock-up |
| Time box | Two weeks from 2026-11-10 |
| Created | 2026-11-04 |

## Why a prototype

The redemption rules are settled (S-01), but how members want to redeem is not: choosing points in steps of 100, finding a voucher at the till, the "points missing" message and sending vouchers to others are Mei's and Priya's assumptions. Reading the requirements cannot settle them; watching members try the flow can.

## Hypotheses

| H | Requirements | We believe | Validated if | Changed if | Dropped if |
| --- | --- | --- | --- | --- | --- |
| H1 | R-049 | Members can choose the points to redeem in steps of 100 without help | At least 5 of 6 complete T1 without help | Fewer than 5 of 6 complete T1 without help, and they describe another way to redeem | n/a (redemption itself is not in question) |
| H2 | R-044 | Members find their unused voucher from the home screen when they are at the till | At least 5 of 6 open the voucher from the home screen in T2, without help or a detour | Fewer than 5 of 6, and they look for it in the same other place | n/a |
| H3 | R-050 | The "points missing" message tells members what they need to do | At least 5 of 6 restate the message correctly in T3 | Fewer than 5 of 6 restate it correctly | At least 4 of 6 say the message puts them off |
| H4 | R-051 | Members want to send an unused voucher to another member | At least 3 of 6 would use it in the next month | n/a (2 of 6 is inconclusive) | At most 1 of 6 would use it |

## Kind and fidelity

- **Kind:** throwaway, because the question is whether these are the right requirements, and some may be dropped; the mock-up is deleted after the round.
- **Fidelity:** mock-up, because navigation, wording and the redemption choice are what is in question, and a clickable mock-up with fake data shows them.
- **Faked or left out:** balances, vouchers and QR images are static; no loyalty service, no POS.
- **Not testable at this fidelity:** R-048 (scanning the voucher QR code at the till) needs a real phone and a TillPoint scanner; interview I-02 reports scans failing on dark screens. Moved to a native spike with the POS vendor (SH-09), open question 1.

## Participants and sessions

| Group | Represents | Number | Recruited by | Notes |
| --- | --- | --- | --- | --- |
| App beta members | Members redeeming in the customer mobile app | 6 | Priya Raman (SH-07) | Mix of frequent and occasional shoppers |

Consent and data: participants appear as P1 to P6; screen recordings and notes hold no names; recordings are deleted once results are recorded, retention confirmed with Farid Osman (SH-04), open question 2.

## Tasks

| T | Task as told to the participant | Hypotheses | Success looks like |
| --- | --- | --- | --- |
| T1 | "You have 1,240 points. Get a voucher you can use at the till today." | H1 | A voucher is created without help |
| T2 | "You are at the till now. Show the cashier your voucher." | H2 | The voucher screen is open without help |
| T3 | "This is an account with 320 points. What is the app telling you?" | H3 | The participant says, in their words, how many points are missing to redeem |
| T4 | Closing question: "Would you send one of your vouchers to someone else in the next month? Why?" | H4 | A yes or no with a reason |

## Measures

| Measure | Hypotheses | How captured | Threshold | Agreed by |
| --- | --- | --- | --- | --- |
| Task success without help (H2: first path taken) | H1, H2 | Observer sheet, yes / no per participant; for T2 also the first screen opened | At least 5 of 6 | Mei Tan, 2026-11-04 |
| Correct restatement | H3 | Observer sheet, correct / incorrect | At least 5 of 6 | Mei Tan, 2026-11-04 |
| Stated intent | H4 | Answer to T4 | Keep: at least 3 of 6; drop: at most 1 of 6 | Mei Tan, 2026-11-04 |
| Wrong turns and quotes | H1 to H4 | Observer notes with the screen where it happened | none (qualitative) | n/a |
| Time on task | H1, H2 | Timer | none agreed: recorded, not judged | n/a |

## Stop criteria

- Time box: two weeks from 2026-11-10.
- Stop early when: every hypothesis has met its validated or dropped threshold; or the first three sessions fail T1 the same way (fix the flow, restart the count).
- Stop and escalate when: the mock-up is being connected to the loyalty service or real member data (decide throwaway or evolutionary first); a participant raises a fraud or privacy concern (inform SH-05 or SH-04).

## Results

| H | Requirements | Evidence | Outcome | Notes |
| --- | --- | --- | --- | --- |
| H1 | R-049 | 2 of 6 completed T1 without help; P1, P3, P4, P5 looked for fixed values. P4: "Just give me 5, 10 or 20 dollars, like a gift card." | changed | Members expect fixed voucher values, not a points amount |
| H2 | R-044 | 5 of 6 opened the voucher from the home screen without help; P6 looked under History first | validated | Threshold met; the History detour is a new candidate |
| H3 | R-050 | 6 of 6 restated the message correctly. P3: "I'm 180 short, so I'll come back on Saturday." | validated | |
| H4 | R-051 | 0 of 6 would send a voucher in the next month. P5: "If someone sends me a voucher I'd think it's a scam." | dropped | P5's concern goes to SH-05 (fraud) |

Outcome: `validated` | `changed` | `dropped` | `inconclusive`.

## Flow back to requirements

| Requirement | Outcome | Proposed change | Confirmed by | Applied |
| --- | --- | --- | --- | --- |
| R-049 | changed | Rewrite with `requirement-phrasing`: "WHEN a member redeems points in the customer mobile app, the customer mobile app shall offer vouchers in fixed values of SGD TBD." (open question 3); Version + 1 | pending | no |
| R-044 | validated | Links + requirements/elicitation/prototype-voucher-redemption.md; Status unchanged | pending | no |
| R-050 | validated | Links + requirements/elicitation/prototype-voucher-redemption.md; Status unchanged | pending | no |
| R-051 | dropped | Status draft → rejected; Links + requirements/elicitation/prototype-voucher-redemption.md | pending | no |

## New candidate requirements

| Candidate | Evidence | Next step |
| --- | --- | --- |
| The vouchers screen is reachable from the History screen | P6 looked for the voucher under History first (T2) | Ask SH-01 whether to add it; draft with `requirement-phrasing` if yes |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | Who runs the native spike for scanning voucher QR codes on a TillPoint test till, and when? | SH-09 POS vendor integration manager, SH-02 Arjun Pillai | R-048 |
| 2 | How long may session recordings be kept before deletion? | SH-04 Farid Osman | Consent and data |
| 3 | Which fixed voucher values should the app offer? | SH-01 Mei Tan | R-049 |
| 4 | By when must the redemption scope be decided? | SH-01 Mei Tan | Decision needed by |
