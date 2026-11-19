---
name: traceability-matrix
description: >-
  Builds and refreshes the requirements trace matrix (source → requirement → decision/ADR → code →
  test) by running the bundled tracer, which reads requirement IDs from registers, decision
  records, code annotations, test names and commit messages. Writes requirements/trace/trace.csv
  and trace/trace.md: coverage counts, a Mermaid graph and a gap report (requirements without
  tests, tests or code citing unknown or withdrawn IDs, agreed requirements with no
  implementation), and lists tests and code that cite no requirement. Use when someone asks "which
  requirements have no tests", "build the trace matrix", "what covers R-041", "traceability for
  the audit", before a release, audit or design review, after a batch of requirement changes, to
  set up a nightly trace job or release gate in CI, or for the conventions for citing requirement
  IDs in commits and tests. Not for scoping one change request (use change-impact), adding
  verification methods (testability-check), or pushing issues to a tracker (issue-sync).
license: MIT
compatibility: Python 3.9+ optional for scripts/trace_matrix.py; works without it.
metadata:
  stage: management
  invocation: model
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §6.6"
  inputs-from: "requirement-phrasing, source-inventory, conflict-to-decision, testability-check, re-ids"
  outputs-to: "change-impact, issue-sync, requirements-review, baseline, spec-assembler"
  work-product: "requirements/trace/trace.csv, requirements/trace/trace.md"
  version: "0.1.0"
---

# Traceability matrix

Trace links answer what an auditor and a tester both ask: where did this requirement come from, and what shows it is built and tested? Links cost nothing when IDs are already in commits, code and tests, and a lot when they are reconstructed before an audit. This skill runs the deterministic tracer over the repository, writes the matrix and the gap report, and turns the gaps into a short, triaged list someone can act on.

## When not to use

