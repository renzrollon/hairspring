# Requirements review YYYY-MM-DD

| Field | Value |
| --- | --- |
| Scope | full set \| IDs: R-nnn, R-nnn \| diff: `git diff <base> -- requirements/` (<n> rows added, <n> changed, <n> deleted) |
| Requirements reviewed | <n>: R-nnn to R-nnn |
| Set checks against | requirements/requirements.csv (<n> rows)<, other registers> |
| Requested by | <name or role> |
| Schema | requirements/schema.json \| defaults (no schema.json found) |
| Lint | `<command>`: exit <n>; `<summary line>` \| manual |
| Perspectives | user, architect, tester (parallel subagents \| sequential, fresh pass each) |
| Verdict | not ready \| ready after fixes \| ready |

## Summary

| Severity | Count |
| --- | --- |
| blocker | <n> |
| major | <n> |
| minor | <n> |

## Requirement grades

Adequacy and understandability are graded first. A row with a blocker or major finding on either is not graded further (—).

| Requirement | Adequate | Understandable | Necessary | Unambiguous | Complete | Verifiable |
| --- | --- | --- | --- | --- | --- | --- |
| R-nnn | ok \| F-nn | ok \| F-nn | ok \| F-nn \| — | ok \| F-nn \| — | ok \| F-nn \| — | ok \| F-nn \| — |

## Set-level checks

| Criterion | Result | Findings |
| --- | --- | --- |
| consistent | pass \| fail | F-nn |
| non-redundant | pass \| fail | F-nn |
| complete | pass \| fail | F-nn |
| modifiable | pass \| fail | F-nn |
| traceable | pass \| fail | F-nn |
| conformant | pass \| fail | F-nn |

## Findings

| ID | Severity | Criterion | Location | Finding | Proposed fix | Found by | Resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-nn | blocker \| major \| minor | <one of the twelve criteria> | R-nnn (<file>:<line>) | <what is wrong and why it matters> | <rewrite or action; TBD plus a question for unknown values> | lint:<rule> \| user \| architect \| tester \| set check | open |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | <question> | <SH-nn name or role> | F-nn, R-nnn |

## Correction log

Filled in only after the author decides on each finding. Resolution values: `open`, `accepted`, `rejected`, `deferred`, `fixed`.

| Finding | Decision | Decided by | Date | Change applied |
| --- | --- | --- | --- | --- |
