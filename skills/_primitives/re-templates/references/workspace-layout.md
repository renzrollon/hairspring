# Workspace layout

Every work product lives under one folder at the repo root, `requirements/` by default (`workspace` in `requirements/schema.json` can rename it). Each file has one owning skill that creates and reshapes it. Other skills read it, and may append rows only where the table below says so.

```text
requirements/
  README.md                    re-setup             Process facets, work products kept, ID scheme, Definition of Ready
  schema.json                  re-setup             IDs, attributes, enums, lifecycle, lint/trace/issue settings (attribute-schema maintains it)
  glossary.md                  glossary             Term table + homonym/synonym findings
  requirements.csv             requirement-phrasing THE register of requirement statements (F, Q, C). Appended by every emitting skill through re-ids
  context.md                   system-context       Context diagram, context table, grey zones, open decisions D-nn
  stakeholders.md              stakeholder-map      Stakeholder table SH-nn, power/interest quadrant, gap check
  sources.csv                  source-inventory     Source register S-nn (stakeholders, documents, systems) with elicitation technique
  candidates.csv               artifact-mining      Candidate requirements CAN-nnn with source quotes; also written by interview/workshop/observation capture
  classification.md            requirement-classifier  Classified statements (F/Q/C, non-requirements, solutions in disguise, Kano guess)
  quality-requirements.md      quality-requirements ISO 25010 walkthrough; quality requirements with metric, target, condition, method (rows also in requirements.csv, Type=Q)
  constraints.csv              constraints-register Constraint details keyed by R-ID (rows also in requirements.csv, Type=C)
  stories/<epic-slug>.md       user-story-refiner   Stories (R-IDs) with acceptance criteria R-nnn.AC1..n, INVEST and DoR results
  models/
    uc-<name>.md               use-case-spec        Use case form + Mermaid diagrams
    domain-model.md            domain-model         Mermaid classDiagram / erDiagram + glossary cross-check
    flow-<name>.md             process-flow         Mermaid flowchart with swimlanes
    state-<entity>.md          state-model          Mermaid stateDiagram-v2 + completeness check
  elicitation/
    questions-<topic>.md       clarifying-questions Question batches, answers with person and date, assumptions
    interview-<role>.md        interview-guide      Guide, capture sheet, summary
    workshop-<slug>.md         elicitation-workshop Plan, agenda, capture template
    questionnaire-<slug>/      questionnaire-builder questionnaire.md, form-import.csv, analysis.csv/xlsx
    observation-<slug>.md      observation-protocol Plan, capture template, debrief
    prototype-<slug>.md        prototype-brief      Hypotheses, fidelity, measures, results
  conflicts.md                 conflict-detector    Conflict register CF-nn with type and recommended technique
  decisions/RDR-nnn-<slug>.md  conflict-to-decision Requirements Decision Records (ADR-compatible)
  reviews/review-YYYY-MM-DD.md requirements-review  Findings F-nn with criterion, severity, proposed fix
  verification.csv             testability-check    Verification method, acceptance criterion, first test idea per R-ID
  trace/trace.csv              traceability-matrix  From,FromType,To,ToType,Relation,Evidence
  trace/trace.md               traceability-matrix  Coverage summary, Mermaid graph, gap report
  changes/CR-nnn-<slug>.md     change-impact        Change request with impact set, options, recommendation, decision
  priorities.csv               prioritization       Items, criteria scores, weights, score, rank, tie flags
  priorities.md                prioritization       Run record: goal, scorers, who agreed the weights and when, disputed items
  views/<view>.md|.csv         attribute-schema     Selective, projective and aggregating views per audience
  baselines/<name>.json        baseline             Manifest of requirement IDs, versions, hashes at a point in time
  baselines/<name>-notes.md    baseline             Requirement release notes since the previous baseline
  spec/spec.md, spec/spec.docx spec-assembler       Assembled specification (SRS / Volere-structured / arc42-aligned chapter)
  exports/                     reqif-bridge         .reqif exports and import-diff-<date>.md reports
openspec/changes/<change>/     to-openspec          OpenSpec change folder (outside requirements/ because OpenSpec expects it there)
```

