---
name: requirement-linter
description: >-
  Runs the deterministic re-lint checks on requirements/requirements.csv and the Markdown
  requirement tables under requirements/ (weak words, universal quantifiers, passive voice,
  incomplete EARS conditions, missing obligation verb, compound requirements, open TBDs, duplicate
  or invalid IDs, missing attributes, invalid enum values, register drift) and explains each
  finding with a rewrite. The script's exit code is the verdict; the model never overrides it. Use
  whenever requirement rows are written or edited, on any diff, branch or pull request that
  touches requirements/ (requirements.csv, stories/*.md), before committing them, when the
  requirements CI check fails, when someone asks to "lint my requirements", "check my
  requirements" or "why did re-lint fail", or to add the lint gate to GitHub Actions or a
  pre-commit hook. Not for judging adequacy, completeness or the set as a whole
  (requirements-review), rewriting statements into EARS (requirement-phrasing), or verification
  methods (testability-check).
license: MIT
compatibility: Python 3.9+ for scripts/lint_requirements.py (stdlib only) or the re-lint package; manual fallback via references/rules.md.
metadata:
  stage: validation
  invocation: model
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §3.2.1"
  inputs-from: "requirement-phrasing, user-story-refiner, quality-requirements, constraints-register, re-ids, testability-check"
  outputs-to: "requirement-phrasing, requirements-review, user-story-refiner"
  work-product: "Lint report (text, json, github or sarif) and exit code"
  version: "0.1.0"
---

# Requirement linter

Weak words, missing actors, half-written conditions and broken IDs are found faster and more reliably by a script than by a reader. This skill runs the `re-lint` checks, reports exactly what the script reports, and adds what a script cannot: why each finding matters and a concrete rewrite. It turns requirement quality into a CI gate like code lint.

## When not to use

- Judging whether requirements are adequate, necessary, complete or consistent as a set: suggest `/requirements-review` (it runs this linter first).
- Rewriting a batch of statements into EARS form: `requirement-phrasing` (it calls this linter at the end).
- Adding verification methods or measurable acceptance criteria: `testability-check`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` and Markdown tables with requirement IDs under `requirements/` (default), or the paths the user names | yes | `requirement-phrasing`, `user-story-refiner`, `quality-requirements` |
| `requirements/schema.json` (`lint` settings, enums, ID patterns) | no (defaults apply) | `re-setup`, `attribute-schema` |
| A git base ref, for `--changed-only` | no | the PR or branch |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| Lint report on stdout and the exit code (no file unless the user asks to save it) | `re-lint check` text, json, github or sarif format | `requirement-phrasing`, `requirements-review`, CI |
| Explanation table in the reply | `ID \| Rule \| Match \| Why it matters \| Suggested rewrite` | the author |
| CI files, only when asked: `.github/workflows/requirements-lint.yml`, `.git/hooks/pre-commit` | `assets/requirements-lint.yml`, `assets/pre-commit-hook.sh` | CI, the team |

## Procedure

1. **Locate.** From the repo root, find `requirements/` (or the `workspace` named in `requirements/schema.json`). Run from the repo root so report paths are repo-relative.
2. **Run.** `re-lint check [PATH ...] [flags]` when the package is installed, else `python3 <skill-dir>/scripts/lint_requirements.py [PATH ...] [flags]` (same flags). No PATH = the whole workspace. On a branch or pull request, add `--changed-only <base>` (ask for the base if the PR does not name it; `HEAD` for uncommitted edits). Without Python: apply `references/rules.md` row by row, report in the same line format, and say the result is manual and has no exit code.

   | Flag | Use it to |
   | --- | --- |
   | `--only-ids R-020,R-021` | check only rows you just wrote |
   | `--changed-only origin/main` | report only rows changed versus a base ref (PRs) |
   | `--format json` | read findings as data (`rule, severity, id, file, line, column, match, message, hint`) |
   | `--format github` / `--format sarif` | annotations on a PR / code scanning upload |
   | `--fail-on warning` | make warnings fail too (default: `error`) |
   | `--disable RULE` / `--enable RULE` | one-off override; lasting settings go in `schema.json` |
   | `--list-rules` | print the rule registry |

3. **Read the result.** Exit `0` = no finding at or above `--fail-on`; `1` = findings; `2` = usage, schema or parse error. On `2`, fix the cause first (invalid JSON in `schema.json`, no `ID` column, unknown rule name, file not found) and run again; do not interpret findings. In text format each finding is `<file>:<line>: <severity> <rule> <ID>: <message>`, then an indented `hint:` line, and the last line is the summary (`re-lint: 8 errors, 4 warnings, 2 info in 14 rows (1 file)`).
4. **Explain.** Group findings by requirement ID. For each one write a row of the explanation table: the rule, the matched words, why it matters (one line from `references/rules.md`), and a suggested rewrite or fix from this table. Rows with Status `withdrawn` or `rejected` only get structural rules; say so if the user wonders why a weak word there passed.

   | Rule | Suggested fix (never invent a value) |
   | --- | --- |
   | `weak-word` | The measurable value from a source, or `TBD` plus a question to the owner ("within TBD seconds") |
   | `universal-quantifier` | Bound the scope ("a member with posted points"), or ask "are there exceptions?" |
   | `passive-voice` | Name the actor from the context or glossary; ask if it is unknown |
   | `nominalization` | The verb with an actor ("the admin console shall let support agents adjust ...") |
   | `incomplete-condition` | Complete the EARS pattern (`IF ..., THEN the <system> shall ...`) |
   | `missing-obligation`, `future-tense` | Decide fact or requirement; if required, use the verb matching the binding level the source gave (`shall` / `should` / `may`); ask if unknown |
   | `compound-requirement` | Split into one row per action; the second row gets a new ID from `re-ids` |
   | `open-tbd` | Answer the open question; keep the ID |
   | `duplicate-id`, `invalid-id` | Keep the first row's ID; give the other row a new ID from `re-ids`; never renumber |
   | `missing-attribute`, `invalid-enum` | Fill from the source or use an allowed value; `TBD` plus a question if nobody said (`high` is not `must` until the owner says so) |
   | `unregistered-source` | Register the source with `source-inventory`, or correct the citation |
   | `register-drift` | Rerun the skill owning the detail register (for `verification.csv`: `testability-check`) or copy the current text |

5. **Never override.** Report the exit code as the script returned it. Do not call a run "passing" while it exits `1`, and never edit the script, add `|| true` or `continue-on-error`, or change `schema.json` to make a run pass. If the author disputes a finding, offer exactly three ways out: rephrase the row; add a defined glossary term to `lint.allow_words`; or change the rule's level in `lint.severity` / `lint.disable`. The last two are team decisions: propose the `schema.json` change with a one-line reason for the PR description and apply it only when the user confirms.
6. **Hand over the rewrites.** This skill edits no requirement. When the author accepts rewrites, apply them with `requirement-phrasing` (same ID, `Version` + 1 if present), then rerun with `--only-ids` on the changed rows.
7. **Configure rules (when asked).** Lasting settings live in `schema.json` under `lint`: `disable` (rule IDs), `severity` (rule ID to `error` / `warning` / `info` / `off`), `extra_weak_words` (team-specific vague words), `allow_words` (defined terms that contain a weak word). Example: `"lint": {"severity": {"universal-quantifier": "error"}, "extra_weak_words": ["snappy"], "allow_words": ["Easy Redeem"]}`. Show the change and its reason; write it only after the user confirms.
8. **Add the gate (when asked).** GitHub Actions: copy `assets/requirements-lint.yml` to `.github/workflows/`; it uses `renzrollon/hairspring@v0.1.0` (inputs `paths`, `fail-on`, `format`, `schema`, `changed-only`, `trace-gaps`), lints only changed rows on pull requests, and shows the pip-install alternative in a comment. Pre-commit: copy `assets/pre-commit-hook.sh` to `.git/hooks/pre-commit` and make it executable; it runs only when staged files touch the workspace and blocks the commit on exit `1` or `2`. Leave existing workflows untouched.

## Quality checks

- [ ] The exit code and summary line in the reply are the ones the script printed.
- [ ] Every finding in the report appears in the explanation table; no finding was added or dropped by judgment.
- [ ] No suggested rewrite contains a number that is not in a source; unknowns are `TBD` with a question and an owner.
- [ ] No requirement, script, workflow or `schema.json` was changed without the user's confirmation.

## Hand-offs

- **Next:** `requirement-phrasing` to apply accepted rewrites; suggest `/requirements-review` once lint is clean.
- **Feeds back to:** `re-ids` for duplicate or invalid IDs; `source-inventory` for unregistered sources; `glossary` when an allowed word needs a definition; `testability-check` on `register-drift` in `verification.csv`.

## Non-interactive mode

In CI or when told not to ask: run, report and explain; change no file.

## References

- `references/rules.md`: the rule registry (generated from `re-lint`; do not edit). Read it at step 4 and for the manual fallback.
- `references/ireb-anchor.md`: handbook section and glossary terms.
- `examples/`: a seeded `requirements.csv`, the exact report the script prints, and the explanation table.
