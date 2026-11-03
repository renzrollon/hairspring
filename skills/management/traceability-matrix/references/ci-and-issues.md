# Running the trace in CI and turning gaps into issues

## Two modes

| Mode | When | Command | Fails the job? |
| --- | --- | --- | --- |
| Nightly report | `schedule` and manual runs | `re-lint trace build` then `re-lint trace gaps --format github` | No. Gaps show up as annotations, and the trace files are uploaded as an artifact |
| Release gate | Tag push, release branch, or a required check on release PRs | `re-lint trace build` then `re-lint trace gaps --format github --fail-on-gaps` | Yes, exit `1` on any gap |

`assets/trace-gate.yml` does both in one workflow: tags fail on gaps, and everything else only reports. Copy it to `.github/workflows/requirements-trace.yml`, then adjust the cron time and the tag pattern.

Check these before you commit the workflow:

- `actions/checkout` with `fetch-depth: 0`. A shallow clone hides older commit messages, so implementation links disappear.
- Every place the repo keeps code or tests is covered by `schema.json` → `trace.code_globs` / `trace.test_globs`. Otherwise the gate fails on gaps that are not real.
- The gate runs after the branch is merged or tagged, not on every feature PR. New requirements start without tests, so a per-PR gate would block normal work.

## Variant: the composite action

When the repo already uses the re-skills lint action on pull requests, a release workflow can reuse it:

```yaml
on:
  push:
    tags: ["v*"]
jobs:
  requirements:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: renzrollon/hairspring@v0.1.0
        with:
          fail-on: error
          trace-gaps: "true"   # runs `re-lint trace build` and `re-lint trace gaps --fail-on-gaps`
```

The action always fails on gaps when `trace-gaps` is `"true"`, so use it for the release gate only, not for a nightly report.

## Other CI systems

The commands are the same anywhere Python 3.9+ runs:

```sh
pip install "git+https://github.com/renzrollon/hairspring@v0.1.0#subdirectory=packages/re-lint"
re-lint trace build
re-lint trace gaps --format text --fail-on-gaps
```

Without `pip`, run the vendored copy from the skill folder: `python3 <skill-dir>/scripts/trace_matrix.py build`.

## From gaps to issues

Draft one issue per gap, never one per run. Use the same shape every time, so a re-run does not create duplicates:

| Field | Value |
| --- | --- |
| Title | `<ID>: <gap>`, e.g. `R-003: no test (trace gap)`, `R-022: withdrawn but still tested` |
| Body | The gap kind, the evidence (`path:line`), the requirement text, and a link to `requirements/trace/trace.md` |
| Labels | `trace-gap`, plus the owner area if the team uses one |
| Owner role | From the triage table in `references/trace-format.md` |

How to file them:

- Recommend `/issue-sync` when the requirement itself should become or update an issue. It keeps the requirement ID in the title and the trace links in the issue body.
- For gap-only issues, give the user the table, or a `gaps.json` excerpt for their tracker's import. This skill does not call trackers itself.
- Before you draft an issue, search the open issues for the same `<ID>:` title prefix. Comment on an existing issue instead of opening a duplicate.
