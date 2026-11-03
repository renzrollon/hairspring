# Integration formats: what the vendored bridge scripts must emit and read

> **Status: design notes, superseded.** These notes guided the first implementation of `to_openspec.py`, `issue_sync.py` and `reqif_bridge.py`. The package (`re-lint <command> --help`) and [`tooling-contract.md`](tooling-contract.md) are now the source of truth; where these notes differ, they are out of date.

For the author of `packages/re-lint` (`openspec.py` → `to_openspec.py`, `reqif_io.py` → `reqif_bridge.py`, `issues.py` → `issue_sync.py`). The CLIs are fixed by `docs/tooling-contract.md`; this note fixes the file formats and the behaviors the three skills in `skills/integration/` rely on. Checked 2026-11-03 against OpenSpec 1.16.0, spec-kit 1.2.6, the OMG ReqIF 1.2 XSD (via strictdoc `reqif` 0.1.0), and the package draft of the same date. Section 4 lists where that draft still differs.

## Golden files

| Golden file | Validated with | Matches the package draft |
| --- | --- | --- |
| `skills/integration/to-openspec/examples/expected-output/openspec/changes/add-voucher-redemption/` | `openspec validate add-voucher-redemption --strict` (1.16.0), then `openspec archive` | yes, except the step-6 edits and the "and" split (4.1) |
| `skills/integration/to-openspec/examples/expected-output/specs/001-voucher-redemption/spec.md` | spec-kit 1.2.6 template sections | yes, except casing (4.2) and the "and" split (4.1) |
| `skills/integration/reqif-bridge/examples/expected-output.reqif` | `reqif validate --use-reqif-schema` | byte-identical to `re-lint reqif export --ids R-040,R-041,R-085 --title "Voucher redemption" --timestamp 2026-11-03T09:12:00Z` |
| `skills/integration/reqif-bridge/examples/vendor-return.reqif` → `expected-import-diff.md` | `reqif validate --use-reqif-schema` | diff classes differ (4.3, 4.4) |
| `skills/integration/issue-sync/examples/expected-plan.json`, `expected-output.md`, `expected-issue-body.md` | shape only (no tracker) | plan shape differs (4.6) |

Inputs: each skill's `examples/input/requirements/`. Step 6 of `to-openspec` is where the agent, with the user, rewrites `## Why`, `## Purpose`, the capability description and `## Impact`, and deletes the "draft" note from the proposal comment; every other line of the golden OpenSpec and spec-kit files is script output.

## 1. `to_openspec.py`

**Selection and gate.** No `--ids`/`--status` means `--status agreed`; `--ids` takes comma or space lists. Never select `withdrawn`, `rejected`, `deferred`, `Priority=wont`. Gate findings the script checks: open `TBD`/`TBC`/`??`/`XXX` (G2), named `draft`/`proposed` rows, no scenario source (G4), body over 500 characters, the R-ID in another open change (G6). Lint errors (G1) are the skill's job, because a vendored module may import only `reqio`. On a blocking finding the script refuses (exit `1`, nothing written) unless an override is given; on an existing change folder it refuses unless `--force`.

**OpenSpec files:** `openspec/changes/<change>/{.openspec.yaml, proposal.md, tasks.md, specs/<capability>/spec.md}`. Never `openspec/specs/`, `openspec/config.yaml` or `design.md`. `.openspec.yaml`: `schema: spec-driven`, `created`, `x-re-skills-source`, `x-re-skills-ids`.

**`proposal.md`**, headings in order: `# Proposal: <change>`, generated-by comment (with a "Why is a draft" note), `## Why`, `## What Changes`, `## Capabilities`, `### New Capabilities`, `### Modified Capabilities`, `## Constraints and Quality Requirements`, `## Impact`, `## Not in this change`, `## Traceability`.

