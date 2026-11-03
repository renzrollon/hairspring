---
name: re-interview
description: >-
  The questioning primitive behind every re-skills skill that asks people things: one question at a
  time (or one prioritized batch), W-questions, a recommended answer, paraphrase to confirm, and the
  answer recorded with its source. Use whenever a re-skills skill needs information from a person
  (clarifying-questions, interview-guide, system-context, quality-requirements, conflict-to-decision,
  and others), or when running without a human and questions must be logged instead of guessed. Not
  a user-facing interview script (that is interview-guide).
license: MIT
user-invocable: false
metadata:
  stage: primitives
  invocation: primitive
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §4.2.2; Principle 3 (shared understanding)"
  inputs-from: "none"
  outputs-to: "clarifying-questions, interview-guide, conflict-detector"
  work-product: "Answers recorded with source; open questions logged"
  version: "0.1.0"
---

# RE interview

Questions are expensive for the person answering them. Ask only what changes the work product, make each question easy to answer, and never let an answer get lost or a gap get filled with a guess.

## When not to use

- Preparing a live interview with a stakeholder: use `interview-guide` (it builds on this).
- Deciding which questions matter before coding: use `clarifying-questions`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| The calling skill's open points | yes | the calling skill |
| `requirements/glossary.md` | no | `glossary` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| Answers in the calling skill's work product, with source | see `references/question-craft.md` | the calling skill |

## Procedure

1. **Filter.** Keep a question only if a different answer would change a requirement, a boundary, a priority or the design. Drop the rest or note them as assumptions.
2. **Shape each question.** One topic per question; a W-word (who, what, when, where, why, how, how much, how often); closed where the options are known, open where they are not. Offer a recommended answer and the reason, so the person can say "yes" in one word.
3. **Order.** Boundary and scope first, then functional behavior, then quality (performance, security, availability, usability...), then constraints. Within a group, highest impact first.
4. **Ask.** Default: one question at a time, wait, then the next. When the calling skill says *batch*, send one numbered batch of at most 7 questions grouped by the order above.
5. **Confirm.** Paraphrase the answer in one sentence with the glossary's terms ("So: exports run asynchronously and the file is kept 7 days. Right?"). Record the confirmed version.
6. **Record.** Every answer carries who answered and when: `PO 2026-11-03`, a stakeholder ID (`SH-02`) or an interview ID (`I-03`). Write it where the calling skill says (usually a new or updated row via `re-ids`).
7. **Stop.** Stop when the remaining questions would not change the work product, or the person asks to stop. List what is still open.

## Non-interactive mode

When no person can answer (CI, autonomous agent run, the user said "don't ask"), do not guess. Write each unanswered question into the work product as an open question with an owner role, put `TBD` in the affected field, and finish the rest of the work.

## Quality checks

- [ ] Every question would change something if answered differently.
- [ ] No answer was invented; every recorded answer has a source and date.
- [ ] Open questions are listed with an owner role.

## Hand-offs

- **Next:** back to the calling skill with the recorded answers.
- **Feeds back to:** `glossary` when an answer introduces or redefines a term.

## References

- `references/question-craft.md`: question patterns by type (boundary, functional, quality, constraint), probes, and anti-patterns. Read it before drafting more than three questions.
