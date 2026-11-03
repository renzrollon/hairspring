# Integration formats: what the vendored bridge scripts must emit and read

For the author of `packages/re-lint` (`openspec.py` → `to_openspec.py`, `reqif_io.py` → `reqif_bridge.py`, `issues.py` → `issue_sync.py`). The CLIs are fixed by `docs/tooling-contract.md`; this note fixes the file formats and the behaviors the three skills in `skills/integration/` rely on. Checked 2026-11-03.

**Golden files.** Treat these as expected output for tests; each was validated with the real tool:

| Golden file | Validated with |
| --- | --- |
| `skills/integration/to-openspec/examples/expected-output/openspec/changes/add-voucher-redemption/` | `openspec validate add-voucher-redemption --strict` (OpenSpec 1.16.0), then `openspec archive` |
| `skills/integration/to-openspec/examples/expected-output/specs/001-voucher-redemption/spec.md` | spec-kit 1.2.6 template sections (spec-kit has no validator) |
| `skills/integration/reqif-bridge/examples/expected-output.reqif`, `vendor-return.reqif` | `reqif validate --use-reqif-schema` (strictdoc reqif 0.1.0, OMG XSD) |
| `skills/integration/issue-sync/examples/expected-plan.json`, `expected-output.md`, `expected-issue-body.md` | shape only (no tracker) |

Inputs for those runs: each skill's `examples/input/requirements/`. The OpenSpec and spec-kit golden files show the state after the skill's step 6: `## Why`, `## Purpose`, `## Impact`, the capability description and the "Not in this change" reasons were refined by the agent with the user. Every other line is what the script must emit.

## 1. `to_openspec.py`

**Selection.** No `--ids` and no `--status` means `--status agreed`. `--ids` is comma-separated. Never select `withdrawn`, `rejected`, `deferred` or `Priority=wont`, even when named: skip and report. Refuse with exit `2` if the target change folder (or spec-kit `spec.md`) exists, unless `--force`. `--out` is the directory that holds `openspec/` (default: repo root).

**Findings** (exit `1`, files still written): `open-tbd` (TBD/TBC/??/XXX in any cell), `strict-keyword` (obligation is `should`/`may`), `not-agreed` (named `draft`/`proposed` row), `too-long` (body over 500 characters including the anchor line), `id-in-open-change` (R-ID already in another `openspec/changes/*/`). A row with no acceptance criterion and no `WHERE`/`WHILE`/`WHEN`/`IF` clause cannot get a scenario: skip it and report `no-scenario-source`. The skill runs its gate before calling the script, so findings here are approved exceptions or mistakes.

**Files (OpenSpec target)**

```text
openspec/changes/<change>/.openspec.yaml       schema: spec-driven / created: YYYY-MM-DD / x-re-skills-source / x-re-skills-ids
openspec/changes/<change>/proposal.md
openspec/changes/<change>/tasks.md
openspec/changes/<change>/specs/<capability>/spec.md
```

Never write `openspec/specs/`, `openspec/config.yaml` or `design.md`.

**`proposal.md`** headings, in order: `# Proposal: <change>`, generated-by comment, `## Why`, `## What Changes`, `## Capabilities`, `### New Capabilities`, `### Modified Capabilities`, `## Constraints and Quality Requirements`, `## Impact`, `## Not in this change`, `## Traceability`.

- `## Why` (OpenSpec parses it; 50 to 1,000 characters): the rationales of the selected F rows joined by spaces, cut at a sentence end before 1,000; if under 50, append `Requirements handed off: <IDs>.`
- `## What Changes` (parsed; must not be empty): `- <ID> <Title> (<Priority>)` per F row.
- Capabilities: `` - `<capability>`: <titles joined by "; "> (<IDs>) ``; a capability goes under Modified if `openspec/specs/<capability>/spec.md` exists, else New; the empty list is `- None`.
- Constraints and Quality Requirements: the line `These restrict the whole change.`, then table `ID | Type | Requirement | Source | Verification`, every Q and C row, text verbatim.
- Impact: `- Sources: <source IDs from Source cells>` and ``- Register: `<workspace>/requirements.csv` ``; the agent adds systems.
- Not in this change: table `ID | Reason` for skipped rows (script reason: `Status=<status>` or the finding, plus `; links: <Links>` when set). Traceability: table `ID | Type | Priority | Status | Source | Lands in`.

