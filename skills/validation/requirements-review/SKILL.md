---
name: requirements-review
description: >-
  Reviews a requirement set, or only the rows a PR changed, against the quality criteria for single
  requirements (adequate, necessary, unambiguous, complete, understandable, verifiable) and for the
  set (consistent, non-redundant, complete, modifiable, traceable, conformant). Runs the linter
  first, grades adequacy and understandability first, then reads from three perspectives (user,
  architect, tester), in parallel subagents where possible. Writes requirements/reviews/review-YYYY-
  MM-DD.md: findings F-nn with criterion, severity (blocker / major / minor), location and proposed
  fix, plus a verdict. Fixes are applied only after the author accepts them. Started explicitly by
  the user: /requirements-review. Use when someone asks to "review these requirements", on a PR
  touching requirements/, or before agreeing a set, a design review, sprint planning or a baseline.
  Not for wording-only checks (requirement-linter), stakeholder disagreements (conflict-detector),
  or verification methods (testability-check).
license: MIT
compatibility: Python 3.9+ optional for scripts/lint_requirements.py; works without it.
disable-model-invocation: true
argument-hint: "[file, R-IDs, or a git base ref such as origin/main for a diff review]"
metadata:
  stage: validation
  invocation: user
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §3.8, §4.4"
  inputs-from: "requirement-phrasing, user-story-refiner, quality-requirements, constraints-register, requirement-linter, system-context, glossary"
  outputs-to: "requirement-phrasing, testability-check, conflict-detector, clarifying-questions, glossary, baseline"
  work-product: "requirements/reviews/review-YYYY-MM-DD.md"
  version: "0.1.0"
---

# Requirements review

A review finds the defects that make a requirement useless or a set misleading, while fixing them still costs minutes. This skill spends script time on everything a script can catch, then human-style judgment on the rest: first whether each requirement is adequate and understandable (without those, nothing else matters), then a reading from the user's, the architect's and the tester's point of view, then checks of the set as a whole. It ends with a findings file and a verdict. Detection and correction are separate: no requirement changes until its author has accepted the finding.

## When not to use

