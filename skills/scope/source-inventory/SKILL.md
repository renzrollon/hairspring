---
name: source-inventory
description: >-
  Builds and maintains requirements/sources.csv, the register of requirement sources: stakeholders,
  documents (regulations, policies, contracts, terms, specifications, runbooks, ticket exports)
  and systems in operation (legacy code, databases, batch jobs, competitor products), each with a
  source ID (S-nn), version, location, contact, the planned elicitation technique, relevance and
  status. Source IDs are what backward traceability points at: requirements cite them in Source.
  Use when a project starts, when someone asks "where do requirements come from?", "what should we
  read or who should we ask?", "plan elicitation", when stakeholders.md or context.md was just
  written, when a requirement cites a document or person that is not registered, or when
  re-lint reports unregistered-source. Not for rating stakeholders' influence and interest (use
  stakeholder-map), for extracting requirements from the documents and systems themselves (use
  artifact-mining), or for building the trace matrix (traceability-matrix).
license: MIT
metadata:
  stage: scope
  invocation: model
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §4.1, §6.6"
  inputs-from: "stakeholder-map, system-context, artifact-mining, re-ids"
  outputs-to: "artifact-mining, interview-guide, traceability-matrix, requirement-linter"
  work-product: "requirements/sources.csv"
  version: "0.1.0"
---

# Source inventory

A requirement whose source nobody recorded cannot be checked, defended or changed safely. This skill keeps one register of everything requirements come from (people, documents, systems in operation), gives each source a stable ID that requirements cite in `Source`, and plans how each one will be elicited. It writes `requirements/sources.csv`.

## When not to use

- You need influence, interest and representatives for each stakeholder: `stakeholder-map` (this skill reads its output).
- You want the candidate requirements inside a document, a codebase or a ticket export: `artifact-mining`.
- You want coverage from sources to requirements to tests: `traceability-matrix` (it reads this register).

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Names of documents, systems and people, from the user or the repo | yes, unless the files below exist | the user |
| `requirements/stakeholders.md` | no | `stakeholder-map` |
| `requirements/context.md` | no | `system-context` |
| `requirements/requirements.csv`, `requirements/candidates.csv` (the `Source` values they cite) | no | `requirement-phrasing`, `artifact-mining` |
| An existing `requirements/sources.csv` | no | earlier runs |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/sources.csv` | `assets/sources.csv` | `artifact-mining`, `interview-guide`, `traceability-matrix`, `requirement-linter` (`unregistered-source`) |

## Procedure

1. **Read the workspace.** Load `schema.json` (defaults if missing), `sources.csv`, `stakeholders.md`, `context.md`, and the `Source` column of `requirements.csv` and `candidates.csv`. Existing rows keep their ID; never renumber, never delete (set Status `retired` with the reason in Notes).
2. **Collect candidate sources.** One per: stakeholder row in `stakeholders.md` with a named representative or proxy; document named in the inputs or in `context.md` (laws, policies, contracts, terms, specifications, runbooks, exports); system in operation (the system being replaced, neighboring systems with documentation, competitor products); free-text sources cited by requirements or candidates ("Grace Lim 2026-10-20", a file path); elicitation records cited as Source (`workshop-<slug> <date>`, `observation-<slug> <date>`), registered as Kind `document`, Category `elicitation record`, with the record's path as Location and its technique.
3. **Keep only identifiable sources** (`references/technique-selection.md` section 7). A source is a named person, a document with a title, or a named system, and someone can find it again. "The internet", "best practice", "common sense", a search result or an assistant's answer are not sources: ask for the document, person or system behind them, and register that instead, or nothing. Stakeholders with representative `TBD` get no row yet; list them in the final message.
4. **Deduplicate.** One row per document version in use, per stakeholder, per system. A person who is a stakeholder and also wrote a document gets two rows (different kinds).
5. **Plan the technique.** Read `references/technique-selection.md`. Choose from the fixed list (`interview`, `workshop`, `questionnaire`, `observation`, `apprenticing`, `document-analysis`, `system-archaeology`, `feedback-analysis`, `reuse`; the same tokens `candidates.csv` uses), several joined with `; ` when needed, by kind of source, kind of knowledge and availability.
6. **Fill the attributes.** `Category`, `Version`, `Location`, `Contact` from the inputs; unknown values are `TBD`, never a guess (no invented version numbers, paths or owners). `Relevance` by the rule in the reference. `Status=planned` unless a work product shows the source was elicited (an `I-nn` record, rows citing it): then `elicited`, with the evidence in Notes.
7. **Allocate IDs.** Use `re-ids` (kind `source`) or `re-lint ids next --kind source`. The next ID is above the highest S-number found anywhere in the workspace, including IDs cited but not registered. A cited-but-unregistered ID (`S-05` in `requirements.csv`, missing from `sources.csv`) is registered under that same ID only when its owner confirms what it refers to; otherwise it is an open question.
8. **Check coverage.** List: S-IDs cited in requirements or candidates but not registered; sources with Status `elicited` that no requirement or candidate cites; `high` relevance sources still `planned`. Report these in the final message; do not edit other skills' registers.
9. **Show, then write.** Show the new and changed rows. After confirmation (or directly in non-interactive mode), write `requirements/sources.csv` with the header of `assets/sources.csv`, in ID order, UTF-8, LF line endings, quoting only fields that need it.
10. **Validate.** Check duplicates and ID patterns with the `re-ids` primitive (or `re-lint ids check requirements/sources.csv`); without either, confirm by hand that no ID appears twice and every ID is `S-` plus digits. If `re-lint` is installed, `re-lint check` should report no `unregistered-source` warning that this run could have fixed.

## Quality checks

- [ ] The header is exactly `ID,Source,Kind,Category,Version,Location,Contact,Technique,Relevance,Status,Notes`.
- [ ] `Kind`, `Technique`, `Relevance` and `Status` use only the values in `references/technique-selection.md`.
- [ ] No vague or unidentifiable source was registered; no version, location or contact was invented.
- [ ] No row is `elicited` without evidence in Notes.
- [ ] IDs are unique; existing rows kept their IDs; `requirements.csv` and `candidates.csv` were not changed.
- [ ] Every stakeholder source names its SH-ID in `Contact` when `stakeholders.md` exists.

## Hand-offs

- **Next:** `artifact-mining` for rows planned as `document-analysis`, `system-archaeology`, `feedback-analysis` or `reuse`; suggest `/interview-guide`, `/elicitation-workshop`, `/questionnaire-builder` or `/observation-protocol` for the other techniques; `traceability-matrix` reads the register for backward trace.
- **Feeds back to:** suggest `/stakeholder-map` when a source needs a stakeholder who is not mapped; `requirement-linter` re-checks `unregistered-source`.

## Non-interactive mode

Register only identifiable sources, keep every unknown attribute `TBD`, keep `Status=planned` without evidence, and end with the coverage findings and the open questions, each with an owner role.

## References

- `references/technique-selection.md`: column values, technique by source and knowledge type, category, relevance and status vocabularies, what is not a source. Read it before step 3.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: the loyalty-points kick-off sources and stakeholder map, and the register they produce.