**Delta `spec.md`**, one per capability. Capability = `cap:<name>` in `Tags`, else the change name minus a leading `add-|update-|change-|remove-|fix-`.

```markdown
# Spec Delta: <capability>

<!-- generated-by comment -->

## Purpose

<new capability only; draft "Covers <titles joined by '; '>." padded to >= 50 characters>

## ADDED Requirements

### Requirement: <ID> <Title, else first 8 words of Text without trailing punctuation>
<!-- <ID> -->
<Text verbatim; whole-word shall/must upper-cased; should/may upper-cased only if no shall/must>

#### Scenario: <ID>.AC<n> <When clause: first 8 words, first letter upper-cased>
- **GIVEN** ...
- **WHEN** ...
- **THEN** ...
```

- **ADDED** when the R-ID appears in no `openspec/specs/**/spec.md`; **MODIFIED** when it does: copy that block's header text exactly, write the full new block, no `## Purpose`. No REMOVED blocks in this version (the skill lists withdrawn IDs still in main specs).
- **Acceptance criteria** come from `<workspace>/stories/*.md`: a table row whose `ID` cell matches `^R-\d{3,}\.AC\d+$` (text from the `Acceptance criterion` column, else the last column), or a list item `- R-nnn.ACn: <text>`. Split into clauses at `Given|When|Then|And|But` (any case) at the start of the text or right after `, ` or `; `; keyword → `**GIVEN**`/`**WHEN**`/`**THEN**`/`**AND**` (`But` → `AND`); clause text verbatim, keyword and final period removed. An `and` inside a clause does not split it. One scenario per criterion, in ID order.
- **Derived scenario** when a row has no criterion: name `<ID> main case (derived from the requirement text)`. Main clause = text after `, THEN ` (IF form), else after the right-most `, ` whose remainder contains the obligation verb and no EARS keyword. Split the condition at upper-case `WHERE|WHILE|WHEN|IF`: `WHERE`/`WHILE` → `**GIVEN**`, `WHEN`/`IF` → `**WHEN**`; main clause → `**THEN**` (verbatim, obligation verb not upper-cased). Text not starting with an EARS keyword: no derived scenario.
- Q and C rows never become `### Requirement:` blocks.

**`tasks.md`**: `# Tasks`, comment, then `## <n>. <capability>` with `- [ ] <n>.<m> Implement <ID> <Title>; verify by an automated test for scenario <first AC ID, or "<ID> main case" in quotes when derived> (<ID>)`, then `## <n>. Quality requirements and constraints` with `- [ ] <n>.<m> Verify <ID> <Title> by <Verification, default test> against the target in proposal.md (<ID>)` (a row whose Source starts with a document source ID: `against <source ID>`). Every tracked line ends with `(<IDs>)`.

**spec-kit target** (`--target spec-kit`, CHANGE_NAME is the folder name such as `004-voucher-redemption`): write only `specs/<change>/spec.md` in the layout of `skills/integration/to-openspec/assets/spec-kit/spec.md`. Header block `# Feature Specification: <title>`, `**Feature Branch**`, `**Created**`, `**Status**: Draft`, `**Input**`; then `## User Scenarios & Testing *(mandatory)*` (one `### User Story N - <Title> (Priority: P1|P2|P3)` per F row, must/should/could → P1/P2/P3, `**Why this priority**: <Rationale>`, `**Independent Test**: <Verification, capitalized> of scenario <first AC ID>.` (derived: `of the scenario derived from <ID>.`), numbered `**Given** ..., **When** ..., **Then** ... (<AC-ID>)` scenarios, `---` between stories, `### Edge Cases` listing IF-THEN rows), `## Requirements *(mandatory)*` (`### Functional Requirements` and `### Constraints`, bullets `- **<ID>**: <text>`), `## Success Criteria *(mandatory)*` / `### Measurable Outcomes` (Q rows), `## Assumptions`. Keys are R-IDs, never `FR-nnn`. An approved `TBD` becomes `[NEEDS CLARIFICATION: value is TBD in requirements/requirements.csv]`. Do not write `.specify/feature.json`.

