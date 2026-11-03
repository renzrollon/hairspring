# IREB anchor: `traceability-matrix`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §6.6 Traceability (backward, forward, between requirements) |
| CPRE FL Syllabus 3.2 | Chapter 6 (Practices for requirements management) |
| IREB Glossary 2.2 terms | Traceability; Backward traceability; Forward traceability; Requirements source; Test case |
| Quality criteria touched | verifiable (single requirement); traceable, complete (set) |
| Other standards | none |

## How this skill applies the practice

- Covers all three directions with one file: backward links (source → requirement), forward links (requirement → decision, code, test) and links between requirements (`Links` column).
- Takes links from evidence the team already produces (IDs in commits, test names, annotations, decision records) instead of a hand-kept spreadsheet, so the matrix stays current at no extra cost.
- Treats a missing link as a finding to triage, not as a number to make green. The status of the requirement decides how serious the gap is.
- Keeps the matrix deterministic and diffable (one row per link, fixed columns, sorted), so a nightly run or a release gate shows exactly what changed.

## What this skill deliberately leaves out

- Deciding how each requirement is verified: `testability-check`.
- Following the links for one change request and sizing it: `change-impact`.
- Filing the gaps in a tracker: `issue-sync`.
