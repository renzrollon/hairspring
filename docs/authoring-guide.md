# Authoring guide

This is the contract every skill in `re-skills` follows. A reviewer rejects a skill PR that breaks a **MUST**. The rules exist so that 35 skills written by different people read like one product, compose as a pipeline, and behave the same on Claude Code, Codex, Copilot and Cursor.

Read this together with:

- [`docs/tooling-contract.md`](tooling-contract.md): the deterministic scripts (`re-lint`) and their CLI.
- [`skills/_primitives/re-templates/references/workspace-layout.md`](../skills/_primitives/re-templates/references/workspace-layout.md): where every work product lives in a user's repo.
- [`skills/_primitives/re-ids/references/id-scheme.md`](../skills/_primitives/re-ids/references/id-scheme.md): IDs, attributes, and the lifecycle.
- [`skills/_primitives/re-interview/SKILL.md`](../skills/_primitives/re-interview/SKILL.md): how every skill asks questions.
- The reference implementation: [`skills/specification/requirement-phrasing/`](../skills/specification/requirement-phrasing/).

## 1. Folder anatomy

```text
skills/<stage>/<skill-name>/
  SKILL.md                    # MUST. Frontmatter + procedure + hand-offs
  references/ireb-anchor.md   # MUST. Handbook section, glossary terms, quality criteria
  references/<topic>.md       # optional. Detail loaded only when a step says so
  assets/<template files>     # MUST for every skill that emits a file: the fixed output shape
  scripts/<helper>.py         # optional. Deterministic helpers, stdlib-only Python 3.9+
  examples/                   # MUST. One input and its expected output, on the loyalty-points sample
  evals/<case-name>/          # MUST. At least 3 cases, one of them adversarial (see section 8)
```

Stages and their directories: `foundations`, `scope`, `elicitation`, `specification`, `negotiation`, `validation`, `management`, `integration`, plus `_primitives` for the shared, non-user-facing skills.

## 2. Frontmatter

```yaml
---
name: requirement-phrasing             # MUST equal the folder name. kebab-case, <= 64 chars
description: >-                         # MUST. <= 1024 chars, written as triggers (see 2.1)
  Rewrite requirement-like sentences into EARS / ISO 29148 phrase templates ...
license: MIT                            # MUST
compatibility: Python 3.9+ optional for scripts/; works without it.   # only if scripts/ exists
disable-model-invocation: true          # MUST on user-invoked skills; MUST NOT on model-invoked ones
argument-hint: "[ticket, file or text]" # optional, user-invoked skills only
metadata:                               # MUST. All values are strings
  stage: specification                  # one of the stage directories above, or "primitives"
  invocation: model                     # user | model | primitive
  priority: P0                          # P0 | P1 | P2
  ireb-anchor: "CPRE FL Handbook 1.2 §3.3.1, §3.2"
  inputs-from: "clarifying-questions, artifact-mining, requirement-classifier"   # skill names, comma-separated, or "none"
  outputs-to: "requirement-linter, requirements-review, testability-check"       # skill names, comma-separated, or "none"
  work-product: "requirements/requirements.csv"
  version: "0.1.0"
---
```

- Only the keys above. Agent-specific keys we allow: `disable-model-invocation`, `user-invocable` (primitives set it to `false`), `argument-hint`. Nothing else, so the files stay portable across agents.
- `inputs-from` and `outputs-to` name only skills that exist in the catalogue. `tools/validate_catalogue.py` checks this, and `docs/pipeline.md` is generated from them.

### 2.1 Writing the description

The description is the only thing an agent sees before it decides to load the skill. Write it for that decision:

1. First sentence: what the skill does and what file it leaves behind. Lead with a verb.
2. `Use when ...`: concrete triggers. Name the phrases people type ("refine this story", "what are the NFRs"), the artefacts they have open (a ticket, a PRD, a transcript, a PR touching `requirements/`), and the moment in the workflow ("before implementing", "before a design review").
3. `Not for ...`: the nearest neighbouring skill and when to pick it instead. This is how 35 skills avoid stepping on each other.
4. Be a little pushy for model-invoked skills (agents under-trigger), and precise for user-invoked ones.
5. No marketing words, no "powerful", no "comprehensive".

## 3. Invocation modes

| Mode | Frontmatter | Who starts it | May call | Line budget for `SKILL.md` |
| --- | --- | --- | --- | --- |
| `user` | `disable-model-invocation: true` | A person, via `/name` (Claude Code, Copilot, Cursor) or `$name` (Codex) | model-invoked skills and primitives | < 500 lines (aim for under 250) |
| `model` | none | The agent, when the description matches | other model-invoked skills and primitives | < 150 lines |
| `primitive` | `user-invocable: false` | Other skills | nothing user-invoked | < 150 lines |

