# Requirements review 2026-11-03

| Field | Value |
| --- | --- |
| Scope | diff: `git diff origin/main -- requirements/` (8 rows added, 0 changed, 0 deleted) |
| Requirements reviewed | 8: R-040 to R-047 |
| Set checks against | requirements/requirements.csv (11 rows) |
| Requested by | Wei Jie Chua (SH-08) |
| Schema | defaults (no schema.json found) |
| Lint | `python3 <skill-dir>/scripts/lint_requirements.py --format json --changed-only origin/main`: exit 1; `re-lint: 2 errors, 0 warnings, 1 info in 11 rows (1 file)` |
| Perspectives | user, architect, tester (parallel subagents) |
| Verdict | not ready |

## Summary

| Severity | Count |
| --- | --- |
| blocker | 1 |
| major | 5 |
| minor | 1 |

## Requirement grades

Adequacy and understandability are graded first. A row with a blocker or major finding on either is not graded further (—).

| Requirement | Adequate | Understandable | Necessary | Unambiguous | Complete | Verifiable |
| --- | --- | --- | --- | --- | --- | --- |
| R-040 | ok | ok | ok | ok | ok | ok |
| R-041 | ok | F-07 | ok | ok | ok | ok |
| R-042 | ok | ok | ok | ok | F-06 | ok |
| R-043 | ok | ok | ok | F-03 | ok | F-03 |
| R-044 | ok | ok | ok | F-05 | ok | F-05 |
| R-045 | ok | ok | F-01 | ok | ok | ok |
| R-046 | F-02 | ok | — | — | — | — |
| R-047 | ok | ok | ok | ok | F-04 | F-04 |

## Set-level checks

| Criterion | Result | Findings |
| --- | --- | --- |
| consistent | fail | F-01 |
| non-redundant | fail | F-01 |
| complete | fail | F-04, F-06 |
| modifiable | pass | |
| traceable | pass | |
| conformant | fail | F-03, F-04 |

## Findings

| ID | Severity | Criterion | Location | Finding | Proposed fix | Found by | Resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-01 | blocker | consistent | R-045 (requirements/requirements.csv:10), R-040 (:5) | R-045 issues a voucher on any request; R-040 requires at least 500 posted points. For a member below 500 the rows give opposite results; above 500 R-045 only repeats R-040. | Withdraw R-045 and keep R-040 if SH-07 confirms the minimum applies (Q5). If SH-07 does not, register the conflict with `conflict-detector`. | user, tester, set check | open |
| F-02 | major | adequate | R-046 (requirements/requirements.csv:11) | Names a database technology and no platform mandate is cited: a design decision, not a stakeholder need. | If PostgreSQL is mandated (Q6), record it as a constraint (Type C) with `constraints-register`; otherwise record the choice in an ADR and withdraw R-046. | architect | open |
| F-03 | major | verifiable | R-043 (requirements/requirements.csv:8) | Weak word "fast": no target, so no test can pass or fail. A `must` quality requirement. | WHEN the POS sends a voucher validation request, the loyalty service shall return the voucher status within TBD ms for TBD % of requests. (Q1) | lint:weak-word, tester | open |
| F-04 | major | complete | R-047 (requirements/requirements.csv:12) | No obligation verb, no actor, no period, and nothing on the redeemed points of an expired voucher; Rationale is TBD. | The loyalty service shall expire an unused voucher TBD days after issue. (Q2) Add a requirement for the points of an expired voucher once Q3 is answered; Rationale from SH-01. | lint:missing-obligation, lint:open-tbd, user | open |
| F-05 | major | unambiguous | R-044 (requirements/requirements.csv:9) | "Recent" has several readings: the last N days, the last N vouchers, unused only. Tests and screens will differ. | WHEN the member opens the vouchers screen, the customer mobile app shall list the member's unused vouchers issued in the last TBD days. (Q4) | user, tester | open |
| F-06 | major | complete | R-042 (requirements/requirements.csv:7) | No response is specified for an unknown, expired or already applied voucher, and "voucher status" values are not defined. | Add: IF the voucher is unknown, expired or already applied, THEN the loyalty service shall return a rejection reason to the POS. Define the voucher statuses (Issued, Applied, Expired, Cancelled) in the glossary. | tester, architect | open |
| F-07 | minor | understandable | R-041 (requirements/requirements.csv:6) | "it" refers to the loyalty service only by position. | WHEN the loyalty service issues a voucher, the loyalty service shall deduct the redeemed points from the member's posted balance. | user | open |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | What is the longest acceptable voucher validation response, and for what share of requests? | SH-02 Arjun Pillai | F-03, R-043 |
| 2 | How many days after issue does an unused voucher expire? | SH-01 Mei Tan | F-04, R-047 |
| 3 | When a voucher expires unused, are its points returned to the balance or lost? | SH-01 Mei Tan, SH-03 Grace Lim | F-04, R-047 |
| 4 | Which vouchers should the vouchers screen list: how far back, and only unused ones? | SH-01 Mei Tan | F-05, R-044 |
| 5 | Did R-045 mean to drop the 500-point minimum, or is it a simplified copy of R-040? | SH-07 Priya Raman | F-01, R-045 |
| 6 | Is PostgreSQL a platform mandate for the loyalty service? | SH-08 Wei Jie Chua | F-02, R-046 |

## Correction log

Filled in only after the author decides on each finding. Resolution values: `open`, `accepted`, `rejected`, `deferred`, `fixed`.

| Finding | Decision | Decided by | Date | Change applied |
| --- | --- | --- | --- | --- |
