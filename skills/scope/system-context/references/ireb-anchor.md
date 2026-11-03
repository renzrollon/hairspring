# IREB anchor: `system-context`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §1.4 System context and boundaries; §3.4.2 Context models |
| CPRE FL Syllabus 3.2 | Chapter 1 (Introduction and overview of requirements engineering); Chapter 3 (Work products and documentation practices) |
| IREB Glossary 2.2 terms | System; System context; System boundary; Context boundary; Context diagram; Context model; Actor; Interface; Scope |
| Quality criteria touched | complete, consistent (set); adequate (single requirement) |
| Other standards | C4 model, System Context diagram (Simon Brown; title only) |

## How this skill applies the practice

- Separates the two boundaries explicitly: what the system itself does, and which parts of its environment matter for its requirements. Each gets its own table so neither is implied by the other.
- Treats uncertainty as a first-class result: grey zones on either boundary are logged as open decisions with an owner, not settled by whoever draws the picture.
- Builds the context diagram from a table of data flows, so the model stays consistent with its text and can be reviewed row by row.
- Keeps the system a black box and names external actors by role, so the model shows the environment and its interfaces, not the solution.
- Starts from evidence in the repository and confirms it with people, which is cheaper than an open-ended interview and surfaces forgotten neighbours such as batch jobs and extracts.

## What this skill deliberately leaves out

- The people and organizations behind each actor, their influence and availability: `stakeholder-map`.
- The register of documents and systems to elicit from: `source-inventory`.
- Taking the scope decisions themselves: `conflict-to-decision`.