A user-invoked skill **never** calls another user-invoked skill. It may *recommend* one as the next step ("Next: suggest the user runs `/conflict-to-decision` on CF-03").

Keep `SKILL.md` lean: put long checklists, pattern catalogues and worked variations in `references/` and tell the agent exactly when to read them ("Read `references/iso25010-checklist.md` before step 3").

## 4. `SKILL.md` body: fixed sections

Every skill uses these headings in this order. Model-invoked skills can keep each one to a few lines.

```markdown
# <Human title>

<One paragraph: the problem, the practice (in our words), the work product it ends with.>

## When not to use
<2 to 4 bullets naming the neighbouring skill to use instead.>

## Inputs
| Input | Required | Usually produced by |

## Outputs
| File | Shape | Consumed by |

## Procedure
1. **<Step name>.** Imperative instructions. Name the file read or written. Say when to stop and ask.
...

## Quality checks
- [ ] Checks the agent runs before saving or handing off. Deterministic ones name the script.

## Hand-offs
- **Next:** `<skill>` when <condition>.
- **Feeds back to:** `<skill>` when <condition>.
```

Optional sections, after `Hand-offs`: `## Non-interactive mode`, `## Pitfalls`, `## References` (the list of files in `references/` with one line on when to read each).

### 4.1 Procedure rules

- **Read the workspace first.** Step 1 of every emitting skill: locate `requirements/` (or the `workspace` set in `requirements/schema.json`), read `schema.json` and `glossary.md` if they exist. If `schema.json` is missing, use the defaults in section 6 and say so in the output. Never stop the work only because `re-setup` was not run.
- **One work product, fixed shape.** Emit the file described in `## Outputs` using the template in `assets/`. Same columns, same headings, every run. Append and update in place; never silently rewrite rows another skill owns.
- **IDs through `re-ids`.** Allocate IDs with the `re-ids` primitive (or `re-lint ids next` if it is installed). Never reuse an ID, including withdrawn ones. Never renumber.
- **Ask, don't invent.** Unknown target values, owners, limits and dates become `TBD` with a matching open question, never a plausible-looking number. Follow `re-interview` for every question you ask.
- **Detect before correcting.** Validation skills list findings first and change requirements only in a separate, confirmed step.
- **Value-oriented depth.** Ask for the detail the next decision needs, not more. Say so when you stop early.
- **Record the source.** Every requirement, term or decision you write carries a source: a source ID (`S-03`), an interview (`I-02`), a person/role and date, or a `file:line`.
- **Show, then write.** For anything longer than a few rows, show the proposed rows or diff and get confirmation before writing to the shared files in interactive mode. In non-interactive mode, write and list what was written.

### 4.2 Portability rules (Claude Code, Codex, Copilot, Cursor)

- Don't name agent-specific tools. Write "ask the user", "read the file", "search the repository", "if you can run subagents, run the three perspectives in parallel; otherwise run them one after another, starting each from a clean summary".
- Refer to other skills by name in backticks: "run the `requirement-linter` skill". Add a fallback when the neighbour might not be installed: "if it is not installed, run `re-lint check` or apply `references/rules.md` by hand".
- Run bundled scripts relative to the skill folder: `python3 <skill-dir>/scripts/<name>.py ...`, where `<skill-dir>` is the directory containing this `SKILL.md`. If Python is unavailable, the skill still works: give the manual fallback in one line.
- Paths in outputs are repo-relative with forward slashes.
- Diagrams: Mermaid first. PlantUML / C4 DSL only when the user asks or `schema.json` says so.
- No network calls in scripts unless the skill is an integration bridge, and then only with an explicit `--apply` flag (dry run by default).

## 5. Work products and the workspace

The canonical layout is in `re-templates/references/workspace-layout.md`. In short: everything lives under `requirements/` at the repo root; `requirements/requirements.csv` is the single register of requirement statements (F, Q and C). Detail work products (`quality-requirements.md`, `constraints.csv`, `verification.csv`, stories, models) reference requirement IDs and may echo the text for readability; when they do, `requirements.csv` wins.

## 6. Minimum schema (inline fallback)

Every skill that emits requirements can rely on this even when `requirements/schema.json` does not exist:

