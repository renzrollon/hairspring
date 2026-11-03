---
name: stakeholder-map
description: >-
  Builds the stakeholder inventory for a system: one row per stakeholder (SH-nn) with role, named
  representative, goals, influence, interest, engagement, availability and source; a
  power/interest quadrant as a Mermaid quadrantChart; and a gap check against a role checklist
  (operations, security, legal, support, data protection, finance, fraud, audit, external system
  owners, ...). Writes requirements/stakeholders.md. Use when a project kicks off or before
  interviews or workshops are planned, when someone types /stakeholder-map, asks "who do we need
  to talk to?",
  "who are the stakeholders?" or "who signs this off?", or has a roster, invite list, org chart,
  RACI or CODEOWNERS file to turn into a map. Not for the system's external actors and interfaces
  (use system-context), for registering stakeholders, documents and systems as sources with an
  elicitation technique (source-inventory), or for preparing an interview with one stakeholder
  (interview-guide).
license: MIT
disable-model-invocation: true
argument-hint: "[roster, invite list, org chart or notes file]"
metadata:
  stage: scope
  invocation: user
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §1.3, §4.1"
  inputs-from: "system-context, glossary, source-inventory, re-interview"
  outputs-to: "source-inventory, interview-guide, elicitation-workshop, prioritization, conflict-detector"
  work-product: "requirements/stakeholders.md"
  version: "0.1.0"
---

# Stakeholder map

A requirement nobody asked for is usually a stakeholder nobody asked. This skill turns whatever the team has (a roster, an invite list, an org chart, the actors in `context.md`) into a stakeholder inventory with named representatives, rates influence and interest by explicit rules, plots the power/interest quadrant, and checks the result against a role checklist so the usual gaps (fraud, legal, data protection, the owners of neighboring systems) show up before elicitation starts. It writes `requirements/stakeholders.md`.

## When not to use

- You need the external actors, systems and data flows of the system: suggest `/system-context`.
- You need each stakeholder registered as a requirement source with a planned elicitation technique: run `source-inventory` (it reads this file).
- You are preparing a conversation with one stakeholder: suggest `/interview-guide`.
- Two stakeholders disagree on a requirement or a priority: `conflict-detector`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| A roster, invite list, org chart, RACI, `CODEOWNERS` or notes, or answers given in the session | yes, at least one | the user |
| `requirements/context.md` (persons and system owners) | no | `system-context` |
| `requirements/glossary.md` (role names) | no | `glossary` |
| `requirements/sources.csv` | no | `source-inventory` |
| An existing `requirements/stakeholders.md` | no | an earlier run |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/stakeholders.md` | `assets/stakeholders.md` | `source-inventory`, `interview-guide`, `elicitation-workshop`, `prioritization`, `conflict-detector` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (defaults if missing), `glossary.md`, `context.md` and `sources.csv`. If `stakeholders.md` exists, update it in place: keep every SH-ID, never renumber or delete a row; a stakeholder who no longer matters gets Engagement `retired (<date>, <reason>)`.
2. **Collect candidates.** From the inputs, list every role, person and organization with `file:line` evidence. Add the persons and the owners of external systems from `context.md`. Merge duplicates: one row per stakeholder role. Keep two rows for one person only when they hold two roles with different goals.
3. **Fill what the evidence gives.** Read `references/mapping-rules.md`. For each row: Role (glossary spelling), Representative (a named person, else `TBD`), Goals (what they want from or fear about the system, one sentence), Influence and Interest (`high`, `low` or `TBD`, by the rules in the reference), Engagement (derived from the two ratings), Availability (how and when they can be reached, else `TBD`), Source.
4. **Ask for what is missing.** Follow `re-interview` with one batch of at most 7 questions, highest-influence rows first: missing representatives, ratings the rules cannot settle, availability. Give a recommended answer with its evidence. Never invent a person's name, a rating or an availability.
5. **Check for gaps.** Read `references/role-checklist.md`. For every role whose trigger applies to this system (use `context.md`, the glossary and the inputs), decide: covered (by which SH-ID), gap, or unclear. For a gap, add the role as a stakeholder row with Representative `TBD` and an open question; for unclear, add an open question only. Name the checklist roles whose trigger does not apply in one line under the table.
6. **Allocate IDs.** Use `re-ids` (kind `stakeholder`) for every new row, in table order. Never reuse an SH-ID.
7. **Plot the quadrant.** Use the coordinate and label rules in `references/mapping-rules.md`: x is interest, y is influence, one point per row with both ratings known, labels `SH-nn <short role>` with letters, digits, spaces and hyphens only. List the rows not plotted under the chart.
8. **Show, then write.** Show the table, the chart and the gap check. After confirmation (or directly in non-interactive mode), write `requirements/stakeholders.md` from `assets/stakeholders.md`, all sections present and in order.
9. **Report.** Final message: number of stakeholders per engagement, the gaps, the open questions with owners, and the next steps.

## Quality checks

- [ ] The stakeholder table has exactly the columns `ID | Role | Representative | Goals | Influence | Interest | Engagement | Availability | Source`.
- [ ] Every Representative is a named person from the inputs or `TBD`; no name was invented.
- [ ] Influence and Interest are `high`, `low` or `TBD`; Engagement matches the rule for every row that is not `retired`.
- [ ] Every plotted point belongs to a row with both ratings known and lies inside that row's quadrant; every row with both ratings known is plotted.
- [ ] Every checklist role whose trigger applies is covered, added with `TBD`, or has an open question.
- [ ] SH-IDs are unique; existing IDs were not renumbered.

## Hand-offs

- **Next:** run the `source-inventory` skill to register each stakeholder with a representative as a source with a planned elicitation technique; suggest `/interview-guide` for each `manage closely` stakeholder.
- **Feeds back to:** `conflict-detector` when two stakeholders' goals contradict; suggest re-running `/system-context` when a stakeholder names a system missing from `context.md`; `glossary` for role names.

## Non-interactive mode

Rate only where the evidence settles the rule, otherwise `TBD`. Never invent names: gap roles get Representative `TBD`. Plot only fully rated rows. End with the open questions, each with an owner role.

## Pitfalls

- Mapping only the people in the room: the gap check exists because the missing roles are rarely invited.
- Rating everyone high: the quadrant then says nothing. Apply the rules and accept `low`.
- Treating a person as the stakeholder: the stakeholder is the role; the representative can change.
- Forgetting the people who lose something: the team running the replaced system, a vendor whose contract ends.

## References

- `references/mapping-rules.md`: influence, interest and engagement rules; goals and availability phrasing; quadrant coordinates and label rules; proxies for user groups. Read it before step 3.
- `references/role-checklist.md`: roles to check, with the trigger that makes each one relevant. Read it before step 5.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: the loyalty-points kick-off roster and the `stakeholders.md` it produces.
