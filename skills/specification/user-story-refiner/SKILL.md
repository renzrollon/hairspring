---
name: user-story-refiner
description: >-
  Rewrites or splits user stories into the Cohn template (As a <role>, I want <goal>, so that
  <benefit>), proposes vertical slices, runs an INVEST pass/fail table, writes Given/When/Then
  acceptance criteria that always include an unwanted-behavior case, and checks the Definition of
  Ready. Leaves requirements/stories/<epic-slug>.md (paste-ready Markdown for Jira or GitHub
  Issues) and one Type F row per story in requirements/requirements.csv. Started explicitly with
  /user-story-refiner. Use when someone says "refine this story", "split this epic", "write
  acceptance criteria", "is this story ready", or brings a ticket, epic or backlog item to
  refinement or sprint planning. Not for turning prose into shall-statements (use
  requirement-phrasing), verification methods for a whole set (testability-check), response-time
  or availability targets (quality-requirements), or pushing issues to a tracker (issue-sync).
license: MIT
compatibility: Python 3.9+ optional for scripts/check_stories.py; works without it.
disable-model-invocation: true
argument-hint: "[story, epic, ticket text or file]"
metadata:
  stage: specification
  invocation: user
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §3.3.1.2"
  inputs-from: "clarifying-questions, artifact-mining, requirement-classifier, elicitation-workshop, stakeholder-map, glossary"
  outputs-to: "testability-check, requirement-linter, requirements-review, prioritization, issue-sync, to-openspec, spec-assembler"
  work-product: "requirements/stories/<epic-slug>.md"
  version: "0.1.0"
---

# User story refiner

A story that reaches a sprint without a real benefit, testable acceptance criteria or a sensible size comes back as rework. This skill puts each story into the Cohn template, splits big ones into vertical slices, writes Given/When/Then acceptance criteria (always with at least one unwanted-behavior case), and records INVEST and Definition of Ready results. Stories are requirements here: each one gets an R-ID and a Type F row in `requirements.csv`; its acceptance criteria (`R-nnn.AC1..n`) and review tables live in `requirements/stories/<epic-slug>.md`, in Markdown that pastes straight into Jira or GitHub Issues.

## When not to use