## 2. `reqif_bridge.py`

**Export** writes exactly the structure of `examples/expected-output.reqif`:

- Root `REQ-IF` with `xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"` and `xml:lang="en"`; add `xmlns:xhtml` only when writing XHTML (never, in this version).
- `REQ-IF-HEADER` (`IDENTIFIER="rs-header-<title-slug>-<YYYYMMDDTHHMMSSZ>"`) children in this XSD sequence: `COMMENT`, `CREATION-TIME` (UTC), `REPOSITORY-ID`, `REQ-IF-TOOL-ID` (`re-lint reqif <version>`), `REQ-IF-VERSION` (always `1.0`, fixed by the schema), `SOURCE-TOOL-ID` (`re-skills`), `TITLE`.
- `REQ-IF-CONTENT` children in this XSD sequence: `DATATYPES`, `SPEC-TYPES`, `SPEC-OBJECTS`, `SPEC-RELATIONS` (empty), `SPECIFICATIONS`, `SPEC-RELATION-GROUPS` (empty).
- One `DATATYPE-DEFINITION-STRING` `rs-dt-string` with the required `MAX-LENGTH` (a package constant, raised to the longest value if needed; the golden file uses 100000).
- One `SPEC-OBJECT-TYPE` `rs-sot-requirement` (`LONG-NAME="Requirement"`) with one `ATTRIBUTE-DEFINITION-STRING` per CSV header column, in file order: `IDENTIFIER="rs-ad-<column lower-cased, other characters than [a-z0-9_.-] as ->"`, `LONG-NAME="<column>"`. One `SPECIFICATION-TYPE` `rs-st-specification`.
- One `SPEC-OBJECT` per row: `IDENTIFIER="<R-ID>"`, one `ATTRIBUTE-VALUE-STRING THE-VALUE=...` per non-empty cell (escape `& < > "`, newline as `&#10;`), then `TYPE/SPEC-OBJECT-TYPE-REF`.
- One `SPECIFICATION` `rs-spec-<title-slug>` (`LONG-NAME=<title>`) with a flat `CHILDREN` list of `SPEC-HIERARCHY IDENTIFIER="rs-sh-<R-ID>"` → `OBJECT/SPEC-OBJECT-REF <R-ID>`, register order.
- Every identifiable gets `LAST-CHANGE` = export time. An R-ID that is not an XML NCName (custom prefix starting with a digit): exit `2`.
- Defaults: `--out <workspace>/exports/<title-slug>-<YYYY-MM-DD>.reqif`; `--title Requirements`; no `--ids` exports every row except `withdrawn` and `rejected`; print the count per status.

**Import** (no flag means `--diff`):

