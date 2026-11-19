# IREB anchor: `spec-assembler`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.6 Documentation structures; §6.5 Views |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices); Chapter 6 (Practices for requirements management) |
| IREB Glossary 2.2 terms | Requirements document; Requirements specification; Glossary; Traceability; View |
| Quality criteria touched | conformant, traceable, modifiable, complete (set); understandable (single requirement) |
| Other standards | ISO/IEC/IEEE 29148:2018, the software requirements specification example outline (clause titles only); arc42, sections "Introduction and Goals", "Architecture Constraints", "Context and Scope", "Quality Requirements", "Glossary" (titles only; arc42 by Hruschka and Starke, CC BY-SA 4.0); Volere Requirements Specification Template (structure option only, licensed, not reproduced) |

## How this skill applies the practice

- Treats the specification as a documentation structure over existing work products, not as a new place to write requirements: every requirement is copied verbatim from the single register, so the document and the register cannot drift.
- Offers three structures for three audiences (a formal SRS for procurement and audits, an arc42 chapter for architecture documentation, a Volere-structured document for organizations that hold its license) and keeps every section of the chosen structure, so gaps are visible instead of silently missing.
- Adds selective and aggregating views (scope by status, counts by type, status and priority) so each reader sees the state of the set at a glance.
- Carries the trace links into the document, backward to sources and forward to decisions, code and tests where they exist.
- Turns every unknown it meets into an open issue with an owner, instead of filling it in.

## What this skill deliberately leaves out

- Writing or correcting requirements: `requirement-phrasing`, `user-story-refiner`, `quality-requirements`, `constraints-register`.
- Reviewing the assembled set: `requirements-review`.
- Building trace links and cutting baselines: `traceability-matrix`, `baseline`.
