# IREB anchor: `process-flow`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.4.4 Function and flow (functional and flow models) |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices) |
| IREB Glossary 2.2 terms | Activity diagram; Activity; Control flow; Process; Stakeholder |
| Quality criteria touched | complete, unambiguous, understandable (single requirement); complete, consistent (set) |
| Other standards | UML 2.5.1 (OMG), clause "Activities" (title only); Mendling, Reijers, van der Aalst, "Seven process modeling guidelines (7PMG)" (2010) |

## How this skill applies the practice

- Models the flow of work as actions, decisions and parallel branches, with one lane per responsible role or system, so every hand-over and every owner is visible.
- Requires every decision outcome to be labeled and every case to be covered or explained, which turns missing branches into open questions.
- Keeps the main flow readable with a fixed, documented size rule and moves long exception paths into their own flows instead of letting one diagram grow.
- Links each step the system performs to the requirements behind it, and lists steps without one as candidates, so the model and the requirement set stay traceable.

## What this skill deliberately leaves out

- One actor's goal-driven interaction with the system: `use-case-spec`.
- The states of one entity: `state-model`.
- Phrasing the requirement candidates: `requirement-phrasing`.