## Rules

1. **One register of statements.** Requirement text lives in `requirements.csv`. Other files reference requirement IDs; if they echo the text, `requirements.csv` wins and `re-lint check` warns on drift.
2. **Append, don't reshape.** A skill that does not own a file only appends rows (through `re-ids`) or updates the columns it is responsible for (for example `testability-check` sets `Verification`, `issue-sync` refreshes `Status`).
3. **Never delete a requirement row.** Set `Status` to `withdrawn` or `rejected` and give the reason in `Rationale` or a decision record.
4. **Dates are ISO 8601** (`2026-11-03`). File slugs are kebab-case.
5. **Diagrams sit next to the text they illustrate**, as fenced `mermaid` blocks inside the Markdown work product.
6. **Missing workspace is not a blocker.** If `requirements/` does not exist, create only the files the current skill emits, use the default schema, and recommend `/re-setup` in the final message.

## Register columns

CSV registers have a fixed header. The owning skill's `assets/` holds the template; this table is the summary.

| File | Columns (in order) |
| --- | --- |
| `requirements.csv` | `ID,Type,Text,Source,Priority,Status,Rationale` then optional `Title,Owner,Version,Stability,Risk,Verification,Kano,Links,Tags` |
| `sources.csv` | `ID,Source,Kind,Category,Version,Location,Contact,Technique,Relevance,Status,Notes` |
| `candidates.csv` | `ID,Statement,Type,Technique,Source,Location,Quote,Disposition,Reason,Owner,Kano,Requirement` |
| `constraints.csv` | `ID,Title,Category,Mandated by,Mandate reference,Expires,Review by,Negotiable,If violated,Affects,Open question` |
| `verification.csv` | `ID,Text,Method,Criterion,Test idea,Level,Verifiable,Question,Basis` |
| `priorities.csv` (Wiegers) | `ID,Title,Benefit,Penalty,Cost,Risk,Score,Rank,Tie` (WSJF and ad hoc variants in the `prioritization` assets) |
| `trace/trace.csv` | `From,FromType,To,ToType,Relation,Evidence` |

**Shared vocabulary.** `Technique` in `sources.csv` (planned) and `candidates.csv` (used) takes the same values: `interview`, `workshop`, `questionnaire`, `observation`, `document-analysis`, `system-archaeology`, `feedback-analysis`; `sources.csv` also allows `apprenticing` and `reuse`, whose candidates are recorded as `observation` and `document-analysis`. Several planned techniques are joined with `; `.

**Key columns in Markdown work products.** Only registers (`requirements.csv`, and CSV detail registers keyed by requirement ID) use a column named `ID` for requirement IDs. Markdown reports and models refer to requirements in a column named `Requirement` (or `R-ID` in model tables), so `re-lint` does not mistake a report table for a register. `re-lint check` also skips `changes/`, `decisions/` and `reviews/` by default.

**Columns other skills update.** `testability-check` sets `Verification`; `issue-sync` refreshes `Status` and appends tracker references to `Links`; `conflict-to-decision` updates the status of the conflict in `conflicts.md` and adds `RDR-nnn` to the affected requirements' `Links`; `change-impact` increments `Version` (an empty `Version` counts as 1).

## Templates in `assets/`

| File | Used by |
| --- | --- |
| `schema.json` | `re-setup`, `attribute-schema`, every script (`DEFAULT_SCHEMA`) |
| `requirements.csv` | every skill that emits requirements |
| `candidates.csv` | `artifact-mining`, `interview-guide`, `elicitation-workshop`, `observation-protocol` (each keeps an identical copy; a test enforces it) |

Skill-specific templates live in each skill's own `assets/` folder.
