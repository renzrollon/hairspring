# Input: push the voucher requirements to Jira, then refresh status (loyalty-points sample)

Day 1, 2026-11-03. The tech lead, Wei Jie Chua (SH-08), types:

> /issue-sync push --tracker jira

Workspace: `input/requirements/requirements.csv` (7 rows) and the acceptance criteria in `input/requirements/stories/voucher-redemption.md`. No `schema.json`, so the default `issues.status_map` applies. R-041 was pushed by hand last week as `LOY-77`; the withdrawn R-044 has an old card `LOY-78`.

Credentials check (values never shown):

```text
JIRA_BASE_URL set
JIRA_EMAIL set
JIRA_API_TOKEN set
JIRA_PROJECT set   (project key LOY)
```

Commands, in order:

```bash
python3 <skill-dir>/scripts/issue_sync.py plan --tracker jira
# user reviews the plan and answers "yes, apply"
python3 <skill-dir>/scripts/issue_sync.py push --tracker jira --ids R-040,R-041,R-042,R-085,R-100 --apply
```

Day 8, 2026-11-10. The board has moved on. Wei Jie types:

> /issue-sync pull --tracker jira

```bash
python3 <skill-dir>/scripts/issue_sync.py pull --tracker jira
# user reviews the status changes and answers "apply"
python3 <skill-dir>/scripts/issue_sync.py pull --tracker jira --apply
```

Board on day 8: LOY-81 (R-040) In Progress, LOY-77 (R-041) Done, LOY-82 (R-042) Done, LOY-78 (R-044) In Progress, LOY-83 (R-085) In Review, LOY-84 (R-100) To Do.

Expected output: `expected-output.md` (both plans and the final messages), `expected-plan.json` (the `plan` JSON), `expected-issue-body.md` (the body of LOY-81).
