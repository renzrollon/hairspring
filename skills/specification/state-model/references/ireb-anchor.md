# IREB anchor: `state-model`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.4.5 State and behavior (behavior models) |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices) |
| IREB Glossary 2.2 terms | State; State machine; State machine diagram; Event; Transition; Model |
| Quality criteria touched | complete, unambiguous, verifiable (single requirement); complete, consistent (set) |
| Other standards | UML 2.5.1 (OMG), clause "StateMachines" (title only); Harel, "Statecharts: A visual formalism for complex systems" (1987); EARS state-driven pattern (Mavin et al., 2009) |

## How this skill applies the practice

- Models behavior as a finite set of business states with explicit events, guards and actions, so status-dependent rules stop hiding inside prose.
- Treats completeness as checkable: every state reachable, every non-final state with a way out, and every state and event combination decided explicitly, so missing behavior becomes a list of questions instead of a production defect.
- Leaves the structural checks to a script and keeps the model's judgment for the questions only a stakeholder can answer.
- Turns each state-dependent behavior into one textual requirement with the state-driven phrase template, so the model and the requirement set stay traceable to each other.

## What this skill deliberately leaves out

- Behavior that crosses several roles or systems with hand-overs: `process-flow`.
- Structure (entities, attributes, multiplicities): `domain-model`.
- Phrasing requirements that are not state-dependent: `requirement-phrasing`.
