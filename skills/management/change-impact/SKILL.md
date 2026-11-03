---
name: change-impact
description: >-
  Scopes a change request: follows trace links from the affected requirement IDs (re-lint trace
  impact) to impacted requirements, decisions, code, tests and interfaces; sizes effort and risk
  relatively (T-shirt sizes with assumptions, never invented hours); drafts the request for the
  repo's change authority (Change Control Board, or a backlog item for the product owner); records
  the decision; only then updates the requirements (Version +1, status rule, CR link). Writes
  requirements/changes/CR-nnn-{slug}.md; without a trace matrix it searches the repo and states
  the lower coverage. Started explicitly with /change-impact. Use when a stakeholder asks to
  change agreed behavior ("raise the limit", "expire after 18 months"), a contract or regulation
  changes, or someone asks "what does this change touch?". Not for a defect where code misses an
  agreed requirement (fix the code), new scope with no requirement yet (clarifying-questions), or
  choosing between conflicting positions (conflict-to-decision).
license: MIT
compatibility: Python 3.9+ optional for scripts/trace_matrix.py; works without it.
disable-model-invocation: true
argument-hint: "[change request text, ticket or file]"
metadata:
  stage: management
  invocation: user
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §6.7"
  inputs-from: "traceability-matrix, re-setup, baseline, conflict-to-decision"
  outputs-to: "requirement-phrasing, requirement-linter, traceability-matrix, conflict-detector, issue-sync, baseline"
  work-product: "requirements/changes/CR-nnn-<slug>.md"
  version: "0.1.0"
---

# Change impact

Changes to agreed requirements are normal. Uncontrolled changes are what hurt: a limit raised in the code but not in the terms, a test still checking the old value, a vendor nobody told. This skill turns a change request into a file a decision-maker can act on. The file records what changes, what it touches (found by following trace links, not from memory), how big and risky it is compared with other work, who decides, what they decided, and which requirement rows changed as a result.

## When not to use

