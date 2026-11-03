---
name: to-openspec
description: >-
  Hands agreed requirements to coding agents as an OpenSpec change folder
  (openspec/changes/<change>/ with proposal.md, tasks.md and specs/<capability>/spec.md) or as a
  spec-kit specs/<feature>/spec.md. Functional requirements become SHALL requirements with
  WHEN/THEN scenarios from their acceptance criteria, quality requirements and constraints go into
  the proposal, and every R-ID stays in headings, scenarios and tasks so the trace survives
  implementation. Gated: only agreed or explicitly selected rows, and no lint errors or TBDs without
  your OK. Started explicitly with /to-openspec. Use when a reviewed set is ready to build, when
  someone says "hand this to OpenSpec", "make an OpenSpec proposal", "export to spec-kit", or before
  /opsx:apply or /speckit.plan on requirements kept in requirements/. Not for writing or fixing
  requirement text (requirement-phrasing), for reviewing the set first (requirements-review), or for
  tracker tickets (issue-sync).
license: MIT
compatibility: Python 3.9+ optional for scripts/to_openspec.py; the OpenSpec CLI is optional for validation. Works without either.
disable-model-invocation: true
argument-hint: "[change-name] [--ids R-001,R-002 | --status agreed] [--target openspec|spec-kit]"
metadata:
  stage: integration
  invocation: user
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §7.1"
  inputs-from: "requirement-phrasing, user-story-refiner, quality-requirements, constraints-register, testability-check, requirements-review"
  outputs-to: "traceability-matrix"
  work-product: "openspec/changes/<change>/ (or specs/<feature>/spec.md for spec-kit)"
  version: "0.1.0"
---

# To OpenSpec

Spec-driven toolkits start at "write the spec" and let the coding agent draft it. When the requirements were already elicited, agreed and checked, re-drafting them throws away the sources, the decisions and the IDs. This skill converts the agreed rows of `requirements/requirements.csv` into the change format a coding agent consumes, with a gate in front so nothing vague, unagreed or failing lint crosses silently. The work product is an OpenSpec change folder (or a spec-kit `spec.md`) in which every requirement, scenario and task carries its R-ID.

## When not to use

- The set is still draft or was never reviewed: suggest `/requirements-review` first, or run `requirement-linter` for a quick pass.
- Text needs rewriting (weak words, missing obligation verb, `TBD`): `requirement-phrasing`, then `clarifying-questions` for the missing values.
- You want tracker issues rather than a spec: `issue-sync`. A customer's DOORS, Polarion or Jama needs the set: `reqif-bridge`.
- Writing the technical design (`design.md`): that is the implementer's work in OpenSpec, not a requirements work product.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` (the rows to hand off) | yes | `requirement-phrasing`, `quality-requirements`, `constraints-register` |
| Acceptance criteria `R-nnn.ACn` in `requirements/stories/*.md` | no (scenarios are derived from EARS text otherwise) | `user-story-refiner` |
| `requirements/verification.csv` (verification method per R-ID) | no | `testability-check` |
| `requirements/schema.json`, `requirements/glossary.md`, `requirements/context.md` | no (defaults apply) | `re-setup`, `glossary`, `system-context` |
| `openspec/specs/` (capabilities that already exist) | no | OpenSpec `archive` |
| Change name, target (OpenSpec or spec-kit), one or two sentences of "why" | yes (ask) | the user |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `openspec/changes/<change>/proposal.md` | `assets/openspec/proposal.md` | reviewers, the coding agent |
| `openspec/changes/<change>/specs/<capability>/spec.md` (one per capability) | `assets/openspec/spec.md` | `openspec validate` / `archive`, the coding agent |
| `openspec/changes/<change>/tasks.md` | `assets/openspec/tasks.md` | the coding agent, `traceability-matrix` |
| `openspec/changes/<change>/.openspec.yaml` | `assets/openspec/openspec.yaml` | the OpenSpec CLI |
| or, for spec-kit, `specs/<NNN-feature>/spec.md` | `assets/spec-kit/spec.md` | `/speckit.clarify`, `/speckit.plan`, `/speckit.tasks` |

This skill never edits `requirements/requirements.csv`, never writes `openspec/specs/` (OpenSpec's `archive` does that) and never writes `design.md`.

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the default columns `ID,Type,Text,Source,Priority,Status,Rationale`; say so), `requirements.csv`, `glossary.md`, `stories/*.md`, `verification.csv` and `context.md` if they exist. Find the repo root. Check which toolkit the repo uses: an `openspec/` folder or a working `openspec --version` means OpenSpec; a `.specify/` folder means spec-kit. If both or neither, ask which target.
2. **Agree the selection and the name.** Default selection: every row with `Status=agreed` (`--status agreed`). If the user names IDs, use exactly those (`--ids`). Never select `withdrawn`, `rejected` or `deferred` rows, or `Priority=wont`. A named `draft` or `proposed` row goes across only after the user says so for that ID; record it. Show the selection (ID, Type, Status, Title or first words of Text). Ask for the change name: OpenSpec uses a verb-led kebab-case name (`add-voucher-redemption`); spec-kit uses `NNN-short-name` with the next free number under `specs/` (`004-voucher-redemption`).
3. **Run the hand-off gate.** Before writing anything, check every selected row:

   | Check | How | Default when it fails |
   | --- | --- | --- |
   | Lint errors | `re-lint check --only-ids <ids> --fail-on error`, or the `requirement-linter` skill; else `references/handoff-gate.md` by hand | leave the row out |
   | Open `TBD`, `TBC`, `??`, `XXX` in Text or attributes | search the rows | leave the row out |
   | Obligation is `should` or `may` | read the verb | ask: keep as `SHOULD`/`MAY` (`openspec validate --strict` then fails), or leave out; rephrasing is `requirement-phrasing`'s job and needs the owner's agreement |
   | No scenario source: no acceptance criterion and no `WHEN`/`IF`/`WHILE`/`WHERE` clause | `stories/*.md` | leave the row out; run `testability-check` or suggest `/user-story-refiner` |
   | Text longer than 500 characters | count | warn; suggest splitting with `requirement-phrasing` |

   Show the gate result as a table (ID, check, finding, action). A blocked row goes across only when the user approves that ID by name ("hand off R-050 with its TBD"). Never fix the text here, and never replace a `TBD` with a value.
