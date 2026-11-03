# CLAUDE.md

@AGENTS.md

## Claude Code specifics

- This repository is also a Claude Code plugin marketplace. `.claude-plugin/marketplace.json` lists one plugin, `re-skills`, whose manifest is `.claude-plugin/plugin.json`. Bump `version` there on release.
- To try your local changes as a plugin: `claude --plugin-dir .` from the repo root, then run a skill, e.g. `/re-skills:clarifying-questions`.
- To run a skill's evals: `cd skills/<stage>/<skill> && claude plugin eval . --allow-tools Write,Edit,Bash --scaffold` (real, billed runs).