- `## Why` (parsed by OpenSpec; 50 to 1,000 characters): each selected row's rationale followed by ` (<ID>)`, joined by spaces.
- `## What Changes` (parsed; not empty): `- <ID> <Title> (<Priority>)` per F row.
- Capabilities: `` - `<capability>`: <titles joined by "; "> (<IDs>) ``; Modified if `openspec/specs/<capability>/spec.md` exists, else New; `- None` when empty.
- Constraints and Quality Requirements: table `ID | Type | Requirement | Source | Verification`, every Q and C row, verbatim.
- Impact: ``- Register: `<workspace>/requirements.csv` ``.
- Not in this change: table `ID | Reason` for rows the gate left out (with `--skip-blocked`), else `None.` Rows never selected are not listed.
- Traceability: `ID | Type | Priority | Status | Source | Lands in` (`specs/<capability>/spec.md; tasks 1.1` or `proposal.md; tasks 2.1`). A row that crossed as an approved exception carries `; exception: <finding>` in its Status cell.

**Delta `spec.md`**, one per capability (`--capability`, else `cap:<name>` in `Tags`, else the change name minus `add-|update-|change-|remove-|fix-`):

```markdown
# Spec Delta: <capability>

<!-- generated-by comment -->

## Purpose

<Capability in title case>: <titles joined by "; "> (<IDs>).

## ADDED Requirements

### Requirement: <ID> <Title, else first 8 words of Text>
<!-- <ID> -->
<Text; whole-word shall/must upper-cased; should/may upper-cased only when there is no shall/must>

#### Scenario: <ID>.AC<n> <When clause: first 8 words, a leading the/a/an dropped, capitalized>
- **GIVEN** ...
- **WHEN** ...
- **THEN** ...
```

- **ADDED** when the R-ID is in no `openspec/specs/**/spec.md`; **MODIFIED** when it is (copy the header exactly, full block, no `## Purpose`). No REMOVED blocks in this version.
- **Acceptance criteria** from `<workspace>/stories/*.md`, ID `R-nnn.ACn`. A clause starts at `Given|When|Then|And|But` (any case) at the start of the criterion or right after `, `, `; ` or `. `; each clause becomes one bullet, verbatim, keyword and final period removed (`But` → `AND`). **An `and` inside a clause never splits it** (4.1).
- **Derived scenario** without a criterion: `<ID> main case (derived from the requirement text)`. Main clause: after `, THEN ` (IF form), else after the right-most `, ` whose remainder holds the obligation verb. Condition clauses split at upper-case `WHERE|WHILE|WHEN|IF`: `WHERE`/`WHILE` → `**GIVEN**`, `WHEN`/`IF` → `**WHEN**`; main clause → `**THEN**`, obligation verb upper-cased, final period kept. Text not opening with an EARS keyword gets none (G4).
- Q and C rows never become `### Requirement:` blocks.

**`tasks.md`**: `# Tasks`, comment, `## <n>. <capability>` with `- [ ] <n>.<m> Implement <ID> <Title>; verify by an automated test for scenario <AC ID or "<ID> main case"> (<ID>)`, then `## <n>. Quality requirements and constraints` with `- [ ] <n>.<m> Verify <ID> <Title> by <test|inspection|analysis|demonstration> against proposal.md (<ID>)`.

**spec-kit** (`--target spec-kit`; CHANGE_NAME is the folder, `004-voucher-redemption`): only `specs/<change>/spec.md`, layout of `skills/integration/to-openspec/assets/spec-kit/spec.md`: header block (`# Feature Specification`, `**Feature Branch**`, `**Created**`, `**Status**: Draft`, `**Input**`); `## User Scenarios & Testing *(mandatory)*` with one `### User Story N - <Title> (Priority: P1|P2|P3)` per F row (must/should/could), `<!-- <ID> -->` on the next line, the text with `(<ID>)`, `**Why this priority**`, `**Independent Test**: An automated test of scenario <first scenario>.`, numbered `**Given** ..., **When** ..., **Then** ... (<AC ID>)`, `---` between stories, `### Edge Cases` for IF-THEN rows; `## Requirements *(mandatory)*` with `### Functional Requirements` and `### Constraints` (`- **<ID>**: <text>`); `## Success Criteria *(mandatory)*` / `### Measurable Outcomes` (Q rows); `## Assumptions`. Keys are R-IDs, never `FR-nnn`. The obligation verb is upper-cased in every requirement text in the file (4.2). An approved `TBD` becomes `[NEEDS CLARIFICATION: ...]`.

