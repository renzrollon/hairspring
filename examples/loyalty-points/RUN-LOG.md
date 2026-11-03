# Run log: loyalty-points sample loop, 2026-11-03

One full pass of the re-skills loop by an engineer new to requirements engineering, following each `SKILL.md` literally. All paths are relative to `examples/loyalty-points/` unless they start with `skills/`, `packages/` or `tools/`. Commands ran from the repository root with `PYTHONPATH=packages/re-lint/src`. Friction cites the skill file as it stood at the end of the run (several skills changed during the run; the newer version was used, see "Skills that changed during the run").

Scenario script (fictional, not BRIEF facts): (1) the facet choices for `re-setup` came from the run instructions; (2) the change request in step 14 ("Lower the minimum redemption from 500 to 300 points", requested by SH-07 Priya Raman on 2026-11-03); (3) in step 15, Mei Tan (SH-01) agreed R-013, R-014, R-015, R-038 and R-039 with priority `must` on 2026-11-03. Nothing else was decided or answered by anyone: every other answer is `TBD` with an open question and an owner.

Severity used below: **high** = the procedure produces a wrong or inconsistent result if followed literally; **medium** = an agent must guess or work around it; **low** = wording or convenience.

## 1. `re-setup`

| Field | Value |
| --- | --- |
| Input files | `BRIEF.md`; `skills/foundations/re-setup/assets/*` |
| Output files | `requirements/README.md`, `requirements/schema.json`, `requirements/requirements.csv` (header) |
| Commands | `python3 -m json.tool examples/loyalty-points/requirements/schema.json`; `re-lint ids check examples/loyalty-points/requirements/requirements.csv`; `python3 skills/_primitives/re-ids/scripts/re_ids.py next --kind <kind> --no-git --workspace examples/loyalty-points/requirements` |
| Result | Non-interactive: facets iterative, explorative, customer-specific, criticality PDPA + DRP-2024, all `assumed`; change authority product owner Mei Tan (to be confirmed); `Verification` column added; 10-item DoR; trace settings `src/**`, `tests/**`, `scan_git_log: false` |
| Friction | **high:** the README template's ID-scheme table (`skills/foundations/re-setup/assets/README.md:42`, filled as in `skills/foundations/re-setup/examples/expected-output.md:62-72`) puts concrete example IDs (`R-012`, `R-031.AC2`, `CAN-041`, `RDR-007`, `D-01`, `CR-014`, `F-05`) into the workspace; `re_ids.py next` counts them as in use, so the first IDs became R-032, CAN-042, RDR-008, CR-015 and D-02. Workaround: wrote the Example column as `R-nnn`, `CAN-nnn`, ... and said why in the README. **medium:** step 8 (`SKILL.md:89`) never mentions the `trace` key, and the README template has no place for it; nothing tells a team how to configure a workspace that is not at the git root. Recorded the trace settings and the reason in Setup history. **medium:** with a nested workspace every `re-lint` call needs `--workspace`; `trace build --repo <dir>` alone resolves the workspace to `<git root>/requirements` (tooling, `reqio.find_workspace`). **medium:** `re-ids` step 1 (`skills/_primitives/re-ids/SKILL.md:47`) does not mention `--no-git`; inside a monorepo `ids next` reads the enclosing repo's commit messages. Used `--no-git` on every call. **low:** step 8 says to create the header from `re-templates/assets/requirements.csv` (7 columns), while `process-facets.md` §6 moves `Verification` into `attributes.columns`; used the schema's 8 columns. **low:** BRIEF.md:79-90 asks for ID ranges per area, which `re-ids` rule 1 (opaque IDs) and `ids next` (highest + 1) cannot honor; followed `re-ids`. |

## 2. `system-context`

| Field | Value |
| --- | --- |
| Input files | `BRIEF.md` |
| Output files | `requirements/context.md` |
| Commands | `re_ids.py next --kind open-decision --count 4 --no-git --workspace ...` |
| Result | 12 external elements, 17 data flows, Mermaid diagram (syntax checked by hand, no renderer installed), D-01 to D-04 open with options, recommendation and owner |
| Friction | **medium:** step 6 (`skills/scope/system-context/SKILL.md:69`) defines `confirmed` as "a person or a specification confirms it", and Non-interactive mode (`:92`) says "unless a specification or the user's notes confirm it": unclear whether a project brief counts. Treated BRIEF.md as the kick-off notes (`confirmed`). **low:** `file:line` sources in a nested example have no stated base; used paths relative to the example folder. **low:** the Owner column asks for the system owner; the brief gives stakeholder interests only, so most owners are `TBD`. |

