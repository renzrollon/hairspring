# Trace files: format and gap kinds

`re-lint trace build` (vendored as `scripts/trace_matrix.py build`) writes three files to `<workspace>/trace/`: `trace.csv`, `trace.md` and `gaps.json`. This page fixes their shape. When you build the files by hand (no Python), follow it exactly, so that `change-impact` and CI can read them.

## `trace.csv`

Header: `From,FromType,To,ToType,Relation,Evidence`. There is one row per distinct link (`From`, `To`, `Relation`). Rows are sorted by `From`, then `To`, then `Relation`. The file has LF line endings, UTF-8 and minimal quoting. It has no timestamps, so a rebuild with no changes gives an identical file.

Links point downstream along the chain source → requirement → decision/ADR → code → test. Read a row as "From *Relation* To".

| Relation | FromType | ToType | Found in |
| --- | --- | --- | --- |
| `source-of` | `source` (`S-nn`), `stakeholder` (`SH-nn`), `interview` (`I-nn`) | `requirement` | The `Source` cell of the requirement row, `sources.csv` |
| `linked-to` | `requirement` | `requirement` | The `Links` cell of the requirement row |
| `decided-by` | `requirement` | `decision` (`RDR-nnn`), `adr` (file path) | `decisions/*.md`, ADR folders, or `Links` |
| `changed-by` | `requirement` | `change` (`CR-nnn`) | `changes/CR-*.md`, or `Links` |
| `implemented-by` | `requirement` | `code` (file path), `commit` (7-character SHA) | Code files under the code globs; `git log` messages |
| `verified-by` | `requirement` | `test` (`path::test name`, or the path when no name is found) | Test files under the test globs |

Column rules:

- **From / To**: an ID exactly as registered (`R-041`, `S-01`, `RDR-007`), a repo-relative path with forward slashes, or a short commit SHA. A `Source` cell with no ID (for example `PO 2026-11-03`) is kept as text, with FromType `source`.
- **Evidence**: where the link was found. Use `path:line` for files and registers (`requirements/requirements.csv:7`, `tests/test_redeem.py:9`), or `git:<sha7>` for a commit, with ` (#NNN)` appended when the subject ends with a PR number. When a link is found in several places, Evidence holds the first one, in this order: register, decision or ADR file, code, test, git.
- Only registered requirement IDs appear in `trace.csv`, withdrawn and rejected ones included. Citations of unknown IDs appear only in the gap report.
- A file that matches a test glob is a test file, even when it also matches a code glob (`internal/redeem/rules_test.go`). Files that match neither are not scanned. Globs are matched against the repo-relative path from the repo root, so `src/**` does not match `web/src/x.ts`. `--code-glob` and `--test-glob` add to the globs in `schema.json` → `trace`; they do not replace them.

Example rows (loyalty-points):

```csv
From,FromType,To,ToType,Relation,Evidence
R-041,requirement,3f9c2ab,commit,implemented-by,git:3f9c2ab (#212)
R-041,requirement,src/loyalty/redeem.py,code,implemented-by,src/loyalty/redeem.py:12
R-041,requirement,tests/test_redeem.py::test_r_041_rejects_below_minimum,test,verified-by,tests/test_redeem.py:9
S-01,source,R-041,requirement,source-of,requirements/requirements.csv:7
```

## `trace.md`

Use these sections, in this order (template: `assets/trace.md`):

1. **Header table**: generated date, commit, command, files read, globs used.
2. **Coverage summary**: the fixed rows in the template. The counts include requirements of every status except `withdrawn` and `rejected`.
3. **Graph**: one Mermaid `graph LR` with sources, requirements, decisions/ADRs, code files and test files. Code and tests are grouped per file, and commits are left out of the graph (they stay in `trace.csv`). Node IDs have the punctuation removed (`R041["R-041"]`). Requirements with a gap get `class ... gap`, and retired requirements get `class ... retired`.
4. **Gaps**: one table per gap kind below, always present. Write `None.` when a table is empty.
5. **Unlinked (informational)**: tests and code files that cite no requirement. They are listed for review and do not count as gaps.

## Gap kinds (`gaps.json` → `kind`)

| Kind | Reported when | trace.md table |
| --- | --- | --- |
| `requirement-without-test` | Status is `agreed`, `implemented` or `verified`; `Verification` is empty or `test`; no `verified-by` link | Requirements without tests |
| `requirement-without-source` | `Source` is empty or `TBD`, or cites an `S-`/`SH-`/`I-` ID that is not registered | Requirements without a source |
| `test-cites-unknown-id`, `test-cites-retired-id` | A test cites an ID that is not in the register, or one whose status is `withdrawn` or `rejected` | Tests citing unknown or retired IDs |
| `code-cites-unknown-id`, `code-cites-retired-id` | The same check, for code files. Commit messages are history that nobody can fix, so they never produce these gaps | Code citing unknown or retired IDs |
| `agreed-without-implementation` | Status is `agreed`, `implemented` or `verified`, and there is no `implemented-by` link | Agreed or later requirements without an implementation reference |
| `test-without-requirement` (info) | A test function under the test globs whose name, docstring and annotations cite no ID | Unlinked (informational) |
| `code-without-requirement` (info) | A file under the code globs that cites no ID | Unlinked (informational) |

Each `gaps.json` entry has these fields: `kind`, `severity` (`gap` or `info`), `id` (empty for unlinked items), `file`, `line`, `detail`. `trace gaps --fail-on-gaps` exits `1` when there is at least one entry with severity `gap`. Entries with severity `info` never fail the gate: a new repository has many unlinked files, and blocking a release on them teaches people to add citations that mean nothing.

If the script you run does not report unlinked items, find them yourself. List the test functions and code files under the globs that appear in no `trace.csv` row.

## Triage (what the skill adds on top of the script)

| Situation | Severity | Typical action | Owner |
| --- | --- | --- | --- |
| `implemented` / `verified` with no test | fix first | Write the test, or move the status back to `agreed` after asking | QA + requirement owner |
| `agreed`, verification `test`, no test | real gap | Plan the test; issue `<ID>: no test` | QA |
| `agreed`, no implementation reference | real gap | Find out whether the work has not started or the code does not cite the ID; then cite it, or plan the work | tech lead |
| Verification `inspection` / `analysis` / `demonstration` | not a test gap | Put the inspection record or analysis in `Links` | requirement owner |
| `draft` / `proposed` without a test | informational | none yet | none |
| Test or code cites a retired ID | stale citation | Delete or retarget the test or code; never reactivate the requirement just to clear the gap | developer + requirement owner |
| Test or code cites an unknown ID | stale citation | Fix the typo, or register the requirement through `requirement-phrasing` | developer |
| Test or code file cites no requirement | informational | Ask whether a requirement is missing (then `requirement-phrasing`) or only the citation is missing. Helpers, glue code and tests of the test setup stay unlinked | tech lead |
