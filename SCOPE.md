# Scope

What `re-skills` is, and what it will not become. Reviewers enforce this file: a PR that moves the project outside it needs a decision in `docs/adr/` first.

## In scope

- Agent skills (agentskills.io `SKILL.md` format) for one requirements-engineering practice each, anchored to the IREB CPRE Foundation Level syllabus and handbook by section number and public glossary term.
- Work products as files in the user's repo: CSV registers, Markdown with Mermaid diagrams, decision records, change requests, review reports, trace matrices.
- Deterministic checks (`packages/re-lint`) that can gate CI: linting, ID and attribute validation, trace coverage, baselines.
- Bridges to the tools teams already run: OpenSpec and spec-kit, GitHub Issues / Jira / Azure DevOps, ReqIF (DOORS, Polarion, Jama).
- Packaging for Claude Code, OpenAI Codex, GitHub Copilot and Cursor from one source tree.
- One sample project (`examples/loyalty-points`) on which every skill is demonstrated.

## Out of scope

| Not this | Why | Use instead |
| --- | --- | --- |
| A requirements management system or database | Files in git are the store; we feed RM tools, we don't replace them | DOORS, Jama, Polarion, StrictDoc, doorstop |
| CPRE exam preparation | Different audience and copyright exposure | A separate study project |
| Reproducing IREB handbook, syllabus or glossary text | IREB copyright | Cite section numbers and term names only |
| Reproducing ISO standard text or licensed templates (Volere) | Copyright and licensing | Cite clause titles; reference Volere as a structure option |
| A graphical modeling tool | All diagrams are text and diffable | Mermaid, PlantUML, C4 DSL |
| Project management (estimation in hours, sprint planning) | Not an RE practice | Your tracker |
| Agent-specific forks of skill text | One source tree, portability rules | `docs/authoring-guide.md` §4.2 |

## Adding a skill

A new skill needs: a CPRE FL practice it maps to that no existing skill covers, a work product with a fixed shape, a named neighbor it hands off to, and a demand signal (an issue from a team that would use it). P2-style skills stay gated on demand.