## 3. `stakeholder-map` and `source-inventory`

| Field | Value |
| --- | --- |
| Input files | `BRIEF.md`, `requirements/context.md` |
| Output files | `requirements/stakeholders.md`, `requirements/sources.csv` |
| Commands | `re_ids.py next --kind stakeholder --count 4 ...`; `re_ids.py next --kind source --count 6 ...`; `re-lint ids check examples/loyalty-points/requirements/sources.csv` |
| Result | 13 stakeholders (SH-01 to SH-09 kept from the brief, SH-10 to SH-13 from the gap check), 5 plotted; 13 sources (S-08 to S-13 are the named stakeholders), S-14 added in step 8 |
| Friction | **medium:** `references/role-checklist.md:41` says a `yes` gap gets a row with Representative `TBD`, but the skill's own example marks "Owners of external systems" `yes` with an open question only; followed the example to stay compact. **medium:** source-inventory step 2 (`skills/scope/source-inventory/SKILL.md:56`) registers every stakeholder with a named representative, so the brief's S-01 to S-07 grew to S-13; did that. **medium:** the brief says interviews I-01 and I-02 took place, but `elicited` needs a work product in the workspace; kept `planned` with a note (S-06 became `elicited` later, once rows cited LOY-118). **low:** relevance rule (`references/technique-selection.md:53`) is silent for a stakeholder whose influence is `TBD`; used `medium`. **low:** stakeholder-map step 6 (`SKILL.md:63`) assumes new rows get fresh IDs; it does not say what to do when the roster already carries SH-IDs (kept them). **changed mid-run:** Technique tokens became hyphenated (`document-analysis`), matching `candidates.csv`; rewrote `sources.csv` as the coordinator asked. |

## 4. `glossary`

| Field | Value |
| --- | --- |
| Input files | `BRIEF.md`, `inputs/*` (created before this step, see below) |
| Output files | `requirements/glossary.md` |
| Commands | `python3 skills/foundations/glossary/scripts/mine_terms.py BRIEF.md inputs --format text --top 80`; the same with `--glossary requirements/glossary.md --only-new` |
| Result | 31 terms (2 `candidate`, 29 `proposed`), 9 findings (2 synonyms, 3 homonyms, 3 undefined, 1 rule in definition), 7 open questions |
| Friction | **medium:** step 3 (`skills/foundations/glossary/SKILL.md:57`) mines `README.md docs src requirements` by default; mining `requirements/` returns the skills' own vocabulary (grey zone, confirmed, row, Mermaid node IDs such as `lps`). Mined `BRIEF.md` and `inputs/` only. **medium:** step 8 (`:62`) expects `--only-new` to come back clean, but single-word candidates (`pending`, `redeem`, `reason`, `cust`) never match multi-word terms (`Pending points`, `Redemption`, `Reason code`) or identifiers listed in Synonyms, so the check always exits 1; reviewed the remaining candidates by hand and listed the dropped ones here: app, loyalty, service, data, system, number, store, sample, show, months, platform, support, vendor, END, ticket, name, nightly, receipt, team, programme, checkout. **low:** the loop runs `glossary` before `artifact-mining`, but the glossary needs the artifacts: the inputs (`inputs/legacy/sp_redeem_points.sql`, `inputs/support-tickets-excerpt.csv`, `inputs/prd-redeem-at-checkout.md`, `inputs/LOY-118.md`) were written first, as pre-existing sources. |

## 5. `artifact-mining`