## 2. `reqif_bridge.py`

**Export**: the structure of `examples/expected-output.reqif`, which is the package draft's output:

- `REQ-IF` (`xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"`, `xml:lang="en"`) → `THE-HEADER/REQ-IF-HEADER IDENTIFIER="rs-header"` with, in XSD order, `COMMENT`, `CREATION-TIME`, `REQ-IF-TOOL-ID`, `REQ-IF-VERSION` (`1.0`, fixed by the schema), `SOURCE-TOOL-ID`, `TITLE`.
- `CORE-CONTENT/REQ-IF-CONTENT` → `DATATYPES` (`DATATYPE-DEFINITION-STRING rs-dt-string`, `MAX-LENGTH="32000"`, raised if a value is longer), `SPEC-TYPES` (`SPEC-OBJECT-TYPE rs-sot-requirement` with one `ATTRIBUTE-DEFINITION-STRING rs-ad-<Column>`, `LONG-NAME=<Column>` per CSV column; `SPECIFICATION-TYPE rs-st-specification`), `SPEC-OBJECTS` (one `SPEC-OBJECT IDENTIFIER=<R-ID>` per row: `TYPE`, then `VALUES` with one `ATTRIBUTE-VALUE-STRING THE-VALUE` per non-empty cell), `SPECIFICATIONS` (`SPECIFICATION rs-specification`, flat `SPEC-HIERARCHY rs-sh-<R-ID>` children, register order). No empty `SPEC-RELATIONS`/`SPEC-RELATION-GROUPS`.
- Every identifiable has `LAST-CHANGE` (the `--timestamp` or export time, UTC). An R-ID that is not an XML NCName: exit `2`.

**Import** (default `--diff`; reads `.reqif` and the `.reqif` inside a `.reqifz`):

- Object identity: `IDENTIFIER` equal to an R-ID, else an `ID` or `ReqIF.ForeignID` value matching the ID pattern, else a **new object**.
- Attribute identity: `LONG-NAME` equal to a column; aliases `ReqIF.ForeignID` → `ID`, `ReqIF.Name` → `Title`, `ReqIF.Text` → `Text`; anything else is unmapped (reported, `--add-columns` only on request).
- Values: XHTML flattened (flag it), enumerations by value name. An attribute definition absent from the file never clears a column.
- Classes the skill needs (`skills/integration/reqif-bridge/references/reqif-mapping.md`): `unchanged`, `changed-text`, `changed-attribute`, `invalid-value`, `new-object`, `missing-object`, `unmapped-attribute`, `xhtml-flattened`.
- `--apply` writes only `changed-text`, `changed-attribute` and `new-object` (next free R-ID, `Status=draft`, `Source=reqif:<file>#<IDENTIFIER>`, empty required cells `TBD`). Never an `invalid-value`. A text change on an `agreed`, `implemented` or `verified` row sets `Status=proposed` and increments `Version` when that column exists. Never deletes a row.
- Reject a file that contains `<!DOCTYPE` (entity-expansion risk with `xml.etree`).

## 3. `issue_sync.py` (full rules: `skills/integration/issue-sync/references/sync-rules.md`)

