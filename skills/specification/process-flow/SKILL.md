---
name: process-flow
description: >-
  Draws a business process or scenario as an activity diagram with swimlanes: a Mermaid
  flowchart with one subgraph per responsible role or system (PlantUML activity optional),
  showing actions, decisions with labeled outcomes, parallel branches and who does each step.
  Long exception paths become separate flows by a fixed readability rule. Writes
  requirements/models/flow-<name>.md with lane, step and decision tables linked to requirement
  IDs. Use when work passes between people, teams or systems (refunds, returns, approvals,
  onboarding, month-end), when someone asks "who does what", "draw the process", "what happens
  after X", "where can this go wrong", or when a ticket or use case hides hand-overs between
  roles. Not for one actor's goal-driven interaction with the system (use use-case-spec), the
  lifecycle of one entity (use state-model), or the system boundary and its interfaces (use
  system-context).
license: MIT
metadata:
  stage: specification
  invocation: model
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §3.4.4"
  inputs-from: "use-case-spec, stakeholder-map, system-context, artifact-mining, observation-protocol, clarifying-questions"
  outputs-to: "requirement-phrasing, state-model, testability-check, requirements-review, spec-assembler"
  work-product: "requirements/models/flow-<name>.md"
  version: "0.1.0"
---

# Process flow

Defects in processes sit at the hand-overs: a step nobody owns, a decision with a missing outcome, a refund that waits for a system it should not wait for. An activity diagram with one lane per responsible role or system makes each hand-over visible. This skill draws the main flow in Mermaid, moves long exception paths into their own flows so the main one stays readable, and links each step to the requirements behind it.

## When not to use

- One primary actor pursuing one goal with the system (main scenario, extensions): `use-case-spec`.
- Which states one entity passes through and what each event does in each state: `state-model`.
- What is inside the system and which external systems and people it talks to: `system-context`.
- The business objects and their relationships: `domain-model`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Process material: interview notes, a runbook, a ticket, an observation record, a use case | yes | `clarifying-questions`, `artifact-mining`, `observation-protocol`, `use-case-spec` |
| `requirements/stakeholders.md`, `requirements/context.md` (who and what can own a lane) | no | `stakeholder-map`, `system-context` |
| `requirements/requirements.csv` (to link steps) | no | `requirement-phrasing` |
| `requirements/glossary.md` | no | `glossary` |
| `requirements/schema.json` | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/models/flow-<name>.md` | `assets/flow.md` | `requirement-phrasing` (candidates), `testability-check`, `requirements-review`, `spec-assembler` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else defaults, and say so), `glossary.md`, `stakeholders.md`, `context.md`, `requirements.csv`, related `models/uc-*.md` and `models/state-*.md`, and an existing `models/flow-<name>.md` (update it in place; keep node IDs stable). The name is a kebab-case noun phrase for the process (`purchase-return`).
2. **Fix the frame.** Write the trigger (what starts the flow), the normal outcome, and the scope (which part of the process, at what level: what each lane does, not how the code does it). If two triggers lead to different processes, draw two flows.
3. **Name the lanes.** One lane per responsible role or system, named as in `stakeholders.md` or `context.md`. No catch-all "System" lane when several systems take part. A step whose owner nobody named goes in a lane `Unassigned (TBD)` with an open question; never pick an owner yourself.
4. **Draw the main flow.** Read `references/activity-diagram-convention.md` and use its shapes. Labels are verb and object ("Refund payment to customer"). One action per node. Every decision is a question whose outgoing edges are labeled and cover every case, or the Decisions table says why a case cannot happen. Steps that happen at the same time with no order between them go between a fork and a join. One start; one end per distinct outcome.
5. **Apply the readability rule.** Main flow: at most 15 action and decision nodes, at most 3 decisions; an exception path stays inline only if it has at most 2 nodes before it ends or rejoins. Anything longer becomes an exception flow, shown in the main flow as one `[[Exception flow: name]]` node. The rule and its reasons are in the convention reference. Record the counts in the Readability check table.
6. **Draw each exception flow.** Its own section and diagram, starting where the main flow hands over, with its own lanes, ending in an end node or naming the main-flow node where it rejoins. The same readability rule applies.
7. **Link the requirements.** For each step the system under development performs, put the R-IDs that require it in the Steps table. A step with no requirement goes to Requirement candidates (statement, source) for `requirement-phrasing`; do not write `requirements.csv` here. Unknown values (durations, limits) are `TBD` with an open question.
8. **Check before saving.** Every node is reachable from the start; every path ends in an end node or an exception-flow node; every decision has at least two labeled outgoing edges; every fork has a matching join, or its branches end separately and the Steps table says so; every node in the diagram is a row in the Steps table and the other way round. The Mermaid uses only the convention's subset.
9. **Show, then write.** Show the diagrams and tables; after confirmation (or directly in non-interactive mode) write `models/flow-<name>.md` from `assets/flow.md`.

## Quality checks

- [ ] Every lane names a role or system from the sources, or is `Unassigned (TBD)` with an open question.
- [ ] Every decision's outgoing edges are labeled and cover all cases, or the Decisions table explains the missing case.
- [ ] The main flow meets the readability rule, or the Readability check row says which limit is exceeded and why.
- [ ] Every system step links an R-ID or appears in Requirement candidates.
- [ ] No invented durations, amounts or owners; each is `TBD` with an open question.
- [ ] Every Mermaid block uses only the subset in `references/activity-diagram-convention.md`.

## Hand-offs

- **Next:** `requirement-phrasing` with the Requirement candidates; `testability-check` (each path from start to end is a test scenario); `requirements-review` for the set.
- **Feeds back to:** `clarifying-questions` with unassigned lanes and `TBD` branches; `state-model` when a decision is really "which state is the entity in"; `stakeholder-map` when a lane has no named representative; `glossary` with new terms.

## Non-interactive mode

Draw what the sources support, put unknown owners in `Unassigned (TBD)` and unknown branches in `TBD` nodes, write the file, and end with the open questions and the requirement candidates.

## References

- `references/activity-diagram-convention.md`: lane and node shapes in Mermaid, fork and join, exception-flow nodes, the readability rule and its reasons, the PlantUML alternative. Read it at steps 4 to 6.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: the purchase-return flow of the loyalty-points sample with its exception flow.
