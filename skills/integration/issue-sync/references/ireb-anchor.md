# IREB anchor: `issue-sync`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §7.1 Management and collaboration tools |
| CPRE FL Syllabus 3.2 | Chapter 7 (Tool support) |
| IREB Glossary 2.2 terms | Requirements management; Attribute; Traceability; Version; Change request; Stakeholder |
| Quality criteria touched | traceable, consistent, modifiable (set) |
| Other standards | ISO/IEC/IEEE 29148:2018, clause "Requirement attributes" (title only) |

## How this skill applies the practice

- Connects the requirements register to the collaboration tool the team already uses, instead of asking the team to manage work in a second place.
- Makes each attribute's owner explicit (text and attributes in the register, workflow status in the tracker, lifecycle decisions in the register), so a two-way link never turns into two competing versions of one requirement.
- Keeps the requirement ID as the identity of the issue and writes the trace links into the issue, so a developer reading the ticket reaches the source, the decision and the tests.
- Refreshes requirement status from real progress, while keeping the lifecycle rules: agreement needs a named person, verification needs evidence.
- Treats every write to an external tool as a reviewed step (plan, then apply), and never deletes, so the history of a requirement stays reconstructable.

## What this skill deliberately leaves out

- Deciding whether a change to an agreed requirement is accepted: `change-impact`.
- Measuring coverage from issues, commits and tests: `traceability-matrix`.
- Refining stories and acceptance criteria before they become tickets: `user-story-refiner`.
