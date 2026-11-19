# IREB anchor: `requirements-review`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.8 Quality criteria for work products and requirements; §4.4 Validation of requirements (validation techniques, perspective-based reading) |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices); Chapter 4 (Practices for requirements elaboration) |
| IREB Glossary 2.2 terms | Validation; Review; Inspection; Defect; Requirement; Stakeholder |
| Quality criteria touched | adequate, necessary, unambiguous, complete, understandable, verifiable (single requirement); consistent, non-redundant, complete, modifiable, traceable, conformant (set) |
| Other standards | ISO/IEC/IEEE 29148:2018, clauses "Characteristics of individual requirements" and "Characteristics of a set of requirements" (titles only) |

## How this skill applies the practice

- Applies the single-requirement and set criteria as two separate passes, because a set can fail (contradictions, gaps) even when every row looks fine on its own.
- Puts value first (IREB Principle 1): adequacy and understandability are graded before anything else, and a requirement that fails them is not polished further.
- Uses perspective-based reading with three independent readers (user, architect, tester), each with its own brief, so the review finds what the author's own perspective hides.
- Lets the deterministic linter handle what it can, so reviewer judgment is spent on meaning, not on wording a script already checks.
- Keeps detection and correction apart: findings are reported with a proposed fix, and requirements change only after the author accepts each finding.

## What this skill deliberately leaves out

- Resolving disagreements between stakeholders: `conflict-detector`, `conflict-to-decision`.
- Validating requirements with prototypes and real users: `prototype-brief`.
- Writing verification methods and acceptance criteria for every row: `testability-check`.