- You only want the deterministic wording and attribute checks: `requirement-linter` (this skill runs it as step 3).
- Two stakeholders want different things: `conflict-detector`, then suggest `/conflict-to-decision`.
- You need verification methods and acceptance criteria for every row: `testability-check`.
- The rows are user stories that need splitting and acceptance criteria: suggest `/user-story-refiner` first, then review.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv`, Markdown requirement tables (`stories/*.md`), or the IDs or base ref the user names | yes | `requirement-phrasing`, `user-story-refiner`, `quality-requirements`, `constraints-register` |
| `requirements/glossary.md`, `requirements/context.md` | no | `glossary`, `system-context` |
| `requirements/conflicts.md`, `requirements/verification.csv`, earlier `requirements/reviews/*.md` | no | `conflict-detector`, `testability-check`, this skill |
| `requirements/schema.json` | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/reviews/review-YYYY-MM-DD.md` | `assets/review.md` | the author, `requirement-phrasing`, `testability-check`, `conflict-detector`, `baseline` |
| `requirements/requirements.csv`, only in the correction step and only for accepted findings | schema columns | `requirement-linter`, `traceability-matrix` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the defaults, and say so in the review header), `glossary.md`, `context.md`, `requirements.csv`, `stories/*.md`, `conflicts.md` and the latest review (open findings from it are not repeated as new; cite their F-ID and review date instead).

2. **Fix the scope.** One of:
   - **Full set** (default): every row except Status `withdrawn` and `rejected`.
   - **IDs**: the rows the user names.
   - **Diff**: run `git diff <base> -- requirements/` (base from the user or the PR; ask if unknown). Scope = IDs of added or changed rows in `requirements.csv` and in Markdown requirement tables. A deleted row is itself a finding (traceable: rows are withdrawn, never deleted). Without git, ask the user for the IDs.

   Single-requirement criteria apply to scoped rows only. Set-level checks compare the scoped rows with the whole register.

3. **Lint first.** Run `python3 <skill-dir>/scripts/lint_requirements.py --format json`, adding `--only-ids <IDs>` for an ID scope or `--changed-only <base>` for a diff scope (or run the `requirement-linter` skill, or `re-lint check` with the same flags). Put the command, the exit code and the counts in the review header, in the linter's summary-line form (`re-lint: 2 errors, 0 warnings, 1 info in 11 rows (1 file)`; JSON gives them as `summary`, `rows_checked` and `files`). Turn every lint finding into a candidate finding: `Found by: lint:<rule>`, criterion and starting severity from the map in `references/quality-criteria.md`. Do not re-judge what the linter already reported. Without Python, use the `requirement-linter` skill's manual fallback and write `Lint: manual` in the header.

4. **Grade adequacy and understandability first.** For each scoped row, using its Source, Rationale, the glossary and the context:
   - **Adequate:** does it state what the stakeholders actually need, at the level the next decision needs? A solution in disguise without a mandate fails here.
   - **Understandable:** would the people who agree, build and test it understand it the same way, in glossary terms?

   A row with a blocker or major finding on either criterion gets `—` for its other criteria in "Requirement grades": polishing a requirement that is wrong or unreadable wastes the author's time. Read `references/quality-criteria.md` for the checks.

5. **Read from three perspectives.** Each perspective has a self-contained brief: `references/perspective-user.md`, `references/perspective-architect.md`, `references/perspective-tester.md`.
   - If you can run subagents, run the three in parallel. Give each only its brief and the scoped rows (plus `glossary.md` and `context.md` if they exist). Do not give them the lint results, your grades or the other briefs.
   - Otherwise run them one after another. Before each pass, re-read only that brief and the rows, and do not look at earlier passes' findings until all three are done.

   Collect each perspective's table of candidate findings. Write in the header which way they ran.

6. **Check the set.** For the six set criteria (consistent, non-redundant, complete, modifiable, traceable, conformant), apply the checks in `references/quality-criteria.md`, comparing scoped rows with the whole register, `context.md` (every interface and actor covered) and `conflicts.md`. A contradiction between stakeholders' positions is a finding whose proposed fix is "register with `conflict-detector`"; do not resolve it here.

7. **Merge, grade and number.**
   - Merge candidates about the same location and the same underlying problem into one finding; list every source in "Found by".
   - Give each finding exactly one criterion (the one whose failure causes the most harm) and a severity by the rules in `references/quality-criteria.md`.
   - Order by severity (blocker, major, minor), then by location. Number `F-01`, `F-02`, ... (unique within this file; `re-ids` kind `finding`).
   - Proposed fix: a concrete rewrite (EARS or story form) or a concrete action ("ask SH-08 whether ..."). Unknown values are `TBD`, with the question in "Open questions" and an owner. Never invent a value.

8. **Decide the verdict.** `not ready` if any blocker; `ready after fixes` if any major; otherwise `ready`.

9. **Write the review.** Fill `assets/review.md` and save it as `requirements/reviews/review-YYYY-MM-DD.md` (if that file exists, add `-2`, `-3`). Every Resolution is `open`. Change nothing else. In the reply, show the verdict, the severity counts and the blocker and major findings, then ask the author which findings they accept.

10. **Correct, only after acceptance.** This is a separate step and needs the author's decision on each finding (accept, reject with a reason, defer):
    1. Record each decision in the "Correction log" (who, date) and set Resolution.
    2. Apply accepted fixes with `requirement-phrasing`: same ID, `Version` + 1 if the column exists, an `agreed` row returns to `proposed` when its text changes. New rows get IDs from `re-ids`. Withdrawals set Status; no row is deleted.
    3. Fixes that wait on an open question keep the `TBD` and stay `accepted` until answered.
    4. Run the linter on the changed IDs and set Resolution `fixed` for each fix that lints clean.

11. **Offer a re-review.** Suggest the user reruns `/requirements-review <base>` on the diff of the fixes.

## Quality checks

- [ ] The linter ran before any judgment; its command, exit code and summary line are in the header; each lint finding appears in exactly one F-nn.
- [ ] Every scoped requirement has a row in "Requirement grades", with adequacy and understandability graded for all of them.
- [ ] Three perspectives ran independently (parallel, or sequential with fresh passes), and the header says which.
- [ ] Every finding has an F-ID, one criterion from the twelve, a severity of blocker, major or minor, a location (ID, and file:line where known) and a proposed fix with no invented value.
- [ ] The verdict follows the rule in step 8.
- [ ] Before the author's decision, no file other than the review was changed. Every applied fix has a Correction log line naming who accepted it.
- [ ] In a diff review, single-requirement findings cite only scoped rows, and set findings cite at least one scoped row.

## Hand-offs

- **Next:** `requirement-phrasing` applies accepted fixes (step 10); `testability-check` for findings on `verifiable`; `conflict-detector` for consistency findings between stakeholders, then suggest `/conflict-to-decision`.
- **Feeds back to:** `clarifying-questions` with the open questions; `glossary` for terms that are undefined or used in two senses; `requirement-linter` when a judgment finding should become a rule (suggest it as a `lint.extra_weak_words` entry).

## Non-interactive mode

Run steps 1 to 9 only. Write the review file, leave every requirement unchanged, and end with the verdict, the counts, the path of the review file and the open questions. Correction always waits for the author.

## Pitfalls

- Reporting fifty minor findings and burying the one blocker. Order by severity and put the blockers in the reply.
- Rewriting a requirement into what the reviewer would like. The fix must keep the stakeholder's meaning; when the meaning is unclear, ask.
- Treating every TBD as a defect. A TBD with an owner and a question is honest; count it under `complete` only when it blocks the next decision.
- Letting the perspectives see each other's results first: they converge and the point of three readings is lost.

## References

- `references/quality-criteria.md`: the twelve criteria with checks, severity rules and the lint-rule map. Read it at steps 3, 4, 6 and 7.
- `references/perspective-user.md`, `references/perspective-architect.md`, `references/perspective-tester.md`: the three self-contained briefs. Pass each one, alone, to its pass at step 5.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: a PR adding the redemption requirements R-040 to R-047, and the review it produces.
