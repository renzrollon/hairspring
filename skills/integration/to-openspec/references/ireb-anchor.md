# IREB anchor: `to-openspec`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §7.1 Tool categories (RE process, documentation) |
| CPRE FL Syllabus 3.2 | Chapter 7 (Tool support) |
| IREB Glossary 2.2 terms | Requirement; Requirements specification; Traceability; Scenario; Acceptance criteria; Work product |
| Quality criteria touched | verifiable, unambiguous (single requirement, through the hand-off gate); traceable, conformant (set) |
| Other standards | OpenSpec 1.16.0 change and delta-spec format (Fission-AI); spec-kit 1.2.6 spec template (GitHub); RFC 2119 keywords (title only); EARS (Mavin et al., 2009) |

## How this skill applies the practice

- Treats the spec-driven toolkit as one more tool in the chain: the requirements stay in the register, and the toolkit receives a generated, read-only view of the agreed set.
- Keeps the requirement ID in every place the coding agent reads (requirement heading, comment anchor, scenario name, task line), so forward traceability from requirement to code and test does not have to be rebuilt after the hand-off.
- Puts a gate in front of the tool: only agreed or explicitly approved requirements cross, and lint errors or open `TBD`s cross only with a named approval, because a tool hand-off is where vague text turns into wrong code.
- Maps the requirement kinds onto the target format honestly: functional requirements become specification requirements with scenarios; quality requirements and constraints, which restrict the whole change, go into the proposal.
- Uses acceptance criteria as scenarios when they exist and derives a scenario from the EARS condition otherwise, so verifiability is visible in the tool without inventing test data.

## What this skill deliberately leaves out

- Writing or correcting requirement text: `requirement-phrasing`. Finding missing values: `clarifying-questions`, `quality-requirements`.
- Set-level validation before the hand-off: `requirements-review`, `requirement-linter`.
- Technical design and implementation planning: the OpenSpec `design.md` / spec-kit `plan.md` steps, owned by the implementer.
