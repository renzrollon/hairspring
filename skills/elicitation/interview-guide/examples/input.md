# Input: interview with the customer support lead (loyalty-points sample)

## Run 1 (phase A), 2026-11-04

> `/interview-guide customer support lead Daniel Ng, 30 min video call tomorrow, about member lookups and points adjustments`

What the skill found in the workspace:

- `requirements/stakeholders.md`: SH-06 Daniel Ng, Customer support lead; SH-03 Grace Lim, Finance controller; SH-04 Farid Osman, data protection officer; SH-08 Wei Jie Chua, platform tech lead (the interviewer).
- `requirements/sources.csv`: S-06 is interview I-01 (Mei Tan), S-07 is interview I-02 (Arjun Pillai). Next interview ID: I-03.
- `requirements/requirements.csv`: R-061 "WHEN a support agent submits a points adjustment, the support console shall require a reason code." and R-062 "WHEN a support agent submits a points adjustment above 5,000 points, the support console shall require approval by a second support user before the loyalty service posts it." Both draft, source S-06.
- `requirements/candidates.csv` holds CAN-001 to CAN-008. LOY-131 (CSV export) was settled on 2026-11-03.

## Run 2 (phase B), 2026-11-05

> `/interview-guide notes for I-03 below`

Interviewer's notes, as typed after the call:

```text
notes only, ok with Daniel
most loyalty contacts = "where are my points" + vouchers not working at the till
agents look up members by phone number most of the time, sometimes card number. Email almost never.
"Lookups must be instant, the member is on the phone."
missing points -> they ask for the receipt. "Give us a big 'fix missing points' button that finds the purchase from the receipt number."
roughly 300 manual adjustments a week, mostly missing points from offline tills
">5,000 needs a second approver. That's Grace's rule from Finance, after the 2024 incident."
reason code list too long, agents pick 'Other' for about 40% of adjustments
"Agents should not see full NRIC or card numbers. Farid told us that last year."
support hours 08:00 to 22:00, seven days. console down -> cases on a spreadsheet, adjust later
new agents need about two weeks before they do adjustments alone
"goodwill points" = adjustment without a purchase, for complaints
read-back: phone/card lookup yes, receipt search yes, reason list yes, NRIC yes but Farid's call, 5,000 rule yes (Grace's)
close: talk to Grace about the threshold; read the support playbook "Loyalty cases v4"
```

The expected output is the interview file after run 2 (`expected-output.md`) and the rows appended to `requirements/candidates.csv` (`expected-candidates.csv`).
