# Clarifying questions: loy-131-csv-export

| Field | Value |
| --- | --- |
| Task | LOY-131 Support console: add export to CSV |
| Asked | 2026-11-03 (batch 1, Q1-Q7) |
| Asked of | Daniel Ng (SH-06); Q5 owned by Farid Osman (SH-04) |
| Mode | interactive |
| Status | open |

## Already answered (not asked)

| Topic | Answer | Where |
| --- | --- | --- |
| Columns of the history | Date, store, transaction type, points, balance after the transaction | R-021 |
| Maximum period available | The last 24 months | R-020 |

## Questions

| # | Group | Question | Why it matters | Recommended answer | Answer | Source | Becomes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Boundary | Who may run the export: support agents only, also support team leads, or also Finance or members in the app? | Decides the permission check and whether the app needs the feature too | Support agents and support team leads, in the support console only | TBD | owner: Daniel Ng (SH-06) | open |
| 2 | Functional | What does one export contain: one member's points history with the R-021 columns, or other data as well? | Decides the query and the file layout | One member, one row per points transaction, the R-021 columns | TBD | owner: Daniel Ng (SH-06) | open |
| 3 | Functional | Which period does the export cover: always the full 24 months of R-020, or a range the agent picks? | Decides the date picker and the range filter | A range the agent picks within the 24 months | TBD | owner: Daniel Ng (SH-06) | open |
| 4 | Quality | How long may the agent wait for the file while the member is on the phone? | Direct download vs background job | No recommendation: needs a business value | TBD | owner: Daniel Ng (SH-06) | open |
| 5 | Quality | Which personal data may the file contain: member ID only, or also name, email and phone number? | Decides the columns and the data protection exposure | Member ID only, no contact data | TBD | owner: Farid Osman (SH-04) | open (blocking) |
| 6 | Constraint | Must each export be recorded in the audit log (agent, member, period, time)? | Decides whether the export writes an audit event | Yes: the file takes personal data out of the system | TBD | owner: Daniel Ng (SH-06) | open |
| 7 | Constraint | May the system store or email the file, or does it only go to the agent's browser as a download? | Decides whether files are stored, and under which retention rule | Browser download only; nothing kept on the server | TBD | owner: Daniel Ng (SH-06) | open |

## Assumptions

| # | Assumption | For question | Reverse by |
| --- | --- | --- | --- |
