# Syncing through a tracker integration, or by hand

Use this when `scripts/issue_sync.py` cannot run (no Python, no network for scripts, Jira Data Center) but your agent has a tracker integration the user already connected, for example an MCP server or a built-in connector for GitHub, Jira or Azure DevOps. The integration holds the credentials; you never see or handle a token.

Every rule in `sync-rules.md` still applies: one issue per ID, the same title and body block, the same field ownership, plan before apply, never delete.

## Push

1. **Plan locally.** If Python runs, `python3 <skill-dir>/scripts/issue_sync.py plan --tracker <tracker>` still works (no network). Otherwise build the plan by hand: select rows as in step 3 of `SKILL.md`, write each title (`<ID>: <Title>`) and each body from `assets/issue-body.md`.
2. **Resolve matches.** With the integration's search or list operation, look in the target repository or project for issues whose title starts with `<ID>: `. Found: `update` (record the key). Not found: `create`. Found more than one: `conflict`, do not touch either.
3. **Show the plan** in the shape of `assets/plan.md` and wait for an explicit yes.
4. **Apply.** For `create`: create the issue with the title and body. For `update`: read the current body, replace only the text between `<!-- re-skills:begin -->` and `<!-- re-skills:end -->`, write it back, and update the title. For lifecycle closes: add a comment with the reason; close on GitHub as "not planned"; on Jira and Azure DevOps ask the user to move the card. Never call a delete operation.
5. **Record references.** Show the `Links` additions (`jira:LOY-81`) as a diff, then write them to `requirements.csv` after the user agrees.

## Pull

1. For each row with a tracker reference (or a title match), read the issue's status with the integration.
2. Map it through `schema.json` → `issues.status_map` and classify it with the pull guard rules in `sync-rules.md`.
3. Show the proposed `Status` changes and the conflicts. After the user agrees, change only the `Status` cells of the `update` rows.

## Without any integration

- **Push:** produce the plan table and one Markdown file per issue (title on the first line, then the body block) for the user to paste. Ask them for the issue keys afterwards and record them in `Links`.
- **Pull:** ask the user for a board export (CSV with issue key, summary and status). Match rows by the `<ID>: ` title prefix or the key in `Links`, then apply the guard rules exactly as above.
