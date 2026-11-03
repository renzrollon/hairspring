---
name: requirement-classifier
description: >-
  Classifies requirement-like statements with the concern test as functional (F), quality (Q) or
  constraint (C), and flags what is not a requirement: facts, present-tense descriptions and
  `will` statements, goals, and solutions in disguise (a technology or design choice nobody
  outside the team mandated). Adds flags for compound or vague statements, a first Kano guess
  (dissatisfier, satisfier, delighter) and the skill each statement goes to next, appended to
  requirements/classification.md as a fixed table. Use when a PRD section, ticket, transcript,
  interview capture, candidates.csv or pasted list mixes requirements with facts and design ideas,
  when someone asks "is this a requirement?", "functional or non-functional?", "which of these are
  NFRs?" or "sort these", and before requirement-phrasing, quality-requirements or
  constraints-register so every statement lands in the right place. Not for rewriting statements
  into EARS (use requirement-phrasing), for eliciting missing values (clarifying-questions) or for
  ranking (prioritization).
license: MIT
metadata:
  stage: foundations
  invocation: model
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §1.2, §4.2.1"
  inputs-from: "artifact-mining, interview-guide, clarifying-questions, elicitation-workshop, observation-protocol"
  outputs-to: "requirement-phrasing, quality-requirements, constraints-register, clarifying-questions, conflict-detector"
  work-product: "requirements/classification.md"
  version: "0.1.0"
---

# Requirement classifier

Mixed input is the norm: a PRD paragraph holds a business rule, a performance wish, a vendor's delivery date and a database choice in four sentences. Sending all of them to the same place produces requirements nobody can test and design decisions nobody agreed. This skill sorts each statement by the concern it addresses, not by whether it says "what" or "how", flags the non-requirements and the solutions in disguise, makes a first Kano guess, and records where each statement goes next in `requirements/classification.md`.

## When not to use

- The statements are already sorted and need rewriting into EARS with IDs: `requirement-phrasing`.
- You know a quality requirement is needed but the target value is missing: `quality-requirements` or `clarifying-questions`.
- You need a ranked backlog: `prioritization` (it can use the Kano guesses after stakeholders confirm them).

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Statements: pasted text, a ticket, a transcript, a capture sheet or `candidates.csv` | yes | `artifact-mining`, `interview-guide`, `clarifying-questions`, `elicitation-workshop`, `observation-protocol` |
| `requirements/glossary.md` | no | `glossary` |
| `requirements/requirements.csv` (to spot duplicates) | no | `requirement-phrasing` |
| `requirements/schema.json` | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/classification.md` (a new batch appended) | `assets/classification.md` | `requirement-phrasing`, `quality-requirements`, `constraints-register`, `clarifying-questions`, `conflict-detector` |

## Procedure

1. **Read the workspace.** Load `schema.json` (defaults if missing), `glossary.md` and `requirements.csv`. If `classification.md` exists, append a new batch at the end; never edit earlier batches.
2. **Split into statements.** One row per statement, quoted as given (drop filler words only). Keep a compound statement in one row with the flag `compound` when all parts get the same verdict and type; split it into rows when the parts differ (a function plus a technology choice).
3. **Record where each came from.** `Source`: a source ID (`S-06`), interview (`I-02`), person and date, or `file:line`. `Ref`: the statement's existing ID (`CAN-012`, `R-020`), else `-`.
4. **Apply the concern test.** Read `references/concern-test.md` and ask its four questions in order: is it something the system must make true (else `fact`, `goal` or `unclear`)? Does someone outside the team restrict the solution or the process (`C`), or is it a design choice nobody mandated (`solution`)? Is the concern how well (`Q`, name the quality characteristic)? Otherwise it is behavior (`F`). Use the tie-breakers in the reference; write the deciding concern in a few words in `Concern`.
5. **Flag.** Add every flag from the fixed list in the reference that applies (`will`, `rule`, `compound`, `weak-word`, `missing-value`, `mandate-unconfirmed`, ...). A `will` statement is a fact until its source says it is binding; never upgrade it yourself.
6. **Guess Kano.** Only for `requirement` rows of type F or Q; `-` for everything else. Use the signals in the reference. It is a guess: say so in the column header, and do not use it to set `Priority`.
7. **Route.** Fill `Next` from the routing table in the reference. A `solution` row names the architect (role or `SH-nn`) and gets an open question about the need behind it. Write the type of that need in `Type` if you can tell it, else `TBD`.
8. **Log open questions.** One row per `unclear`, `goal`, `missing-value`, `mandate-unconfirmed` or `will` whose binding level is unknown, each with an owner role or `SH-nn`.
9. **Show, then write.** Show the batch table and the summary line. After confirmation (or directly in non-interactive mode), append the batch to `requirements/classification.md` using `assets/classification.md` exactly.
10. **Apply only when asked.** If the user asks to correct existing register rows (rows whose `Ref` is an `R-` ID), list each proposed change (`R-020 Type Q → F`) and change only `Type` (and `Kano` if the column exists) after confirmation. Never add rows to `requirements.csv`: `requirement-phrasing` does that.

## Quality checks

- [ ] The batch table has exactly the columns `# | Statement | Source | Ref | Verdict | Type | Concern | Kano (guess) | Flags | Next`.
- [ ] Verdict, Type, Kano and Flags use only the values in `references/concern-test.md`.
- [ ] Every `solution` row routes to a named architect role and has an open question about the need behind it.
- [ ] Kano is `-` on every row that is not an F or Q requirement.
- [ ] The summary counts add up to the number of rows.
- [ ] `requirements.csv` was not changed, unless step 10 was confirmed.

## Hand-offs

- **Next:** `requirement-phrasing` with the `requirement` rows; `quality-requirements` with Q rows that lack a target; `constraints-register` with C rows.
- **Feeds back to:** `clarifying-questions` with `unclear`, `goal` and `missing-value` rows; `conflict-detector` with rows flagged `conflict?`; `glossary` with words the classification needed but the glossary lacks.

## Non-interactive mode

Write the batch directly, keep every judgment call visible in `Concern` and `Flags`, and end with the summary line and the open questions.

## References

- `references/concern-test.md`: the four questions, tie-breakers, Kano signals, the fixed flag and routing vocabularies. Read it before step 4.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: a loyalty-points PRD section and the batch it becomes.
