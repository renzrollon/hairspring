# Tracker credentials

**Checked:** 2026-11-03. Token screens and scope names change; if a step below no longer matches what you see, follow the tracker's own documentation and keep the same principle: the narrowest scope, one project, a short expiry.

## Rules

1. **Least privilege.** `plan` needs no credentials. `pull` needs read access to issues. `push` needs read and write access to issues in one repository or project. Nothing else (no admin, no delete, no other projects).
2. **One token per purpose and place.** A personal token on your machine; a separate CI secret for pipelines. Prefer a service account for shared automation.
3. **Short expiry.** Pick the shortest expiry your release rhythm allows and put the renewal date in your calendar.
4. **Environment only.** Load tokens into environment variables from a password manager or CI secret store. A local `.env` file is acceptable only if `.gitignore` lists it. Never commit a token, never put one in `requirements/`, an issue, a prompt, a log or a command line argument.
5. **Never print.** Check that a variable is set without showing it (below). If a token was printed or pasted anywhere, revoke it and create a new one.

Check presence without printing:

```bash
for v in JIRA_BASE_URL JIRA_EMAIL JIRA_API_TOKEN JIRA_PROJECT; do
  if [ -n "$(printenv "$v")" ]; then echo "$v set"; else echo "$v missing"; fi
done
```

```powershell
foreach ($v in "ADO_ORG_URL","ADO_PROJECT","ADO_PAT") { if ([Environment]::GetEnvironmentVariable($v)) { "$v set" } else { "$v missing" } }
```

## GitHub Issues (`--tracker github`)

The script uses the `gh` CLI, so `gh` must be installed and authenticated.

| Item | Setting |
| --- | --- |
| Quick start | `gh auth login` (browser flow). It grants broad default scopes; fine on a personal machine, too wide for automation |
| Least privilege | a fine-grained personal access token: Repository access "Only select repositories" (the one repo); Repository permissions "Issues: Read and write" for push, "Issues: Read-only" for pull; "Metadata: Read-only" (always required). Provide it as `GH_TOKEN` in the environment; `gh` uses it instead of the stored login |
| Organization with SAML SSO | authorize the token for the organization, or calls return 403/404 |
| Which repository | the current directory's git remote; set `GH_REPO=owner/repo` to target another |
| GitHub Actions | `env: GH_TOKEN: ${{ github.token }}` with job `permissions: issues: write` (push) or `issues: read` (pull) |
| Check | `gh auth status` (shows the account and scopes, masks the token). Never `gh auth token` and never `--show-token` |

## Jira Cloud (`--tracker jira`)

| Variable | Value |
| --- | --- |
| `JIRA_BASE_URL` | `https://<site>.atlassian.net` for a classic API token. For a scoped API token, use the API gateway: `https://api.atlassian.com/ex/jira/<cloudId>` (the cloud ID is shown at `https://<site>.atlassian.net/_edge/tenant_info`) |
| `JIRA_EMAIL` | the Atlassian account email of the token owner (a service account for shared use) |
| `JIRA_API_TOKEN` | the API token |
| `JIRA_PROJECT` | the project key, for example `LOY` |

- Create the token in the Atlassian account settings (Security, API tokens). Prefer "Create API token with scopes" and set an expiry. Scopes: `read:jira-work` for pull; add `write:jira-work` for push.
- The account needs these project permissions: Browse Projects (pull); Create Issues, Edit Issues, Add Comments (push).
- Scoped tokens and the gateway URL: as of November 2026 this is based on Atlassian community reports, not verified by us against Atlassian's reference. If a scoped token returns 401 on the site URL, switch `JIRA_BASE_URL` to the gateway form, or use a classic token while you check with your Jira admin.
- Jira Data Center and Server use personal access tokens with bearer authentication, which these variables do not cover. Use `references/tracker-integration.md` there.

## Azure DevOps (`--tracker ado`)

| Variable | Value |
| --- | --- |
| `ADO_ORG_URL` | `https://dev.azure.com/<organization>` |
| `ADO_PROJECT` | the project name |
| `ADO_PAT` | a personal access token |

- Create the token under User settings, Personal access tokens. Organization: only the target organization. Scopes: "Custom defined", then "Work Items: Read" for pull or "Work Items: Read & write" for push. Nothing else.
- Check the project's process (Agile, Scrum, Basic, CMMI) before the first sync: it decides the work item states and therefore `issues.status_map` (see `sync-rules.md`).
- Azure Pipelines: store the PAT as a secret variable and map it to `ADO_PAT` in the step's `env:`; secret variables are not exposed to scripts otherwise.
