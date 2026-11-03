---
name: use-case-spec
description: >-
  Writes one use case as a Cockburn-style form: primary actor, goal, scope, level, stakeholders
  and interests, preconditions, minimal and success guarantees, trigger, main success scenario,
  alternatives, exceptions, business rules and open issues, plus a Mermaid use case diagram and,
  for branching scenarios, an activity diagram. Every system step links a requirement ID or gets
  a new draft requirement. Writes requirements/models/uc-{name}.md and appends rows to
  requirements/requirements.csv. Started explicitly with /use-case-spec followed by the goal.
  Use when a team needs the end-to-end interaction for one actor goal before splitting stories,
  writing tests or estimating: "write the use case for redeem voucher", "what are the
  alternative flows", "main flow and exceptions for checkout". Not for work across several roles
  with no single actor goal (use process-flow), an entity lifecycle (use state-model), or
  backlog stories with acceptance criteria (use user-story-refiner).
license: MIT
disable-model-invocation: true
argument-hint: "[actor goal, e.g. 'redeem voucher']"
metadata:
  stage: specification
  invocation: user
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §3.3.2, §3.4.2.2"
  inputs-from: "system-context, stakeholder-map, glossary, requirement-phrasing, clarifying-questions, artifact-mining"
  outputs-to: "user-story-refiner, testability-check, requirements-review, requirement-linter, traceability-matrix"
  work-product: "requirements/models/uc-<name>.md, requirements/requirements.csv"
  version: "0.1.0"
---

# Use case specification

A requirement list says what the system must do; it does not say in which order an actor and the system interact to reach a goal, or what happens when a step goes differently. A use case does: one primary actor, one goal, a main success scenario, and every extension that branches off it, each ending explicitly. This skill interviews for the frame, writes the use case in a fixed Cockburn-style form, draws the use case diagram (and an activity diagram when the scenario branches a lot), and links every system step to a requirement ID, proposing new draft requirements where none exists.

## When not to use

