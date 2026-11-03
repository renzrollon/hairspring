# Tooling contract: `re-lint` and the vendored scripts

Deterministic checks run as code, not as model judgment, so they can gate CI. They live in one Python package, `packages/re-lint` (import name `re_lint`, CLI `re-lint`), and are **vendored** into the skills that need them so a skill installed on its own still works.

- Stdlib-only, Python 3.9+. No runtime dependencies.
- Every command module is a single file that imports only the standard library and `reqio` (the shared reader/writer), using:

  ```python
  try:  # inside the package
      from . import reqio
  except ImportError:  # vendored next to reqio.py in a skill's scripts/
      import reqio
  ```

- Every module exposes `build_parser() -> argparse.ArgumentParser`, `run(args) -> int` and `main(argv=None) -> int`, so `python3 scripts/<file>.py ...` and `re-lint <command> ...` take the same arguments.
- Exit codes: `0` clean, `1` findings at or above `--fail-on`, `2` usage, schema or parse error.
- Output formats where findings are produced: `text` (default, human), `json` (machine), `github` (GitHub Actions `::error file=...,line=...::` annotations), `sarif` (code scanning; `check` only).

## Vendoring map

`tools/vendor_scripts.py` copies these files; `tools/vendor_scripts.py --check` fails CI on drift.

| Package module | Vendored as | Into skills |
| --- | --- | --- |
| `re_lint/reqio.py` | `scripts/reqio.py` | every skill listed below |
| `re_lint/lint.py` | `scripts/lint_requirements.py` | `requirement-linter`, `requirement-phrasing`, `requirements-review` |
| `re_lint/ids.py` | `scripts/re_ids.py` | `re-ids` |
| `re_lint/tracing.py` | `scripts/trace_matrix.py` | `traceability-matrix`, `change-impact` |
| `re_lint/baseline.py` | `scripts/baseline.py` | `baseline` |
| `re_lint/views.py` | `scripts/views.py` | `attribute-schema` |
| `re_lint/prioritize.py` | `scripts/prioritize.py` | `prioritization` |
| `re_lint/reqif_io.py` | `scripts/reqif_bridge.py` | `reqif-bridge` |
| `re_lint/openspec.py` | `scripts/to_openspec.py` | `to-openspec` |
| `re_lint/issues.py` | `scripts/issue_sync.py` | `issue-sync` |
| `skills/_primitives/re-templates/assets/schema.json` | `assets/schema.json` | `re-setup`, `attribute-schema` |

Generated docs (also written by `tools/vendor_scripts.py`): `skills/validation/requirement-linter/references/rules.md` from the rule registry in `lint.py`.

## Shared reader: `reqio.py`

Public API every module uses:

| Function | Purpose |
| --- | --- |
| `find_workspace(start=".") -> Path` | Walk up from `start` to the repo root; return `<root>/<workspace>` where `workspace` comes from `requirements/schema.json` (default `requirements`). |
| `load_schema(path=None, workspace=None) -> dict` | Load `schema.json` merged over `DEFAULT_SCHEMA` (deep merge, user values win). Never fails on a missing file. |
| `DEFAULT_SCHEMA` | The defaults in `skills/_primitives/re-templates/assets/schema.json`. |
| `read_table(path) -> Table` | Read a `.csv` file, or every Markdown pipe table in a `.md` file that has an `ID` column. Rows keep their source line number (`row.line`) and file (`row.file`). |
| `read_requirements(paths, schema) -> list[Row]` | All requirement rows (IDs matching the requirement ID pattern) from the given files. |
| `write_csv(path, rows, columns)` | Write with the schema column order, LF line endings, minimal quoting, UTF-8, trailing newline. |
| `id_regex(kind, schema) -> re.Pattern` | Compiled pattern for an ID kind (`requirement`, `source`, ...). |
| `ID_IN_TEXT` | Regex that finds any requirement-like ID in free text (commit messages, test names, code comments). |

`Row` is a `dict` subclass with `.file` and `.line` attributes.

## Commands

### `re-lint check` (vendored as `lint_requirements.py`)

```text
re-lint check [PATH ...] [--schema FILE] [--format text|json|github|sarif]
              [--fail-on error|warning|info] [--disable RULE[,RULE]] [--enable RULE[,RULE]]
              [--only-ids R-001,R-002] [--changed-only BASE_REF]
```

- Default paths: `<workspace>/requirements.csv` plus Markdown tables under `<workspace>/` whose `ID` column holds requirement IDs.
- `--changed-only origin/main`: report only rows whose line changed versus the base ref (uses `git diff`; falls back to all rows if git is unavailable).
- Rules are configurable in `schema.json` under `lint.disable`, `lint.severity`, `lint.extra_weak_words`, `lint.allow_words`.

Rule registry (IDs are stable; never rename one):

