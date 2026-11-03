# IREB anchor: `domain-model`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.4.3 Structure and data (structural models) |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices) |
| IREB Glossary 2.2 terms | Domain model; Class diagram; Entity-relationship model; Glossary; Synonym; Homonym |
| Quality criteria touched | unambiguous, understandable (single requirement); consistent, complete (set) |
| Other standards | UML 2.5.1 (OMG), clauses "Classification" and "Structured Classifiers" (titles only); Chen, "The entity-relationship model: toward a unified view of data" (1976) |

## How this skill applies the practice

- Models the business objects the system must know about, with their facts and how many of one belong to another, at the level stakeholders can review, not at database level.
- Ties every class to a glossary term and every multiplicity to a source, so the model is evidence about the requirements rather than a design sketch.
- Uses the model as a cross-check of the vocabulary: gaps between glossary and model, synonyms and homonyms are reported as findings for the glossary owner, which is how shared understanding is tested instead of assumed.
- Keeps the deterministic part (class names against glossary terms) in a script and leaves the semantic part (two words, one concept) to the model, with evidence.

## What this skill deliberately leaves out

- Writing and maintaining glossary entries: `glossary`.
- The behavior of an entity over time: `state-model`.
- Physical data design (keys, indexes, normalization): a design activity outside requirements engineering.