4. **Choose capabilities (OpenSpec only).** One `specs/<capability>/spec.md` per durable behavior (`voucher-redemption`, not `add-voucher-endpoint`). If `openspec/specs/` exists, list its capabilities (`openspec list --specs`, or the folder names) and reuse an existing path. The script takes the capability from a `cap:<name>` entry in the `Tags` column, else from the change name without its leading verb. Propose `cap:` tags when the selection spans more than one behavior, and add them only with the user's OK.
5. **Generate.** Run `python3 <skill-dir>/scripts/to_openspec.py <change> --ids <gated IDs> --target openspec` (or `re-lint openspec ...`; `--target spec-kit` for spec-kit; `--out DIR` if the toolkit lives below the repo root). Exit code `1` lists findings: read each one. Without `--force` the script refuses to overwrite an existing change folder; show the user what differs and ask, and never use `--force` on a change whose `tasks.md` has ticked boxes. Manual fallback without Python: copy the files in `assets/` and fill them using the mapping table in `references/openspec-format.md` (or `references/spec-kit-format.md`).
6. **Fill the human parts.** Replace the generated `## Why` with one or two sentences the user confirms (50 to 1,000 characters), and check the generated `## Purpose` of each new capability (at least 50 characters). Write `## Impact` from the interfaces in `context.md` and the sources cited. Do not add requirements, scenarios, numbers or design choices that are not in the register.
7. **Validate.** If the OpenSpec CLI is installed, run `openspec validate <change> --strict --no-interactive` and fix structure only (headings, bullets, lengths), never meaning. Without the CLI, run the checklist in `references/openspec-format.md`. For spec-kit, check the mandatory sections listed in `references/spec-kit-format.md`.
8. **Show and hand off.** Show the file tree and a trace table (R-ID, file, heading or task number). End with what went across, what was left out and why, and the next command for the coding agent.

## Quality checks

- [ ] Every row that went across is `agreed` or was approved by ID; nothing withdrawn, rejected, deferred or `wont` went across.
- [ ] No requirement block carries a `TBD` or a lint error unless the user approved that ID; approvals and exclusions are listed in `proposal.md`.
- [ ] Every `### Requirement:` heading starts with its R-ID and is followed by `<!-- R-nnn -->`; the text equals `requirements.csv` except for the upper-cased obligation verb.
- [ ] Every requirement has at least one `#### Scenario:` with a `WHEN` or `GIVEN` step and a `THEN` step; scenarios from acceptance criteria keep their AC ID.
- [ ] Every quality requirement and constraint is in `proposal.md` under "Constraints and Quality Requirements"; every task line ends with its R-IDs in parentheses.
- [ ] `openspec validate <change> --strict` passes, or the manual checklist does; any approved `SHOULD`/`MAY` is named as the reason if it does not.

## Hand-offs

- **Next:** the coding agent implements the change (`/opsx:apply <change>`, or `/speckit.clarify` then `/speckit.plan` and `/speckit.tasks`). After implementation, run `traceability-matrix` to confirm each R-ID has code and test evidence.
- **Feeds back to:** `requirement-phrasing` for rows blocked by lint, `TBD` or `should`/`may`; `testability-check` for rows without a scenario source; suggest `/requirements-review` when the set was never reviewed, and `/change-impact` when a re-export changes requirements that are already implemented.

## Non-interactive mode

Use `--status agreed`. Leave every row that fails the gate out and list it under "Not in this change" in `proposal.md` with the reason. Never use `--force`. Keep the generated `## Why` and mark it for review. End with the IDs handed off, the IDs left out with their reasons, and the validation result.

## References

- `references/openspec-format.md`: the OpenSpec 1.16.0 structure this skill targets, with sources and check date, the field mapping, and the validation checklist. Read it at step 5 when writing by hand, and at step 7.
- `references/spec-kit-format.md`: the spec-kit 1.2.6 `spec.md` structure and mapping. Read it when the target is spec-kit.
- `references/handoff-gate.md`: the gate rules and the error-level lint checks to apply by hand when no linter is available. Read it at step 3 if `re-lint` and `requirement-linter` are missing.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: five loyalty-points requirements and the change folder (and spec-kit spec) they become.
