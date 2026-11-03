# AGENTS.md

Instructions for coding agents (Codex, Copilot, Cursor, Claude Code) working **on this repository**, the `re-skills` catalogue. If you want agents in *your* repository to use the skills, paste [`docs/agents/AGENTS.snippet.md`](docs/agents/AGENTS.snippet.md) into your own AGENTS.md instead.

## What this repo is

- `skills/<stage>/<skill>/`: 35 Agent Skills plus 3 primitives in `skills/_primitives/`. Each folder: `SKILL.md`, `references/`, `assets/`, `examples/`, `evals/`, optional `scripts/`.
- `packages/re-lint/`: stdlib-only Python package and CLI (`re-lint`). The source of truth for every script.
- `tools/`: `vendor_scripts.py` (copies package modules into skills), `validate_catalogue.py` (enforces the authoring guide), `list_skills.py`.
- `examples/loyalty-points/`: the sample project; `BRIEF.md` has the domain facts every example uses.
- `docs/`: authoring guide, tooling contract, ADRs, generated catalogue and pipeline.

## Rules

1. Read `docs/authoring-guide.md` before editing any skill, and `docs/tooling-contract.md` before editing `packages/re-lint`.
2. Never edit a file whose header says `VENDORED from`. Edit the module in `packages/re-lint/src/re_lint/` and run `python3 tools/vendor_scripts.py`.
3. Never paste IREB handbook, syllabus or glossary text, ISO text, or Volere template text. Cite section numbers and names.
4. Keep `SKILL.md` within budget: model-invoked and primitives under 150 lines, user-invoked under 500.
5. Skill bodies must stay agent-neutral: no agent-specific tool names; scripts run as `python3 <skill-dir>/scripts/<file>.py`.
6. US spelling in skill names and skill text.

## Checks to run before you finish

```bash
python3 -m pytest -q packages/re-lint/tests tests
python3 tools/vendor_scripts.py --check --strict
python3 tools/validate_catalogue.py
python3 tools/validate_catalogue.py --check-docs
```

If `--check-docs` fails, run `python3 tools/validate_catalogue.py --write-docs` and commit the regenerated `docs/catalogue.md` and `docs/pipeline.md`.
