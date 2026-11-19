# IREB anchor: `baseline`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §6.3–6.4 Versions, configurations and baselines |
| CPRE FL Syllabus 3.2 | Chapter 6 (Practices for requirements management) |
| IREB Glossary 2.2 terms | Baseline; Configuration; Version; Release |
| Quality criteria touched | consistent, modifiable, traceable (set) |
| Other standards | none |

## How this skill applies the practice

- Freezes a consistent set of requirement versions under one name, so a release, a contract or an audit refers to something exact instead of "the requirements as they were then".
- Stores the configuration as a small manifest (ID, version, status, text hash) next to a git commit, which makes any later change detectable without copying the whole register.
- Treats a baseline as immutable: a correction is a new baseline, so earlier references stay valid.
- Compares baselines by fixed classes (added, changed, status-changed, withdrawn, removed) and ties every change to the decision that allowed it, which exposes changes that bypassed the change authority.

## What this skill deliberately leaves out

- Deciding whether a change is accepted: `change-impact`.
- Versioning the text of a single requirement: the `Version` attribute, maintained by `change-impact`.
- Handing a baselined set to a customer tool: `reqif-bridge`.
