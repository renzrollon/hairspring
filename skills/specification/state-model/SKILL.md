---
name: state-model
description: >-
  Builds the state machine of one business entity as a Mermaid stateDiagram-v2 (states, events,
  guards, actions), checks it for unreachable states, dead ends and missing transitions with a
  state x event matrix in which every cell is explicit, and emits one EARS WHILE requirement per
  state-dependent behavior. Writes requirements/models/state-{entity}.md and appends draft rows to
  requirements/requirements.csv. Use when an entity has a lifecycle or a status field (payment,
  voucher, points transaction, order, application), when requirements say "only while", "once it
  is posted", "after it expires", when someone asks "what states can X be in" or "what happens if
  Y arrives when X is already Z", or before implementing a status column or workflow. Not for
  work passing between several roles or systems (use process-flow), one actor's interaction with
  the system (use-case-spec), or the entity's attributes and relationships (domain-model).
license: MIT
compatibility: Python 3.9+ optional for scripts/check_states.py; works without it.
metadata:
  stage: specification
  invocation: model
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §3.4.5"
  inputs-from: "domain-model, glossary, requirement-phrasing, use-case-spec, artifact-mining, clarifying-questions"
  outputs-to: "requirement-linter, testability-check, requirements-review, clarifying-questions, conflict-detector"
  work-product: "requirements/models/state-<entity>.md, requirements/requirements.csv"
  version: "0.1.0"
---

# State model

Status-driven behavior breaks in the cells nobody thought about: a return that arrives after the points were redeemed, a hold released after the purchase was reversed. A state machine makes those cells visible. This skill draws the entity's states and transitions, fills a state x event matrix where every cell is a transition, `ignored` or `impossible`, runs a deterministic completeness check, and turns each state-dependent behavior into one EARS `WHILE` requirement.

## When not to use

