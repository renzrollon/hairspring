# IREB anchor: `constraints-register`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §1.2 Kinds of requirements (constraints); §4.2 Elicitation of requirements (restrictions of the solution space) |
| CPRE FL Syllabus 3.2 | Chapter 1 (Introduction and overview of requirements engineering); Chapter 4 (Practices for requirements elaboration) |
| IREB Glossary 2.2 terms | Constraint; Requirement; Requirements source; Stakeholder |
| Quality criteria touched | adequate, necessary, traceable (single requirement); consistent, complete (set) |
| Other standards | arc42, section "Architecture Constraints" (title only; arc42 by Hruschka and Starke, CC BY-SA 4.0); architecture decision records (Michael Nygard, 2011) |

## How this skill applies the practice

- Treats a constraint as a kind of requirement that limits the solution space, kept in the same register as functional and quality requirements so it is reviewed, traced and baselined like them.
- Makes the mandate the defining property: a restriction is a constraint only when someone outside the team requires it, and the register records who that is and where it is written.
- Separates constraints from design decisions so architecture choices stay open for discussion and get their own decision record.
- Gives every constraint a review date, because mandates change (contracts end, standards are revised) and a stale constraint blocks better solutions.
- Keeps the source attached so backward traceability to the regulation, contract or standard is there for audits.

## What this skill deliberately leaves out

- Quality targets: `quality-requirements`.
- Resolving a constraint that contradicts other requirements: `conflict-detector`, then `conflict-to-decision`.
- Assessing the impact of a changed or expired constraint: `change-impact`.
