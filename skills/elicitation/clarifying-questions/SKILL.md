---
name: clarifying-questions
description: >-
  Before you implement a vague ticket, feature request or task, ask the smallest set of questions
  whose answers would change the design: at most 7, grouped boundary / functional / quality /
  constraint, each with a recommended answer. The Q&A goes to
  requirements/elicitation/questions-<topic>.md and every answer becomes a requirement in
  requirements/requirements.csv with the person and date as source. Use when a task leaves out who,
  which data, how much, how fast, which errors or which limits ("add export to CSV", "make it
  faster", "add notifications", "support SSO", "add an endpoint for X"), when you are about to
  guess a requirement, or when the user says "ask me first", "grill me", "what's unclear". Skip it
  when the task is fully specified or a pure refactor, rename, formatting change or dependency
  bump: say so in one line and proceed. Not for a planned stakeholder interview (use
  interview-guide), a full quality walkthrough (quality-requirements), or rewording known
  statements (requirement-phrasing).
license: MIT
metadata:
  stage: elicitation
  invocation: model
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §4.2.2; Principle 3 (shared understanding)"
  inputs-from: "glossary, system-context, artifact-mining, requirement-phrasing, requirements-review"
  outputs-to: "requirement-phrasing, requirement-linter, quality-requirements, system-context, testability-check"
  work-product: "requirements/elicitation/questions-<topic>.md, requirements/requirements.csv"
  version: "0.1.0"
---

# Clarifying questions

An agent that guesses a requirement ships the guess. This skill finds the few unknowns in a task whose answers would change the design, asks them in one prioritized batch with a recommended answer each, and records every answer as a requirement with its source. The Q&A lives in `requirements/elicitation/questions-<topic>.md`; the requirements go to `requirements/requirements.csv`.

## When not to use

- The task is fully specified, or is a pure refactor, rename, formatting change or dependency bump with no behavior change: write "No clarifying questions: <reason>." and proceed. Create no file.
- A planned, live conversation with a stakeholder: `interview-guide`.
- A systematic pass over every quality characteristic: `quality-requirements`.
- The statements are known and only need rewording: `requirement-phrasing`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| The task: ticket, issue, feature request or chat message | yes | the user, a tracker |
| Code, tests and docs the task touches | no | the repository |
| `requirements/requirements.csv`, `glossary.md`, `context.md`, `candidates.csv` | no | `requirement-phrasing`, `glossary`, `system-context`, `artifact-mining` |
| Open `TBD`s and review findings | no | `requirement-phrasing`, `requirements-review` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/elicitation/questions-<topic>.md` | `assets/questions.md` | the implementer, `requirements-review` |
| `requirements/requirements.csv` (appended rows) | `assets/requirements.csv` | `requirement-linter`, `requirements-review`, `testability-check` |

## Procedure

1. **Read first.** Read the task, then the code, tests and docs it touches, and `requirements/schema.json` (else the default columns `ID,Type,Text,Source,Priority,Status,Rationale`), `requirements.csv`, `glossary.md` and `context.md` if they exist. Anything these answer is not a question: note it under *Already answered* with where you found it.
2. **Decide whether to ask.** List the unknowns, using `references/unknowns-by-ticket-shape.md` for the task's shape. Apply the design test to each: would two plausible answers lead to different code, data model, interface, permission or test? If no unknown passes, write "No clarifying questions: <reason>." and proceed without creating a file.
3. **Pick the smallest set.** Keep only unknowns that pass. Rank by the cost of a wrong guess: security, personal data, money, irreversible data changes and external interfaces first; wording and layout last. Keep at most 7. The rest wait for a later batch or become assumptions (step 8).
4. **Shape each question** with the `re-interview` primitive in batch mode: one topic, a W-word, closed with options when the options are known. Order the groups Boundary, Functional, Quality, Constraint. Fill *Why it matters* (the design choice the answer decides) and *Recommended answer* (the option you would build, with a short reason). A number in a recommended answer must come from the task, the repo or a cited source; otherwise recommend an option that needs no number, or write "no recommendation: needs a business value".
5. **Write, then ask.** Create `requirements/elicitation/questions-<topic>.md` from `assets/questions.md` (`<topic>`: kebab-case ticket key plus subject, for example `loy-131-csv-export`) with every *Answer* `TBD`. Then ask in one message: the numbered batch, grouped, each question with its recommended answer, ending "Reply per number: ok, or your answer." When a question belongs to someone other than the user (security, data protection, finance), say who. Stop and wait.
6. **Record answers.** Paraphrase any ambiguous answer and confirm it. Fill *Answer*; set *Source* to the person and date (`Mei Tan (SH-01) 2026-11-03`; `PO 2026-11-03` if you only know the role; a relayed answer names the person who gave it). "ok" means that person accepted the recommended answer. An unanswered question keeps `TBD` and `owner: <person or role>` in *Source*.
7. **Turn answers into requirements.** For every answer that adds or changes behavior, a quality target or a constraint, write one requirement per sentence with the `requirement-phrasing` skill (if it is not installed: an EARS pattern, `shall`, no weak words, and a vague answer such as "a few seconds" stays `TBD` plus a follow-up question). Allocate IDs with `re-ids`. Set `Source` from step 6, `Status=draft`, `Priority` only if someone stated it (else `TBD`), and a one-sentence `Rationale`. Show the rows, then append them to `requirements.csv` and put their IDs in *Becomes*. An answer that confirms an existing requirement cites that ID; a boundary answer that leaves scope open becomes a `D-nn` for `system-context`.
8. **Proceed on what is known.** Implement only what answers and stated assumptions cover. An assumption is allowed only when it is cheap to reverse: add it under *Assumptions* (A1, A2, ... with its question number) and repeat it in the PR description or final message. Questions on security, personal data, money, legal duties or destructive data changes are *blocking*: build only the most restrictive option (least exposed, deleted, paid or granted), recorded as an assumption, or leave that part out.

## Quality checks

- [ ] At most 7 questions per batch; each passes the design test and names the choice it decides.
- [ ] Nothing the task, code, docs or requirements already answer was asked.
- [ ] No number in a recommended answer was invented.
- [ ] Every recorded answer names a person (or role) and an ISO date; no recommended answer was recorded without that person's "ok".
- [ ] New rows have all attributes, `Status=draft` and the answer's source; `requirement-linter` (or `re-lint check --only-ids <new IDs>`) reports no errors.
- [ ] Every assumption is labelled, points to its question, and takes the most restrictive option when its question is blocking.

## Hand-offs

- **Next:** `requirement-linter` on the new rows, `testability-check` before writing tests, then implement.
- **Feeds back to:** `quality-requirements` when several quality answers stay vague; `system-context` with `D-nn` boundary questions; `glossary` with new or redefined terms; `conflict-detector` when an answer contradicts an existing requirement.

## Non-interactive mode

When nobody can answer (CI, an autonomous run, "don't wait for me"): write the questions file with every *Answer* `TBD` and the owner in *Source*, append no requirement rows, and proceed only under assumptions per step 8. End with the open questions, their owners, and the assumptions you built on. Never record a recommended answer as an answer.

## References

- `references/unknowns-by-ticket-shape.md`: design-changing unknowns for common ticket shapes (export, import, "make it faster", notifications, search, delete, roles, integration, rule change, batch job), what the repo usually answers, and skip examples. Read it at step 2.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: ticket LOY-131 (CSV export) on the loyalty-points sample, the questions file after the answers, and the rows appended.