| Rule | Default | Detects | Example that fires | Fix hint |
| --- | --- | --- | --- | --- |
| `weak-word` | error | Vague qualifiers with no measurable meaning | `quickly`, `user-friendly`, `appropriate`, `fast`, `easy`, `flexible`, `robust`, `efficient`, `adequate`, `as soon as possible`, `etc.`, `and/or`, `if possible`, `normally`, `sufficient`, `state-of-the-art`, `seamless`, `intuitive`, `minimal`, `optimal`, `reasonable`, `several`, `some`, `various`, `approximately` | Replace with a measurable criterion or a reference to a defined term |
| `universal-quantifier` | warning | Absolute claims that are rarely true and hard to verify | `all`, `every`, `always`, `never`, `none`, `each and every`, `any` (as "every"), `no one`, `nothing`, `everything` | Bound the scope or name the exceptions |
| `passive-voice` | warning | Passive construction with no actor | `is validated`, `shall be stored`, `are notified` without `by <actor>` | Name the actor: `the system shall validate` |
| `nominalization` | info | Process words hiding who does what | `validation of`, `processing`, `management of`, `handling of`, `the creation of` | Use the verb with an actor |
| `incomplete-condition` | error | A condition with no consequence, or `IF` without `THEN` in unwanted-behavior form, or `WHEN`/`WHILE`/`WHERE`/`IF` with no `shall`/`should`/`may` | `WHEN the user logs in, the balance` | Complete the EARS pattern |
| `missing-obligation` | error | No `shall`/`should`/`may`/`must` and not a user story (`As a ..., I want ...`) | `The system displays the balance` | Add the obligation verb that matches the binding level |
| `future-tense` | warning | `will` used as the obligation verb | `The system will log every refund` | `will` states a fact; use `shall` if it is required |
| `compound-requirement` | warning | More than one obligation verb, or `and`/`or` joining two actions under one `shall` | `shall export the file and email the user` | Split into one requirement per sentence |
| `open-tbd` | info | `TBD`, `TBC`, `??`, `XXX` in text or attributes | `within TBD ms` | Resolve the open question; keep the ID |
| `duplicate-id` | error | Same ID twice in one register (or across registers in the same run) | two `R-012` rows | Allocate a new ID with `re-lint ids next` |
| `invalid-id` | error | ID not matching the schema pattern | `REQ12` | Use the schema prefix and digits |
| `missing-attribute` | error | A required attribute empty (`schema.attributes.required`) | empty `Source` | Fill it; unknown values are `TBD` with an open question |
| `invalid-enum` | error | Attribute value outside `schema.attributes.enums` | `Type=NFR`, `Priority=high` | Use an allowed value |
| `unregistered-source` | warning | `Source` cites an `S-`/`SH-`/`I-` ID not found in the workspace (only when `sources.csv` / `stakeholders.md` exist) | `S-19` not in `sources.csv` | Register the source with `source-inventory` |
| `register-drift` | warning | A detail register echoes requirement text that differs from `requirements.csv` | `verification.csv` text for R-012 is stale | Copy the current text or drop the echo |

`TBD` is a valid placeholder in any attribute: it is reported by `open-tbd`, never by `missing-attribute` or `invalid-enum`, so unknowns stay visible without failing CI. Teams that want `TBD` to block a release run `--fail-on info` on the release branch.

Text rules (`weak-word` .. `open-tbd`) run on `Text`. Story-form requirements (`As a ..., I want ...`) skip `missing-obligation`, `future-tense` and `passive-voice`. Rows with status `withdrawn` or `rejected` only get the structural rules. Each finding has `rule`, `severity`, `id`, `file`, `line`, `column` (where known), `match`, `message`, `hint`.

### `re-lint ids` (vendored as `re_ids.py`)

```text
re-lint ids next [--kind requirement|source|stakeholder|interview|candidate|conflict|decision|open-decision|change|finding] [--count N] [--workspace DIR]
re-lint ids check [PATH ...]      # duplicates, pattern, required attributes (structural subset of `check`)
re-lint ids list [--kind KIND]    # every ID in the workspace with its file:line
```

`next` scans every file under the workspace (and `git log` messages if available) for the kind's prefix, takes the highest number including withdrawn IDs, and prints the next free IDs zero-padded to the schema's digits, one per line.

### `re-lint trace` (vendored as `trace_matrix.py`)

```text
re-lint trace build [--repo DIR] [--out DIR] [--since REV] [--code-glob G ...] [--test-glob G ...] [--format text|json]
re-lint trace impact ID [ID ...] [--trace FILE] [--format text|json|md]
re-lint trace gaps [--trace FILE] [--format text|json|github] [--fail-on-gaps]
```

`build` reads requirement IDs from the workspace registers, then finds references in: `sources.csv` (backward), `decisions/*.md` and ADR folders (`docs/adr`, `doc/adr`, `adr`), code files, test files (by glob and by test names such as `test_r_012_*` or `R-012` in a docstring/annotation), and `git log` messages. Writes `<out>/trace.csv` (`From,FromType,To,ToType,Relation,Evidence`), `<out>/trace.md` (coverage summary, Mermaid `graph LR`, gap tables) and `<out>/gaps.json`. Default `--out` is `<workspace>/trace`.

