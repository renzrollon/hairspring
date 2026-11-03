# Getting started: your first requirements loop

This walks one feature through the MVP loop (**scope → elicit → specify → validate → trace**) in a real repository. Plan on about 30 minutes the first time and 10 after that. Commands are shown for Claude Code, GitHub Copilot and Cursor (`/skill`); in Codex type `$skill` instead. Model-invoked skills also start on their own when the conversation matches their description; you can always name them explicitly ("use the requirement-linter skill").

Install first: see [Install](../README.md#install).

## 0. Set up the workspace (once per repo, about 5 minutes)

```text
/re-setup
```

Answer up to eight short questions (each has a recommended default). You get:

```text
requirements/
  README.md        process facets, which work products you keep, ID scheme, Definition of Ready
  schema.json      IDs, attributes, enums, lint and trace settings
  glossary.md      empty term table
  requirements.csv header: ID,Type,Text,Source,Priority,Status,Rationale
```

Commit it. Every other skill reads `schema.json`; if you skip this step they fall back to the defaults and say so.

## 1. Scope: draw the boundary before you elicit

```text
/system-context  loyalty-points service
```

You get `requirements/context.md`: a Mermaid context diagram, a table of external actors, systems and interfaces, and the grey zones written as open decisions (`D-01: is the points-expiry batch job in scope?`). Take the open decisions to whoever owns scope **before** writing requirements for those areas.

Optional the first time: `/stakeholder-map` (who to ask, who is missing) and `source-inventory` (which documents and systems to mine).

## 2. Elicit: ask the questions that change the design

Paste the ticket you are about to implement and ask for questions:

```text
Before we build LOY-118 ("show points after purchase"), what do we need to clarify?
```

The `clarifying-questions` skill starts (or name it explicitly). It returns at most seven prioritized questions, each with a recommended answer, grouped by boundary, functional, quality and constraint. Answer them, or forward them to the product owner. Answers are recorded as requirements with the person and date as the source, in `requirements/requirements.csv`, and the Q&A is kept in `requirements/elicitation/questions-<topic>.md`.

Working on legacy or migration code? Ask the agent to mine it: the `artifact-mining` skill extracts candidate requirements with `file:line` sources into `requirements/candidates.csv`, each marked keep / drop / confirm.

## 3. Specify: one testable sentence per requirement

- Prose and candidates → requirements: `requirement-phrasing` (EARS: `WHEN ..., the system shall ...`).
- Stories → `/user-story-refiner`: INVEST check, Given/When/Then acceptance criteria including an unwanted-behavior case, vertical slices.
- Quality and constraints (the requirements elicitation under-collects) → `/quality-requirements`: an ISO 25010 walkthrough that produces measurable requirements (metric, target, condition, method) and tags architecture drivers.

Rule throughout: an unknown number is `TBD` plus an open question, never a guess.

## 4. Validate: catch defects while they cost minutes

```bash
re-lint check            # or: python3 .claude/skills/requirement-linter/scripts/lint_requirements.py
```

The linter is deterministic: weak words, universal quantifiers, passive voice without an actor, incomplete EARS conditions, missing obligation verbs, duplicate IDs, missing attributes. Fix errors with `requirement-phrasing`.

Then review the set as a whole:

```text
/requirements-review requirements/requirements.csv
```

You get `requirements/reviews/review-<date>.md`: findings with criterion, severity and a proposed fix, from three perspectives (user, architect, tester). Detection and correction stay separate: accept or reject each finding, then apply the fixes in a second pass.

Finally `testability-check` gives every requirement a verification method, a measurable acceptance criterion and a first test idea (`requirements/verification.csv`).

## 5. Trace: prove coverage from IDs you already write

Cite requirement IDs as you build:

```text
git commit -m "feat(loyalty): show updated balance after posting (R-023)"
def test_r_023_balance_visible_after_posting(): ...
```

Then:

```bash
re-lint trace build && re-lint trace gaps
```

`requirements/trace/trace.md` shows coverage and gaps: requirements without tests, tests that cite retired IDs, agreed requirements with no implementation reference. Run it nightly or as a release gate (see [CI](#ci)).

## 6. When something changes

```text
/change-impact Raise the minimum redemption from 500 to 300 points
```

The skill follows the trace links to the impacted requirements, tests and code, sizes the change, drafts `requirements/changes/CR-001-*.md` for whoever holds change authority, and updates the affected requirements only after the decision.

## CI

Add the linter to pull requests touching `requirements/` (copy [`docs/ci/requirements-lint.yml`](ci/requirements-lint.yml)):

```yaml
- uses: renzrollon/hairspring@v0.1.0
  with:
    fail-on: error
    changed-only: origin/${{ github.base_ref }}
```

## Which skill when

| You have... | Use |
| --- | --- |
| A vague ticket you are about to implement | `clarifying-questions` |
| A PRD, transcript or chat full of requirement-ish sentences | `requirement-classifier`, then `requirement-phrasing` |
| A user story or epic for refinement | `/user-story-refiner` |
| "It must be fast / secure / scalable" | `/quality-requirements` |
| Legacy code, runbooks, support tickets | `artifact-mining` |
| A new project or service | `/re-setup`, `/system-context`, `/stakeholder-map` |
| A PR that changes `requirements/` | `requirement-linter`, `/requirements-review` |
| Two requirements that cannot both be true | `conflict-detector`, then `/conflict-to-decision` |
| An auditor asking "which tests cover R-044?" | `traceability-matrix` |
| A change request | `/change-impact` |
| A backlog to rank | `/prioritization` |
| Coding agents that should implement from the requirements | `/to-openspec` |
| Requirements that must live in Jira / GitHub Issues / Azure DevOps | `/issue-sync` |
| A customer on DOORS or Polarion | `/reqif-bridge` |

The full catalogue with every skill's work product is in [`docs/catalogue.md`](catalogue.md); how the skills feed each other is in [`docs/pipeline.md`](pipeline.md).
