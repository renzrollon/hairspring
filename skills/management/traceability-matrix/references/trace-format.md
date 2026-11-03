# Trace files: format and gap kinds

`re-lint trace build` (vendored as `scripts/trace_matrix.py build`) writes three files to `<workspace>/trace/`: `trace.csv`, `trace.md` and `gaps.json`. This page describes their shape. When you build the files by hand (no Python), follow it exactly, so that `change-impact` and CI can read them.

## `trace.csv`

Header: `From,FromType,To,ToType,Relation,Evidence`. Every row starts at a requirement and points to one artifact. There is one row per distinct (`From`, `To`, `Relation`), sorted by the requirement number, then `To`, then `Relation`. The file has LF line endings, UTF-8 and minimal quoting. It has no timestamps, so a rebuild with no changes gives an identical file.

| `ToType` | `Relation` | `To` | Found in |
| --- | --- | --- | --- |
| `source` | `derives-from` | A source, stakeholder or interview ID (`S-01`, `SH-02`, `I-03`), or the `Source` text when it holds no ID | The `Source` cell of the requirement row; `sources.csv` rows that cite the requirement |
| `decision` | `decided-by` | `RDR-nnn` for files named `RDR-nnn-*.md` and for decision IDs in `Links`; the repo-relative path for other ADR files | `requirements/decisions/`, the ADR folders in `schema.json` → `trace.adr_dirs`, and the `Links` cell |
| `code` | `implemented-by` | Repo-relative file path | Files under the code globs, and code paths in `Links` |
| `test` | `verified-by` | `path::test name`, or the path when no test name is found nearby | Files under the test globs, and test paths in `Links` |
| `commit` | `mentioned-in` | Short commit hash | `git log` subjects and bodies (when `trace.scan_git_log` is true) |
| `code` | `mentioned-in` | Repo-relative path of an OpenSpec file | Files under `openspec/` (hand-offs written by `to-openspec`). A mention is not an implementation reference and never closes or opens a gap |

Column rules:

- **From**: the requirement ID as cited. It keeps an acceptance-criterion suffix (`R-041.AC2`) when the citation names one. `FromType` is always `requirement`.
- **Evidence**: `path:line` where the link was found (`requirements/requirements.csv:7`, `tests/test_redeem.py:9`), or the short hash for a commit.
- **Unknown IDs** cited in code or tests still get a row, so the gap report has evidence. `trace gaps` flags them.
- **IDs of other kinds** in `Links` (`CR-`, `CF-`, `R-`) produce no row. `trace impact` reads them from the register instead.

Which files are scanned:

- A file under a decision folder is a decision, a file matching a test glob is a test, and any other file matching a code glob is code, in that order. `internal/redeem/rules_test.go` is therefore a test.
- Globs are matched against the repo-relative path. `**` spans folders, and a pattern without `/` matches at any depth, so `src/**` does not match `web/src/x.ts`.
- `--code-glob` and `--test-glob` **replace** the globs in `schema.json` for that run. Pass every glob you need, or add the extra ones to `schema.json` → `trace` so CI sees them too.
- Files under the workspace (`requirements/`) are not scanned as code. Files under `openspec/` are scanned for mentions only (`code`, `mentioned-in`). Binary files, dependency folders (`node_modules`, `vendor`, `.venv`, ...) and files larger than `--max-bytes` are skipped.
- In test files, the test-name forms `test_r_041_...`, `TestR041_...` and `r041` count inside identifiers that start with `test`. Elsewhere in a test file, only `R-041` and the marker spelling `R041` count. Set `"trace": {"test_name_forms": false}` to accept only `R-041`.

Example rows (loyalty-points):

```csv
From,FromType,To,ToType,Relation,Evidence
R-041,requirement,3f9c2ab,commit,mentioned-in,3f9c2ab
R-041,requirement,S-01,source,derives-from,requirements/requirements.csv:7
R-041,requirement,src/loyalty/redeem.py,code,implemented-by,src/loyalty/redeem.py:12
R-041,requirement,tests/test_redeem.py::test_r_041_rejects_below_minimum,test,verified-by,tests/test_redeem.py:9
```

The reader also accepts hand-built rows in the upstream direction (`S-01,source,R-041,requirement,source-of,...`) and the types `adr`, `change`, `stakeholder`, `interview`, and normalizes them. When you write rows by hand, use the form above anyway.

## `trace.md`

The sections come in this order (template: `assets/trace.md`):

1. **Header table**: generated date, commit, command, files read, and globs used. A line under it says the file is generated.
2. **Coverage summary**: the fixed rows in the template. The counts are for requirements of every status except `withdrawn` and `rejected`, plus the register size and the number of links.
3. **Graph**: one Mermaid `graph LR` of requirements, sources, decisions, code files and test files. Code and tests are grouped per file, and commits are left out. Node IDs have the punctuation removed (`R041["R-041"]`, `srcloyaltyredeempy[["src/loyalty/redeem.py"]]`). Requirements with a gap get `class ... gap`, retired ones get `class ... retired`. Above `--max-graph-edges` links, the graph is cut and a note says so.
4. **Gaps**: one table per gap kind below, always present. An empty table shows `None.`.
5. **Matrix**: one row per requirement with its sources, decisions, code, tests, commits and specs (`openspec/` mentions).
6. **Commits citing requirement IDs**: short hash and subject. This section appears only when commits were found.

## Gap kinds (`gaps.json` → `gaps[].kind`)

| Kind | Reported when | trace.md table |
| --- | --- | --- |
| `requirement-without-test` | Status `agreed`, `implemented` or `verified`; `Verification` empty or `test`; no `verified-by` link | Requirements without tests |
| `requirement-without-source` | `Source` empty or `TBD`, or citing an `S-`/`SH-` ID missing from `sources.csv` / `stakeholders.md` (when those files exist) | Requirements without a source |
| `agreed-without-implementation` | Status `agreed`, `implemented` or `verified`, and no code link and no commit citing the ID | Agreed or later requirements without an implementation reference |
| `test-cites-unknown-id`, `test-cites-retired-id` | A test cites an ID that is not in the register, or one whose status is `withdrawn` or `rejected` | Tests citing unknown or retired IDs |
| `code-cites-unknown-id`, `code-cites-retired-id` | The same check for code files | Code citing unknown or retired IDs |

Commit messages are history that nobody can fix, so they never produce a gap. `gaps.json` is `{"summary": {...}, "gaps": [{"kind", "id", "file", "line", "detail", ...}]}`. `trace gaps --fail-on-gaps` exits with `1` when any gap is reported. `--only KIND ...` limits the run to some kinds, and `--status S ...` changes which statuses the requirement-level gaps apply to.

## Unlinked files (the skill checks these, not the script)

The tracer does not report tests or code that cite no requirement. List them yourself: the test functions and code files under the globs that appear in no `trace.csv` row. Report them as informational in the final message, never as gaps. A new repository has many of them, and pressure to link them produces citations that mean nothing.

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
| Test or code file cites no requirement | informational | Ask whether a requirement is missing (then `requirement-phrasing`) or only the citation is missing. Helpers and glue code stay unlinked | tech lead |
