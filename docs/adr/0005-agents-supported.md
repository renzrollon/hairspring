# ADR 0005: Supported agents and the portability rules

- Status: accepted
- Date: 2026-11-03

## Context

The epic asks for Claude Code first and recommends Copilot as the enterprise default; engineering organizations also run Codex and Cursor. All four read the Agent Skills format (`SKILL.md` with YAML frontmatter), but they discover skills in different folders and honor different optional frontmatter keys.

## Decision

- One source tree (`skills/<stage>/<skill>/`) serves every agent. No per-agent forks of skill text.
- Distribution: a Claude Code plugin + marketplace (`.claude-plugin/`), `npx skills add`, and a cross-platform installer (`install.py`) that flattens skills into each agent's skills folder.
- Skill bodies follow the portability rules in `docs/authoring-guide.md` §4.2: no agent-specific tool names, scripts addressed relative to the skill folder, manual fallbacks when Python is missing.
- Frontmatter uses only the agentskills.io keys plus three widely honored extensions (`disable-model-invocation`, `user-invocable`, `argument-hint`). On agents that ignore `disable-model-invocation`, user-invoked skills still state in their description that they are started explicitly.

## Consequences

- Behavior differences between agents are confined to discovery and invocation syntax, documented in `docs/agents.md`.
- `skills-ref validate` (the agentskills.io reference validator) may reject the extension keys; our own `tools/validate_catalogue.py` enforces the spec rules plus our conventions, and is the CI gate.
