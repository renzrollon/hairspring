# IREB anchor: `source-inventory`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §4.1 Requirements sources; §6.6 Traceability (backward traceability to sources before the requirements specification) |
| CPRE FL Syllabus 3.2 | Chapter 4 (Practices for elaborating requirements); Chapter 6 (Practices for requirements management) |
| IREB Glossary 2.2 terms | Requirements source; Stakeholder; Elicitation; Elicitation technique; Traceability |
| Quality criteria touched | traceable, complete (set) |
| Other standards | none |

## How this skill applies the practice

- Treats the three kinds of requirements sources (stakeholders, documents, systems in operation) as one register, so a forgotten regulation or legacy batch job is as visible as a forgotten person.
- Gives each source a stable ID at registration, which is what backward traceability needs: every requirement's `Source` points at a row that says what, which version, and where.
- Plans an elicitation technique per source from the kind of source, the kind of knowledge it holds and its availability, so tacit knowledge gets observation and binding documents get analysis.
- Refuses sources nobody can find again, and records the evidence before a source is marked as elicited.
- Reports coverage gaps (cited but unregistered, registered but never used), which is the cheapest backward-traceability check there is.

## What this skill deliberately leaves out

- Rating stakeholders and finding missing roles: `stakeholder-map`.
- Extracting candidate requirements from documents and systems: `artifact-mining`.
- Building and checking the full trace matrix: `traceability-matrix`.