- Title `<ID>: <Title or first 80 characters of Text>`; match by that prefix; two candidates → ambiguous, untouched. Never delete an issue or a row.
- Body block: `skills/integration/issue-sync/assets/issue-body.md` between `<!-- re-skills:begin -->` and `<!-- re-skills:end -->`; replace only that span (Jira ADF: the markers are paragraphs). Markers missing or doubled → leave the body, report it.
- `plan`/`push` default selection: `agreed`. `withdrawn`/`rejected` rows are never pushed (the skill lists linked ones as `move-on-board` for a person to close).
- `pull` writes only `Status`, only for rows the guard table in `sync-rules.md` marks `update`; GitHub "closed as not planned" maps through `closed:not_planned` only.
- Credentials: `gh` for GitHub; `JIRA_*`, `ADO_*` env vars; `JIRA_BASE_URL` used as given, so the `https://api.atlassian.com/ex/jira/<cloudId>` gateway form works. Never print, log or pass a token on a command line.

## 4. Differences in the package draft (2026-11-03)

| # | Severity | Module | Difference | Fix |
| --- | --- | --- | --- | --- |
| 4.1 | should | openspec | `_AND_SPLIT` cuts a Then clause at "and the/a/its ...": "then the POS shows the value and the expiry date" becomes a broken step `AND the expiry date` | split only at clause-opening keywords (section 1) |
| 4.2 | should | openspec | spec-kit: the obligation verb is upper-cased in the Functional Requirements list only, not in stories, Constraints or Success Criteria | one rule for every requirement text |
| 4.3 | **must** | reqif | `import --apply` writes `Status=Accepted` from `vendor-return.reqif` (no `schema.attributes.enums` check), and writes a text change to an `agreed` row without moving it to `proposed` | add `invalid-value` (never written) and the lifecycle rule |
| 4.4 | should | reqif | objects without a requirement ID are skipped as "headings, notes", so a vendor's new requirement can be lost; `import --diff` exits `0` when it finds changes | report them as `new-object`; exit `1` on findings (contract) |
| 4.5 | **must** | issues | `transition_allowed` accepts any forward move along draft → ... → verified, so `pull --apply` would write `draft → implemented`, `proposed → agreed` (no named person) and `implemented → verified` (no evidence) | add the `needs-person`, `needs-evidence` and `conflict` classes of `sync-rules.md` |
| 4.6 | should | issues | `plan` prints `ID / Title / Labels` without the action per row; JSON is `{tracker, apply, items}`; `push --apply` does not record the tracker reference in `Links` | the table of `assets/plan.md` and the JSON of `examples/expected-plan.json`; append `jira:LOY-81`-style references to `Links` |
| 4.7 | **must** | openspec | a named draft that *was* handed off is listed under "Not in this change" ("in this change ... confirm the approval"), which contradicts the heading | mark approved exceptions in the Traceability Status cell (this followed an ambiguous sentence in an earlier draft of these notes, since fixed) |
| 4.8 | should | reqif | `export` without `--ids` includes `withdrawn` and `rejected` rows | exclude them by default |

The skills already guard against 4.3, 4.5 and 4.7 (review before `--apply`, apply clean rows by hand), so these do not block the skills' release, but each makes the script unsafe on its own.

## 5. Contract gaps (flags the package draft has and the contract lacks)

`re-lint openspec`: `--allow-tbd`, `--skip-blocked`, `--capability`, `--date`, `--title`, `--workspace`, `--schema`. `re-lint issues`: `--status`, `--format text|json`, `--repo`, `--issue-type`, `--label`, `--out`, `--ids` on `pull`, `--ignore-lifecycle`. `re-lint reqif`: `--timestamp`, `--format text|json|md`, `--add-columns`. Adding them to `docs/tooling-contract.md` lets the skills name them; until then the skills use only the contract flags and follow the override hints the scripts print. Also suggested: `--ids` on `reqif import --apply`, and `schema.json` keys `issues.jira_issue_type` / `issues.ado_work_item_type` (today `--issue-type`) and an optional `reqif.attribute_names` map for tools that need the ProSTEP `ReqIF.*` names on export.