- Scoping one change request ("what does raising the limit touch?"): suggest `/change-impact`, which reads this matrix.
- A requirement has no verification method or acceptance criterion yet: `testability-check` first; the tracer cannot find a test nobody planned.
- Creating tracker issues from the gaps: draft them here, then recommend `/issue-sync`.
- Comparing requirement versions between releases: suggest `/baseline`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` | yes | `requirement-phrasing`, `re-ids` |
| `requirements/schema.json` (`trace` globs, ID patterns) | no (defaults apply) | `re-setup`, `attribute-schema` |
| `requirements/sources.csv` | no | `source-inventory` |
| `requirements/decisions/*.md`, ADR folders (`docs/adr`, ...) | no | `conflict-to-decision` |
| `Verification` column or `requirements/verification.csv` | no | `testability-check` |
| Code, tests and commit messages that cite IDs | yes, for useful coverage | developers, following `references/citation-conventions.md` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/trace/trace.csv` | `assets/trace.csv`: `From,FromType,To,ToType,Relation,Evidence` | `change-impact`, `requirements-review`, `baseline`, `spec-assembler` |
| `requirements/trace/trace.md` | `assets/trace.md`: coverage summary, Mermaid graph, gap tables | reviewers, auditors, `issue-sync` |
| `requirements/trace/gaps.json` | written by the script | CI |
| `.github/workflows/requirements-trace.yml` (only when asked) | `assets/trace-gate.yml` | CI |

## Procedure

1. **Read the workspace.** Locate `requirements/` (or the `workspace` in `requirements/schema.json`). Read `schema.json` → `trace` (`code_globs`, `test_globs`, `adr_dirs`, `scan_git_log`); if it is missing, the defaults apply, and you say so in the final message. List the repo's top-level folders. If code or tests sit outside the globs (`web/__tests__/`, `modules/`), note the extra globs for step 2.
2. **Build.** Run `re-lint trace build` if the package is installed, else `python3 <skill-dir>/scripts/trace_matrix.py build` (same flags). For extra folders from step 1, pass `--code-glob` / `--test-glob`. These replace the `schema.json` globs for the run, so list the existing globs too, and propose adding the new ones to `schema.json` → `trace` so CI sees them. Add `--since <rev>` only to limit the commit-message scan on a very long history. Exit code 2 means a usage or parse error: fix the cause and run again. Never hand-edit `trace.csv` after a script run; change the inputs and rebuild.
   Without Python: search the repository for the ID forms in `references/citation-conventions.md`, then fill `assets/trace.csv` and `assets/trace.md` by hand, and write "built manually" in the trace.md header.
3. **Read the gaps.** Run `re-lint trace gaps --format json` (or `trace_matrix.py gaps --format json`) and read the coverage summary in `trace/trace.md`. The gap kinds and their meaning are in `references/trace-format.md`.
4. **Triage.** Sort every gap into one of these, using the requirement's `Status` and `Verification`:
   - **Fix first:** an `implemented` or `verified` requirement with no test. Its status claims more than the evidence shows.
   - **Real gap:** an `agreed` requirement with verification `test` (or empty) and no test, or with no implementation reference.
   - **Not a test gap:** verification is `inspection`, `analysis` or `demonstration`. The evidence belongs in `Links`, not in a test.
   - **Informational:** `draft` or `proposed` requirements. No test is expected yet.
   - **Stale citation:** a test or code cites a withdrawn, rejected or unknown ID. The cause is an obsolete test, a typo (`R-41`), or a requirement nobody registered. Ask the requirement owner which one it is. Never reactivate a requirement to silence a gap.
   - **Unlinked (informational):** a test or code file under the globs appears in no `trace.csv` row. The script does not report these; find them yourself. Ask whether a requirement is missing (then `requirement-phrasing`) or only the citation is missing. Helpers and glue code stay unlinked.
5. **Explain the conventions when coverage is low.** If most requirements have no code or test link, the team is probably not citing IDs yet. Show the short convention block from `references/citation-conventions.md` for the repo's languages. Add an ID to an existing test only when the user confirms that the test really checks that requirement.
6. **Report.** End with the coverage counts (copied from `trace.md`), the triaged gaps (fix-first items at the top), and a draft issue list with one row per gap: `Title` (`<ID>: <gap>`), `Evidence`, `Owner role`. Recommend `/issue-sync`, or the team's tracker, to file them. See `references/ci-and-issues.md`.
7. **Set up CI (only when asked).** Copy `assets/trace-gate.yml` to `.github/workflows/requirements-trace.yml`. The nightly run reports gaps. A release tag fails on gaps. Explain both in two lines, and read `references/ci-and-issues.md` for the variants.

## Quality checks

- [ ] `trace/trace.csv` has the header `From,FromType,To,ToType,Relation,Evidence`, and every row has Evidence (`path:line`, or a short hash for a commit).
- [ ] Every link comes from the script or from a search hit you can cite. No link is inferred from file names or guessed.
- [ ] No test, code file or requirement was edited to close a gap unless the user confirmed that it reflects reality.
- [ ] No requirement `Status` was changed. Only the owner sets `verified`, and only with evidence.
- [ ] The gap counts in your message match `trace/trace.md`.

## Hand-offs

- **Next:** suggest `/change-impact` for change requests (it reads `trace.csv`) and `/issue-sync` to file the gap issues. Run `testability-check` for requirements that have no verification method.
- **Feeds back to:** `requirement-phrasing` when code or tests cite IDs that are not registered. `source-inventory` when a requirement has no registered source. `attribute-schema` to store extra trace globs in `schema.json`.

## Non-interactive mode

For a nightly job or "don't ask": run `build` and `gaps`, write the trace files, and do not edit code, tests or requirements. End with the summary, the triaged gaps and the draft issue list.

## References

- `references/trace-format.md`: the type and relation vocabulary of `trace.csv`, the sections of `trace.md`, and the gap kinds. Read it at step 3.
- `references/citation-conventions.md`: how to cite IDs in commits, PRs, code and tests (pytest, jest/vitest, JUnit, Go). Read it at step 5 or when asked "how do we tag tests?".
- `references/ci-and-issues.md`: nightly job, release gate, composite action, and turning gaps into issues. Read it at step 7.
- `references/ireb-anchor.md`: the handbook section and glossary terms this skill applies.
- `examples/`: a loyalty-points repo snapshot with its `trace.csv`, `trace.md` and final message.
