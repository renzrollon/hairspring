# Clarifying questions: <topic>

| Field | Value |
| --- | --- |
| Task | <ticket key and title, or a one-line summary> |
| Asked | <YYYY-MM-DD> (one date per batch) |
| Asked of | <name (SH-nn) or role>; other owners per question in Source |
| Mode | interactive \| non-interactive |
| Status | open \| partly answered \| answered |

## Already answered (not asked)

| Topic | Answer | Where |
| --- | --- | --- |
| <topic> | <what the repo, ticket or register already says> | <file:line, R-nnn or ticket> |

## Questions

| # | Group | Question | Why it matters | Recommended answer | Answer | Source | Becomes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Boundary | <one topic, W-question, options if known> | <the design choice the answer decides> | <what you would build, and why> | TBD | owner: <person or role> | open |

Group: `Boundary`, `Functional`, `Quality`, `Constraint`, in that order; at most 7 rows per batch, and a follow-up batch continues the numbering.
Answer: the confirmed answer, `Accepted` (the person said "ok" to the recommended answer), or `TBD`.
Source: `<name> (SH-nn) YYYY-MM-DD` or `<role> YYYY-MM-DD` once answered; `owner: <person or role>` while open.
Becomes: `R-nnn` (requirement written), `R-nnn (existing)` (answer confirms it), `D-nn` (open boundary decision), `open`, or `open (blocking)`.

## Assumptions

Only when work proceeds before an answer. A blocking question takes the most restrictive option.

| # | Assumption | For question | Reverse by |
| --- | --- | --- | --- |
| A1 | <what is built as if it were answered> | <#> | <what changes if the answer differs> |