- Work passes between several roles, teams or systems: `process-flow`.
- One actor pursuing one goal, with alternatives and exceptions: suggest `/use-case-spec`.
- You do not yet know which entities exist or how they relate: `domain-model` first, then model the entity whose status drives behavior.
- The lifecycle of requirements themselves (draft, agreed, ...): already defined in `re-ids`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Lifecycle material for one entity: requirements, business rules, notes, a ticket, a status enum in code | yes | `requirement-phrasing`, `artifact-mining`, `clarifying-questions`, `use-case-spec` |
| `requirements/models/domain-model.md` | no | `domain-model` |
| `requirements/glossary.md` | no | `glossary` |
| `requirements/requirements.csv` | no | `requirement-phrasing` |
| `requirements/schema.json` | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/models/state-<entity>.md` | `assets/state-model.md` | `testability-check`, `requirements-review`, `traceability-matrix` |
| `requirements/requirements.csv` (appended `WHILE` rows) | `assets/requirements.csv` | `requirement-linter`, `testability-check` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the default columns in `assets/requirements.csv`, and say so), `glossary.md`, `requirements.csv`, `models/domain-model.md`, and an existing `models/state-<entity>.md` (update it in place; keep transition numbers `T1..Tn`). The entity name is its glossary term; the slug is kebab-case (`PointsTransaction` becomes `state-points-transaction.md`). One entity per file.
2. **List the states.** A state is a business condition in which the entity reacts differently to at least one event. Use glossary words, PascalCase identifiers. Technical conditions (`RETRYING`, `is_deleted`, status code `3`, queue lag) are not business states: ask what business condition they stand for, or leave them out and say why. Mark the initial state and every final state. Fill the States table with meaning and source.
3. **List the events.** One name per thing that happens to the entity: a message (`returnReceived`), an actor decision, a time event (`returnWindowElapsed`). camelCase, with who sends it and the source. The creating event goes on `[*] --> Initial` and is not a matrix column. Durations and limits you were not given are `TBD` plus an open question.
4. **Draw the transitions.** Read `references/state-diagram-syntax.md`. One line per transition: `From --> To : event [guard] / action`. Guards are business conditions; when every transition for one state and event is guarded, add an `[else]` transition or say what happens otherwise in the matrix. An event that does something without a state change is a self-transition (one per state: Mermaid draws only one; a second reaction usually means a separate state). Composite states, `<<choice>>`, fork and join are not supported by the checker: flatten them.
5. **Fill the state x event matrix.** Run `python3 <skill-dir>/scripts/check_states.py <file> --print-matrix` for a skeleton (without Python: one row per state, one column per event, by hand). Every cell is `→ Target`, `ignored (reason, source)`, `impossible (reason, source)`, or `TBD (Qn)`. Use the decision rule in `references/completeness-and-requirements.md`. Never choose `ignored` or `impossible` yourself without a source: ask with `re-interview`, or write `TBD (Qn)`.
6. **Check completeness.** Run `python3 <skill-dir>/scripts/check_states.py requirements/models/state-<entity>.md`. Fix unreachable states, dead ends, ambiguous transitions and matrix mismatches. Never delete a state or transition only to silence a finding: ask. Every remaining `matrix-gap` must have an open question. Record the result in the Completeness check section. Without Python, run the same checks by hand: reachability from `[*]`, an exit from every non-final state, no blank cell.
7. **Derive the requirements.** Follow the derivation table in `references/completeness-and-requirements.md`: one `WHILE <entity> is <State>, the <system> shall ...` row per state-dependent behavior, `WHILE ..., WHEN <event>, ...` where one event gets different responses by state. Link existing requirements first (the Transitions table's `Covered by` column). Allocate new IDs with `re-ids` (or `re-lint ids next`). `Type=F` (or `Q`), `Source` = the source of the state or cell, `Priority` from the input or `TBD`, `Status=draft`, `Rationale` names the state or cell.
8. **Show, then write.** Show the diagram, the matrix and the new rows; after confirmation (or directly in non-interactive mode) write `state-<entity>.md` from `assets/state-model.md` and append the rows to `requirements.csv` in schema column order.
9. **Lint.** Run the `requirement-linter` skill on the new IDs (or `re-lint check --only-ids <IDs>`). Fix every error before handing off.

## Quality checks

- [ ] Every state is reachable from `[*]`; every non-final state has a transition to another state.
- [ ] Every matrix cell is a transition, `ignored` or `impossible` with a reason and source, or `TBD (Qn)` with a matching open question.
- [ ] `check_states.py` exits 0, or exits 1 with only `matrix-gap` findings that each match an open question.
- [ ] State and event names use glossary terms; no technical states; no invented durations or limits.
- [ ] Each derived requirement has one `WHILE` clause, one `shall`, a source, `Status=draft`; no ID reused.
- [ ] The Mermaid block uses only the subset in `references/state-diagram-syntax.md`.

## Hand-offs

- **Next:** `requirement-linter` on the new rows; `testability-check` (each transition and each matrix cell is a test case); suggest `/requirements-review` for the set.
- **Feeds back to:** `clarifying-questions` with every `TBD` cell; `glossary` with new state and event names; `domain-model` when a state needs an attribute; `conflict-detector` when two sources disagree on a transition (for example a final state that one source reopens); `requirement-phrasing` for transitions no requirement covers.

## Non-interactive mode

Do not guess cells. Write `TBD (Qn)` with an owner role for each unknown, run the check, write the file and the rows, and end with the IDs written, the check result and every open question.

## References

- `references/state-diagram-syntax.md`: the Mermaid stateDiagram-v2 subset that renders on GitHub and that `check_states.py` reads, naming rules, PlantUML alternative. Read it at step 4.
- `references/completeness-and-requirements.md`: matrix cell rules, the checker's finding kinds and fixes, the `WHILE` derivation table. Read it at steps 5 to 7.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: the PointsTransaction lifecycle from the loyalty-points sample, its model file and the rows it adds.
