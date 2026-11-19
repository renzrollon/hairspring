# Requirements workspace: loyalty-points

The Harbourline loyalty-points service (REST API, event consumer and admin console) that lets members earn, see and redeem points, built by the platform team for the loyalty team.

Set up with `re-setup` on 2026-11-03 by Wei Jie Chua (SH-08). Edit this file freely; re-run `/re-setup` to change the process facets. Tools read `schema.json`; if this file and `schema.json` disagree, correct this file.

## Process facets

| Facet | Choice | Confirmed by | Evidence | What it changes |
| --- | --- | --- | --- | --- |
| Time | iterative | Wei Jie Chua, 2026-11-03 | `README.md:5` (two-week sprints) | Stories and a prioritized backlog; only the next sprint's items must meet the DoR |
| Purpose | explorative | Wei Jie Chua, 2026-11-03 | No contract or tender documents in the repo | Requirements may stay `proposed` until prioritized; no specification document |
| Target | customer-specific | Wei Jie Chua, 2026-11-03 | `README.md:7` (PO Mei Tan) | The loyalty team, represented by Mei Tan, agrees requirements |
| Criticality | PDPA; data retention policy DRP-2024 | Wei Jie Chua, 2026-11-03 | `docs/compliance.md:3` | Sources, constraints, trace matrix, verification and release baselines are kept from the start |

## Change authority

`schema.json` → `process.change_authority`: `product-owner`.

| Requirement status | Who may change it | How the change is recorded |
| --- | --- | --- |
| `draft`, `proposed` | The author | Edit in place |
| `agreed`, `implemented`, `verified` | Product owner: Mei Tan (SH-01) | `Version` + 1 and `Status` back to `proposed` until Mei Tan agrees again |
| In a baseline | Product owner: Mei Tan (SH-01) | `CR-nnn` via `change-impact`, then a new baseline |

## Work products kept

`yes` = start now. `later` = start when the trigger happens. `no` = skip; re-run `/re-setup` to change.

| Work product | Path | Owning skill | Kept | Why |
| --- | --- | --- | --- | --- |
| Workspace README | `requirements/README.md` | `re-setup` | yes | Always |
| Schema | `requirements/schema.json` | `re-setup` | yes | Always |
| Glossary | `requirements/glossary.md` | `glossary` | yes | Always |
| Requirement register | `requirements/requirements.csv` | `requirement-phrasing` | yes | Always |
| System context | `requirements/context.md` | `system-context` | yes | Always |
| Quality requirements | `requirements/quality-requirements.md` | `quality-requirements` | yes | Always |
| Verification | `requirements/verification.csv` | `testability-check` | yes | Always |
| Decision records | `requirements/decisions/` | `conflict-to-decision` | yes | Written when a conflict or open decision is settled |
| Stakeholders | `requirements/stakeholders.md` | `stakeholder-map` | yes | Always |
| Elicitation records | `requirements/elicitation/` | `clarifying-questions`, `interview-guide` | yes | One file per technique used |
| Sources | `requirements/sources.csv` | `source-inventory` | yes | Criticality named: PDPA and DRP-2024 need backward traceability |
| Constraints | `requirements/constraints.csv` | `constraints-register` | yes | Criticality named: retention and data protection constraints |
| Stories | `requirements/stories/` | `user-story-refiner` | yes | Iterative |
| Reviews | `requirements/reviews/` | `requirements-review` | yes | Iterative: on pull requests that touch `requirements/` |
| Trace matrix | `requirements/trace/` | `traceability-matrix` | yes | Criticality named: audit evidence |
| Baselines | `requirements/baselines/` | `baseline` | yes | Criticality named: one per release (cadence is open question 2) |
| Change requests | `requirements/changes/` | `change-impact` | yes | Baselines are kept |
| Priorities | `requirements/priorities.csv` | `prioritization` | yes | Iterative |
| Specification document | `requirements/spec/` | `spec-assembler` | no | Neither linear nor prescriptive |
| Models | `requirements/models/` | `use-case-spec`, `domain-model`, `process-flow`, `state-model` | later | Trigger: a flow, structure or state too complex for sentences |
| Candidates, classification | `requirements/candidates.csv`, `requirements/classification.md` | `artifact-mining`, `requirement-classifier` | later | Working files |
| Views | `requirements/views/` | `attribute-schema` | later | Trigger: an audience asks for its own list |
| Exports | `requirements/exports/`, `openspec/changes/` | `reqif-bridge`, `to-openspec` | later | Trigger: a hand-off to OpenSpec or a ReqIF tool |

## ID scheme

IDs are opaque: never encode type, component or priority in them, never reuse one (withdrawn and rejected included), never renumber. Allocate with `re-ids` or `re-lint ids next --kind <kind>`.

