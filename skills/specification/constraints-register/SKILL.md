---
name: constraints-register
description: >-
  Records constraints (technical, legal or regulatory, organizational, cultural, environmental)
  with source, rationale, mandator, expiry and review date, and separates them from design
  decisions: a constraint restricts the solution space because someone outside the team mandates
  it; a choice the team made itself is a design decision for an ADR. Writes Type C rows to
  requirements/requirements.csv and details to requirements/constraints.csv. Use whenever a
  statement says the solution must use, run on, comply with, integrate through, stay in, or be
  live by something, or cites a regulation, contract, license, policy, platform standard, vendor
  interface, deadline or budget; when someone says "we have to use X", "legal says", "the
  platform team requires", "data must stay in"; and when another skill finds a mandate. Not for
  quality targets like latency (quality-requirements), the team's own technology choices (record
  an ADR), or contradictions between constraints and requirements (conflict-detector).
license: MIT
metadata:
  stage: specification
  invocation: model
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §1.2, §4.2"
  inputs-from: "requirement-classifier, artifact-mining, clarifying-questions, interview-guide, source-inventory, system-context, quality-requirements, user-story-refiner"
  outputs-to: "conflict-detector, requirements-review, traceability-matrix, change-impact, spec-assembler, to-openspec"
  work-product: "requirements/constraints.csv"
  version: "0.1.0"
---

# Constraints register

A constraint is a requirement the team cannot negotiate away on its own: a regulation, a contract, a platform standard, a vendor interface, a deadline. Missed constraints surface late and expensively; fake ones ("we must use Kafka" when nobody mandated it) freeze a design decision before anyone discussed it. This skill applies the mandate test, records each real constraint as a Type C requirement with who mandates it, when it expires and when to review it, and routes everything else to where it belongs.

## When not to use

