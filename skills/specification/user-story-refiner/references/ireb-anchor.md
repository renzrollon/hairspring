# IREB anchor: `user-story-refiner`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.3.1.2 User-story template and acceptance criteria |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices) |
| IREB Glossary 2.2 terms | User story; Acceptance criteria; Functional requirement; Requirement; Stakeholder |
| Quality criteria touched | adequate, necessary, verifiable, understandable (single requirement); complete, traceable (set) |
| Other standards | User story template (Mike Cohn, *User Stories Applied*, 2004); INVEST (Bill Wake, 2003); Given/When/Then from behavior-driven development (Dan North) and Gherkin (Cucumber); story-splitting patterns (Richard Lawrence, Humanizing Work) |

## How this skill applies the practice

- Uses the story template as a phrase template: role, goal and benefit must each be present and distinct, so the need and its reason are visible before anyone estimates.
- Treats acceptance criteria as the part of a story that makes it verifiable, and requires an unwanted-behavior case so error handling is agreed before code, not discovered in test.
- Treats each story as a requirement with an identifier and attributes in the shared register, so stories trace to sources, tests and change requests like any other requirement.
- Checks readiness against the team's own Definition of Ready instead of a generic one, and records the evidence per item.
- Splits by user-visible behavior (vertical slices), which keeps every slice valuable and testable on its own.

## What this skill deliberately leaves out

- Verification methods and measurable forms of subjective criteria: `testability-check`.
- Quality requirements that apply across stories: `quality-requirements`.
- Ranking the stories: `prioritization`.
