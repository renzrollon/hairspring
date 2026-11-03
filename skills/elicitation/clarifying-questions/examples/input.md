# Input: ticket LOY-131 (loyalty-points sample)

> **LOY-131: Support console: add export to CSV**
>
> Support agents need to export a member's points history to CSV so they can send it to members who dispute their balance. Needed for the support console go-live.
>
> Reporter: Daniel Ng (Customer support lead, SH-06), 2026-11-02.

The user's prompt: "Implement LOY-131."

## What the agent found before asking

- `src/admin/exports.py:5-6` already writes CSV as UTF-8 with a byte-order mark and a comma delimiter for the finance extracts (`EXPORT_ENCODING`, `EXPORT_DELIMITER`).
- `requirements/requirements.csv` holds R-001 to R-029. R-020: the support console shall display a member's points history for the last 24 months. R-021: the points-history columns are date, store, transaction type, points and balance after the transaction.
- `requirements/elicitation/` does not exist yet.

## Answers, given by Daniel Ng in chat on 2026-11-03

> 1 ok. 2 ok. 3 agent picks the range, last 3 months preselected, nice to have though. 4 a few seconds, the member is on the phone; our biggest members have about 2,000 transactions in 24 months. 5 not my call, ask Farid. 6 yes, Grace wants that too. 7 ok.

The expected output is the questions file after these answers (`expected-output.md`) and the rows appended to `requirements/requirements.csv` (`expected-output.csv`).