- Prose, a PRD or interview notes that should become shall-statements: `requirement-phrasing`.
- Verification methods and measurable criteria for a whole requirement set: `testability-check`.
- Quality targets (response time, availability, security levels) for the system: suggest `/quality-requirements`.
- Creating or updating issues in the tracker: suggest `/issue-sync` after this skill.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Story, epic or ticket text (pasted, a file, or a tracker export) | yes | the user, `clarifying-questions`, `elicitation-workshop`, `artifact-mining` |
| `requirements/requirements.csv` | no | every emitting skill |
| `requirements/schema.json` (`definition_of_ready`, ID scheme) | no (defaults apply) | `re-setup` |
| `requirements/glossary.md`, `requirements/stakeholders.md` (role names) | no | `glossary`, `stakeholder-map` |
| `requirements/stories/<epic-slug>.md` from an earlier run | no | `user-story-refiner` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/stories/<epic-slug>.md` | `assets/stories.md` | `testability-check`, `requirements-review`, `issue-sync`, `to-openspec`, `spec-assembler` |
| `requirements/requirements.csv` (one Type F row per story) | `assets/requirements.csv` | `requirement-linter`, `prioritization`, `traceability-matrix` |

## Procedure

1. **Read the workspace.** Locate `requirements/` (or the `workspace` named in `requirements/schema.json`). Read `schema.json` for the ID scheme and `definition_of_ready`; if it is missing, use the default columns `ID,Type,Text,Source,Priority,Status,Rationale` and the default Definition of Ready rows in `assets/stories.md`, and say so in the stories file header. Read `glossary.md` and `stakeholders.md` for role names, `requirements.csv` for existing stories and the highest ID, and `stories/<epic-slug>.md` if this epic was refined before (update it in place; the slug is the epic title in kebab-case).
2. **Take the input apart.** List every role, goal, benefit, business rule, data variant, interface and existing acceptance criterion, each with its source (ticket key, source ID, or person and date). Move what is not a story into the *Not stories* table:

   | Statement | It is | Do |
   | --- | --- | --- |
   | A quality target ("fast", "secure", "within 2 s") | quality requirement | Open question; suggest `/quality-requirements`. Do not hide it in an acceptance criterion |
   | A mandate ("must use the TillPoint spec", "PDPA says") | constraint | Run `constraints-register` if installed (else list it); name it under *Constraints* in the story's Notes |
   | A solution or task ("add a Postgres table", "As a developer I want an endpoint") | design decision or task | Not a story. Ask for the user need behind it; route the decision to the architect as an ADR candidate |
   | A fact (`will`, present tense) | context | Not a story; keep it as context |

3. **Ask what changes the stories.** Follow `re-interview` in batch mode: one numbered batch of at most 7 questions about missing benefits, unknown roles, rule values, the team's sizing rule and scope boundaries. Skip anything the input or workspace answers. For target values, recommend a reference (a vendor limit, a baseline, a policy), never a number you made up. In non-interactive mode, ask nothing: write `TBD` and log the open question with an owner.
4. **Rewrite to the Cohn template.** One role, one goal, one benefit per story:

   | Part | Rule | Wrong | Right |
   | --- | --- | --- | --- |
   | Role | A named role from `stakeholders.md` or the glossary | "As a user", "As the system", "As a developer" | "As a member", "As a cashier" |
   | Goal | One capability in the role's words; no UI widget, technology or algorithm | "I want a button that calls the voucher API" | "I want to spend 500 of my posted points as an SGD 5 voucher at the till" |
   | Benefit | Why the role wants it, different from the goal | "so that I can redeem points" (restates the goal) | "so that my points reduce what I pay" |

   Unknown benefit: write `so that TBD` and add an open question; never invent one. A goal joined by "and" or "or" is a split signal (step 5).
5. **Split into vertical slices.** Read `references/splitting-patterns.md` when *Small* fails, the goal joins two goals, or the input is an epic. Each slice must reach a user-observable outcome on its own; reject slices by layer (API, database, screen). Put the thinnest end-to-end path first. When an unknown blocks estimating, propose a spike (a time-boxed question, no R-ID). Show the *Slicing* table and get the user's confirmation before writing.
6. **Write acceptance criteria.** Read `references/acceptance-criteria.md` before the first one. Per story: the happy path, each business rule, and **at least one unwanted-behavior case** (invalid input, rule violation, external system failure, duplicate or concurrent action, missing permission). One `When` per criterion, an observable `Then`, concrete values from the input or the business rules, `TBD` for unknown values. Tag each criterion `_(happy path)_`, `_(alternative)_` or `_(unwanted behavior)_`.
7. **Flag what cannot be tested.** For each criterion decide: *testable*; *blocked* (a `TBD` value, testable once an open question is answered: add `**Flag:** blocked by Qn`); or *untestable* (subjective or unobservable outcome such as "easy", "nice", "without help": add `**Flag:** untestable: <reason>; routed to testability-check`). Run the `testability-check` skill on the story IDs if it is installed; it sets `Verification` and proposes measurable forms. If it is not installed, keep the flags and list them in the final message. Never replace a subjective word with a number nobody gave you.
8. **Run INVEST.** Fill the table for every story with `pass` or `fail` and one line of evidence:

   | Criterion | Pass when | Fail when | Fix |
   | --- | --- | --- | --- |
   | Independent | It can be built, tested and released without another unbuilt story | It needs another unbuilt story first | Order it after that story and name it under *Depends on*; a later slice that depends only on the first slice fails here and that is normal |
   | Negotiable | The goal states a need and leaves the how to the team | The goal prescribes a UI element, technology or algorithm | Move the solution to Notes or an ADR candidate |
   | Valuable | The benefit names a gain for the role or the business, different from the goal | No benefit, a restated goal, or a layer as the role | Ask for the benefit; rewrite as a vertical slice |
   | Estimable | No open question changes what is built | An open question changes the scope | Ask, or split out a spike |
   | Small | It fits one iteration by the team's sizing rule; without a rule, no pattern in `references/splitting-patterns.md` yields two slices that each deliver value | Too big by the team's rule, the goal joins two goals, or a pattern yields two valuable slices | Split (step 5) |
   | Testable | Every criterion is testable or blocked | A criterion is untestable | Flag it and route it (step 7) |

9. **Allocate IDs and write the rows.** Use `re-ids` (or `re-lint ids next --kind requirement --count <n>`) for new story IDs; acceptance criteria are `<story ID>.AC1`, `.AC2`, ... in order and are never renumbered (mark a removed one `(withdrawn)`). Each story gets one `requirements.csv` row: `Type=F`, `Text` = the story sentence exactly as in the stories file, `Source`, `Priority` (from the input, else `TBD`), `Status=draft`, and a one-sentence `Rationale` (where the story came from and why; name the split pattern for slices). Fill `Title`, `Links` or `Tags` only if those columns already exist. Rewriting an existing story keeps its ID (increment `Version` if present; an `agreed` story moves back to `proposed`). Splitting an existing story creates new IDs and sets the original to `withdrawn` with `Rationale` "Split into R-..."; if the original is `agreed` or later, propose this and let its owner decide.
10. **Check the Definition of Ready.** Evaluate every item of `definition_of_ready` for every story as `pass`, `fail` or `n/a`, with evidence. For the default items: attributes complete in the `requirements.csv` row; linter clean (step 12); `Verification` set and no untestable criterion; every open question for the story answered or `deferred` with an owner; *Depends on* and *Constraints* filled (or `none`). A story is `ready` only when no item fails. Judge team-specific items from the files; if they cannot be checked, mark `fail` and say who must confirm.
11. **Show, then write.** Show the *Summary*, the *Slicing* table and one full story, and get confirmation. Then write `requirements/stories/<epic-slug>.md` from `assets/stories.md` (same sections, same order, `none` in empty ones) and append the rows to `requirements.csv` in schema column order. In non-interactive mode, write directly.
12. **Check.** Run the `requirement-linter` skill on the new story IDs (or `re-lint check --only-ids <IDs>`); story-form rows skip the obligation-verb rules, so only wording and attribute findings matter. Run `python3 <skill-dir>/scripts/check_stories.py requirements/stories/<epic-slug>.md --requirements requirements/requirements.csv` and fix every error. Without Python, walk the quality checks below by hand.
13. **Report.** End with: story IDs written, the *Summary* table, flagged criteria, open questions with owners, and the next steps from *Hand-offs*. Tell the user that each section between `<!-- paste-start -->` and `<!-- paste-end -->` pastes into a tracker as is (`references/tracker-paste.md`).

## Quality checks

- [ ] Every story sentence reads `As a <role>, I want <goal>, so that <benefit>.` with a named role (not user, system or developer) and a benefit that differs from the goal or is `TBD` with an open question.
- [ ] Every story has at least one criterion tagged `_(unwanted behavior)_`; every criterion has Given, exactly one When, and an observable Then.
- [ ] Criterion IDs are `<story ID>.ACn`, unique, never renumbered.
- [ ] No invented values: every unknown is `TBD` with an open question and owner; untestable criteria are flagged and routed to `testability-check`.
- [ ] Every story has an INVEST table (six rows, `pass`/`fail`, evidence) and a Definition of Ready table using `schema.json` items or the defaults.
- [ ] No slice is a technical layer; spikes have no R-ID.
- [ ] `requirements.csv` has one Type F row per story whose `Text` equals the story sentence; existing rows are unchanged except as confirmed; no ID reused.
- [ ] Paste blocks contain only headings-free Markdown (bold, bullets), no tables.
- [ ] `scripts/check_stories.py` exits 0.

## Hand-offs

- **Next:** `testability-check` for flagged criteria and the `Verification` attribute; `requirement-linter` on the new rows; suggest `/issue-sync` to push the stories to Jira, GitHub or Azure DevOps, `/prioritization` to rank them, and `/requirements-review` before sprint planning.
- **Feeds back to:** `clarifying-questions` with the open questions; `glossary` with new roles or terms; `constraints-register` with mandates found; suggest `/quality-requirements` for quality targets from *Not stories*.

## Non-interactive mode

Ask nothing. Write the stories file and the rows with `Status=draft`, `TBD` for every unknown, and the full open-question list. Propose slices but do not withdraw an existing story; list the proposed withdrawal in the final message instead.

## References

- `references/splitting-patterns.md`: the seven splitting patterns with loyalty-points examples, slice rules and anti-patterns. Read it at step 5.
- `references/acceptance-criteria.md`: Given/When/Then rules, the unwanted-behavior catalogue, testable/blocked/untestable examples. Read it before step 6.
- `references/tracker-paste.md`: pasting into GitHub Issues, Jira Cloud and Jira Data Center. Read it when the user names a tracker.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: epic LOY-210 from the loyalty-points sample and the stories file and rows it becomes.