- Work crosses several roles or teams with no single actor goal (refund handling, month-end close): `process-flow`.
- You need the states of one entity and what each event does in each state: `state-model`.
- You need backlog items with acceptance criteria: `/user-story-refiner` (a finished use case is a good input for it).
- The system boundary or the list of actors is still unclear: `/system-context` first.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| The goal to specify (the argument), plus notes, tickets or transcripts about it | yes | the user, `clarifying-questions`, `artifact-mining` |
| `requirements/context.md` (system boundary, actors, interfaces) | no (ask when missing) | `system-context` |
| `requirements/stakeholders.md` | no | `stakeholder-map` |
| `requirements/requirements.csv` | no | `requirement-phrasing` |
| `requirements/glossary.md` | no | `glossary` |
| `requirements/schema.json` | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/models/uc-<name>.md` | `assets/use-case.md` | `user-story-refiner`, `testability-check`, `requirements-review`, `traceability-matrix` |
| `requirements/requirements.csv` (appended draft rows) | schema columns, default `ID,Type,Text,Source,Priority,Status,Rationale` | `requirement-linter`, `testability-check` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the default columns, and say so in the output), `context.md`, `stakeholders.md`, `glossary.md`, `requirements.csv`, and every `models/uc-*.md`. If the use case already exists, update it in place; when you renumber steps, update every extension reference. If another file already covers the goal under another name, say so and stop.

2. **Name the goal and check the level.** The name is a verb and an object from the primary actor's view: `Redeem voucher`, not `Voucher processing`. The slug is kebab-case: `uc-redeem-voucher`. Apply the level tests in `references/form-guide.md` (summary, user goal, subfunction). A name like "Manage X", "Maintain X" or a list of create/read/update/delete operations is not one goal: list the goals hidden in it, ask which one to write now, and wait. In non-interactive mode, write no file; return the candidate goals and stop.

3. **Interview for the frame.** Use `re-interview`: one question at a time, each with a recommended answer the person can accept in one word. Ask only what the sources do not answer, in this order:
   1. Primary actor: who wants the goal (a role from `stakeholders.md` or `context.md`).
   2. Scope: the system under design, treated as a black box (from `context.md`).
   3. End point: what the primary actor has when the use case succeeds. This decides where the scenario stops.
   4. Trigger: the event that starts it.
   5. Preconditions: what the system can rely on being true at the start.
   6. Stakeholders and interests: who else cares and what they need protected.
   7. Minimal guarantee: what must hold even when the goal fails.

   Record each answer with who gave it and when. Stop asking when further answers would not change the scenario. Unknown values are `TBD` with an open issue; never a plausible guess.

4. **Write the main success scenario.** Three to nine steps, numbered. Each step names who acts (the primary actor, a supporting actor, or the system by its name) and one intention: `<actor> <verb> <object>`. No conditions (no "if"), no user-interface or technology words (button, screen, click, field, API, endpoint, table, queue, framework names). "The system validates the request" is not enough: say what it checks and put the rule in Business rules (`BR2`). Step patterns are in `references/form-guide.md`.

5. **Find the extensions.** Walk every step and ask "what can go differently here?". For each condition the actor or system can detect, number it `<step><letter>` (`2a`; `*a` for any step), write its sub-steps (`2a1`, `2a2`), and end it explicitly: `resume at step N`, `use case ends in success`, or `use case ends in failure`. Put it under Alternatives if the goal is still reached, under Exceptions if it is not (the minimal guarantee must hold there). If nobody knows what should happen, write the condition under Exceptions with the action `TBD (Qn); use case ends in failure` until answered.

6. **Link the requirements.** For every step and sub-step the system performs, find existing requirements in `requirements.csv` by meaning, not by wording, and list their IDs. Where none exists, draft one requirement: `WHEN <trigger>, the <system> shall <response>.` for scenario steps, `IF <condition>, THEN the <system> shall <response>.` for exceptions (the `requirement-phrasing` skill has the full pattern set). Allocate IDs with `re-ids` (or `re-lint ids next`). Rows get `Type=F` (or `Q`), `Source` = the source of the step, `Priority` from the input or `TBD`, `Status=draft`, and a `Rationale` naming the use case and step. Steps by the primary or a supporting actor get `none: actor step`; a system step whose response is still `TBD` gets `none until Qn`.

7. **Draw the use case diagram.** Follow `references/diagram-conventions.md`: actors outside a subgraph for the system boundary, the use case as a stadium node inside it, primary actors on the left, supporting actors on the right, plain lines for associations. PlantUML only when the user asks or `schema.json` says so.

8. **Decide on the activity diagram.** Draw one when any of these holds: more than 3 extensions; an extension resumes at an earlier step (a loop); the scenario spans more than one session or channel. Use the activity convention in `references/diagram-conventions.md` (the same shapes as `process-flow`). Draw resolved paths only and list the `TBD` extensions under the diagram. Otherwise write one line saying why no activity diagram is needed.

9. **Show, then write.** Show the form, the diagrams and the new requirement rows. After the user confirms, write `requirements/models/uc-<name>.md` from `assets/use-case.md` (every heading, in order) and append the rows to `requirements.csv` in schema column order.

10. **Lint and close.** Run the `requirement-linter` skill on the new IDs (or `re-lint check --only-ids <IDs>`; without either, check the rows against `requirement-phrasing`'s pitfalls by hand). Fix every error. End with the file written, the IDs added, the open issues with owners, and the recommended next step.

## Quality checks

- [ ] The name is a verb and an object; one primary actor; the level is stated; the scope is the system under design.
- [ ] The main success scenario has 3 to 9 steps, no conditions, no user-interface or technology words.
- [ ] Every extension has a detectable condition, numbered sub-steps and an explicit ending.
- [ ] Minimal guarantee and success guarantee are filled.
- [ ] Every system step links an R-ID; every new row is `draft`, has a source, and passes the linter with no errors.
- [ ] No invented values: limits, durations and amounts come from a source or are `TBD` with an open issue.
- [ ] Both diagrams follow `references/diagram-conventions.md`; the activity diagram exists when step 8 requires it.

## Hand-offs

- **Next:** recommend `/user-story-refiner` to slice the scenario and its extensions into stories; run `testability-check` on the new rows (each path through the scenario is a test case); recommend `/requirements-review` for the set.
- **Model-invoked skills this skill may run:** `re-interview`, `re-ids`, `requirement-linter`, `testability-check`, `glossary`, `state-model` (when an object in the use case has a lifecycle, for example Voucher), `process-flow` (when the scenario hides hand-overs between several roles).
- **Feeds back to:** `clarifying-questions` with every `TBD`; `glossary` with new terms; recommend `/system-context` when scope or actors are unclear.

## Non-interactive mode

When nobody can answer (CI, an agent run, or the user said "don't ask"): do not guess. Write the use case with `TBD` in every unknown field and an open issue for each, append the new rows as `draft`, and end with the file path, the IDs written and the open issues. Exception: a goal that fails the level test in step 2 produces no file, only the candidate goals.

## Pitfalls

| Pitfall | Example | Instead |
| --- | --- | --- |
| Screen script | "Member taps the red Redeem button" | "Member asks to redeem a number of points" |
| CRUD use case | "Manage points: create, read, update, delete" | One use case per goal: "Adjust member points", "Review points history" |
| Everything is "the system" | "The system gets the voucher and the system checks it" | Name who acts in each step: member, cashier, fraud engine, loyalty service |
| Extension without an ending | "4a. Fraud hold: show error" | "4a1 ... 4a2 ... use case ends in failure" |
| Design decision as a step | "The service publishes to the Kafka topic" | The intention ("sends the redemption for scoring"); the design choice goes to the architect |

## References

- `references/form-guide.md`: what goes in each field, the level tests, step patterns, extension numbering, alternative versus exception. Read it at steps 2 to 5.
- `references/diagram-conventions.md`: the Mermaid use case diagram convention, the activity diagram convention, PlantUML alternatives. Read it at steps 7 and 8.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: "Redeem voucher" on the loyalty-points sample, with the rows it adds.
