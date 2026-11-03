# spec-kit format targeted by `to-openspec --target spec-kit`

**Checked:** 2026-11-03, against spec-kit **1.2.6** (repository `github/spec-kit`, release 2026-11-02, commit `ba8363f`). spec-kit has no structural validator; its commands (`/speckit.clarify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.analyze`) read the file as Markdown.

**Sources** (re-check on each spec-kit minor release):

- Spec template: <https://github.com/github/spec-kit/blob/main/templates/spec-template.md>
- `/speckit.specify` command (feature folder naming, `.specify/feature.json`, quality checklist, `[NEEDS CLARIFICATION]` limit): <https://github.com/github/spec-kit/blob/main/templates/commands/specify.md>
- `/speckit.analyze` (how requirement keys are inventoried): <https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md>
- Feature numbering: <https://github.com/github/spec-kit/blob/main/scripts/bash/create-new-feature.sh>

## Folder

```text
specs/<NNN-short-name>/spec.md      written by to-openspec
specs/<NNN-short-name>/plan.md      later, by /speckit.plan
specs/<NNN-short-name>/tasks.md     later, by /speckit.tasks
.specify/feature.json               {"feature_directory": "specs/<NNN-short-name>"}; how later commands find the feature
```

- `<NNN>` is the next free three-digit number after the existing `specs/NNN-*` folders (`001` in a fresh repo). Projects initialized with timestamp numbering use `YYYYMMDD-HHMMSS` instead; check `.specify/init-options.json` (`feature_numbering`).
- The change name passed to the script is the whole folder name: `to_openspec.py 004-voucher-redemption --target spec-kit`.
- to-openspec does not write `.specify/feature.json`. Tell the user to run the next spec-kit command from a branch with the same name, or to set `SPECIFY_FEATURE_DIRECTORY=specs/<NNN-short-name>`.

## `spec.md`

The template's mandatory sections are `User Scenarios & Testing`, `Requirements` and `Success Criteria`. The header block and the order below follow the template; `### Constraints` is a re-skills addition inside `## Requirements`.

```markdown
# Feature Specification: <Feature title>

**Feature Branch**: `<NNN-short-name>`

**Created**: <YYYY-MM-DD>

**Status**: Draft

**Input**: Agreed requirements exported from `requirements/requirements.csv` by re-skills to-openspec (<R-IDs>)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - <Title> (Priority: P1)
...
### Edge Cases

## Requirements *(mandatory)*

### Functional Requirements
### Constraints

## Success Criteria *(mandatory)*

### Measurable Outcomes

## Assumptions
```

## Mapping from the register

| Register | spec-kit |
| --- | --- |
| Each `Type=F` row | one `### User Story N - <Title> (Priority: Pn)`, ordered by priority then register order; `<!-- R-nnn -->` on the next line; then the text with `(R-nnn)`, `**Why this priority**:` the Rationale, `**Independent Test**: An automated test of scenario <first scenario>.` (or `An inspection`, `An analysis`, `A demonstration`), `**Acceptance Scenarios**:` numbered |
| Acceptance criterion `R-nnn.ACn` | `1. **Given** ..., **When** ..., **Then** ... (R-nnn.ACn)` |
| No acceptance criterion, EARS text | one scenario derived as in `openspec-format.md` (`WHILE`/`WHERE` → Given, `WHEN`/`IF` → When, main clause → Then), marked `(R-nnn, derived from the requirement text)` |
| `IF ... THEN` rows | also one bullet under `### Edge Cases`: `- R-nnn: <Title> (see User Story N)` |
| `Type=F` text | `- **R-nnn**: <text>` under `### Functional Requirements`. In every requirement text in the file (stories and lists), the obligation verb is upper-cased as for OpenSpec |
| `Type=C` text | `- **R-nnn**: <text>` under `### Constraints` |
| `Type=Q` text | `- **R-nnn**: <text>` under `### Measurable Outcomes`; if none were selected, one bullet saying so |
| `Priority` | `must` → P1, `should` → P2, `could` → P3 (`wont` never goes across) |
| `TBD` in an approved row | `[NEEDS CLARIFICATION: <the open question, or "value is TBD in requirements/requirements.csv">]`; spec-kit expects at most three such markers per spec, so more than three is a reason to stop and run `clarifying-questions` first |
| Rows left out by the gate (not rows that were never selected) | one bullet each under `## Assumptions`: `- Not in this feature: R-nnn (<reason>)` |

**Requirement keys.** spec-kit's template numbers requirements `FR-001` and success criteria `SC-001`, and `/speckit.analyze` uses an explicit identifier as the key when one is present. to-openspec writes the project's R-IDs as the key instead, so commits, tests and `traceability-matrix` keep matching. A comment under `## Requirements` says so. Do not renumber to `FR-nnn`: an `FR-040` does not match `R-040` in the trace.

## Checks before handing over

- [ ] The three mandatory sections exist and are not empty.
- [ ] Every selected F row has a user story with at least one numbered acceptance scenario.
- [ ] Every selected Q row is under Measurable Outcomes and every C row under Constraints, text verbatim.
- [ ] No more than three `[NEEDS CLARIFICATION]` markers.
- [ ] No implementation details were added (languages, frameworks, APIs): spec-kit's own quality checklist fails on them.
