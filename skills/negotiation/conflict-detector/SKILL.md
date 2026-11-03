---
name: conflict-detector
description: >-
  Finds conflicts in a requirement set and registers them in requirements/conflicts.md (CF-nn):
  contradictions, overlaps, inconsistent conditions, differing levels of detail, and stakeholders
  who disagree on priority. Classifies each by root cause (subject matter, data, interest, value,
  relationship, structural), recommends a resolution technique, and routes relationship and
  structural conflicts to escalation instead. Edits no requirement. Use when rows from several
  stakeholders or sources meet, before a refinement, baseline or design review, when two rows set
  different values for the same thing ("12 vs 18 months"), when a regulation or policy seems to
  clash with a requirement, when stakeholders rank the same item differently, or when someone asks
  "do these contradict?", "any conflicts?", "who disagrees?". Not for running the resolution session
  (use conflict-to-decision), for a full quality review (requirements-review), or for wording
  defects (requirement-linter).
license: MIT
metadata:
  stage: negotiation
  invocation: model
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §4.3.1, §4.3.2"
  inputs-from: "requirement-phrasing, stakeholder-map, source-inventory, prioritization, constraints-register, quality-requirements, requirements-review"
  outputs-to: "conflict-to-decision, requirements-review, glossary"
  work-product: "requirements/conflicts.md"
  version: "0.1.0"
---

# Conflict detector

A requirement set with no conflicts usually means nobody compared the rows. A conflict found now costs a conversation; found in testing it costs a release. This skill compares requirements, constraints and stakeholder positions, registers each real conflict with its evidence, names its root-cause type and a resolution technique, and routes it: to a resolution session (`/conflict-to-decision`) or, for relationship and structural conflicts, to escalation. It decides nothing and edits no requirement.

## When not to use

- The conflict is known and the people are ready to decide: suggest the user runs `/conflict-to-decision`.
- You want every quality criterion checked, not only consistency: suggest `/requirements-review`.
- Wording defects (weak words, passive voice, missing `shall`): `requirement-linter`.
- One term used in two senses with no disagreement about the requirement itself: `glossary`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv`, or the rows or IDs the user names | yes | `requirement-phrasing` |
| `requirements/stakeholders.md`, `requirements/sources.csv` | no | `stakeholder-map`, `source-inventory` |
| `requirements/priorities.csv` or notes with each stakeholder's priority | no | `prioritization` |
| `requirements/constraints.csv`, `requirements/quality-requirements.md` | no | `constraints-register`, `quality-requirements` |
| `requirements/conflicts.md` (existing register) | no | this skill |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/conflicts.md` (new entries appended, existing entries kept) | `assets/conflicts.md` | `conflict-to-decision`, `requirements-review` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the defaults, and say so in the register header), `glossary.md`, `requirements.csv` and the optional inputs above. Skip rows with Status `withdrawn` or `rejected`. Read the existing `conflicts.md` so a known conflict keeps its CF-ID.
2. **Group by subject.** Cluster rows that talk about the same thing (entity plus attribute or behavior, in glossary terms): "points expiry", "transaction retention", "redemption minimum". Note each row's Source and the stakeholder behind it.
3. **Scan.** Within and across groups, look for the five kinds in `references/detection-checklist.md`: contradiction, overlap, inconsistent conditions, differing level of detail, priority disagreement. Compare requirements against constraints and quality requirements as well; contradictions hide there.
4. **Confirm.** A candidate is a conflict only if the statements cannot all be satisfied for the same scope and time, or named stakeholders hold different positions on it. When the call depends on a fact you do not have ("does R-061 apply only to Gold members?"), ask one question with `re-interview` (with a recommended answer) or log it as an open question. Candidates that fail the test go to "Checked, not a conflict" with the reason.
5. **Name the positions.** For each conflict, list every stakeholder involved (SH-ID, name, role) and their position in one line, with its source. Unknown owner: `TBD` plus an open question; suggest `/stakeholder-map` when a role is missing.
6. **Classify.** Ask the root-cause questions in `references/conflict-types.md` in order; the first "yes" is the type. Write the reason in one clause. Never classify from the requirement text alone when a stakeholder statement says otherwise.
7. **Recommend and route.** Take the technique and analysis aid from the technique table in `references/conflict-types.md`. Relationship and structural conflicts: Route `escalate to <role>` (sponsor, the parties' common manager, steering group), Technique `none (escalation)`, Status `escalated`; the requirements engineer does not resolve them. All other types: Route `/conflict-to-decision CF-nn` with the decision-makers (default: the role in `schema.json` `process.change_authority`), Status `open`. Do not propose the winning option or a compromise value.
8. **Allocate IDs.** New conflicts get the next `CF-` IDs from `re-ids` (kind `conflict`; or `re-lint ids next --kind conflict`). Never renumber or reuse one.
9. **Show, then write.** Show the register table first. After confirmation, or directly in non-interactive mode, write `requirements/conflicts.md` from `assets/conflicts.md`: one register row plus one detail block per conflict. Update existing entries in place; never delete one (set Status `not-a-conflict` with the reason instead).

## Quality checks

- [ ] Every conflict cites at least two requirement IDs, or one requirement and two stakeholder positions, each with a source.
- [ ] Every conflict has exactly one kind, one type with a reason, a technique (or `none (escalation)`) and a route.
- [ ] Relationship and structural conflicts are routed to escalation, never to `/conflict-to-decision`.
- [ ] No row in `requirements.csv` was changed and no resolution was chosen.
- [ ] CF-IDs are unique; existing entries kept their IDs and Status.
- [ ] Unknown positions, owners and decision-makers are `TBD` with an open question.

## Hand-offs

- **Next:** suggest the user runs `/conflict-to-decision CF-nn` for each `open` conflict, starting with the one on the highest-priority requirement.
- **Feeds back to:** `glossary` when the root cause is one term used in two senses; suggest `/stakeholder-map` when a position has no owner; `requirement-phrasing` when a data conflict is settled by correcting a row (only after its owner confirms).

## Non-interactive mode

Do not ask. Register every candidate that passes step 4 on the evidence you have, put an open question in the detail block of each uncertain one, and end with the list of CF-IDs written, their routes and the open questions.

## References

- `references/detection-checklist.md`: the five kinds, how to scan for each, where conflicts hide, and loyalty-points examples. Read it at step 3.
- `references/conflict-types.md`: root-cause questions, the technique table and the escalation rule. Read it at steps 6 and 7.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: the loyalty-points register scanned, and the five conflicts it yields.