| Field | Value |
| --- | --- |
| Input files | `inputs/legacy/sp_redeem_points.sql` (S-04, 39 lines), `inputs/support-tickets-excerpt.csv` (S-03, 12 tickets), `requirements/sources.csv`, `requirements/glossary.md` |
| Output files | `requirements/candidates.csv` |
| Commands | `re_ids.py next --kind candidate --count 19 ...`; `python3 skills/elicitation/artifact-mining/scripts/check_candidates.py requirements/candidates.csv --root .` (from `examples/loyalty-points`); a negative test with a wrong quote to confirm the checker bites |
| Result | 19 candidates: 4 keep, 2 drop (XMAS2018 rule, legacy `ADJ` type), 13 confirm; checker 0 errors; `Requirement` filled in step 8 |
| Friction | **medium:** the keep rule (`SKILL.md` disposition table) needs "a current, authoritative source"; the brief's business rules (BRIEF.md:58-63) are not attributed to a registered source, except expiry (S-01 draft). Treated BRIEF.md lines as authoritative and cited them in Reason. (During the run the rule was relaxed: a whole document labeled draft now backs `keep`.) **medium:** `references/candidates-columns.md:18` says a `confirm` candidate becomes a requirement only after its owner confirms, yet the conflict loop needs the disputed expiry rule as a requirement; phrased R-019 from S-01 instead and kept CAN-012 `confirm` with `Requirement` R-019. Neither `drop` ("covered by") nor `keep` fits that case. **low:** feedback counts ("212 of 1,240 tickets") assume the full export; counted within the excerpt and said so. |

## 6. `clarifying-questions` on LOY-118

| Field | Value |
| --- | --- |
| Input files | `inputs/LOY-118.md`, `requirements/glossary.md`, `requirements/context.md`, `requirements/candidates.csv` |
| Output files | `requirements/elicitation/questions-loy-118-points-after-purchase.md` |
| Commands | none (no script) |
| Result | Non-interactive: 6 topics already answered by the brief, 7 questions (2 blocking), 6 assumptions; no requirement rows appended in this step |
| Friction | **medium:** Non-interactive mode (`SKILL.md:80`) says "append no requirement rows", while the loop expects the answers to feed `requirement-phrasing`. Phrasing later wrote TBD rows from the ticket itself, and nothing says who updates *Becomes* to `R-nnn (open)` afterwards; updated it by hand in step 8. **low:** the solution in disguise ("Use Redis to cache balances") has no place in the questions file; put it under "Already answered" with a pointer to its need (question 6). |

## 7. `requirement-classifier`

| Field | Value |
| --- | --- |
| Input files | `inputs/prd-redeem-at-checkout.md` (written for the sample from the brief and LOY-118) |
| Output files | `requirements/classification.md` |
| Commands | none |
| Result | 15 statements: 7 F, 1 Q, 2 C, 1 solution, 3 facts, 1 unclear; 5 open questions |
| Friction | **medium:** routing (`references/concern-test.md:77`) sends F rows to `requirement-phrasing` "or `user-story-refiner` when the team writes stories"; with stories kept, both skills could write the same rule rows. Sent the business rules to phrasing and the epic to the story refiner, and the stories cite the rule IDs. **low:** splitting a PRD statement into two rows shifts the classification numbering against the PRD's; cited PRD lines in Source to keep them findable. |

## 8. `requirement-phrasing`, `/user-story-refiner`, `/quality-requirements`, `constraints-register`

| Field | Value |
| --- | --- |
| Input files | `requirements/candidates.csv` (keep rows), `inputs/LOY-118.md`, `requirements/classification.md`, `BRIEF.md`, `requirements/glossary.md` |
| Output files | `requirements/requirements.csv` (R-001 to R-037), `requirements/stories/redeem-points-at-checkout.md`, `requirements/quality-requirements.md`, `requirements/constraints.csv`; `requirements/sources.csv` (S-14 added by a `source-inventory` re-run) |
| Commands | `re_ids.py next --kind requirement --count <n> ...` per skill; `python3 skills/specification/requirement-phrasing/scripts/lint_requirements.py examples/loyalty-points/requirements/requirements.csv`; `re-lint check ... --only-ids <new IDs>`; `python3 skills/specification/user-story-refiner/scripts/check_stories.py examples/loyalty-points/requirements/stories/redeem-points-at-checkout.md --requirements examples/loyalty-points/requirements/requirements.csv` |
| Result | 23 phrased rows, 3 stories (7 + 3 + 2 acceptance criteria), 7 quality rows (all targets TBD), 1 function handed back ("auditable", R-034), 3 constraints (Kubernetes left out: no mandator); lint 0 errors and 0 warnings on every batch; `check_stories.py` 0 errors |
| Friction | **medium:** Priority: `clarifying-questions` step 7 and `requirement-phrasing` step 6 say `TBD` unless someone stated it, but phrasing's own example sets `should`/`must` from ticket wording. Used `should`/`must` only where the stakeholder's own words said so (LOY-118 "should", SH-02 "must"); 27 rows stay `TBD`. **medium:** `user-story-refiner` step 7 (`SKILL.md:81`) runs `testability-check` during refinement, while the loop runs it after review; deferred it, so the DoR item "has a verification method" fails for every story. **medium:** story Notes want constraint R-IDs, but `constraints-register` runs after the stories in the loop; cited S-02 and S-05 instead. **medium:** `constraints-register` step 3 (`SKILL.md:65`) writes no row without a named mandator; the brief names the Kubernetes platform only as SH-08's interest, so the run instructions' "Kubernetes platform" constraint became an open question, not a row. **low:** the ID allocator happily counts forward references: I mentioned R-027 and R-037 in the stories file before they existed and the next ID jumped to R-038; removed the references (nothing warns about a cited-but-unallocated ID). **low:** `constraints-register` step 5 puts the mandate in the columns, not the sentence; removed "for audit" from R-036. |

