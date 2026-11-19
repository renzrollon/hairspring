---
name: testability-check
description: >-
  Gives each requirement a verification method (test, inspection, analysis, demonstration), a
  measurable acceptance criterion and a first test idea with its level (unit, integration, e2e,
  manual), written to requirements/verification.csv keyed by R-ID, and sets the Verification column
  in requirements/requirements.csv. Flags unverifiable requirements and proposes a measurable form
  whose unknown targets stay TBD with a question for the owner: it never invents a target. Use
  when requirements were just written or changed, before sprint or test planning, for the
  Definition of Ready, when someone asks "is this testable?", "how would we verify this?", "write
  acceptance criteria" or "test ideas", or when a review reports an unverifiable requirement. Not
  for Given/When/Then acceptance criteria on user stories (user-story-refiner), for eliciting the
  missing quality targets (quality-requirements or clarifying-questions), or for finding which
  tests already cover a requirement (traceability-matrix).
license: MIT
metadata:
  stage: validation
  invocation: model
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §3.8, §3.3.1.2"
  inputs-from: "requirement-phrasing, quality-requirements, constraints-register, user-story-refiner, requirements-review"
  outputs-to: "traceability-matrix, requirement-phrasing, quality-requirements, prototype-brief, to-openspec"
  work-product: "requirements/verification.csv"
  version: "0.1.0"
---

# Testability check

A requirement nobody can verify is a wish: it cannot be accepted, tested or traced. This skill decides, row by row, how each requirement will be shown to be met, writes the pass/fail criterion and a first test idea, and marks the ones that cannot be verified as written, with the measurable form they would need and the question that would complete it. Test strategy then starts from facts instead of guesses.

## When not to use

- User stories that need Given/When/Then acceptance criteria and INVEST: suggest `/user-story-refiner`.
- The requirement lacks a quality target and you want to elicit it with stakeholders: suggest `/quality-requirements` or use `clarifying-questions`.
- You want to know which existing tests cover which requirement: `traceability-matrix`.
- Full quality review of the set: suggest `/requirements-review`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv`, or the IDs the user names | yes | `requirement-phrasing` |
| `requirements/verification.csv` (earlier results) | no | this skill |
| `requirements/quality-requirements.md`, `requirements/constraints.csv`, `requirements/stories/*.md` | no | `quality-requirements`, `constraints-register`, `user-story-refiner` |
| `requirements/context.md`, `requirements/glossary.md` | no | `system-context`, `glossary` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/verification.csv` (one row per R-ID, updated in place) | `assets/verification.csv` | `traceability-matrix`, a test strategy, `to-openspec` |
| `requirements/requirements.csv`: the `Verification` column only | schema enum `test \| inspection \| analysis \| demonstration` | `attribute-schema` views, Definition of Ready |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the defaults, and say so), `glossary.md`, `context.md`, `requirements.csv`, `verification.csv`, and the optional inputs above. Targets, metrics and measurement methods already agreed in `quality-requirements.md` or `constraints.csv` are sources; use them.
2. **Select rows.** The IDs the user names, else every row whose Status is not `withdrawn` or `rejected`. Keep an existing `verification.csv` row when its `Text` still matches `requirements.csv`; redo it when the text changed (the linter reports this as `register-drift`) or the user asks.
3. **Judge verifiability.** Set `Verifiable` with the rules in `references/measurability.md`: `yes` (a pass/fail check follows from the text), `tbd` (the measurable form is clear but a target is `TBD`), `no` (as written it cannot pass or fail: subjective, unbounded, nothing observable).
4. **Choose the method and level.** Use the decision tables in `references/verification-methods.md`. One method per row. The level says where the first check runs: `unit`, `integration`, `e2e` or `manual`.
5. **Write the criterion.** One pass/fail sentence: the situation, the observable result, and the limit. Numbers come only from the requirement text, `quality-requirements.md`, `constraints.csv`, or a named person with a date. Boundaries come from the text (above 5,000 means 5,000 passes without approval). A fact quoted in a Rationale ("last year's peak was about 9,000 per minute") is context for the question, not a target. Unknown value: `TBD` and a `Question` with an owner.
6. **Propose a measurable form for `no` rows.** Use the patterns in `references/measurability.md`: keep every target `TBD`, set `Basis` to `proposed`, and ask the owner the question that would complete it. Do not edit the requirement text; the rewrite goes through `requirement-phrasing` once the question is answered.
7. **Write a first test idea.** One or two sentences a tester can start from: setup, action, what to check, including the boundary or failure case that matters most.
8. **Ask, or log.** In interactive mode, send the open questions as one batch through `re-interview` (at most 7, highest-impact first). Record answers with their source and date in `Basis`, and update the criterion. Otherwise leave them in `Question`.
9. **Show, then write.** Show the table. After confirmation (or directly in non-interactive mode):
   - write `requirements/verification.csv` with the header of `assets/verification.csv`, one row per ID, rows for other IDs kept as they are; `Text` is an exact copy of the requirement's current text;
   - set `Verification` in `requirements.csv` to the method for `yes` and `tbd` rows, and leave it empty for `no` rows. If the column is missing, add it in the schema's optional-column order. Change no other column.
10. **Lint.** Run the `requirement-linter` skill (or `re-lint check`) and confirm there is no `register-drift` or `invalid-enum` finding for the rows you wrote.
11. **Hand to test strategy.** End with counts per method, level and `Verifiable` value, and the list of `no` and `tbd` rows with their questions. If a test-strategy skill is installed (for example `testing-strategy`), give it `requirements/verification.csv`; otherwise give the summary to the test lead.

## Quality checks

- [ ] Every selected R-ID has exactly one row in `verification.csv`; the header matches `assets/verification.csv`.
- [ ] `Method` and `Level` use only the allowed values; `Verifiable` is `yes`, `tbd` or `no`.
- [ ] Every number in `Criterion` appears in the requirement text, a register, or a dated statement by a named person; all others are `TBD` with a `Question` naming an owner.
- [ ] Every `no` row has a proposed measurable form with `Basis` `proposed`, and an empty `Verification` in `requirements.csv`.
- [ ] No requirement `Text`, `Status` or `Version` was changed.
- [ ] The linter reports no `register-drift` or `invalid-enum` for the rows written.

## Hand-offs

- **Next:** a test strategy with `verification.csv`; `traceability-matrix` once tests exist (name them `test_r_nnn_...` so the trace finds them).
- **Feeds back to:** `requirement-phrasing` to rewrite `no` rows once their question is answered; `quality-requirements` or `clarifying-questions` for `TBD` targets; suggest `/prototype-brief` when only users can say what passes (usability, comprehension).

## Non-interactive mode

Do not ask. Write both files, keep every unknown as `TBD` with its question, and end with the summary of step 11 and the list of rows written.

## References

- `references/verification-methods.md`: choosing test, inspection, analysis or demonstration, and the test level; examples. Read it at step 4.
- `references/measurability.md`: the `yes` / `tbd` / `no` rules, criterion patterns for F, Q and C rows, and measurable forms for common unverifiable phrasings. Read it at steps 3, 5 and 6.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: eleven loyalty-points requirements and the `verification.csv` they produce.
