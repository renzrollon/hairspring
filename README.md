# re-skills

**Requirements engineering skills for AI-assisted engineering teams.** Get IREB-grade requirements work without a requirements engineer in the room. That means asking the questions that change the design before anyone codes, writing one testable sentence per requirement, catching defects in CI, and tracing every requirement to its tests.

[![CI](https://github.com/renzrollon/hairspring/actions/workflows/ci.yml/badge.svg)](https://github.com/renzrollon/hairspring/actions/workflows/ci.yml)
![skills](https://img.shields.io/badge/skills-35%20%2B%203%20primitives-0f766e)
![agents](https://img.shields.io/badge/agents-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Copilot%20%C2%B7%20Cursor-11203a)
![license](https://img.shields.io/badge/license-MIT-blue)

- **35 skills, one practice each.** Each skill follows the RE lifecycle from scoping to change management and ends in a file a reviewer can diff: a context diagram, an EARS requirements register, review findings, a trace matrix, a change request.
- **Deterministic where it can be.** Weak words, passive voice without an actor, incomplete conditions, duplicate IDs and missing attributes are caught by `re-lint`, a stdlib-only Python linter with a GitHub Action, not by model judgment.
- **Composes with what you run.** Requirements flow into OpenSpec and spec-kit for coding agents, into GitHub Issues, Jira or Azure DevOps, and out to DOORS or Polarion via ReqIF.
- **Works on every major agent.** The same `SKILL.md` files work on Claude Code, OpenAI Codex, GitHub Copilot (VS Code, CLI, coding agent) and Cursor.

> re-skills is an independent project. It is aligned with the public IREB CPRE Foundation Level syllabus and glossary, but it is not affiliated with or endorsed by IREB. Skills cite handbook section numbers and glossary term names; they do not reproduce IREB text. See [Standards and licensing](#standards-and-licensing).

## Install

Pick one method. Every method installs the same skills. [docs/agents.md](docs/agents.md) has the details and the per-agent differences.

**Any agent, no clone, no Node:**

```bash
curl -fsSL https://raw.githubusercontent.com/renzrollon/hairspring/main/install.py | python3 - --agent claude --ref main
```

Set `--agent` to `claude`, `codex`, `copilot`, `cursor` or `all`. Add `--scope user` to install for yourself rather than for the project, and `--priority P0` to install only the 12 MVP skills.

**Claude Code plugin:**

```text
/plugin marketplace add renzrollon/hairspring
/plugin install re-skills@hairspring
```

The same marketplace works with `codex plugin marketplace add renzrollon/hairspring` and `copilot plugin marketplace add renzrollon/hairspring`.

**npx skills:**

```bash
npx skills@latest add renzrollon/hairspring -a claude-code -a codex -a github-copilot -a cursor
```

Then, once per repository:

```text
/re-setup          (Claude Code, Copilot, Cursor)
$re-setup          (Codex)
```

To make the skills part of your team's routine, paste [docs/agents/AGENTS.snippet.md](docs/agents/AGENTS.snippet.md) into your `AGENTS.md` or `CLAUDE.md`. It tells coding agents to clarify before implementing, cite requirement IDs in commits and tests, and lint requirement changes.

## The loop in one minute

```text
/re-setup                                   requirements/README.md, schema.json, glossary.md
/system-context loyalty-points service      context.md: diagram, interfaces, open boundary decisions
"Before we build LOY-118, what's unclear?"  clarifying-questions → 7 questions → answers become R-041..R-047
/quality-requirements                       measurable quality requirements, architecture drivers tagged
re-lint check                               deterministic lint, CI-ready exit code
/requirements-review                        findings from user, architect and tester perspectives
"Add verification methods"                  testability-check → verification.csv
re-lint trace build && re-lint trace gaps   source → requirement → code → test, with gaps
/change-impact "raise the limit to 200k"    CR-001 with impact set, options and a recommendation
```

The full walkthrough is in [docs/getting-started.md](docs/getting-started.md). Every skill is demonstrated on one fictional sample project, [examples/loyalty-points](examples/loyalty-points/).

## The catalogue

Two kinds of skill. **User-invoked** skills (`/name`) are orchestrators that you start, such as `/requirements-review`. **Model-invoked** skills start on their own when the conversation matches. For example, `clarifying-questions` runs before an agent implements a vague ticket. User-invoked skills can call model-invoked ones, never each other.

**P0** is the MVP (12 skills that cover one full pass), **P1** is v1 and **P2** is v2.

| Stage | Skills |
| --- | --- |
| **0 Foundations** | `/re-setup` P1 · `glossary` **P0** · `requirement-classifier` P1 |
| **1 Scope and context** | `/system-context` **P0** · `/stakeholder-map` P1 · `source-inventory` P1 |
| **2 Elicitation** | `clarifying-questions` **P0** · `/interview-guide` P1 · `artifact-mining` **P0** · `/elicitation-workshop` P2 · `/questionnaire-builder` P2 · `/observation-protocol` P2 |
| **3 Specification** | `requirement-phrasing` **P0** · `/user-story-refiner` **P0** · `/quality-requirements` **P0** · `/use-case-spec` P1 · `domain-model` P1 · `process-flow` P1 · `state-model` P1 · `constraints-register` P1 · `/spec-assembler` P2 |
| **4 Negotiation** | `conflict-detector` P1 · `/conflict-to-decision` P1 |
| **5 Validation** | `/requirements-review` **P0** · `requirement-linter` **P0** · `testability-check` **P0** · `/prototype-brief` P2 |
| **6 Management** | `traceability-matrix` **P0** · `/change-impact` **P0** · `/prioritization` P1 · `attribute-schema` P2 · `/baseline` P2 |
| **7 Integration** | `/to-openspec` P1 · `/issue-sync` P1 · `/reqif-bridge` P2 |
| Primitives | `re-interview` (how every skill asks questions) · `re-ids` (IDs and attributes) · `re-templates` (schema and workspace layout) |

The generated catalogue, with each skill's work product and IREB anchor, is in [docs/catalogue.md](docs/catalogue.md). The hand-off graph is in [docs/pipeline.md](docs/pipeline.md).

## Requirements quality as a CI gate

```yaml
# .github/workflows/requirements-lint.yml
on:
  pull_request:
    paths: ["requirements/**"]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: renzrollon/hairspring@v0.1.0
        with:
          fail-on: error
          changed-only: origin/${{ github.base_ref }}
```

Findings appear as annotations on the PR diff. You can also run it locally:

```bash
pip install "git+https://github.com/renzrollon/hairspring#subdirectory=packages/re-lint"
re-lint check
```

The rules and their configuration are in [packages/re-lint/README.md](packages/re-lint/README.md).

## How the skills work

- **The workspace.** Everything lives in `requirements/` in your repo. `requirements.csv` is the one register of requirement statements (`ID,Type,Text,Source,Priority,Status,Rationale`). Diagrams are Mermaid blocks inside Markdown, next to the text they illustrate. [Workspace layout](skills/_primitives/re-templates/references/workspace-layout.md).
- **IDs and attributes from the first requirement.** Every row gets a unique, never-reused ID (`R-012`), a type (functional, quality or constraint), a source, a priority, a status and a rationale. Cite the IDs in commits and test names, and traceability falls out for free.
- **Ask, don't invent.** A missing limit, target or owner becomes `TBD` plus an open question, never a plausible-looking number. With no human available (CI, autonomous runs), skills log their questions and finish the rest of the work.
- **Detect before correcting.** Validation skills list findings first. Requirements change only in a separate, confirmed step.
- **Declared hand-offs.** Every skill states what it consumes and what it emits, and which skill comes next. That is what turns 35 skills into a pipeline.

## Standards and licensing

| Standard | How re-skills uses it | Position |
| --- | --- | --- |
| IREB CPRE Foundation Level (syllabus 3.2, handbook 1.2, glossary 2.2) | Section numbers and glossary term names in each skill's `references/ireb-anchor.md` | Cited, never reproduced; independent of IREB |
| EARS (Mavin et al.) | Phrase templates in `requirement-phrasing` and the linter | Freely usable with attribution |
| ISO/IEC/IEEE 29148:2018 | Requirement attributes, SRS outline in `spec-assembler` | Clause titles only |
| ISO/IEC 25010:2023 | Quality characteristics as a checklist in `quality-requirements` | Characteristic names only |
| Volere | A structure option in `spec-assembler` | Referenced, not embedded (licensed template) |
| Example Mapping / Gherkin, C4, Planguage | Acceptance criteria, context diagrams, quality metrics | Public techniques, attributed |
| agentskills.io specification | Skill format | Conformant; `tools/build_dist.py --validate` proves it |

Code and skill text are MIT-licensed ([LICENSE](LICENSE)).

## Repository layout

```text
skills/<stage>/<skill>/   SKILL.md, references/, assets/, examples/, evals/, scripts/, agents/openai.yaml
skills/_primitives/       re-interview, re-ids, re-templates
packages/re-lint/         stdlib-only Python linter and tools (source of every bundled script)
examples/loyalty-points/  the sample project, with one full loop committed
docs/                     getting started, agents, authoring guide, tooling contract, ADRs
tools/                    vendoring, catalogue validation, agent sidecar files, portable builds
install.py                installer for Claude Code, Codex, Copilot, Cursor
action.yml                GitHub Action: lint requirements on pull requests
.claude-plugin/           Claude Code plugin + marketplace (also read by Codex and Copilot)
.cursor-plugin/           Cursor plugin + marketplace
```

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [docs/authoring-guide.md](docs/authoring-guide.md) (the contract every skill follows) and [SCOPE.md](SCOPE.md). The reference implementation for a skill is [skills/specification/requirement-phrasing](skills/specification/requirement-phrasing/).
