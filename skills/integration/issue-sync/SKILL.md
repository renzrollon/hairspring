---
name: issue-sync
description: >-
  Syncs requirements/requirements.csv with GitHub Issues, Jira or Azure DevOps in both directions:
  push creates or updates one issue per requirement, with the R-ID in the title and the text,
  attributes and trace links in a managed block of the body; pull refreshes the Status column from
  the board. Dry run first: plan shows every create, update, close and status change, and nothing
  is written to the tracker or the register without --apply after you review it. Never deletes
  issues, never prints tokens. Started explicitly with /issue-sync. Use when someone says "push
  these requirements to Jira", "create GitHub issues for the agreed requirements", "sync status from
  the board", "refresh requirement status from Azure DevOps", or when an agreed set needs tickets.
  Not for handing a spec to a coding agent (to-openspec), for ReqIF exchange with DOORS or Polarion
  (reqif-bridge), or for refining stories before they become tickets (user-story-refiner).
license: MIT
compatibility: Python 3.9+ for scripts/issue_sync.py; network access and tracker credentials for push and pull (the gh CLI for GitHub). A manual procedure works without them.
disable-model-invocation: true
argument-hint: "[plan|push|pull] --tracker github|jira|ado [--ids R-001,R-002]"
metadata:
  stage: integration
  invocation: user
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §7.1"
  inputs-from: "requirement-phrasing, user-story-refiner, testability-check, traceability-matrix"
  outputs-to: "traceability-matrix, baseline, change-impact"
  work-product: "Tracker issues (one per R-ID) and the Status column of requirements/requirements.csv"
  version: "0.1.0"
---

# Issue sync

Teams plan work in a tracker and keep requirements in the register. When the two drift, nobody knows which version of a requirement is being built or whether it shipped. This skill keeps exactly one issue per requirement and splits ownership so the two sides never overwrite each other: the register owns the text and attributes, the tracker owns the workflow status, and nothing is ever deleted on either side. The work products are the issues and a refreshed `Status` column, each change shown as a plan before it is applied.

## When not to use

