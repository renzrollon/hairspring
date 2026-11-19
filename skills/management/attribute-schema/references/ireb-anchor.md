# IREB anchor: `attribute-schema`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §6.3–6.5 Life cycle, attributes and views |
| CPRE FL Syllabus 3.2 | Chapter 6 (Practices for requirements management) |
| IREB Glossary 2.2 terms | Requirements attribute; Status; Version; Requirements management |
| Quality criteria touched | conformant, modifiable, traceable (set) |
| Other standards | ISO/IEC/IEEE 29148:2018, clause "Requirement attributes" (title only) |

## How this skill applies the practice

- Defines the attribute set once, in a schema the scripts enforce, so status, priority, source and owner mean the same thing in every file and every skill.
- Models the life cycle as explicit states and allowed transitions, and checks that the register only uses those states.
- Keeps the schema small and grows it only on demand, because every required attribute costs every author time on every requirement.
- Provides the three kinds of views (selective, projective, aggregating) as saved, regenerable definitions, so each audience sees what it needs without a hand-kept copy that drifts.
- Protects identifiers and values that other work products depend on: renames and removals go through a migration, never a silent edit.

## What this skill deliberately leaves out

- Choosing process facets and the first schema of a repository: `re-setup`.
- Allocating IDs and filling attributes when rows are written: `re-ids`.
- Baselines and versions across releases: `baseline`.
