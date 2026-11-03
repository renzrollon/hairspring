# Expected output: Jira push and pull (loyalty-points sample)

## Day 1: `plan --tracker jira`

Tracker: jira project LOY · Command: plan · Network: no · Generated: 2026-11-03T09:12:00Z

| ID | Action | Issue | Title | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| R-040 | create-or-match | - | R-040: Issue voucher on redemption request | agreed -> To Do | no tracker reference; matched by title before creating |
| R-041 | update | jira:LOY-77 | R-041: Validate voucher at checkout | agreed -> (tracker owns status) | title and managed block refreshed |
| R-042 | create-or-match | - | R-042: Reject redemption below minimum | agreed -> To Do | no tracker reference; matched by title before creating |
| R-043 | skip | - | R-043: Print remaining balance on receipt | draft | not selected: draft; name it in --ids to push it |
| R-044 | move-on-board | jira:LOY-78 | R-044: Send voucher code by SMS | withdrawn -> (manual) | comment with the reason (RDR-003); move the card to your closed column by hand |
| R-085 | create-or-match | - | R-085: Voucher validation response time at peak | agreed -> To Do | no tracker reference; matched by title before creating |
| R-100 | create-or-match | - | R-100: Use TillPoint voucher validation interface v2.1 | agreed -> To Do | no tracker reference; matched by title before creating |

Summary: 4 create-or-match, 1 update, 1 move-on-board, 1 skip (push)

Nothing has been written. To apply: `push --tracker jira --ids R-040,R-041,R-042,R-044,R-085,R-100 --apply`.

The body of each issue follows `assets/issue-body.md`; the one for R-040 is in `expected-issue-body.md`. On Jira the two marker lines are visible as plain text.

## Day 1: after "yes, apply"

> Created LOY-81 (R-040), LOY-82 (R-042), LOY-83 (R-085), LOY-84 (R-100). Updated LOY-77 (R-041). Commented on LOY-78 (R-044, withdrawn per RDR-003): please move it to your closed column, I did not change its status. Nothing was deleted. `requirements.csv`: `Links` now holds jira:LOY-81, jira:LOY-82, jira:LOY-83, jira:LOY-84; no other cell changed. Next: run `traceability-matrix` after the first commits that cite these IDs.

## Day 8: `pull --tracker jira` (dry run)

Tracker: jira project LOY · Command: pull dry run · Network: read-only · Generated: 2026-11-10T08:40:00Z

| ID | Action | Issue | Title | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| R-040 | unchanged | jira:LOY-81 | R-040: Issue voucher on redemption request | agreed -> In Progress (agreed) | |
| R-041 | update | jira:LOY-77 | R-041: Validate voucher at checkout | agreed -> Done (implemented) | written with --apply |
| R-042 | update | jira:LOY-82 | R-042: Reject redemption below minimum | agreed -> Done (implemented) | written with --apply |
| R-044 | conflict-lifecycle | jira:LOY-78 | R-044: Send voucher code by SMS | withdrawn -> In Progress | withdrawn on 2026-10-31 (RDR-003) but the card is active; owner: SH-01 Mei Tan |
| R-085 | unmapped | jira:LOY-83 | R-085: Voucher validation response time at peak | agreed -> In Review | "In Review" is not in issues.status_map; add it with attribute-schema |
| R-100 | unchanged | jira:LOY-84 | R-100: Use TillPoint voucher validation interface v2.1 | agreed -> To Do (agreed) | |

Summary: 2 update, 2 unchanged, 2 not written (pull)

Nothing has been written. To apply: `pull --tracker jira --apply`.

## Day 8: after "apply"

> `requirements.csv`: R-041 and R-042 changed from `agreed` to `implemented`; no other cell changed. Open: R-044 is withdrawn but LOY-78 is In Progress: ask Mei Tan (SH-01) whether the work stops or the decision RDR-003 is revisited. R-085: decide what "In Review" means for a requirement (likely `agreed`) and add it to `issues.status_map`. Next: suggest `/baseline` once the release's requirements are implemented; `testability-check` before anything moves to `verified`.
