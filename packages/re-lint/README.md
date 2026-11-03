# re-lint

Deterministic requirement checks for the [re-skills](https://github.com/renzrollon/hairspring) catalogue: weak words, universal quantifiers, passive voice, incomplete EARS conditions, missing obligation verbs, compound requirements, open TBDs, duplicate or malformed IDs, empty required attributes and values outside the schema enums. It runs the same way on a laptop, in a skill's `scripts/` folder and in CI, so a red build means the same thing everywhere.

- Python 3.9+, standard library only, no runtime dependencies.
- Reads `requirements/requirements.csv` (and Markdown tables with requirement IDs) in the shape the re-skills catalogue writes.
- Output for people (`text`), machines (`json`), pull requests (`github` annotations) and code scanning (`sarif`).

## Install

```bash
# From GitHub (works today)
pip install "git+https://github.com/renzrollon/hairspring#subdirectory=packages/re-lint"

# Pin a release
pip install "git+https://github.com/renzrollon/hairspring@v0.1.0#subdirectory=packages/re-lint"

# From PyPI, once published
pip install re-lint          # or: pipx install re-lint
```

Check the install with `re-lint --version`. `python3 -m re_lint` works too.

## Quick start

From the root of a repository that has a `requirements/` workspace:

```console
$ re-lint check
requirements/requirements.csv:14: error weak-word R-012: weak word "quickly" has no measurable meaning
    hint: Replace with a measurable criterion or a reference to a defined term
requirements/requirements.csv:19: warning passive-voice R-017: passive voice "shall be stored" names no actor
    hint: Name the actor: `the system shall validate`
requirements/requirements.csv:22: info open-tbd R-020: open placeholder "TBD" in Text
    hint: Resolve the open question; keep the ID
re-lint: 1 error, 1 warning, 1 info in 20 rows (1 file)
$ echo $?
1
```

Allocate IDs the same way every skill does:

```console
$ re-lint ids next --count 2
R-021
R-022
```

## Commands

| Command | What it does |
| --- | --- |
| `re-lint check [PATH ...]` | Lint requirement text and attributes (the CI gate). |
| `re-lint ids next\|check\|list` | Allocate the next free IDs, check registers for duplicate or malformed IDs, list every ID with its `file:line`. |
| `re-lint trace`, `baseline`, `views`, `prioritize`, `reqif`, `openspec`, `issues` | Traceability, baselines, views, prioritization and bridges; see [`docs/tooling-contract.md`](../../docs/tooling-contract.md). |

`re-lint --help` lists every command; `re-lint COMMAND --help` explains every flag.

Exit codes for every command: `0` clean, `1` findings at or above `--fail-on`, `2` usage, schema or parse error.

## `re-lint check`

```text
re-lint check [PATH ...] [--schema FILE] [--format text|json|github|sarif]
              [--fail-on error|warning|info] [--disable RULE[,RULE]] [--enable RULE[,RULE]]
              [--only-ids R-001,R-002] [--changed-only BASE_REF] [--list-rules]
```

| Flag | Meaning |
| --- | --- |
| `PATH` | `.csv` or `.md` files, or workspace folders. Default: `<workspace>/requirements.csv` plus Markdown tables under the workspace whose `ID` column holds requirement IDs. |
| `--schema FILE` | Schema to use. Default: `<workspace>/schema.json`, else `requirements/schema.json` at the repo root, else the built-in defaults. |
| `--format` | `text` (default), `json`, `github` (workflow annotations on the PR diff), `sarif` (SARIF 2.1.0 for code scanning). |
| `--fail-on` | Exit `1` when a finding has this severity or higher. Default `error`. |
| `--disable`, `--enable` | Turn rules off or on for this run (repeatable or comma-separated). `--enable` overrides `lint.disable`. |
| `--only-ids` | Report only these requirement IDs (plus header-level problems). |
| `--changed-only BASE_REF` | Report only rows added or changed since the merge base with `BASE_REF` (via `git diff -U0`). Untracked files count as changed. Falls back to all rows, with a warning, when git cannot answer. |
| `--list-rules` | Print the rule registry and exit. |

How files are read:

- `requirements.csv` (or any CSV with `ID`, `Text` and one of `Type`, `Status`, `Priority`, `Source`) is a **register**: every rule applies, and an ID may appear once across all registers in a run. A Markdown table whose header has every required attribute is a register too.
- Any other table holding requirement IDs is a **view** (a story file, a spec chapter, a report). A row whose ID is in a register is an echo: only `register-drift` checks it. A row whose ID is in no register gets the text rules on its `Text` column, once per ID; IDs, attributes and enums are not checked in views, because reports hold transitions (`agreed -> To Do`) and scores that are not attribute values.
- In the default run, other CSV files under the workspace (`verification.csv`, `constraints.csv`, ...) are scanned for stale echoes only. Generated outputs (`trace/`, `views/`, `baselines/`, `exports/`) and historical records (`changes/`, `decisions/`, `reviews/`) are skipped.

## Rules

Rule IDs are stable and never renamed.

| Rule | Default | Detects | Example that fires | Fix hint |
| --- | --- | --- | --- | --- |
| `weak-word` | error | Vague qualifiers with no measurable meaning | `quickly`, `user-friendly`, `appropriate`, `fast`, `easy`, `as soon as possible`, `etc.`, `and/or`, `some` | Replace with a measurable criterion or a reference to a defined term |
| `universal-quantifier` | warning | Absolute claims that are rarely true and hard to verify | `all`, `every`, `always`, `never`, `none`, `any` (as "every"), `no one`, `everything` | Bound the scope or name the exceptions |
| `passive-voice` | warning | Passive construction with no actor | `is validated`, `shall be stored`, `are notified` without `by <actor>` | Name the actor: `the system shall validate` |
| `nominalization` | info | Process words hiding who does what | `validation of`, `processing`, `management of` | Use the verb with an actor |
| `incomplete-condition` | error | A condition with no consequence, `IF` without `THEN`, or `WHEN`/`WHILE`/`WHERE`/`IF` with no obligation verb | `WHEN the user logs in, the balance` | Complete the EARS pattern |
| `missing-obligation` | error | No `shall`/`should`/`may`/`must` and not a user story | `The system displays the balance` | Add the obligation verb that matches the binding level |
| `future-tense` | warning | `will` used as the obligation verb | `The system will log every refund` | `will` states a fact; use `shall` if it is required |
| `compound-requirement` | warning | More than one obligation verb, or `and`/`or` joining two actions under one `shall` | `shall export the file and email the user` | Split into one requirement per sentence |
| `open-tbd` | info | `TBD`, `TBC`, `??`, `XXX` in text or attributes | `within TBD ms` | Resolve the open question; keep the ID |
| `duplicate-id` | error | Same ID twice in one register, or across registers in one run | two `R-012` rows | Allocate a new ID with `re-lint ids next` |
| `invalid-id` | error | ID not matching the schema pattern | `REQ12` | Use the schema prefix and digits |
| `missing-attribute` | error | A required attribute (`schema.attributes.required`) is empty, or its column is missing | empty `Source` | Fill it; unknown values are `TBD` with an open question |
| `invalid-enum` | error | Attribute value outside `schema.attributes.enums` | `Type=NFR`, `Priority=high` | Use an allowed value |
| `unregistered-source` | warning | `Source` cites an `S-`/`SH-`/`I-` ID not found in the workspace (only when `sources.csv` / `stakeholders.md` exist) | `S-19` not in `sources.csv` | Register the source with `source-inventory` |
| `register-drift` | warning | A detail register echoes requirement text that differs from `requirements.csv` | `verification.csv` text for R-012 is stale | Copy the current text or drop the echo |

The full word lists live in [`skills/validation/requirement-linter/references/rules.md`](../../skills/validation/requirement-linter/references/rules.md), generated from the registry in `lint.py`.

How the rules apply:

- `TBD` is a valid placeholder in any attribute. `open-tbd` reports it (info); `missing-attribute` and `invalid-enum` never do, so unknowns stay visible without failing CI. Run `--fail-on info` on a release branch to block on open TBDs.
- Story-form requirements (`As a ..., I want ...`) skip `missing-obligation`, `future-tense` and `passive-voice`.
- Rows with status `withdrawn` or `rejected` only get the structural rules.
- Quoted (`"..."`) and backticked spans are not linted as prose.
- In EARS sentences, `universal-quantifier`, `passive-voice` and `compound-requirement` look at the response clause, so a condition such as `WHILE the account is locked` is not reported.
- Errors are tuned for precision: when a heuristic is unsure, it stays quiet.

## Configuration

Rules are configured in `requirements/schema.json` (see the `re-setup` and `attribute-schema` skills):

```json
{
  "lint": {
    "disable": ["nominalization"],
    "severity": {"passive-voice": "error", "open-tbd": "off"},
    "extra_weak_words": ["blazing"],
    "allow_words": ["Flexible Spending Account"]
  }
}
```

| Key | Meaning |
| --- | --- |
| `lint.disable` | Rules that never run. |
| `lint.severity` | Per-rule `error`, `warning`, `info` or `off`. |
| `lint.extra_weak_words` | More words or phrases for `weak-word`. |
| `lint.allow_words` | Words or phrases (glossary terms) never reported by `weak-word`, `universal-quantifier` or `nominalization`. |

ID prefixes and digits (`ids`), required attributes (`attributes.required`) and allowed values (`attributes.enums`) come from the same file. Precedence: built-in defaults, then `schema.json`, then `--disable`, then `--enable`.

## `re-lint ids`

```text
re-lint ids next [--kind KIND] [--count N] [--workspace DIR] [--no-git]
re-lint ids check [PATH ...] [--format text|json|github]
re-lint ids list [--kind KIND] [--all] [--format text|json]
```

- `next` scans every file under the workspace and the `git log` messages of all refs for the kind's prefix, takes the highest number in use (withdrawn and rejected IDs included, so an ID is never reused) and prints the next free IDs zero-padded to the schema's digits, one per line. Kinds: `requirement`, `source`, `stakeholder`, `interview`, `candidate`, `conflict`, `decision`, `open-decision`, `change`, `finding`.
- `check` reports duplicate IDs, IDs that do not match the schema pattern and empty required attributes in the registers that define IDs (`requirements.csv`, `sources.csv`, `stakeholders.md`, `candidates.csv`, `conflicts.md`, and the file names in `decisions/` and `changes/`).
- `list` prints every ID with the `file:line` that defines it (`--all` for every mention).

## CI

### GitHub Action

```yaml
# .github/workflows/requirements-lint.yml
on:
  pull_request:
    paths: ["requirements/**"]
jobs:
  re-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0              # only needed for changed-only
      - uses: renzrollon/hairspring@v0.1.0
        with:
          fail-on: error
          format: github              # annotations on the PR diff
          changed-only: origin/${{ github.base_ref }}   # optional: lint only the rows this PR touches
```

The action installs re-lint from its own checkout, so it never needs PyPI. Inputs: `paths`, `fail-on`, `format`, `schema`, `changed-only`, `trace-gaps`. A copy-paste workflow is in [`docs/ci/requirements-lint.yml`](../../docs/ci/requirements-lint.yml).

### Without the action

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install "git+https://github.com/renzrollon/hairspring@v0.1.0#subdirectory=packages/re-lint"
      - run: re-lint check --format github --fail-on error
```

For GitHub code scanning, write SARIF and upload it:

```yaml
      - run: re-lint check --format sarif > re-lint.sarif || true
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: re-lint.sarif
```

Other CI systems: run `re-lint check --format json` (or `text`) and use the exit code.

## Vendored copies in skills

Skills that need a command carry a copy of its module in `scripts/` (for example `skills/validation/requirement-linter/scripts/lint_requirements.py` with `reqio.py` next to it), so a skill installed on its own still works: `python3 <skill-dir>/scripts/lint_requirements.py --help`. The copies are produced by `tools/vendor_scripts.py` and checked in CI; edit the module here, never the copy.

## Development

```bash
pip install -e "packages/re-lint[dev]"
pytest packages/re-lint/tests
python3 tools/vendor_scripts.py          # refresh the vendored copies and rules.md
```

Each command module is a single file that imports only the standard library and `reqio`, and exposes `build_parser()`, `run(args)` and `main(argv=None)`.

## License

MIT. re-skills is independent of IREB and not endorsed by it.