## 9. `conflict-detector` and `/conflict-to-decision`

| Field | Value |
| --- | --- |
| Input files | `requirements/requirements.csv`, `constraints.csv`, `quality-requirements.md`, `candidates.csv`, `classification.md`, `stakeholders.md` |
| Output files | `requirements/conflicts.md`, `requirements/decisions/RDR-001-points-expiry-period.md` |
| Commands | `re_ids.py next --kind conflict --count 2 ...`; `re_ids.py next --kind decision ...` |
| Result | CF-01 (expiry, interest, compromise or variants, decision matrix), CF-02 (retention vs PDPA, subject matter, variants or agreement); 7 "checked, not a conflict"; RDR-001 `proposed`, outcome "Pending: decision by Mei Tan (SH-01)", 5 options, criteria without weights; `requirements.csv` and `conflicts.md` unchanged as Non-interactive mode requires |
| Friction | **medium:** the five kinds (`SKILL.md:58`, `references/detection-checklist.md`) assume two requirement rows; CF-01 is one row (R-019) against a stakeholder position with no row (the skill's example invents an 18-month R-061). Used kind `contradiction` with the position quoted. **medium:** `conflict-to-decision` step 9 adds `RDR-nnn CF-nn` to `Links`, but `re-setup` never adds a `Links` column and the schema keeps it optional; logged a follow-up in RDR-001 (review finding F-25). **medium (found in step 13):** the RDR template (`references/rdr-format.md:24`, Constraints) cites other requirements by ID; the tracer reads every R-ID in `decisions/*.md` as `decided-by` (`skills/management/traceability-matrix/references/trace-format.md:12`), so the proposed RDR-001 "decides" R-020 and R-036 in `trace.csv`. Left as is and reported. |

## 10. `requirement-linter` and `/requirements-review`

| Field | Value |
| --- | --- |
| Input files | the whole workspace |
| Output files | `requirements/reviews/lint-2026-11-03-run1.txt`, `requirements/reviews/review-2026-11-03.md`, `requirements/reviews/lint-2026-11-03-run2.txt`; rows R-004, R-005, R-013, R-015, R-034 rewritten, R-038 and R-039 added |
| Commands | `python3 skills/validation/requirement-linter/scripts/lint_requirements.py examples/loyalty-points/requirements` (run 1 and run 2); `re-lint check examples/loyalty-points/requirements --format json`; `re-lint check ... --only-ids R-004,R-005,R-013,R-015,R-034,R-038,R-039` |
| Result | Lint run 1: exit 0, `0 errors, 0 warnings, 39 info in 40 rows (11 files)` (38 `open-tbd`, 1 `nominalization` on R-015). Review: `not ready`, 1 blocker, 17 major, 7 minor. Second pass (author's decisions): 6 accepted (5 fixed, F-13 partly), 1 rejected (F-21), 18 deferred to owners. Lint run 2: exit 0, `0 errors, 0 warnings, 40 info in 42 rows (11 files)`: the `nominalization` is gone, the two new rows add `Priority=TBD` infos |
| Friction | **medium:** review quality check (`skills/validation/requirements-review/SKILL.md:104`) wants each lint finding in exactly one F-nn, while step 7 (`:85`) merges only "the same location"; 27 `open-tbd` findings on Priority would be 27 findings. Merged them into one set-level finding (F-24) and said so. **medium:** step 5 (`:76`) prefers parallel subagents; none were available, so the passes ran sequentially and the header says so. **low:** `requirement-linter` writes no file (`skills/validation/requirement-linter/SKILL.md:51`) and the layout has no path for a saved lint report; saved both runs under `requirements/reviews/`, which `re-lint check` skips. **observation:** lint run 1 had nothing to fix because every emitting skill lints its own rows; the defects worth fixing came from the three reading perspectives. |

## 11. `testability-check`

| Field | Value |
| --- | --- |
| Input files | `requirements/requirements.csv`, `quality-requirements.md`, `constraints.csv`, `stories/redeem-points-at-checkout.md` |
| Output files | `requirements/verification.csv`; `Verification` column in `requirements.csv` |
| Commands | `re-lint check examples/loyalty-points/requirements` (no `register-drift`, no `invalid-enum`) |
| Result | 39 rows: 37 test, 1 analysis (R-030), 1 inspection (R-037); 24 `yes`, 14 `tbd`, 1 `no` (R-007); levels 7 unit, 23 integration, 7 e2e, 2 manual |
| Friction | none beyond the ordering noted in step 8 |

## 12. Implementation

| Field | Value |
| --- | --- |
| Input files | `requirements/requirements.csv`, `requirements/verification.csv`, `skills/management/traceability-matrix/references/citation-conventions.md` |
| Output files | `src/loyalty/__init__.py`, `earning.py`, `posting.py`, `redemption.py`; `tests/conftest.py`, `test_earning.py`, `test_posting.py`, `test_redemption.py` |
| Commands | `python3 -m pytest -q examples/loyalty-points/tests` |
| Result | 16 passed. R-015 and R-039 (voucher validation) deliberately not built or tested. Assumption: points that are not a multiple of 100 raise an error until stories Q2 is answered (most restrictive option) |
| Friction | none |

## 13. `traceability-matrix`

| Field | Value |
| --- | --- |
| Input files | the workspace, `src/`, `tests/` |
| Output files | `requirements/trace/trace.csv`, `trace.md`, `gaps.json` |
| Commands | `python3 skills/management/traceability-matrix/scripts/trace_matrix.py build --repo examples/loyalty-points --workspace examples/loyalty-points/requirements`; `trace_matrix.py gaps --workspace ...`; `trace_matrix.py gaps --workspace ... --status draft --only requirement-without-test` |
| Result | Run 1 (all draft): 39 requirements, 60 links, 8 with tests, 6 with code, 0 gaps; 29 untested drafts as informational. Final rebuild after step 15: 90 links (OpenSpec mentions added), 4 gaps: R-015 and R-039 without test and without implementation |
| Friction | **medium:** with every row `draft` the default gap report is empty, so a first loop shows "0 gaps" while 29 requirements have no test; the skill's triage calls drafts informational but the files never list them. Ran `gaps --status draft` and reported it here. **medium:** the `decided-by` overreach from step 9. **low:** the `trace.md` header shows the enclosing repo's commit, which does not contain the uncommitted register. |

## 14. `/change-impact`

| Field | Value |
| --- | --- |
| Input files | the request (scripted), `requirements/trace/trace.csv`, `requirements.csv`, `stories/`, `verification.csv`, `context.md`, `stakeholders.md`, `README.md` |
| Output files | `requirements/changes/CR-001-lower-minimum-redemption.md` |
| Commands | `python3 skills/management/change-impact/scripts/trace_matrix.py impact R-013 R-024 R-025 --workspace examples/loyalty-points/requirements --format md`; `re_ids.py next --kind change ...` |
| Result | 15 impact rows (trace, search, user), options 0/A/B, sizes M (proposed by the agent), risk medium, decision `pending` with Mei Tan (SH-01); `requirements.csv` unchanged |
| Friction | **high:** routing (`skills/management/change-impact/SKILL.md:72`, `references/impact-analysis.md:68`) uses the value `ccb`, but `re-setup` writes `change-control-board` (`skills/foundations/re-setup/references/process-facets.md:71`, `assets/README.md:20`); a linear or prescriptive team set up by `re-setup` lands in "any other value: ask". Not hit here (product owner). **medium:** applying an approved CR needs `Version` and `Links` (step 11), neither of which `re-setup` adds for an iterative team; noted in CR-001 section 9. **low:** `trace impact` cannot see acceptance criteria and `verification.csv` rows that copy the 500-point value; found them by search, as §1 of the reference says. |

## 15. `/to-openspec` and `/baseline`

| Field | Value |
| --- | --- |
| Input files | `requirements/requirements.csv`, `stories/`, `verification.csv`, `context.md` |
| Output files | `openspec/changes/add-voucher-redemption/` (`.openspec.yaml`, `proposal.md`, `specs/voucher-redemption/spec.md`, `tasks.md`); `requirements/baselines/v0.1-sample.json`; `Owner` column and the agreed status in `requirements.csv` |
| Commands | dry run into the scratchpad: `to_openspec.py add-voucher-redemption --workspace ...` (refused: nothing agreed) and `--ids ... --allow-draft` (gate G2 blocks `Priority=TBD`); then `re-lint check ... --only-ids R-013,R-014,R-015,R-038,R-039 --fail-on info`; `python3 skills/integration/to-openspec/scripts/to_openspec.py add-voucher-redemption --ids R-013 R-014 R-015 R-038 R-039 --skip-blocked --date 2026-11-03 --workspace examples/loyalty-points/requirements --out examples/loyalty-points`; `python3 skills/management/baseline/scripts/baseline.py create v0.1-sample --workspace examples/loyalty-points/requirements --message "..."`; `baseline.py diff v0.1-sample working ...` |
| Result | 5 requirements handed off (manual checklist passes; the `openspec` CLI is not installed); 7 not-agreed redemption rows listed under "Not in this change"; baseline 39 entries, `git_commit` 14fa842 (the previous checkpoint), no tag; diff against working: 0 changes |
| Friction | **high:** no skill owns "a named person agrees a requirement": `re-ids` (`references/id-scheme.md:78`) needs the person in `Source`, `Owner` or a decision record, but the default schema has no `Owner` column and no skill adds one. Added `Owner` as an optional column for the five rows. **medium:** gate G2 (`skills/integration/to-openspec/SKILL.md:68`, `references/handoff-gate.md`) treats `Priority=TBD` like a TBD in the text, and Non-interactive mode (`:104`) forbids `--allow-tbd`; an agreement without a priority would hand off nothing, so the scripted agreement includes the priority. **medium:** without a `Title` column the generated headings, bullets and tasks are the first words of the sentence ("R-013 IF a member requests a redemption of fewer"), `references/openspec-format.md:112`; rewrote only the Purpose and the capability bullet, as step 6 allows. **medium:** baseline pre-check (`skills/management/baseline/SKILL.md:69`) asks to commit first; this run may not commit, so the manifest points at the previous checkpoint and its message says so. |

## Skills that changed during the run

Checked with `git diff f032491 -- skills/<stage>/<skill>/{SKILL.md,assets,references}` after step 15. Most changes were placeholder formatting (`<x>` to `{x}`). Changes that mattered and what was done:

| Skill | Change | Action |
| --- | --- | --- |
| `source-inventory` | Technique tokens hyphenated; Category `elicitation record` added | `requirements/sources.csv` rewritten (coordinator message) |
| `re-setup` | Story template became the Given/When/Then bullet form of `user-story-refiner` | README Story template section updated; Setup history row added |
| `artifact-mining` | A document labeled draft as a whole can back `keep` | Dispositions unchanged (they cite BRIEF.md); friction in step 5 kept for the brief case |
| `requirement-phrasing`, `to-openspec`, `quality-requirements`, `constraints-register` | Read after the update (set-aside rules, `--skip-blocked`, `IF ... THEN` for fault tolerance, mandate dates) | Already followed |

## Final checks

| Check | Result |
| --- | --- |
| `PYTHONPATH=packages/re-lint/src python3 -m re_lint check examples/loyalty-points/requirements/requirements.csv --fail-on error` | exit 0: `0 errors, 0 warnings, 35 info in 39 rows (1 file)` |
| `python3 -m pytest -q examples/loyalty-points/tests` | 16 passed |
| `python3 tools/validate_catalogue.py` | 38 skills checked: 38 ok, 0 errors, 0 warnings |
| `python3 tools/validate_catalogue.py --check-docs` | generated docs are up to date |
| `python3 -m pytest -q packages/re-lint/tests tests` | 547 passed |
| `re-lint ids check --workspace examples/loyalty-points/requirements` | no findings in 89 rows |
| `check_candidates.py`, `check_stories.py` | 0 errors |
| `trace_matrix.py gaps` | 4 gaps (R-015, R-039), as intended |