- A quality target (response time, availability, encryption strength) with no outside mandate: suggest `/quality-requirements`.
- A technology or architecture choice the team made itself: an ADR for the architect, not a requirement.
- A constraint that contradicts another constraint or a requirement: `conflict-detector`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Statements that mandate something (text, PRD, policy, contract, transcript, findings of another skill) | yes | `requirement-classifier`, `artifact-mining`, `clarifying-questions`, `quality-requirements`, `user-story-refiner` |
| `requirements/requirements.csv`, `requirements/constraints.csv` | no | `constraints-register`, every emitting skill |
| `requirements/sources.csv`, `requirements/stakeholders.md` | no | `source-inventory`, `stakeholder-map` |
| `requirements/schema.json` | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/requirements.csv` (Type C rows) | `assets/requirements.csv` | `requirement-linter`, `conflict-detector`, `traceability-matrix` |
| `requirements/constraints.csv` (one detail row per Type C row, same ID) | `assets/constraints.csv` | `spec-assembler`, `change-impact`, `to-openspec`, `requirements-review` |

## Procedure

1. **Read the workspace.** Locate `requirements/` (or the `workspace` in `schema.json`). Read `schema.json` (else the default columns `ID,Type,Text,Source,Priority,Status,Rationale`; say so), `requirements.csv` and `constraints.csv` (existing constraints: update, don't duplicate), `sources.csv` and `stakeholders.md` (mandators and source IDs).
2. **Spot candidates.** Look for "must use / run on / comply with / integrate through / only in / not allowed / by {date} / within {budget}", and for named laws, regulations, standards, contracts, licenses, policies, vendors and platforms.
3. **Apply the mandate test.** Ask in order; the first "no" decides. Worked cases are in `references/constraint-kinds.md`.

   | # | Question | If no |
   | --- | --- | --- |
   | 1 | Does it restrict *how* the solution may be built, run or delivered (technology, location, interface, process, date, money), rather than *what* it does or *how well*? | A function: `requirement-phrasing`. A quality target: suggest `/quality-requirements` |
   | 2 | Does someone outside the team mandate it (law, regulator, contract, customer, vendor, enterprise or platform standard, management)? Name them. | Design decision: report it as an ADR candidate; write no row |
   | 3 | Is the team unable to change it alone? | Design decision: ADR candidate |

   **No mandator, no constraint.** If the mandator is unknown, ask "Who requires this? What happens if we don't?" following `re-interview`. In non-interactive mode, report it as "unconfirmed: design decision unless a mandator is named", with the open question, and write no row.
4. **Categorize.** `technical`, `legal`, `organizational`, `cultural` or `environmental` (definitions and examples in `references/constraint-kinds.md`). Contracts, licenses and regulations are `legal`; deadlines, budgets, staffing and mandated processes are `organizational`.
5. **Phrase it.** One constraint per sentence with `shall`, naming the system and the restriction: "The loyalty service shall run on the shared Kubernetes platform." Apply the `requirement-phrasing` rules: no weak words, no `will`, no compound sentences. The mandate goes in the columns, not in the sentence.
6. **Fill the details.** One `constraints.csv` row per constraint (columns in `assets/constraints.csv`):

   | Column | Holds | Unknown |
   | --- | --- | --- |
   | `ID` | The same R-ID as the `requirements.csv` row | never unknown |
   | `Title` | A short label | |
   | `Category` | One of the five values | ask |
   | `Mandated by` | The person, role or body outside the team, with a stakeholder ID if one exists | no row (step 3) |
   | `Mandate reference` | The document, clause or statement with its source: `S-05 (DRP-2024)`, `SH-08 2026-11-03 (verbal)` | `TBD` |
   | `Expires` | `YYYY-MM-DD`, `none` (the mandator said it does not expire), or `TBD` | `TBD` |
   | `Review by` | The date to re-check that the mandate still holds: a date the mandator gave, or the date of an event they named (a contract renewal, a vendor upgrade) | `TBD`, with the event in the open question |
   | `Negotiable` | `no`, `yes` (the mandator can grant an exception), or `TBD` | `TBD` |
   | `If violated` | The consequence: penalty, failed audit, integration failure, contract breach | `TBD` |
   | `Affects` | Space-separated R-IDs, interfaces or components | `TBD` |
   | `Open question` | One question to the mandator covering every `TBD` in the row, or `none` | |

   Never invent a date, clause or mandator. Flag a `Review by` date before today as *review overdue* and a passed `Expires` as *expired*; propose `Status=withdrawn` for an expired constraint only after its owner confirms.
7. **Allocate IDs and write.** Use `re-ids` (or `re-lint ids next --kind requirement`). In `requirements.csv`: `Type=C`, the sentence, `Source` (the mandate's source ID, or person and date), `Priority` (`must` for a binding mandate, `should` when the mandator allows exceptions, else `TBD`), `Status=draft`, `Rationale` (why the mandator requires it, one sentence). Append both rows in column order. In interactive mode, show the rows first when there are more than three.
8. **Check and report.** Run `requirement-linter` on the new IDs (or `re-lint check --only-ids <IDs>`). Confirm every Type C row has exactly one `constraints.csv` row and vice versa. Send any constraint that contradicts another constraint or a requirement to `conflict-detector`. Report: constraints written, ADR candidates, rerouted statements, open questions, overdue reviews.

## Quality checks

- [ ] Every Type C row names a mandator outside the team and a mandate reference; nothing was written without a mandator.
- [ ] Every Type C row in `requirements.csv` has exactly one `constraints.csv` row with the same ID, and vice versa.
- [ ] `Category` is one of the five values; `Review by` is a date (`YYYY-MM-DD`) or `TBD`; `Expires` is a date, `none` or `TBD`; every `TBD` is covered by the row's open question.
- [ ] No invented dates, clauses or mandators; no ID reused.
- [ ] Design decisions, quality targets and functions are reported, not written as constraints.
- [ ] The linter reports no errors on the new rows.

## Hand-offs

- **Next:** `conflict-detector` when a constraint contradicts another constraint or a requirement; `requirement-linter` on the new rows; `traceability-matrix` so constraints trace to their mandate sources; report ADR candidates to the architect.
- **Feeds back to:** `source-inventory` when a mandate document has no source ID; `clarifying-questions` with unknown mandators and dates; suggest `/quality-requirements` for quality targets found and `/change-impact` when a constraint changes or expires.

## Non-interactive mode

Ask nothing. Write rows only for statements whose mandator is named in the input; report the rest as "unconfirmed: design decision unless a mandator is named" with the open question. Unknown dates, references and consequences are `TBD`. End with the IDs written, ADR candidates, rerouted statements, open questions and overdue reviews.

## References

- `references/constraint-kinds.md`: the five categories, the mandate test on worked cases, phrasing and date rules. Read it the first time you run step 3.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: statements from the loyalty-points sample and the rows they become.
