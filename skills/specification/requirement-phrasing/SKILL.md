---
name: requirement-phrasing
description: >-
  Rewrites requirement-like sentences into EARS / ISO 29148 phrase templates: one requirement per
  sentence, the right obligation verb (shall / should / may), measurable wording, an ID and the
  full attribute set, appended to requirements/requirements.csv. Use when a ticket, PRD, transcript,
  chat, candidate list or review finding contains requirements that must become unambiguous and
  verifiable, when someone says "turn this into requirements", "write this as EARS", "rewrite with
  shall", "make these testable", or when requirement-linter flags weak words, passive voice or
  missing obligations. Not for user stories with acceptance criteria (use user-story-refiner),
  eliciting the missing numbers (use clarifying-questions or quality-requirements), mandates such
  as regulations, platforms or deadlines (use constraints-register), or deciding F/Q/C when unsure
  (use requirement-classifier).
license: MIT
compatibility: Python 3.9+ optional for scripts/lint_requirements.py; works without it.
metadata:
  stage: specification
  invocation: model
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §3.3.1, §3.2"
  inputs-from: "clarifying-questions, artifact-mining, requirement-classifier, requirements-review, requirement-linter"
  outputs-to: "requirement-linter, requirements-review, testability-check, to-openspec"
  work-product: "requirements/requirements.csv"
  version: "0.1.0"
---

# Requirement phrasing

Natural-language requirements fail in predictable ways: vague words, missing actors, hidden conditions, two requirements in one sentence. Phrase templates remove most of that by construction. This skill rewrites each statement into one EARS pattern, keeps its source, and appends it to the requirement register.

## When not to use

- The input is a user story that needs acceptance criteria or splitting: suggest `/user-story-refiner`.
- A target value is missing (how fast, how many): ask first with `clarifying-questions`, or suggest `/quality-requirements` for a whole quality walkthrough.
- The statement is a mandate from outside the team (regulation, platform, interface spec, deadline): `constraints-register`.
- You are not sure whether a statement is a requirement at all: `requirement-classifier` first.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Statements to phrase (text, ticket, `candidates.csv`, review findings) | yes | `clarifying-questions`, `artifact-mining`, `requirement-classifier`, `requirements-review` |
| `requirements/glossary.md` | no | `glossary` |
| `requirements/schema.json` | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/requirements.csv` (appended or updated rows) | `assets/requirements.csv` | `requirement-linter`, `requirements-review`, `testability-check`, `to-openspec` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the default columns `ID,Type,Text,Source,Priority,Status,Rationale`, and say so in the final message), `glossary.md`, and the existing `requirements.csv` to avoid duplicates.
2. **Split.** Break the input into atomic statements: one condition set, one actor, one obligation. Set aside what is not a requirement to phrase, and say where it went:
   - a fact (present tense or `will`): context, no row;
   - a solution in disguise ("use Redis", "add a Kafka topic"): a design decision; ask for the need behind it and report it for the architect, no row;
   - a mandate from outside the team (regulation, platform standard, interface spec, deadline): hand it to `constraints-register`.
3. **Pick the pattern.** Use `references/ears-patterns.md`: ubiquitous, `WHEN` (event), `WHILE` (state), `WHERE` (feature), `IF ... THEN` (unwanted behavior), or a complex combination. Name the system or actor explicitly; use glossary terms.
4. **Fix the obligation.** `shall` = binding, `should` = expected, `may` = optional. Replace `will`, `can` and passive voice; rewrite `must` to `shall` unless the existing register already uses `must` as its binding verb (then keep the register's convention).
5. **Make it measurable.** Replace weak words with a value, a range or a defined term. If the value is unknown, write `TBD` in the text and add an open question; never invent a number.
6. **Allocate IDs and attributes.** Use `re-ids` for new IDs (or `re-lint ids next --kind requirement --count <n>`). Set `Type` (F/Q/C), `Source` (the statement's origin: source ID, person and date, or `file:line`), `Priority` (from the input; `TBD` if nobody said), `Status=draft`, and a one-sentence `Rationale`. Keep the old ID when rephrasing an existing row: increment `Version` if that column exists, and move an `agreed` row back to `proposed`.
7. **Show, then write.** Show a before/after table with the columns `Original`, `Rewritten`, `Pattern`, `Requirement` (the ID, or `n/a` for statements set aside at step 2). After confirmation (or directly in non-interactive mode), append to `requirements.csv` in schema column order.
8. **Lint.** Run `python3 <skill-dir>/scripts/lint_requirements.py --only-ids <new IDs>` from the repository root (or the `requirement-linter` skill, or `re-lint check --only-ids <new IDs>`). Without Python, walk the pitfalls table in `references/ears-patterns.md` over each new row. Fix every error before handing off.

## Quality checks

- [ ] One obligation verb per requirement; no `will`, no passive without an actor.
- [ ] Every condition (`WHEN`, `WHILE`, `IF`) has a consequence with `shall`/`should`/`may`.
- [ ] No weak words left; every unknown value is `TBD` with an open question.
- [ ] Every row has ID, Type, Text, Source, Priority, Status, Rationale; no ID reused.
- [ ] Linter passes with no errors on the new rows.

## Hand-offs

- **Next:** `requirement-linter` on the new rows; `testability-check` to add verification methods; suggest `/requirements-review` for a set-level review.
- **Feeds back to:** `clarifying-questions` with every `TBD`; `glossary` with any new term; `requirement-classifier` when the F/Q/C call was unclear; `constraints-register` with mandates found at step 2.

## Non-interactive mode

Write the rows directly, keep `Status=draft`, and end with a list of the IDs written and every open question.

## References

- `references/ears-patterns.md`: the six EARS patterns with templates, examples, and the natural-language pitfalls to remove. Read it at step 3.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: a ticket from the loyalty-points sample and the rows it becomes.
