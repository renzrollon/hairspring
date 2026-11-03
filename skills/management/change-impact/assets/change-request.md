# CR-nnn: {title}

| Field | Value |
| --- | --- |
| ID | CR-nnn |
| Status | draft |
| Requested by | {name (stakeholder ID)}, {YYYY-MM-DD} |
| Source | {ticket, email, meeting note, or source ID} |
| Change authority | {process.change_authority}: {named person or board} |
| Route | {backlog item for the product owner \| request to the Change Control Board \| ...} |
| Trace coverage | {trace matrix: requirements/trace/trace.csv, built YYYY-MM-DD \| search only (lower coverage)} |
| Links | {seed requirement IDs, CF-nn, RDR-nnn, earlier CR-nnn} |

## 1. Requested change

> {the request, verbatim}

| Statement | Before | After |
| --- | --- | --- |
| {ID or "new"} | {current text or value} | {requested text or value, or TBD} |

## 2. Reason

{Why the requester wants it, in their words, with source. TBD and an open question if not given.}

## 3. Impact set

| # | Item | Kind | Impact | Evidence | Found by |
| --- | --- | --- | --- | --- | --- |
| 1 | {ID or path} | {requirement \| source \| decision \| code \| test \| work product \| interface \| stakeholder} | {text change \| new \| withdraw \| re-implement \| re-test \| review \| update document \| inform} | {trace.csv row, path:line, or "user"} | {trace \| search \| user} |

## 4. Conflicts and dependencies

| Item | Conflicts with or depends on | Note | Next step |
| --- | --- | --- | --- |

## 5. Options

| Option | What changes | Effort (relative) | Risk | Assumptions |
| --- | --- | --- | --- | --- |
| 0 | No change (reject or defer) | n/a | {level: factors} | {consequence of not changing} |
| A | {the request as asked} | {XS \| S \| M \| L \| XL} (proposed by the agent \| confirmed by {team}, {date}) | {level: factors} | {statements to confirm} |
| B | {smaller or phased alternative, if any} | | | |

## 6. Recommendation

{Option and the reason in two or three sentences. This is the agent's recommendation; the change authority decides.}

## 7. Draft for the change authority

{A backlog item for the product owner, or a request to the Change Control Board, in the form given in references/impact-analysis.md section 5.}

## 8. Decision

| Field | Value |
| --- | --- |
| Decision | pending |
| Option | |
| Decided by | |
| Date | |
| Conditions | |
| Decision record | {RDR-nnn if a conflict was resolved, else "none"} |

## 9. Requirement updates

Applied: no (requirement rows are changed only after an approved decision)

| Requirement | Change | Text before | Text after | Version | Status |
| --- | --- | --- | --- | --- | --- |

## 10. Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
