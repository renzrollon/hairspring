---
name: system-context
description: >-
  Interviews the team for the system boundary (what the system does versus what other systems and
  teams do) and the context boundary (what around the system shapes its requirements versus what
  is ignored), names the grey zones on each, draws a Mermaid context diagram (C4 context or
  PlantUML on request) and writes a context table of external actors, systems, interfaces and data
  flows. Every unresolved boundary question becomes an open decision D-nn with options, a
  recommendation and an owner. Writes requirements/context.md. Use when a project kicks off or
  before elicitation or design starts, when someone types /system-context, asks "what is in
  scope?", "what does this system talk to?" or "draw the context diagram", or when a migration,
  integration or new service needs its boundary agreed. Not for the people behind each actor (use stakeholder-map), for the
  internal architecture of the system (a container or component view), or for listing documents
  to elicit from (source-inventory).
license: MIT
disable-model-invocation: true
argument-hint: "[system name, notes file or brief]"
metadata:
  stage: scope
  invocation: user
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §1.4, §3.4.2"
  inputs-from: "glossary, artifact-mining, stakeholder-map, source-inventory, re-interview"
  outputs-to: "stakeholder-map, source-inventory, quality-requirements, constraints-register, conflict-to-decision, use-case-spec"
  work-product: "requirements/context.md"
  version: "0.1.0"
---

# System context

Most late requirements are boundary mistakes: a batch job everyone assumed someone else owned, an interface nobody listed, a regulation that only surfaces in acceptance testing. This skill makes two boundaries explicit before elicitation starts: the system boundary (what the system does itself) and the context boundary (what in its environment matters for its requirements). It drafts both from the repo, confirms them in a short interview, turns every grey zone into an open decision, and writes a context diagram and a context table to `requirements/context.md`.

## When not to use

- You need the people behind the actors, their influence and availability: suggest `/stakeholder-map`.
- You need the internal structure (services, queues, databases): that is an architecture view (C4 container or component), not a context diagram.
- You need a register of documents and systems to elicit from: run `source-inventory`.
- A grey zone is ready for a structured decision with options and criteria: suggest `/conflict-to-decision`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Kick-off notes, a brief, or answers given in the session | yes, unless running non-interactively on the repo | the user |
| Repo evidence: `README*`, `docs/` (architecture, ADRs), OpenAPI or AsyncAPI specs, client configuration, `docker-compose*`, infrastructure code, scheduled-job definitions | no | the team |
| `requirements/glossary.md` | no | `glossary` |
| `requirements/stakeholders.md`, `requirements/sources.csv` | no | `stakeholder-map`, `source-inventory` |
| An existing `requirements/context.md` | no | an earlier run |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/context.md` | `assets/context.md` | `stakeholder-map`, `source-inventory`, `quality-requirements`, `constraints-register`, `conflict-to-decision`, `use-case-spec` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (defaults if missing), `glossary.md`, `stakeholders.md` and `sources.csv`. If `context.md` exists, update it in place: keep every row number and D-ID, mark an element that disappeared as `removed (<date>, <reason>)` instead of deleting it, and never renumber.
2. **Mine the repo before asking.** Read `references/context-checklist.md` section 1 for where to look. List candidate external elements, each with `file:line` evidence and the data that flows. If you can run subagents, mine docs, API specs and configuration in parallel; otherwise one after another. An element needs a data flow or a rule it imposes; an imported library alone is not an element.
3. **Draft the boundaries.** Sort what you found into: inside (capabilities the system performs or owns), outside (done by another system or team, named), context (external elements that exchange data with the system or impose rules on it), irrelevant (in the environment but deliberately ignored, with the reason). Anything you are unsure about is a grey zone candidate.
4. **Interview.** Follow `re-interview`: one question at a time with a recommended answer and its evidence, or one batch of at most 7 if the user asks for a batch. Use the patterns in `references/context-checklist.md` section 3, in this order:
   1. Confirm the system name and its purpose in one sentence.
   2. Each grey zone candidate on the system boundary: "Does our system do X, talk to X, or is X out of scope?"
   3. Gaps on the context boundary, using the element checklist in section 2.
   4. For each element: what flows in and out, through which interface, who owns it.

   Aim for 10 minutes and at most 8 questions. Record every answer in Questions and answers with who gave it and the date. Stop when the next question would not change the diagram.
5. **Turn every unresolved answer into an open decision.** An answer with "maybe", "probably", "depends", "later", "both", "not decided" or "ask X" becomes `D-nn` (allocate with `re-ids`, kind `open-decision`): the question, at least two options (one of them "outside"), a recommended option with its reason, an owner (role or `SH-nn`) and status `open`. Never resolve a grey zone by assumption. When the owner answers in the session, set the status to `decided: <answer> (<who>, <date>)`.
6. **Write the context table.** One row per data flow: element, kind (`person`, `system`, `organization`), direction (`in` = to the system, `out` = from the system, `via <element>` = a person who reaches the system only through another system), data flow, interface, owner, status, source. Status is `confirmed` (a person or a specification confirms it), `assumed` (inferred from code, configuration or docs only) or `grey zone: D-nn`. Name people by role; names belong in `stakeholders.md`.
7. **Draw the diagram from the table.** Read `references/diagram-patterns.md`. Default: Mermaid `flowchart LR` with a context-boundary subgraph around a system-boundary subgraph that holds exactly one node, the system. One edge per table row, labeled `<#> <data flow>`; `via` rows and grey zones are dotted; grey-zone nodes use the `grey` class. Use C4 context or PlantUML only when the user asks.
8. **Show, then write.** Show the diagram, the tables and the open decisions. After confirmation (or directly in non-interactive mode), write `requirements/context.md` from `assets/context.md`, all sections present and in order.
9. **Cross-check.** Every table element is a node and every node except the system is in the table; edge numbers match table rows; every grey zone in the boundary tables has a D-ID in Open decisions and the reverse. If a Mermaid renderer is available, render the block once to catch syntax errors; otherwise check the rules in `references/diagram-patterns.md`.
10. **Report.** Final message: number of external elements and data flows, the open decisions with their owners, and the next steps.