- Parse with `xml.etree.ElementTree`; reject a file with a `<!DOCTYPE` (exit `2`); `.reqifz` is not read (exit `2`, "unzip first").
- Object identity: `SPEC-OBJECT@IDENTIFIER` equal to an R-ID; else the value of an attribute named `ID` or `ReqIF.ForeignID` matching the ID pattern; else `new-object`.
- Attribute identity: definition `LONG-NAME` equal to a CSV column; aliases `ReqIF.ForeignID` → `ID`, `ReqIF.Name` → `Title`, `ReqIF.Text` → `Text`. Anything else → `unmapped-attribute`.
- Values: STRING as is; XHTML flattened to text (tags removed, whitespace collapsed), flag `xhtml-flattened`; ENUMERATION → `LONG-NAME` of the referenced `ENUM-VALUE`; INTEGER/REAL/BOOLEAN/DATE → `THE-VALUE` text. A definition absent from the file leaves the column alone; a defined attribute with no value on an object is a change to empty.
- Classes: `unchanged`, `changed-text`, `changed-attribute`, `invalid-value` (outside `schema.attributes.enums`), `new-object`, `missing-object`, `unmapped-attribute`, `xhtml-flattened`. `missing-object` = an ID in the newest `<workspace>/exports/*.reqif` with the same `SPECIFICATION@IDENTIFIER` but not in the import; register rows in neither are "not exported" (read-only).
- `--diff` prints Markdown in the shape of `skills/integration/reqif-bridge/assets/import-diff.md` (see `examples/expected-import-diff.md`); exit `1` if any row is not `unchanged`.
- `--apply` writes `changed-text`, `changed-attribute` and `new-object` only. A text change on an `agreed`, `implemented` or `verified` row sets `Status=proposed` and increments `Version` if that column exists. New objects get the next free R-ID (same algorithm as `ids next`), `Status=draft`, `Source=reqif:<file name>#<IDENTIFIER>`, empty required cells `TBD`. Never delete a row. Write through `reqio.write_csv`; print every cell changed.

## 3. `issue_sync.py` (summary; full rules in `skills/integration/issue-sync/references/sync-rules.md`)

- Title `<ID>: <Title or first 80 characters of Text>`; match existing issues by that prefix, then by the tracker reference in `Links` (`github:<owner>/<repo>#<n>`, `jira:<KEY-n>`, `ado:<id>`), which `push --apply` appends. Never delete an issue or a row.
- Body block exactly `skills/integration/issue-sync/assets/issue-body.md` between `<!-- re-skills:begin -->` and `<!-- re-skills:end -->`; replace only that span; markers missing or doubled → leave the body, report `markers-missing`. On Jira the markers are plain-text paragraphs.
- `plan` (no network) and the dry runs print the table of `assets/plan.md`; the JSON shape is `examples/expected-plan.json`. Action and class names are the ones in `sync-rules.md`.
- `push` default selection: `agreed`/`implemented`/`verified` rows plus rows already linked; never creates issues for `withdrawn`/`rejected`/`deferred`; for those, comment, and on GitHub close as "not planned", elsewhere report `move-on-board`. Push never changes tracker workflow status otherwise.
- `pull` writes only `Status`, only for class `update`, guarded by `schema.lifecycle.transitions`, no `agreed` from `draft`/`proposed` (`needs-person`), no `verified` without evidence in `Links` or `trace/trace.csv` (`needs-evidence`), never over `withdrawn`/`rejected`/`deferred` (`conflict-lifecycle`), unknown tracker status → `unmapped`; report issues titled with unknown IDs as `orphan-issue`.
- GitHub through `gh` (repo from the git remote or `GH_REPO`); Jira uses `JIRA_BASE_URL` as given (the `https://api.atlassian.com/ex/jira/<cloudId>` gateway form must work); never print or log a token, never put one on a command line, redact env values from error messages.
- Exit codes: `0` nothing to report, `1` any finding class, `2` usage, configuration or authentication error.

## Contract gaps (proposed additions, not yet in `docs/tooling-contract.md`)

1. `re-lint openspec --capability NAME`, to avoid editing `Tags` for one-capability changes.
2. `--ids` on `re-lint issues pull` and on `re-lint reqif import --apply`, so a partially accepted review can be applied by the script instead of by hand.
3. `--format text|json` on `re-lint issues plan` (the contract says "JSON + table" without the flag).
4. `schema.json` keys `issues.jira_issue_type` and `issues.ado_work_item_type` (which type `push` creates), and an optional `reqif.attribute_names` map (`{"Text": "ReqIF.Text", ...}`) for tools that need the ProSTEP names on export.