- Columns of `requirements.csv`, in this order: `ID,Type,Text,Source,Priority,Status,Rationale`. Optional columns after them: `Title,Owner,Version,Stability,Risk,Verification,Kano,Links,Tags`.
- `ID` matches `R-\d{3,}` (`R-001`). `Type` is `F` (functional), `Q` (quality) or `C` (constraint).
- `Priority`: `must | should | could | wont`. `Status`: `draft | proposed | agreed | implemented | verified | deferred | rejected | withdrawn`.
- New requirements start as `draft`. Only a named person moves a requirement to `agreed`.

## 7. `references/ireb-anchor.md`

Use [`docs/templates/ireb-anchor.md`](templates/ireb-anchor.md). It names the CPRE Foundation Level Handbook 1.2 section(s) given for the skill in `docs/epics.md` (do not invent other section numbers), public IREB glossary terms by name only, the quality criteria the skill touches, and any other standard by name and clause title only. It then explains in our own words, in 3 to 6 bullets, how the skill applies the practice.

**Never** paste or closely paraphrase handbook, syllabus or glossary text. Never paste ISO text. EARS patterns may be shown with attribution to Mavin et al. Volere is referenced as a structure option only.

## 8. Examples and evals

`examples/` holds `input.md` (or the real input file) and `expected-output.<ext>` for one run on the loyalty-points sample project ([`examples/loyalty-points/BRIEF.md`](../examples/loyalty-points/BRIEF.md)). The expected output uses the asset template exactly.

`evals/` follows the skill-creator case-folder format so `claude plugin eval .` can run it from the skill folder:

```text
evals/<case-name>/
  prompt.md        # settings block, then the prompt as a user would type it
  case.yaml        # schema_version "1.1", name (= folder), expected_outcome
  graders/01-<few-words>.md   # one verifiable statement per file
  files/           # optional input files; add place-files.sh and context.scaffold_script when present
```

`prompt.md`:

```markdown
---
tags: [re-skills, <skill-name>]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

<prompt exactly as a user would type it>
```

`case.yaml`:

```yaml
schema_version: "1.1"
name: <case-name>
expected_outcome: |
  <What a good result looks like, in two to five sentences.>
```

`graders/NN-few-words.md`:

```markdown
---
type: llm
focus: trace
weight: 1
---

<One verifiable statement, e.g. "requirements/requirements.csv contains a row whose Text starts with 'WHEN' and contains 'shall'">
```

Rules:

- At least three cases: one happy path, one realistic messy input, and **one adversarial** case whose folder name starts with `adversarial-` (vague input, contradictory statements, or a design decision in disguise). The adversarial case checks that the skill refuses to invent, flags the problem, or routes to the right neighbour.
- Graders state observable facts about files or the final message. "The output is good" is not a grader.
- Keep input files small (under 100 lines) and on the loyalty-points domain unless the case is about something else on purpose.

## 9. Scripts

- Stdlib-only Python 3.9+, `#!/usr/bin/env python3`, `--help` that explains every flag, exit code `0` (ok), `1` (findings), `2` (usage or parse error).
- Scripts used by more than one skill, or by CI, are maintained in `packages/re-lint` and **vendored** into each skill's `scripts/` by `tools/vendor_scripts.py`. Never edit a vendored copy; CI fails if a copy drifts. See `docs/tooling-contract.md`.
- Single-skill helpers live only in that skill's `scripts/` and get a test under `tests/skill_scripts/`.

## 10. Style

- US spelling in skill names and skill text (`prioritization`, `behavior`).
- Second person, imperative, short sentences. Tables over prose for anything with columns.
- Use the IREB vocabulary consistently: *requirement*, *functional requirement*, *quality requirement*, *constraint*, *stakeholder*, *system context*, *system boundary*, *context boundary*, *source*, *trace*, *baseline*, *change request*. Avoid "NFR" except as a search trigger in descriptions.
- Obligation verbs in requirement text: `shall` (binding), `should` (expected), `may` (optional). `will` states a fact or an intention, not a requirement.
- No invented numbers in templates or references. Examples may use numbers, clearly on the sample project.

## 11. Review checklist (copy into the PR)

- [ ] `python3 tools/validate_catalogue.py` passes (frontmatter, sections, line budgets, anchors, assets, examples, evals, hand-off names).
- [ ] The description reads as triggers and names the neighbour in `Not for`.
- [ ] `references/ireb-anchor.md` cites sections and terms only; no copied text.
- [ ] Inputs and outputs are declared; the output shape is in `assets/`.
- [ ] `examples/` has one real input and its expected output.
- [ ] At least three eval cases including one `adversarial-*`.
- [ ] The hand-off to at least one neighbouring skill was run and the result is committed (in `examples/` or `examples/loyalty-points/`).
- [ ] User-invoked skills carry `disable-model-invocation: true`; model-invoked skills are under 150 lines.