| Kind | Prefix | Digits | Pattern | Lives in |
| --- | --- | --- | --- | --- |
| requirement | `R-` | 3 | `R-nnn` | `requirements.csv` |
| acceptance criterion | `<R-ID>.AC` | n | `R-nnn.ACn` | `stories/*.md` |
| source | `S-` | 2 | `S-nn` | `sources.csv` |
| stakeholder | `SH-` | 2 | `SH-nn` | `stakeholders.md` |
| interview | `I-` | 2 | `I-nn` | `elicitation/` |
| candidate | `CAN-` | 3 | `CAN-nnn` | `candidates.csv` |
| conflict | `CF-` | 2 | `CF-nn` | `conflicts.md` |
| decision | `RDR-` | 3 | `RDR-nnn` | `decisions/` |
| open-decision | `D-` | 2 | `D-nn` | `context.md`, then a decision record |
| change | `CR-` | 3 | `CR-nnn` | `changes/` |
| finding | `F-` | 2 | `F-nn` | `reviews/` |

## Attribute schema

Columns of `requirements.csv`, in this order: `ID,Type,Text,Source,Priority,Status,Rationale,Verification,Links`.

| Attribute | Column | Required | Allowed values |
| --- | --- | --- | --- |
| ID | yes | yes | `R-` and 3 or more digits |
| Type | yes | yes | `F`, `Q`, `C` |
| Text | yes | yes | One requirement per sentence; EARS or story form |
| Source | yes | yes | `S-nn`, `SH-nn`, `I-nn`, a role and date, or `file:line` |
| Priority | yes | yes | `must`, `should`, `could`, `wont` |
| Status | yes | yes | `draft`, `proposed`, `agreed`, `implemented`, `verified`, `deferred`, `rejected`, `withdrawn` |
| Rationale | yes | yes | One sentence |
| Verification | yes | no | `test`, `inspection`, `analysis`, `demonstration` |
| Links | yes | no | Space-separated IDs or paths |
| Title | optional | no | Short label |
| Owner | optional | no | Person or role |
| Version | optional | no | Integer |
| Stability | optional | no | `stable`, `volatile`, `unknown` |
| Risk | optional | no | `high`, `medium`, `low` |
| Kano | optional | no | `dissatisfier`, `satisfier`, `delighter`, `indifferent` |
| Tags | optional | no | Space-separated tags |

Unknown values are `TBD` plus an open question, never a guess. Lifecycle: `draft` → `proposed` → `agreed` → `implemented` → `verified`, plus `deferred`, `rejected` and `withdrawn` (transitions in `schema.json` → `lifecycle`). Only a named person moves a requirement to `agreed`.

## Definition of Ready

A requirement or story is ready for implementation when:

- [ ] Has an ID, type, source, priority and rationale
- [ ] Passes re-lint check with no errors
- [ ] Has a verification method and a measurable acceptance criterion
- [ ] Open questions are resolved or explicitly deferred with an owner
- [ ] Dependencies and constraints are named
- [ ] Is written as a story with a benefit and acceptance criteria, one of them for unwanted behavior
- [ ] Is agreed by a named customer representative
- [ ] Cites the regulation, policy or contract clause in Source or Links where one applies
- [ ] Requirements touching personal data or audit evidence are reviewed by the compliance or data protection role
- [ ] Member-facing text is reviewed by Marketing (SH-07)

## Story template

`user-story-refiner` writes each story in this shape to `requirements/stories/<epic-slug>.md`, with INVEST and Definition of Ready results below it.

```markdown
## {R-nnn}: {short title}

**Story:** As a {role, spelled as in glossary.md}, I want {goal}, so that {benefit}.

**Acceptance criteria**

**{R-nnn}.AC1: {short name}** _(happy path)_
- **Given** {state before the trigger}
- **When** {one trigger}
- **Then** {observable outcome}

**{R-nnn}.AC2: {short name}** _(unwanted behavior)_
- **Given** {state}
- **When** {error, timeout, invalid input or abuse}
- **Then** {observable outcome}

**Notes:** Source {S-nn, SH-nn or I-nn} · Priority {must / should / could / wont} · Depends on {R-IDs or none} · Constraints {R-IDs, source IDs or none} · Open questions {question numbers or none}
```

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | Must the data protection officer (SH-04 Farid Osman) co-approve changes to agreed requirements that touch personal data? | SH-01 Mei Tan | Change authority |
| 2 | Is a baseline cut for every production release, or on a fixed calendar? | SH-08 Wei Jie Chua | Baselines |

## Setup history

| Date | Change | By |
| --- | --- | --- |
| 2026-11-03 | Initial setup: iterative, explorative, customer-specific, PDPA and DRP-2024; `Verification` and `Links` columns added | Wei Jie Chua (SH-08) |
| 2026-11-03 | Dropped the explorative DoR item: assumptions are tracked on the product owner's discovery board | Wei Jie Chua (SH-08), Mei Tan (SH-01) |
| 2026-11-03 | Added DoR item: member-facing text reviewed by Marketing | Wei Jie Chua (SH-08) |