- Handing a set to a coding agent as a spec: `to-openspec`. Exchanging with DOORS, Polarion or Jama: `reqif-bridge`.
- Stories without acceptance criteria or not yet split: suggest `/user-story-refiner` first; tickets copy whatever quality they are given.
- The discussion in an issue changed what an agreed requirement says: that is a change request; suggest `/change-impact`, then change the register and push again. Edits inside the managed block are overwritten on the next push.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` | yes | `requirement-phrasing` |
| `requirements/schema.json` → `issues.status_map`, `lifecycle` | no (defaults apply) | `re-setup`, `attribute-schema` |
| Tracker access: `gh auth` (GitHub); `JIRA_*` or `ADO_*` environment variables | for `push` and `pull` | the user, see `references/credentials.md` |
| Trace context for the body: `sources.csv`, `stories/*.md` (acceptance criteria), `decisions/`, `trace/trace.csv` | no | `source-inventory`, `user-story-refiner`, `conflict-to-decision`, `traceability-matrix` |

## Outputs

| File or system | Shape | Consumed by |
| --- | --- | --- |
| One tracker issue per requirement, titled `<ID>: <Title or first 80 characters of Text>` | body block `assets/issue-body.md` | the team, `traceability-matrix` |
| `requirements/requirements.csv`: `Status` (pull) and the tracker reference in `Links` (push) | schema columns | `traceability-matrix`, `baseline`, `change-impact` |
| The sync plan shown before every `--apply` | `assets/plan.md` | the user |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the defaults; say so), `requirements.csv` and, for the body, `sources.csv`, `stories/*.md`, `decisions/` and `trace/trace.csv` if they exist. Ask which tracker (`github`, `jira`, `ado`) if the user did not say. For GitHub the target is the repository of the current git remote unless `GH_REPO=owner/repo` is set.
2. **Check credentials without showing them.** Follow `references/credentials.md`: `gh auth status` for GitHub, a set/missing test for each `JIRA_*` or `ADO_*` variable. Never print, log, paste or write a token anywhere, and never use `gh auth token` or `--show-token`. If a user pastes a token into the chat, do not repeat it and tell them to revoke it. Missing credentials stop `push` and `pull`; `plan` still works because it needs no network.
3. **Select.** `push` without `--ids` takes rows with `Status` `agreed`, `implemented` or `verified`, plus rows already linked to an issue. `draft` and `proposed` rows go only when the user names them in `--ids`. Rows with `withdrawn`, `rejected` or `deferred` status never get a new issue; if linked, their issue is closed or flagged (see `references/sync-rules.md`).
4. **Plan.** Run `python3 <skill-dir>/scripts/issue_sync.py plan --tracker <tracker> [--ids <IDs>]` (or `re-lint issues plan ...`). Show the table in the shape of `assets/plan.md` and explain each action in one line. `create-or-match` means push will search the tracker for an issue titled `<ID>: ` first and update it rather than create a duplicate.
5. **Push after review.** Ask "Apply this plan?" and wait for an explicit yes. Then run `python3 <skill-dir>/scripts/issue_sync.py push --tracker <tracker> --ids <the IDs in the plan> --apply`, passing the plan's IDs so nothing outside the reviewed plan is written. To see how `create-or-match` rows resolve before deciding, run the same command without `--apply` first: it reads the tracker but writes nothing. Report the issue keys created and updated.
6. **Pull after review.** Run `python3 <skill-dir>/scripts/issue_sync.py pull --tracker <tracker>` (dry run). Show every proposed `Status` change and every conflict, using the guard rules in `references/sync-rules.md`. Run it again with `--apply` only after the user approves; `--apply` writes only the `update` rows. Conflicts go to their owner (a requirement becomes `agreed` only through a named person); never resolve one by editing the tracker or the register yourself.
7. **Report.** List issues created, updated and closed; `Status` changes written; conflicts still open, each with an owner role; issues reported as orphans or missing. Recommend the next step.

No Python, or an agent with its own tracker integration (for example an MCP server for GitHub or Jira): follow `references/tracker-integration.md`, which applies the same plan-then-apply rules by hand.

## Quality checks

- [ ] A plan or dry run was shown and the user approved it before any `--apply`; the `--apply` call used exactly the plan's IDs.
- [ ] No token value appears in the output, in a file, in an issue body or in the chat.
- [ ] No issue was deleted; issues of withdrawn, rejected or deferred requirements were closed or flagged with a comment.
- [ ] Every issue title starts with `<ID>: `; every body has one managed block between `<!-- re-skills:begin -->` and `<!-- re-skills:end -->`, and text outside it is untouched.
- [ ] `requirements.csv` changed only in `Status` (pull) and tracker references in `Links` (push); each status change is an allowed lifecycle transition, and none set `agreed` without a named person.
- [ ] Every conflict is listed with an owner role instead of being resolved by a guess.

## Hand-offs

- **Next:** `traceability-matrix` to refresh coverage now that issues and status exist (agreed requirements without implementation show up as gaps); suggest `/baseline` when a pull marks a release's requirements `implemented` or `verified`.
- **Feeds back to:** `requirement-phrasing` when an issue discussion shows the requirement text is wrong (change the register, then push); suggest `/change-impact` when that requirement is already `agreed`; `testability-check` when a pull is blocked from `verified` for lack of evidence.

## Non-interactive mode

Run `plan` and `pull` without `--apply` only, and put their output in the job log or the final message. Never pass `--apply` in a run where no person reviewed the plan in the same session. A scheduled job may report drift (a non-empty pull plan) and fail, so a person runs the sync.

## References

- `references/sync-rules.md`: identity and title rules, the field ownership (conflict) rule, the status mapping both ways, the pull guard rules, and how each tracker renders the body markers. Read it before step 5 and step 6.
- `references/credentials.md`: per-tracker setup with least-privilege token scopes, and how to check credentials without printing them. Read it at step 2.
- `references/tracker-integration.md`: syncing through an agent's tracker integration, or by hand, when the script cannot run.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: a loyalty-points push plan for Jira, its JSON, an issue body, and a pull a week later.
