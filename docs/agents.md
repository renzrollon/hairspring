# Using re-skills with Claude Code, Codex, Copilot and Cursor

One source tree serves every agent ([ADR 0005](adr/0005-agents-supported.md)). What differs is where each agent looks for skills, how you start a skill explicitly, and which optional frontmatter keys it honors. Facts below were checked on 2026-11-03 against Claude Code 2.1.317, Codex CLI 0.166.0, Copilot CLI 1.0.105, the VS Code docs of 2026-10-28 and `skills` 1.7.6. Cursor facts come from its public docs pages and forum, not from a test run.

## Summary

| Agent | Project skills folder | User skills folder | Start a skill explicitly | Keeps user-invoked skills out of auto-triggering |
| --- | --- | --- | --- | --- |
| Claude Code | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` | `/name` (plugin: `/re-skills:name`) | yes (`disable-model-invocation`) |
| Codex (CLI, IDE) | `.agents/skills/` | `~/.agents/skills/` | `$name`, or the `/skills` picker | yes, via the generated `agents/openai.yaml` (`allow_implicit_invocation: false`) |
| Copilot in VS Code | `.github/skills/<name>/` (also `.claude/skills`, `.agents/skills`) | `~/.copilot/skills/` | `/name` | yes |
| Copilot CLI | `.github/skills/`, `.agents/skills/`, `.claude/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` | `/name` | yes |
| Copilot coding agent (github.com) | `.github/skills/`, `.agents/skills/`, `.claude/skills/` in the repo | dotfiles repo `.copilot/skills` | picked automatically | not documented |
| Cursor | `.cursor/skills/`, `.agents/skills/` (also reads `.claude/skills`) | `~/.cursor/skills/` | `/name` in Agent chat | documented; a forum report says it is ignored under `.agents/skills`, so install into `.cursor/skills` |

**Verified install runs (2026-11-03):**

- **Claude Code 2.1.317:** `claude plugin install re-skills@hairspring` loads all 38 skills.
- **Codex CLI 0.166.0:** after `install.py --agent codex`, the model's implicit catalog lists the 18 model-invoked skills and primitives. The 20 user-invoked skills are absent, as intended, and run only via `$name`.
- **Copilot CLI 1.0.105:** after `install.py --agent copilot`, `copilot skill list` shows all 38 project skills.
- **Cursor:** not run.

Two rules follow from this table:

1. **Install flat.** VS Code and Claude Code look exactly one level deep (`<folder>/<skill>/SKILL.md`). The repo keeps skills in stage folders, so always install through one of the methods below. They flatten the folders; copying `skills/` by hand does not work.
2. **Commit project-level installs** (`.claude/skills`, `.github/skills`, `.agents/skills`, `.cursor/skills`) when the whole team should get the skills, including Copilot's coding agent on github.com.

## Install methods

### A. `install.py` (any agent, any OS, no Node required)

```bash
curl -fsSL https://raw.githubusercontent.com/renzrollon/hairspring/main/install.py | python3 - --agent claude --ref main
```

```bash
python3 install.py --agent all                 # from a clone: all four agents, project scope
python3 install.py --agent copilot --scope user
python3 install.py --agent cursor --priority P0  # only the 12 MVP skills (+ primitives)
python3 install.py --agent codex --uninstall
```

The installer copies each skill into the agent's folder, leaves out `evals/`, records what it installed in `.re-skills-manifest.json`, and upgrades or removes only its own folders. Use `--link` in a clone to symlink while you edit skills.

### B. Claude Code plugin

In a Claude Code session:

```text
/plugin marketplace add renzrollon/hairspring
/plugin install re-skills@hairspring
```

From a shell: `claude plugin marketplace add renzrollon/hairspring && claude plugin install re-skills@hairspring --scope project`. Plugin skills are namespaced: `/re-skills:requirements-review`. The plugin manifest lists every stage folder, so nothing needs flattening.

The same `.claude-plugin/` manifests also install in **Codex** (`codex plugin marketplace add renzrollon/hairspring`, then `codex plugin add re-skills@hairspring`) and **Copilot CLI** (`copilot plugin marketplace add renzrollon/hairspring`, then `copilot plugin install re-skills@hairspring`). In VS Code, add `"chat.plugins.marketplaces": ["renzrollon/hairspring"]` to your settings. Cursor has its own manifest in `.cursor-plugin/`.

### C. `npx skills` (needs Node 22.20+)

```bash
npx skills@latest add renzrollon/hairspring -a claude-code
npx skills@latest add renzrollon/hairspring -a codex -a github-copilot -a cursor
npx skills@latest add renzrollon/hairspring -a claude-code --skill clarifying-questions --skill requirement-linter
```

`npx skills` finds the nested skills and flattens them. For Codex, Copilot and Cursor it installs into `.agents/skills/` (all three read it); for Claude Code into `.claude/skills/` (as a link to the same copy). With `-g` it uses `~/.agents/skills` and `~/.claude/skills`.

### D. claude.ai and the Skills API

Upload paths accept only the six agentskills.io frontmatter keys. Build spec-strict zips with `python3 tools/build_dist.py` and upload `dist/zips/<skill>.zip`. In those surfaces user-invoked skills can also trigger automatically, because `disable-model-invocation` is removed.

## Behavior differences that matter

| Topic | What to know |
| --- | --- |
| Running bundled scripts | Skills say `python3 <skill-dir>/scripts/<file>.py`, where `<skill-dir>` is the folder holding the `SKILL.md`. Every agent resolves that from where it loaded the skill. Claude Code also offers `${CLAUDE_SKILL_DIR}`; we don't use it, so the text stays portable. If the `re-lint` package is installed (`pip install "git+https://github.com/renzrollon/hairspring#subdirectory=packages/re-lint"`), skills prefer the `re-lint` command. |
| Subagents | `requirements-review` reads from three perspectives in parallel when the agent can run subagents (Claude Code, Codex, Copilot agent mode), and one after another otherwise. The findings file has the same shape either way. |
| User-invoked skills on Codex | The generated `agents/openai.yaml` sets `allow_implicit_invocation: false`, so `$re-setup`, `$requirements-review` and the other user-invoked skills run only when you type them. `tools/gen_agent_files.py` regenerates these files and CI checks they are current. |
| Primitives | `re-interview`, `re-ids` and `re-templates` set `user-invocable: false`: hidden from the `/` menu in Claude Code and Copilot, still loaded by other skills. Codex and Cursor may list them; that is harmless. |
| Copilot coding agent | It reads project-level skills from the repo. Commit `.github/skills/` (or `.agents/skills/`) and add the snippet in [`agents/AGENTS.snippet.md`](agents/AGENTS.snippet.md) to your `AGENTS.md` or `.github/copilot-instructions.md`. |
| Spec validators | `skills-ref validate` rejects our three extension keys. `python3 tools/build_dist.py --validate` proves every skill conforms once those keys are stripped; CI runs it. |

## Tell your agents when to use the skills

Skills trigger from their descriptions, but a short standing instruction makes the loop reliable across a team. Paste [`docs/agents/AGENTS.snippet.md`](agents/AGENTS.snippet.md) into:

- `AGENTS.md` (Codex, Copilot, Cursor and others read it),
- `CLAUDE.md` (Claude Code; or add `@AGENTS.md` to it),
- `.github/copilot-instructions.md` (Copilot, if you don't use `AGENTS.md`).