## Quality checks

- [ ] The system is exactly one node; no internal services, databases, queues or modules are drawn.
- [ ] Every context-table element appears as a node, every node except the system appears in the table, and edge numbers match the table's `#`.
- [ ] Every grey zone has a `D-nn` with options, a recommendation, an owner and a status; the agent decided none of them.
- [ ] Every row has a `Source`; rows inferred only from code, configuration or docs are `assumed`.
- [ ] Persons are named by role, not by personal name.
- [ ] D-IDs were allocated with `re-ids`, none reused, none renumbered.
- [ ] The Mermaid block follows the syntax rules in `references/diagram-patterns.md`.

## Hand-offs

- **Next:** suggest the user runs `/stakeholder-map` for the people behind each actor and system owner; run the `source-inventory` skill to register the systems and documents found here as sources; run `glossary` for new terms.
- **Feeds back to:** suggest `/conflict-to-decision` for each `D-nn` that needs a structured decision; `quality-requirements` and `constraints-register` for interface qualities and for the regulations listed in the context boundary.

## Non-interactive mode

Draft from evidence only. Every element is `assumed` unless a specification or the user's notes confirm it; every grey zone becomes a `D-nn` with the most likely owner role or `TBD`; never decide scope. End with the list of open decisions and unanswered questions.

## Pitfalls

- Drawing the architecture instead of the context. Internal parts belong in a container view.
- One arrow per element labeled "data". Name what flows, one edge per direction.
- Forgetting batch jobs, reporting extracts, admin and support tools, and the systems that replace a legacy module: that is where boundary mistakes hide.
- Accepting "everything is in scope". Ask who runs and pays for each part after go-live.

## References

- `references/context-checklist.md`: where to look in a repo, the external-element checklist, boundary question patterns, grey-zone patterns. Read it before step 2.
- `references/diagram-patterns.md`: the Mermaid template and syntax rules, C4 context and PlantUML variants. Read it before step 7.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: the loyalty-points kick-off notes and the `context.md` they produce.
