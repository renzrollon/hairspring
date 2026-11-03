# IREB anchor: `use-case-spec`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.3.2 Form templates; §3.4.2.2 Use case diagrams |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices) |
| IREB Glossary 2.2 terms | Use case; Use case diagram; Actor; Scenario; Precondition; Postcondition; Template |
| Quality criteria touched | complete, unambiguous, understandable, verifiable (single requirement); consistent, traceable (set) |
| Other standards | Cockburn, *Writing Effective Use Cases* (2001), fully dressed form (structure only); UML 2.5.1 (OMG), clauses "UseCases" and "Activities" (titles only); EARS (Mavin et al., 2009) for the linked requirements |

## How this skill applies the practice

- Uses a form template so every use case has the same fields, which makes missing parts (no minimal guarantee, an extension with no ending) visible at a glance.
- Describes the interaction from the primary actor's goal, technology-free, so the scenario stays valid when the user interface or the architecture changes.
- Treats extensions as the main source of missed requirements: every step is examined for what can go differently, and every extension must end explicitly.
- Draws the use case diagram to show the system boundary and who takes part, and an activity diagram only when the branching would otherwise be hard to follow.
- Links every system step to a requirement ID, so the use case and the requirement register can be traced to each other and reviewed together.

## What this skill deliberately leaves out

- Processes that span several roles without one actor goal: `process-flow`.
- Splitting the scenario into backlog stories with acceptance criteria: `user-story-refiner`.
- Defining the system boundary and the actor list: `system-context`.
