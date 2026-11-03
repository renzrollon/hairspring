# IREB anchor: `requirement-classifier`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §1.2 Kinds of requirements; §4.2.1 Kano model |
| CPRE FL Syllabus 3.2 | Chapter 1 (Introduction and overview of requirements engineering); Chapter 4 (Practices for requirements elaboration) |
| IREB Glossary 2.2 terms | Requirement; Functional requirement; Quality requirement; Constraint; Kano model; Dissatisfier; Satisfier; Delighter |
| Quality criteria touched | adequate, necessary, unambiguous (single requirement) |
| Other standards | ISO/IEC 25010:2023, product quality model (characteristic names only); Kano et al. (1984), attractive quality model |

## How this skill applies the practice

- Classifies by the concern a statement addresses, which avoids the endless "is this what or how?" debate and puts security or performance wishes in the quality bucket even when they mention a function.
- Separates requirements from statements that only look like them: facts about the world, intentions of other parties (`will`), goals that still need a measurable outcome, and technology choices nobody outside the team mandated.
- Treats a constraint as a restriction imposed from outside the team, so a design decision does not gain the authority of a constraint by being written as one.
- Adds a first Kano guess so dissatisfiers, which stakeholders rarely mention, are visible early, while marking it as a guess to confirm.
- Routes each statement to the practice that handles it next, so nothing is lost and nothing is phrased before it is understood.

## What this skill deliberately leaves out

- Writing the requirement text with a phrase template and IDs: `requirement-phrasing`.
- Confirming Kano categories with stakeholders and ranking: `elicitation-workshop`, `prioritization`.
- Recording constraint details (source, expiry): `constraints-register`.
