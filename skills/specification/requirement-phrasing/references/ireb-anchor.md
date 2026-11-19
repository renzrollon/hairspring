# IREB anchor: `requirement-phrasing`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.3.1 Phrase templates; §3.2 Natural-language-based work products (rules for writing) |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices) |
| IREB Glossary 2.2 terms | Requirement; Functional requirement; Quality requirement; Constraint; Requirements template |
| Quality criteria touched | unambiguous, verifiable, understandable, complete (single requirement); conformant (set) |
| Other standards | EARS (Mavin et al., 2009); ISO/IEC/IEEE 29148:2018, clauses "Requirement construct" and "Characteristics of individual requirements" (titles only) |

## How this skill applies the practice

- Uses a phrase template so the structure of every requirement (condition, actor, obligation, response) is visible and checkable.
- Treats the obligation verb as the binding level, and `will` as a statement of fact, not a requirement.
- Removes the classic natural-language defects (vague qualifiers, missing actors, incomplete conditions, compound statements) at writing time, and leaves the deterministic double check to `requirement-linter`.
- Keeps the source and rationale attached at the moment of writing, so backward traceability is never reconstructed.

## What this skill deliberately leaves out

- User-story templates and acceptance criteria: `user-story-refiner`.
- Eliciting the missing values: `clarifying-questions`, `quality-requirements`.
- Set-level checks (consistency, redundancy): `requirements-review`, `conflict-detector`.