Gaps reported: requirements without tests, requirements without a source, tests citing unknown or retired IDs, code citing unknown or retired IDs, agreed requirements without any implementation reference.

### `re-lint baseline` (vendored as `baseline.py`)

```text
re-lint baseline create NAME [--message TEXT] [--tag]      # writes <workspace>/baselines/NAME.json; --tag also creates git tag req-NAME
re-lint baseline diff OLD NEW [--format md|json]           # OLD/NEW are baseline names or files; NEW may be "working"
re-lint baseline notes OLD NEW                             # requirement release notes in Markdown
```

Manifest: `{"name", "created", "git_commit", "message", "requirements": [{"ID","Version","Status","Type","Priority","text_sha256"}]}`. Diff classes: added, changed (text or attributes), status-changed, withdrawn, removed.

### `re-lint views` (vendored as `views.py`)

```text
re-lint views [--view NAME ...] [--out DIR] [--format md|csv]
```

Views are defined in `schema.json` under `views` (selective = row filter, projective = column list, aggregating = group-by counts). Built-in views: `po`, `architect`, `qa`. Writes `<workspace>/views/<name>.md`.

### `re-lint prioritize` (vendored as `prioritize.py`)

```text
re-lint prioritize ITEMS.csv [--weights benefit=2,penalty=1,cost=1,risk=0.5] [--method wiegers|wsjf] [--tie-band 0.05] [--out FILE]
```

Wiegers: `priority = (benefit*wb + penalty*wp) / (cost*wc + risk*wr)` on relative percentages; WSJF: `(business value + time criticality + risk reduction) / job size`. Items within `--tie-band` of each other are flagged `tie, do not over-interpret`. Output CSV adds `Score,Rank,Tie`.

### `re-lint reqif` (vendored as `reqif_bridge.py`)

```text
re-lint reqif export [--out FILE] [--ids ...] [--title TEXT]
re-lint reqif import FILE [--diff] [--apply]
```

Minimal ReqIF 1.2 with one `SPEC-OBJECT-TYPE` and `ATTRIBUTE-DEFINITION-STRING` per CSV column; `IDENTIFIER` is the requirement ID so round-trips merge cleanly. `import --diff` prints a requirement-level diff against the workspace; `--apply` writes changes into `requirements.csv`. Full-fidelity tool exchange can use the `reqif` library from strictdoc instead.

### `re-lint openspec` (vendored as `to_openspec.py`)

```text
re-lint openspec CHANGE_NAME [--ids R-001,R-002 | --status agreed] [--target openspec|spec-kit] [--out DIR] [--force]
```

OpenSpec: writes `openspec/changes/<change>/proposal.md`, `tasks.md`, and `specs/<capability>/spec.md` with `### Requirement:` blocks, `SHALL` text and `#### Scenario:` blocks (WHEN/THEN) taken from acceptance criteria. spec-kit: writes `specs/<change>/spec.md`. Every requirement keeps its ID as an anchor (`<!-- R-012 -->` and in the heading).

### `re-lint issues` (vendored as `issue_sync.py`)

```text
re-lint issues plan  --tracker github|jira|ado [--ids ...]          # what push would do, JSON + table; no network
re-lint issues push  --tracker github|jira|ado [--ids ...] [--apply]
re-lint issues pull  --tracker github|jira|ado [--apply]            # refresh Status in requirements.csv from the tracker
```

Dry run unless `--apply`. GitHub uses the `gh` CLI; Jira uses `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT`; Azure DevOps uses `ADO_ORG_URL`, `ADO_PROJECT`, `ADO_PAT`. Issue title is `<ID>: <Title or first 80 chars of Text>`; the body carries the text, attributes and trace links in a fenced block delimited by `<!-- re-skills:begin -->` / `<!-- re-skills:end -->` so re-syncs replace only that block. Status mapping is configurable under `schema.json` → `issues.status_map`.

## GitHub Action (`action.yml` at the repo root)

So teams can gate pull requests without installing anything:

```yaml
- uses: renzrollon/hairspring@v0.1.0
  with:
    paths: ""            # default: the workspace registers
    fail-on: error        # error | warning | info
    format: github        # annotations on the PR diff
    schema: ""           # default: requirements/schema.json
    changed-only: ""     # e.g. origin/main to lint only changed rows
    trace-gaps: "false"  # "true" also runs `re-lint trace build` and `trace gaps --fail-on-gaps`
```

The action installs `packages/re-lint` from the action's own checkout (`pip install "$GITHUB_ACTION_PATH/packages/re-lint"`), so it never needs PyPI. A copy-paste workflow lives in `docs/ci/requirements-lint.yml`.
