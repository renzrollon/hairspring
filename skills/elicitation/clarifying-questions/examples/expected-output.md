# Clarifying questions: loy-131-csv-export

| Field | Value |
| --- | --- |
| Task | LOY-131 Support console: add export to CSV |
| Asked | 2026-11-03 (batch 1, Q1-Q7); 2026-11-03 (batch 2, Q8) |
| Asked of | Daniel Ng (SH-06); Q5 owned by Farid Osman (SH-04) |
| Mode | interactive |
| Status | partly answered |

## Already answered (not asked)

| Topic | Answer | Where |
| --- | --- | --- |
| File encoding and delimiter | UTF-8 with byte-order mark, comma delimiter, as for the finance extracts | `src/admin/exports.py:5-6` |
| Columns of the history | Date, store, transaction type, points, balance after the transaction | R-021 |
| Maximum period available | The last 24 months | R-020 |

## Questions

| # | Group | Question | Why it matters | Recommended answer | Answer | Source | Becomes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Boundary | Who may run the export: support agents only, also support team leads, or also Finance or members in the app? | Decides the permission check and whether the app needs the feature too | Support agents and support team leads, in the support console only; Finance already receives the warehouse extract | Accepted | Daniel Ng (SH-06) 2026-11-03 | R-030 |
| 2 | Functional | What does one export contain: one member's points history with the R-021 columns, or other data as well? | Decides the query and the file layout | One member, one row per points transaction, the R-021 columns | Accepted | Daniel Ng (SH-06) 2026-11-03 | R-031 |
| 3 | Functional | Which period does the export cover: always the full 24 months of R-020, or a range the agent picks? | Decides whether the UI needs a date picker and the API a range filter | A range the agent picks within the 24 months | The agent picks a range within the 24 months, last 3 months preselected; nice to have | Daniel Ng (SH-06) 2026-11-03 | R-032 |
| 4 | Quality | How long may the agent wait for the file while the member is on the phone? | Decides between a direct download and a background job with a notification | No recommendation: needs a business value | "A few seconds"; the largest histories hold about 2,000 transactions in 24 months. Seconds still open (Q8) | Daniel Ng (SH-06) 2026-11-03 | R-033 |
| 5 | Quality | Which personal data may the file contain: member ID only, or also name, email and phone number? | Decides the columns and the data protection exposure of every exported file | Member ID only, no contact data, which keeps the file's personal data to a minimum | TBD (Daniel: "not my call") | owner: Farid Osman (SH-04) | open (blocking) |
| 6 | Constraint | Must each export be recorded in the audit log (agent, member, period, time)? | Decides whether the export writes an audit event, and its fields | Yes: the file takes personal data out of the system | Yes; Grace Lim (SH-03) wants it too | Daniel Ng (SH-06) 2026-11-03 | R-034 |
| 7 | Constraint | May the system store or email the file, or does it only go to the agent's browser as a download? | Decides whether files are stored, and under which retention rule (DRP-2024, S-05) | Browser download only; nothing kept on the server | Accepted | Daniel Ng (SH-06) 2026-11-03 | R-035 |
| 8 | Quality | How many seconds, at most, may the download take for a history of 2,000 transactions? | Sets the target and the test for R-033 | No recommendation: needs a business value | TBD | owner: Daniel Ng (SH-06) | R-033 (open) |

## Assumptions

| # | Assumption | For question | Reverse by |
| --- | --- | --- | --- |
| A1 | The export contains the member ID and the R-021 columns, and no name, email or phone number. | 5 | Adding columns to the export query and file header once SH-04 answers |
| A2 | The download is generated directly in the request (no background job). | 4, 8 | Moving generation to a background job if the Q8 target cannot be met for 2,000 transactions |
