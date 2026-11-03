---
name: domain-model
description: >-
  Builds the domain model: a Mermaid classDiagram (or erDiagram) of the business objects, their
  business attributes and the multiplicities of their associations, derived from
  requirements/requirements.csv and requirements/glossary.md, then cross-checks model and
  glossary: terms with no class, classes with no term, two words for one concept, one word for
  two concepts. Writes requirements/models/domain-model.md and hands the glossary findings to
  the glossary skill. Use when requirements or tickets mention several business objects and
  nobody has drawn how they relate, when someone asks for "the data model", "an ER diagram",
  "the entities", "is a customer the same as a member", before designing a database schema or
  API resources, or when code names and glossary terms drift apart. Not for the lifecycle of one
  entity (use state-model), for writing or editing glossary entries (use glossary), or for
  physical database design with keys and indexes (out of scope: this stays at business level).
license: MIT
compatibility: Python 3.9+ optional for scripts/check_glossary.py; works without it.
metadata:
  stage: specification
  invocation: model
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §3.4.3"
  inputs-from: "glossary, requirement-phrasing, artifact-mining, system-context, requirement-classifier"
  outputs-to: "glossary, state-model, requirement-phrasing, requirements-review, spec-assembler"
  work-product: "requirements/models/domain-model.md"
  version: "0.1.0"
---

# Domain model

Requirements name business objects in passing ("the member's voucher", "the store of a purchase") and nobody checks that the names, the relationships and the counts fit together. A domain model makes them explicit: which objects the system must remember, which facts each holds, how many of one belong to another. Drawing it next to the glossary exposes vocabulary defects early: a term with no object, an object nobody defined, two words for one thing. This skill draws the model in Mermaid, records every multiplicity with its source, and lists the vocabulary findings for the glossary owner.

## When not to use

- The lifecycle of one entity (states, events, what happens when): `state-model`.
- Writing, merging or redefining glossary entries: `glossary` (this skill only raises findings).
- Physical database design (keys, indexes, normalization, column types): a design activity, not requirements.
- Steps and responsibilities across roles: `process-flow`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` (or the requirement text you were given) | yes | `requirement-phrasing`, `requirement-classifier` |
| `requirements/glossary.md` | no (without it every class becomes a `class-without-term` finding) | `glossary` |
| `requirements/context.md` (system boundary) | no | `system-context` |
| Legacy material: schema, API contracts, code | no | `artifact-mining` |
| `requirements/schema.json` | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/models/domain-model.md` | `assets/domain-model.md` | `glossary`, `state-model`, `requirements-review`, `spec-assembler` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else defaults, and say so), `glossary.md`, `requirements.csv`, `context.md`, and an existing `models/domain-model.md` (update it in place; never rename a class without a cross-check finding). Model only what lies inside the system boundary or what the system must remember about its context.
2. **Collect candidates.** List the nouns in requirement text and the glossary terms. Classify each with the table in `references/modeling-rules.md`: business object (class), attribute, actor or role, rule or process, synonym of another candidate, technical artefact. Only business objects become classes.
3. **Choose the notation.** `classDiagram` by default. `erDiagram` only when the user asks for it or `schema.json` says so; it cannot show an unknown multiplicity, see `references/mermaid-class-er.md`.
4. **Draw.** Read `references/mermaid-class-er.md`. Class names are glossary terms in PascalCase. Attributes are business facts with business types (`Points`, `Money`, `Date`, `DateTime`, `Text`, `Code`, `Number`, or an enumeration). No technical keys, foreign keys, audit columns, methods, or classes like `MemberService`, `PointsRepository`, `BalanceCache`. Every association has a verb-phrase label and a multiplicity at both ends, each taken from a requirement, a rule or the glossary; unknown is `"TBD"` with an open question. Generalization only when the subtype adds attributes or associations of its own.
5. **Fill the tables.** Classes (class, glossary term, meaning, key attributes, source) and Associations (from, multiplicity, label, multiplicity, to, source), from `assets/domain-model.md`.
6. **Cross-check against the glossary.** Run `python3 <skill-dir>/scripts/check_glossary.py requirements/models/domain-model.md` (without Python, compare class names and glossary terms by hand). Then read the requirement text for what a script cannot see: one concept under two words (`customer` and `member`), one word for two concepts (`balance` for all points and for redeemable points). Record every finding in the Glossary cross-check table with evidence and a proposed action. For terms you decide are not business objects (actors, rules), record the decision and rerun with `--ignore "<term>,<term>"`.
7. **Never edit the glossary here.** The `glossary` skill owns `glossary.md`. Hand it the cross-check rows; if it is not installed, leave them in the table for the glossary owner and say so.
8. **Show, then write.** Show the diagram and the findings; after confirmation (or directly in non-interactive mode) write `models/domain-model.md`. Requirements that use a synonym go to `requirement-phrasing` for rewording; do not edit `requirements.csv` here.

## Quality checks

- [ ] Every class maps to a glossary term, or has a cross-check finding.
- [ ] Every association has a label and two multiplicities; each multiplicity has a source or is `TBD` with an open question.
- [ ] No technical artefacts: no IDs, foreign keys, timestamps for auditing, methods, or service/repository/cache/DTO classes.
- [ ] `check_glossary.py` exits 0, or exits 1 with every finding recorded in the cross-check table.
- [ ] `requirements/glossary.md` and `requirements/requirements.csv` are unchanged.
- [ ] The Mermaid block uses only the subset in `references/mermaid-class-er.md`.

## Hand-offs

- **Next:** `glossary` with the cross-check findings; `state-model` for each class whose status drives behavior (an attribute typed with a state enumeration); `requirements-review` for the set.
- **Feeds back to:** `requirement-phrasing` when a requirement uses a synonym or an undefined term; `clarifying-questions` with every `TBD` multiplicity; `system-context` when a class turns out to live outside the system boundary.

## Non-interactive mode

Write the file with `TBD` multiplicities and open questions, run the cross-check, and end with the list of glossary findings and open questions.

## References

- `references/mermaid-class-er.md`: the classDiagram and erDiagram subset that renders on GitHub, multiplicity notation, PlantUML alternative. Read it at step 4.
- `references/modeling-rules.md`: what becomes a class, attribute rules, multiplicity rules, the cross-check finding kinds and their actions. Read it at steps 2 and 6.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: the loyalty-points glossary and requirements, and the domain model they produce.