- The code does not do what an agreed requirement says. That is a defect: fix the code and keep the requirement.
- The scope is new and no existing requirement changes: use `clarifying-questions`, then `requirement-phrasing`.
- Two stakeholders want opposite things and someone has to choose. Register the conflict with `conflict-detector` and suggest `/conflict-to-decision`, then come back here with the decision.
- You want the coverage gaps of the whole repository: use `traceability-matrix`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| The change request (text, ticket, email, meeting note) with requester and date | yes | stakeholders |
| `requirements/requirements.csv` | yes | `requirement-phrasing` |
| `requirements/trace/trace.csv` | no (fallback: repository search) | `traceability-matrix` |
| `requirements/schema.json` → `process`, and `requirements/README.md` | no (default change authority: product owner) | `re-setup` |
| `conflicts.md`, `decisions/`, `stakeholders.md`, `context.md` under `requirements/` | no | `conflict-detector`, `conflict-to-decision`, `stakeholder-map`, `system-context` |
| Earlier `requirements/changes/CR-*.md` | no | this skill |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/changes/CR-nnn-<slug>.md` | `assets/change-request.md` | the change authority, `baseline`, `traceability-matrix`, `issue-sync` |
| `requirements/requirements.csv`: affected rows, changed only after an approved decision | schema columns, plus `Version` and `Links` | `requirement-linter`, `traceability-matrix`, `baseline` |

## Procedure

1. **Read the workspace.** Locate `requirements/` (or the `workspace` in `schema.json`). Read `schema.json` (`process.change_authority`, `process.lifecycle`, ID settings), the process section of `README.md`, `requirements.csv`, `glossary.md`, and the existing `changes/`. If an open CR already covers this request, update that CR instead of creating a new one. If `schema.json` is missing, use the defaults (the change authority is the product owner) and say so in the CR.
2. **Pin down the request.** Quote the request verbatim, with the requester and the date. Fill the before/after table. Use `re-interview` (one question at a time) to ask only what you cannot find: what changes from what to what, why, who asked, by when. Anything still unknown becomes `TBD` plus an open question. If you cannot say what changes, stop and ask; do not analyze a guess. If the request describes a defect, say so and stop.
3. **Seed the impact set.** Collect the requirements the change touches directly. Start with the IDs named in the request, then search the `Text` column of `requirements.csv` for the request's terms, values and glossary synonyms. Show the seed list and confirm it. Note which requirements must be added and which withdrawn.
4. **Follow the trace links.**
   - If `requirements/trace/trace.csv` exists, run `re-lint trace impact <IDs> --format md` (or `python3 <skill-dir>/scripts/trace_matrix.py impact <IDs> --format md`). If code or tests changed after the trace was built, rebuild it first with `re-lint trace build` (or `trace_matrix.py build`), or run the `traceability-matrix` skill. The trace is a generated file, so rebuilding it is safe.
   - If there is no trace matrix, or Python is unavailable, search the repository as described in `references/impact-analysis.md` §2. Mark each confirmed hit `search`, and write "search only (lower coverage)" in the CR header.
   - Add what links cannot show (`references/impact-analysis.md` §1): work products that cite the IDs, interfaces and external parties from `context.md`, configuration and copy texts, sources that must change (terms, contracts), and stakeholders to inform.
   - Give every impact row its evidence: a `trace.csv` link, a `path:line`, or "user".
5. **Check for conflicts.** Compare the change with other requirements, `conflicts.md`, `decisions/`, and stakeholder positions stated in `Rationale` or `stakeholders.md`. If the change contradicts any of them, run `conflict-detector` to register the conflict, put the CF ID in the CR, and recommend `/conflict-to-decision` before the decision is taken. Do not resolve the conflict yourself.
6. **Write the options.** Always include option 0 (no change: reject or defer, and what that costs) and option A (the request as asked). Add option B when a smaller or phased alternative exists. For each option, list the requirement changes and the other work-product changes.
7. **Size effort and risk.** Sizes are relative only. Use the T-shirt scale and the risk factors in `references/impact-analysis.md` §3–4, and write the assumptions behind each size. Never write hours, days, story points or money unless the team gave them; if they did, quote the figure with its source. Ask the team to confirm the sizes. Until they do, mark each size "proposed by the agent".
8. **Route to the change authority.** Apply the routing table in `references/impact-analysis.md` §5. `product-owner` gets a backlog item; `ccb` gets a request to the Change Control Board; any other value means you ask who decides. If `README.md` and `schema.json` disagree, ask. Put the draft in section 7 of the CR, and the decider's name, not just the role, in the header.
9. **Write the CR.** Allocate the ID with `re-ids`, kind `change` (or run `re-lint ids next --kind change`; without either, take the highest `CR-` number under `requirements/` plus one). Write `requirements/changes/CR-nnn-<slug>.md` from `assets/change-request.md` with Status `draft`. Show it, then save it. Do not touch `requirements.csv` in this step. Set Status `submitted` when the user says the request went to the change authority.
10. **Record the decision.** A decision needs three things: the option (or rejected / deferred), the decider, and the date. If any of them is missing, ask. The decider must match the change authority; if they do not, flag the mismatch and ask. Fill section 8 and set Status to `approved`, `rejected` or `deferred`. A rejected or deferred CR changes no requirement.
11. **Apply an approved change.** Only after step 10 has recorded `approved`:
    - Change each affected row as the option says, following the table below. Show the before/after diff, then write.
    - `Version`: add 1 for every text change. An empty cell counts as 1. If the column is missing, add `Version` (an optional schema column) and set `2` on the changed rows.
    - `Links`: append `CR-nnn` (space-separated).
    - New requirements get IDs from `re-ids`, with `Source` set to `CR-nnn`. Withdrawn requirements get Status `withdrawn` and a `Rationale` that cites the CR. Never delete a row.
    - Run `requirement-linter` (or `re-lint check --only-ids <IDs>`) on the changed rows, then rebuild the trace (`trace_matrix.py build`). List the code and tests from the impact set that must now change.
    - Fill section 9 with what was written, and set the CR Status to `applied`.

| Status before | Approved with final wording | Approved, wording still open |
| --- | --- | --- |
| `draft`, `proposed` | unchanged | unchanged |
| `agreed` | `agreed` | `proposed` |
| `implemented`, `verified` | `agreed` (to be re-implemented and re-verified) | `proposed` |
| `deferred` | `proposed` | `proposed` |
| `withdrawn`, `rejected` | Do not edit; add a new requirement | Do not edit; add a new requirement |

## Quality checks

- [ ] The CR names the requester and the date, and has a before/after for every changed statement. Unknowns are `TBD` with an open question.
- [ ] Every impact row has evidence. The header says whether coverage comes from the trace or from search only.
- [ ] Effort and risk are relative (T-shirt size; high/medium/low with the factors named) and state their assumptions. No hours, days or money appear unless the team supplied them.
- [ ] The route matches `process.change_authority`, and the decider is a named person or board.
- [ ] `requirements.csv` is unchanged unless the CR records an approved decision. After one, every changed row has `Version` +1, the status from the table, and `CR-nnn` in `Links`.
- [ ] Conflicts are registered with a CF ID and left for the decision-makers to resolve.
- [ ] The linter reports no errors on the changed rows.

## Hand-offs

- **Next:** suggest `/conflict-to-decision` when step 5 found a conflict. Use `requirement-phrasing` for new or rewritten text and `traceability-matrix` after applying. Suggest `/issue-sync` to create the backlog item, and `/baseline` to cut a baseline once the change ships.
- **Feeds back to:** `traceability-matrix` when the impact set came from search only. `clarifying-questions` with the open questions. Suggest `/prioritization` when the backlog item must be ranked against other work.

## Non-interactive mode

Write the CR as `draft`. Mark the sizes "proposed by the agent" and make every unknown `TBD` with an open question. Record a decision, and apply it, only when the input names the option, the decider and the date. Otherwise leave section 8 `pending` and `requirements.csv` untouched. End with the CR path, the impact summary and the open questions.

## Pitfalls

- Changing the requirement first and writing the CR afterwards. The CR then documents a done deal, and the decision is no longer real.
- Sizing from the code alone. Terms, vendor interfaces, data migration and communication are often the expensive part.
- Treating a search hit as a trace link. A search for `500` finds unrelated code, so confirm every hit.

## References

- `references/impact-analysis.md`: turning trace output into impact rows, the fallback search, the T-shirt scale, risk factors, change-authority routing, and CR statuses. Read it at steps 4, 7 and 8.
- `references/ireb-anchor.md`: the handbook section and glossary terms this skill applies.
- `examples/`: a loyalty-points change request (lower the minimum redemption), built from the `traceability-matrix` example's `trace.csv`.
