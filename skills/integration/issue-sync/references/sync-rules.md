# Sync rules

Two-way sync only works if each fact has one owner. These rules decide who wins for every field, and what `plan`, `push` and `pull` do with each row. The vendored `scripts/issue_sync.py` implements them; when you sync by hand or through a tracker integration, apply them yourself.

## Identity

- **One issue per requirement ID.** Primary match: the issue title starts with `<ID>: ` (the exact ID, a colon, a space). Secondary match: the tracker reference in the row's `Links` column.
- **Title:** `<ID>: <Title>`, or `<ID>: ` plus the first 80 characters of `Text` when the row has no `Title`.
- **Tracker reference in `Links`** (space-separated): `github:<owner>/<repo>#<number>`, `jira:<ISSUE-KEY>`, `ado:<work-item-id>`. `push --apply` records it. When you push by hand, add it after the push (show the diff first).
- `plan` has no network, so a row without a tracker reference is `create-or-match`: `push` searches for a title starting with `<ID>: ` and updates that issue if it exists. It never creates a second issue for the same ID.

## Field ownership (the conflict rule)

| Field | Wins | `push` | `pull` |
| --- | --- | --- | --- |
| Title, `Text`, `Type`, `Priority`, `Source`, `Rationale`, other attributes, trace links | `requirements.csv` | writes the title and replaces the managed block | never copies them back; a title or block edited in the tracker is reported as `text-drift` |
| Workflow status (`agreed` → `implemented` → `verified`) | tracker | sets nothing after create; a new issue starts in the tracker's initial state | writes `Status` through `issues.status_map`, guarded by the table below |
| Lifecycle decisions (`withdrawn`, `rejected`, `deferred`) | `requirements.csv` | never pushed; a linked issue is listed as `move-on-board` so a person closes it with the reason (on GitHub: close as "not planned"); no workflow transition is guessed | never overwrites these statuses; reports `conflict-lifecycle` |
| Text outside the managed block, comments, assignee, labels, sprint, estimates | tracker | never touched | never read |
| Existence | nobody deletes | never deletes an issue | never deletes a row; an issue titled with an ID missing from the register is reported as `orphan-issue` |

## Status mapping

`schema.json` → `issues.status_map` maps each tracker status to a requirement status. Defaults:

| Tracker | Tracker status → requirement status |
| --- | --- |
| `github` | `open` → `agreed`; `closed` → `implemented` |
| `jira` | `To Do` → `agreed`; `In Progress` → `agreed`; `Done` → `implemented` |
| `ado` | `New` → `agreed`; `Active` → `agreed`; `Resolved` → `implemented`; `Closed` → `verified` |

GitHub issues closed as "not planned" are looked up under the key `closed:not_planned`, which defaults to `rejected`; set it in `issues.status_map.github` to map them elsewhere (for example `"closed:not_planned": "deferred"`). They never fall back to `closed`, which means implemented.

The Azure DevOps defaults follow the Agile process. Scrum (`New`, `Approved`, `Committed`, `Done`) and Basic (`To Do`, `Doing`, `Done`) projects, and Jira boards with extra columns (`In Review`), need their own entries: add them with `attribute-schema` or by editing `issues.status_map`. A status missing from the map is reported as `unmapped`, never guessed.

## Pull guard rules

For each linked row, `pull` maps the tracker status and classifies the result. Only `update` rows are written, and `pull` exits `1` when any row lands in another class that needs a person. When you pull by hand, apply this table yourself.

| Class | When | Example | Written |
| --- | --- | --- | --- |
| `update` | the mapped status differs and the move is an allowed transition in `schema.json` → `lifecycle` | `agreed` + Jira `Done` → `implemented`; `implemented` + GitHub reopened (`open`) → `agreed` | yes |
| `unchanged` | the mapped status equals the current one | `agreed` + `In Progress` | no |
| `needs-person` | the mapped status is `agreed` and the row is `draft` or `proposed` | `proposed` + `To Do` | no: `agreed` needs a named person in `Source`, `Owner` or a decision record |
| `needs-evidence` | the mapped status is `verified` and neither `Links` nor `trace/trace.csv` holds a test, inspection or demonstration for the ID | `implemented` + Azure DevOps `Closed` | no: run `testability-check` / `traceability-matrix` |
| `skip-coarse-map` | the move is not allowed, because the tracker map is coarser than the lifecycle | `verified` + GitHub `closed` → `implemented` | no |
| `conflict` | the move is not allowed and work went ahead anyway | `draft` + Jira `Done` | no: owner is the product owner |
| `conflict-lifecycle` | the row is `withdrawn`, `rejected` or `deferred` and the issue is still active | `withdrawn` + `In Progress` | no |
| `unmapped` | the tracker status is not in `issues.status_map` | Jira `In Review` | no |
| `missing-issue` | the tracker reference is broken, or the title no longer starts with the ID | issue moved or renamed | no |

## Managed body block

The script writes the block in `assets/issue-body.md` between `<!-- re-skills:begin -->` and `<!-- re-skills:end -->` and replaces only what is between them on each push.

| Tracker | How the markers survive |
| --- | --- |
| GitHub | Markdown body; the markers are HTML comments, invisible and preserved |
| Jira Cloud | the description format (Atlassian Document Format or wiki markup) has no HTML comments, so the markers are stored as plain text lines and are visible. Do not edit those two lines |
| Azure DevOps | `System.Description` is HTML; the markers are HTML comments, which the web editor may drop when someone edits the description |

If the markers are missing or appear twice, `push` leaves that issue's body alone and reports `markers-missing`. Restore the block by hand (copy it from the plan) and push again.

## Issue type

A new issue gets the type given with `--issue-type TYPE`: by default `Story` in Jira and `User Story` in Azure DevOps. CMMI projects in Azure DevOps have a `Requirement` type; Agile ones use `User Story`. Check with the board owner before the first push.
