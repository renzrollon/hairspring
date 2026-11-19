<!-- Paste this section into your repository's AGENTS.md (Codex, Copilot, Cursor) and/or CLAUDE.md (Claude Code).
     It tells coding agents when to use the re-skills requirements skills. Edit the paths if your workspace is not requirements/. -->

## Requirements workflow (re-skills)

Requirements for this repository live in `requirements/` (register: `requirements/requirements.csv`, IDs `R-nnn`). The re-skills catalogue is installed; follow these rules.

**Before implementing**
- If a ticket, issue or request is ambiguous (missing actors, limits, error behavior, data, quality targets), use the `clarifying-questions` skill before writing code. Skip it only when the task is fully specified or a pure refactor, and say so.
- Never invent a limit, timeout, size or percentage. Record it as `TBD` with an open question.
- If a statement in the task is a design decision ("use Redis", "use Kafka"), ask for the quality or constraint behind it.

**While implementing**
- Cite requirement IDs in commit messages (`feat: CSV export (R-041)`) and in test names (`test_r_041_masks_pii`) so the trace matrix finds them.
- When behavior changes an agreed requirement, do not edit `requirements.csv` silently: draft a change request with the `change-impact` skill.

**When `requirements/` changes in a PR**
- Run `re-lint check --changed-only origin/main` (or the `requirement-linter` skill) and fix every error.
- For new or substantially changed requirements, run the `requirements-review` skill and attach the findings file.

**Vocabulary**
- Use the terms in `requirements/glossary.md`. If a term is missing or used in two senses, use the `glossary` skill.
