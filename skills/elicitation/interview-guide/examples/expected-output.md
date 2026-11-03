# Interview I-03: customer support lead

| Field | Value |
| --- | --- |
| Interview ID | I-03 |
| Interviewee | Daniel Ng (SH-06), Customer support lead |
| Interviewer / note-taker | Wei Jie Chua (SH-08) / Wei Jie Chua (SH-08) |
| Date, duration, format | 2026-11-05, 30 min, video |
| Consent | notes only |
| Status | summarized |

## Goals

| # | Goal | Feeds |
| --- | --- | --- |
| G1 | Settle how agents find a member and a purchase during a call or chat | Lookup candidates; R-020 area |
| G2 | Confirm the adjustment rules: reason codes and second approval | R-061, R-062 |
| G3 | Find the quality needs of support work: waiting, availability, what agents may see | `quality-requirements` input |

Out of scope: the CSV export (LOY-131, settled 2026-11-03); the member app.

## Prepare

- [x] Read: S-03 support ticket export summary, R-020, R-061, R-062, CAN-001 to CAN-008
- [x] Send the interviewee the goals and the time box
- [x] Bring the closed questions of block 3b on screen

## Script

| Block | Min | Focus |
| --- | --- | --- |
| 1 Warm-up | 3 | Consent, role, a normal shift |
| 2 Open | 9 | What members want from support, last difficult case, what slows agents |
| 3 Narrow and closed | 6 | Finding members and purchases, wrong adjustments, volumes; confirm R-061, R-062 |
| 4 Quality | 5 | Performance efficiency, interaction capability, security, reliability |
| 5 Constraints | 3 | Organizational, legal and regulatory |
| 6 Confirm | 3 | Read back the main points |
| 7 Close | 1 | What we missed, who else, documents, follow-up |
| Total | 30 | |

### 1. Warm-up

1. Is it all right if I take notes? I will not record audio.
2. What does a typical shift look like for your agents, and how much of it is about loyalty?

### 2. Open questions

1. When members contact support about points, what do they usually want?
2. Tell me about the last difficult points case your team handled.
3. What slows your agents down most today?

### 3. Narrowing and closed questions

1. How do agents find the member during a call or chat? What do they ask the member for?
2. When a member says points are missing, how do agents find the purchase?
3. What happens when an adjustment turns out to be wrong? Who corrects it?
4. How many manual adjustments does the team make in a typical week?

Confirm (3b):

| Ref | Closed question |
| --- | --- |
| R-061 | Every adjustment needs a reason code. Is that still right? |
| R-062 | Adjustments above 5,000 points need a second approver. Who set that limit? |

### 4. Quality probes

| Characteristic | Probe | Quantify follow-up |
| --- | --- | --- |
| Performance efficiency | Where in a call do agents wait on the system? | What wait would be too long while the member is on the line? |
| Interaction capability | How long does a new agent take to handle points cases alone? | Which step do new agents get wrong most often? |
| Security | Which member data should agents not see or change? | What must be traceable afterwards? |
| Reliability | During which hours must the console work? What do agents do when it is down? | How long an outage can the team bridge? |

### 5. Constraint probes

| Category | Probe |
| --- | --- |
| Organizational | Which approval rules for adjustments are set outside your team, and by whom? |
| Legal and regulatory | Which data protection rules does your team follow for lookups? Who owns them? |

### 6. Confirmation

Read back the summary rows marked for confirmation; correct the capture sheet live.

### 7. Close

1. What should I have asked and didn't?
2. Who else should I talk to about lookups and adjustments?
3. Which documents or reports should I read?
4. May I come back with follow-up questions?

## Capture sheet

| # | Block | Statement (speaker's words) | Kind | Follow-up |
| --- | --- | --- | --- | --- |
| C1 | 1 | Notes only is fine. | fact | |
| C2 | 2 | Most loyalty contacts are "where are my points" and vouchers not working at the till. | problem | |
| C3 | 3 | Agents look up members by phone number most of the time, sometimes card number. Email almost never. | need | |
| C4 | 4 | Lookups must be instant, the member is on the phone. | quality | What wait is too long, measured from search to result? |
| C5 | 3 | When points are missing we ask for the receipt. Give us a big 'fix missing points' button that finds the purchase from the receipt number. | solution | Need behind it: find the purchase by receipt number |
| C6 | 3 | Roughly 300 manual adjustments a week, mostly missing points from offline tills. | fact | |
| C7 | 3b | Above 5,000 points needs a second approver. That's Grace's rule from Finance, after the 2024 incident. | rule | Grace Lim (SH-03) to confirm the threshold |
| C8 | 3 | The reason code list is too long; agents pick 'Other' for about 40% of adjustments. | problem | Which reasons hide behind 'Other'? |
| C9 | 4 | Agents should not see full NRIC or card numbers. Farid told us that last year. | constraint | Farid Osman (SH-04) to confirm the rule and its source |
| C10 | 4 | Support hours are 08:00 to 22:00, seven days a week. When the console is down we write cases on a spreadsheet and adjust later. | quality | Availability target for support hours (SH-08) |
| C11 | 4 | New agents need about two weeks before they do adjustments alone. | fact | |
| C12 | 2 | Goodwill points: an adjustment without a purchase, given for complaints. | term | |

## Summary

| Ref | Statement | Kind guess | From | Confirmed | Open question | Candidate |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Support agents find a member by mobile phone number or card number. | F | C3 | yes | | CAN-009 |
| S2 | Member lookup results appear while the member is still on the call. | Q | C4 | yes | OQ1 | CAN-010 |
| S3 | Support agents find the purchase behind a missing-points claim by its receipt number. | F | C5 | yes | | CAN-011 |
| S4 | A points adjustment above 5,000 points needs approval by a second support user. | F | C7 | yes | OQ2 | R-062 (existing) |
| S5 | The adjustment reason codes match the reasons agents actually record. | F | C8 | yes | OQ3 | CAN-012 |
| S6 | Support agents do not see full NRIC or card numbers of members. | C | C9 | yes | OQ4 | CAN-013 |
| S7 | The support console is available during support hours, 08:00 to 22:00 every day. | Q | C10 | no | OQ5 | CAN-014 |
| S8 | Most loyalty contacts concern missing points and vouchers rejected at the till. | fact | C2 | | | |
| S9 | About 300 manual adjustments a week, mostly missing points from offline tills. | fact | C6 | | | |
| S10 | New agents need about two weeks before they do adjustments alone. | fact | C11 | | | |
| S11 | Goodwill points: an adjustment without a purchase, given for complaints. | term | C12 | | | |

R-061 (reason code required) was confirmed in block 3b; no change.

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| OQ1 | What is the longest acceptable wait from starting a member search to seeing the result? | Daniel Ng (SH-06) | S2, CAN-010 |
| OQ2 | Is the 5,000-point threshold for a second approver still current, and who may approve? | Grace Lim (SH-03) | S4, R-062 |
| OQ3 | Which reasons do agents record under 'Other'? (a sample of recent adjustments) | Daniel Ng (SH-06) | S5, CAN-012 |
| OQ4 | Which identifiers must be masked for agents, and which policy says so? | Farid Osman (SH-04) | S6, CAN-013 |
| OQ5 | What availability does the support console need during support hours, and when may maintenance happen? | Wei Jie Chua (SH-08) | S7, CAN-014 |

## Follow-ups

- People to talk to: Grace Lim (SH-03) on the approval threshold; Farid Osman (SH-04) on masking.
- Documents to read: support playbook "Loyalty cases v4" (register with `source-inventory`).
- Glossary terms: goodwill points.
