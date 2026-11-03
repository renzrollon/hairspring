---
name: baseline
description: >-
  Cuts a named requirements baseline with re-lint baseline create: a manifest of every requirement
  ID with version, status, type, priority and a text hash, saved as
  requirements/baselines/{name}.json, optionally with git tag req-{name}. Diffs two baselines, or
  a baseline against the working register (added, changed, status-changed, withdrawn, removed),
  and writes requirement release notes in which every change cites its change request or decision
  record, and changes without one are flagged as uncontrolled. Started explicitly with /baseline.
  Use when a release, contract signature, audit or vendor hand-over needs a frozen set ("freeze
  the requirements", "what changed since v1.0", "requirement release notes"), or when a customer
  asks which requirement versions a delivery covers. Not for scoping one pending change
  (change-impact), test coverage (traceability-matrix), exporting requirements to a customer's
  tool (reqif-bridge), or adding attributes or lifecycle states (attribute-schema).
license: MIT
compatibility: Python 3.9+ optional for scripts/baseline.py; works without it.
disable-model-invocation: true
argument-hint: "[create NAME | diff OLD NEW | notes OLD NEW]"
metadata:
  stage: management
  invocation: user
  priority: P2
  ireb-anchor: "CPRE FL Handbook 1.2 §6.3–6.4"
  inputs-from: "requirement-phrasing, change-impact, conflict-to-decision, attribute-schema, prioritization"
  outputs-to: "change-impact, spec-assembler, reqif-bridge, traceability-matrix"
  work-product: "requirements/baselines/<name>.json, requirements/baselines/<name>-notes.md"
  version: "0.1.0"
---

# Baseline

A baseline is the agreed state of the requirements at one point in time: the thing a release, a contract or an audit refers to. Without one, "what changed since we signed?" gets answered from memory. This skill freezes the register into a small manifest (IDs, versions, statuses, text hashes) and optionally tags the commit. It compares baselines and writes release notes in which every change points to the decision that allowed it.

## When not to use

- One pending change needs scoping and a decision: `/change-impact`.
- You want to know which requirements have tests: `traceability-matrix`.
- A customer needs the requirements in DOORS, Polarion or Jama: `/reqif-bridge`.
- You want to version the text of one requirement: that is its `Version` attribute, which `change-impact` updates.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` (and `stories/*.md`) | yes | `requirement-phrasing`, `change-impact` |
| Baseline name, purpose, and who approved it | yes, for `create` | the user |
| `requirements/baselines/*.json` | yes, for `diff` and `notes` | this skill |
| `requirements/changes/CR-*.md`, `requirements/decisions/RDR-*.md` | no, but the notes are incomplete without them | `change-impact`, `conflict-to-decision` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/baselines/<name>.json` | `assets/baseline.json`; rules in `references/manifest-and-diff.md` | `diff` and `notes`, `change-impact`, auditors |
| `requirements/baselines/<new>-notes.md` | `assets/release-notes.md` | release managers, customers, auditors |
| git tag `req-<name>` (only when asked) | created by `--tag`, not pushed | CI, auditors |

## Procedure

1. **Read the workspace.** Read `requirements.csv`, `schema.json`, every `baselines/*.json` (list the name, created date and message of each), and the `changes/` and `decisions/` folders.
2. **Pick the action.** Take it from the arguments: `create NAME`, `diff OLD NEW` or `notes OLD NEW`. If none is given, ask, and show the existing baselines.

**Create**

3. **Name and message.** The name uses letters, digits, `.`, `-` and `_` (`v1.0-contract`). If `baselines/NAME.json` already exists, stop. Baselines are never overwritten and this skill never passes `--force`, so propose a new name (`v1.0.1-contract`, `v1.1`). The message states the purpose, who approved it and the date; ask for whatever is missing.
4. **Pre-checks.** Run all of them, report the results together, then ask.
   - **Lint:** run `re-lint check`, or the `requirement-linter` skill. A duplicate or invalid ID blocks the baseline, because the manifest would be ambiguous. List other errors, and cut only if the user accepts them.
   - **Status mix:** count the rows by status. A release or contract baseline normally holds requirements that are `agreed` or later. List the `draft` and `proposed` rows and ask whether to cut anyway; the manifest records statuses, so it stays honest either way.
   - **Uncommitted changes (in a git repository):** run `git status --porcelain -- requirements/`. If the register has uncommitted changes, ask the user to commit first, because the manifest's `git_commit` must point at the content it describes.
   - **Deleted rows:** if an ID in the latest baseline is missing from the register, stop. Requirement rows are never deleted; restore the row with Status `withdrawn`.
5. **Cut.** Run `re-lint baseline create NAME --message "<message>"` (or `python3 <skill-dir>/scripts/baseline.py create ...`, same arguments). Add `--tag` only when the user asks for a git tag. It creates the local tag `req-NAME`; pushing it (`git push origin req-NAME`) is the user's decision, so say so. Outside a git repository, `git_commit` is `null`; say so. Without Python, write the manifest by hand from `assets/baseline.json`, following `references/manifest-and-diff.md`.
6. **Check the manifest.** `name`, `created`, `git_commit` and `message` must be present, with one entry per register row, withdrawn rows included. Compare the entry count with the register.

**Diff and notes**

7. **Resolve OLD and NEW.** Each is a baseline name or a manifest path; NEW may also be `working`, the current register. If NEW is a release that has no baseline yet, offer to cut it first (steps 3 to 6).
8. **Diff.** Run `re-lint baseline diff OLD NEW --format json` (or `baseline.py diff ...`) (or `--format md` to show the user). The classes are added, changed, status-changed, withdrawn and removed; they are defined in `references/manifest-and-diff.md`.
9. **Write the notes.** Run `re-lint baseline notes OLD NEW --out requirements/baselines/<NEW>-notes.md` (or `baseline.py notes ...`). This writes the generated part of `assets/release-notes.md`. Notes against `working` are a preview: show them and do not save them. Without Python, fill the generated part from the diff by hand.
10. **Add the review part.** Append the comment line and the review sections of `assets/release-notes.md` under the generated part; do not edit the generated bullets. For every changed, status-changed or withdrawn row without a `Decision:`, search `changes/CR-*.md` and `decisions/RDR-*.md` for the ID, and record what you find or `none found`. Never invent a link. List the `changed` and `withdrawn` rows that still have none and were `agreed` or later in OLD under "Uncontrolled changes", ask the user about them, and recommend `/change-impact` to document each one after the fact. List removed rows as errors, with the action "restore as withdrawn".
11. **Report.** Give the counts per class, the uncontrolled changes, and the paths of the files written.

## Quality checks

- [ ] No existing baseline file was modified or overwritten.
- [ ] The manifest has one entry per register row (withdrawn included), each with `ID`, `Version`, `Status`, `Type`, `Priority` and `text_sha256`. `git_commit` refers to committed content, or is `null` outside git, which the message says.
- [ ] Every changed, status-changed or withdrawn row has a decision link: in the generated `Decision:`, or in the review table as an ID that exists or `none found`.
- [ ] Every `changed` or `withdrawn` row with `none found` that was `agreed` or later in OLD is listed under Uncontrolled changes.
- [ ] No requirement row was deleted, and this skill changed no `Status`.
- [ ] A git tag was created only when asked, and was not pushed.

## Hand-offs

- **Next:** suggest `/change-impact` for each uncontrolled change. Use `traceability-matrix` to record trace coverage for a release baseline. Suggest `/reqif-bridge` or `/spec-assembler` to hand the baselined set to a customer.
- **Feeds back to:** `requirement-linter` when the lint pre-check fails, and `attribute-schema` when the team wants `Version` or other attributes tracked from the next baseline on.

## Non-interactive mode

Create a baseline only when the name and the message are given and the lint pre-check finds no duplicate or invalid IDs. Never overwrite a baseline, never tag unless asked, and never delete or edit requirement rows. Write the notes, and end with the uncontrolled changes and any `draft` or `proposed` rows the baseline contains.

## References

- `references/manifest-and-diff.md`: naming, the exact manifest format and hash rule, diff classes and their precedence, release-note rules, and uncontrolled changes. Read it at steps 3, 5 and 8 to 10.
- `references/ireb-anchor.md`: the handbook sections and glossary terms this skill applies.
- `examples/`: the `v1.1` baseline of the loyalty-points sample and its release notes against `v1.0-contract`.
