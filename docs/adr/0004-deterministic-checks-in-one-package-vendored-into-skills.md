# ADR 0004: Deterministic checks live in one package and are vendored into skills

- Status: accepted
- Date: 2026-11-03

## Context

Design principle 6: whatever can be checked by a script is checked by a script, so it can run in CI. Skills are installed one folder at a time (`npx skills add`, plugin installs, manual copies), so a skill cannot import code from a sibling folder. Maintaining several copies of the same linter by hand would drift.

## Decision

- The single source of truth is `packages/re-lint` (stdlib-only Python 3.9+, CLI `re-lint`).
- Each command module is one self-contained file that imports only the standard library and `reqio.py`.
- `tools/vendor_scripts.py` copies modules into the skills that need them (`scripts/<name>.py` + `scripts/reqio.py`), with a "do not edit" header. CI runs `--check` and fails on drift.
- The same code is exposed as a composite GitHub Action (`action.yml`) that installs the package from the action checkout, so CI never depends on PyPI availability.

## Consequences

- A skill installed alone still runs its checks; a team that only wants CI uses the Action or `pip install`.
- Contributors edit only `packages/re-lint`; vendored copies are regenerated.
- Some duplication in the installed footprint (a few hundred KB). Accepted.
