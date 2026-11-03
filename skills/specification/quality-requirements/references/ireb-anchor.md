# IREB anchor: `quality-requirements`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §1.2 Kinds of requirements (quality requirements); §4.2 Elicitation of requirements (ISO/IEC 25010 as a checklist) |
| CPRE FL Syllabus 3.2 | Chapter 1 (Introduction and overview of requirements engineering); Chapter 4 (Practices for requirements elaboration) |
| IREB Glossary 2.2 terms | Quality requirement; Functional requirement; Constraint; Stakeholder; Requirements source |
| Quality criteria touched | verifiable, unambiguous, adequate (single requirement); complete (set) |
| Other standards | ISO/IEC 25010:2023, clause "Product quality model" (title only; characteristic and sub-characteristic names only); Planguage (Tom Gilb, *Competitive Engineering*, 2005) |

## How this skill applies the practice

- Uses the product quality model as an elicitation checklist, so a whole class of requirements is asked about on purpose instead of discovered after go-live.
- Tailors the checklist to the system type, so the walkthrough spends its questions where the risk is and records why the rest was skipped.
- Makes every quality requirement verifiable by construction: metric, target, condition and measurement method, with the target coming from a stakeholder and never from the agent.
- Separates quality requirements from the functions, constraints and design decisions that hide behind quality words ("auditable", "secure", "use a cache").
- Marks architecture drivers so the quality requirements that shape the design reach the architect before the design review.

## What this skill deliberately leaves out

- Constraints found during the walkthrough: `constraints-register`.
- Verification planning per requirement: `testability-check`.
- Resolving competing targets: `conflict-detector`, then `conflict-to-decision`.
