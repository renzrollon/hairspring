---
name: attribute-schema
description: >-
  Defines and validates the requirement attributes, enum values and lifecycle states in
  requirements/schema.json, and generates audience views of the register with the bundled views
  script (re-lint views): selective (row filter), projective (column subset) and aggregating
  (group-by counts), written to requirements/views/<name>.md. Built-in views: po, architect, qa.
  Use when a team wants a new attribute (component, release, owner, risk), a new status or
  lifecycle rule, a check that rows only use allowed values, or a view for one audience ("show the
  architect the agreed quality requirements", "what has no verification method", "a finance view
  of the S-05 requirements"), or before spec-assembler needs attribute views. Not for allocating
  IDs or filling attributes on new rows (re-ids), wording checks (requirement-linter), first-time
  repository setup (re-setup), or mapping tracker statuses (issue-sync).
license: MIT
compatibility: Python 3.9+ optional for scripts/views.py; works without it.
metadata:
  stage: management
  invocation: model
  priority: P2
  ireb-anchor: "CPRE FL Handbook 1.2 §6.3–6.5"
  inputs-from: "re-setup, re-templates, requirement-phrasing"
  outputs-to: "re-ids, requirement-linter, spec-assembler, baseline, issue-sync"
  work-product: "requirements/schema.json, requirements/views/<name>.md"
  version: "0.1.0"
---

# Attribute schema

Attributes make a requirement manageable: status says where it stands, priority says when, source says why, owner says who. Views make a register of a hundred rows readable for one audience. This skill keeps the attribute set and the lifecycle in `requirements/schema.json` small and consistent. It generates views from definitions kept in the same file, so every audience reads the same register through its own lens and nobody keeps a private spreadsheet copy.

## When not to use

- Setting up a new repository (process facets, work products, first schema): `re-setup`.
- Allocating IDs, or completing attributes on rows you are about to write: `re-ids`.
- Checking the wording of requirement text: `requirement-linter`.
- Mapping Jira, GitHub or Azure DevOps statuses: `issue-sync` (`schema.json` → `issues.status_map`), not new `Status` values.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/schema.json` | no (start from `assets/schema.json`) | `re-setup` |
| `requirements/requirements.csv` (and `stories/*.md`) | yes, for validation and views | `requirement-phrasing`, `user-story-refiner` |
| The audience, and what it needs to see or decide | yes, for a new view | the user |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/schema.json`: `attributes`, `lifecycle`, `views` | structure of `assets/schema.json`; views as in `references/views-format.md` | every skill and script |
| `requirements/views/<name>.md` (or `.csv`) | `assets/view.md` | the audience: PO, architect, QA, others |
| `requirements/requirements.csv`: a new optional column, only on request | schema column order | every skill |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json`. If it is missing, copy `assets/schema.json` (the vendored default) to `requirements/schema.json` as the starting point, and say so. Read the header of `requirements.csv` and the distinct values used in each enum column.
2. **Classify the request.** Decide whether it concerns an attribute, an enum value, the lifecycle, a view, or validation only. Several are fine; handle them in that order.
3. **Change attributes and enums.** Follow `references/attributes-and-lifecycle.md`. New attributes go into `attributes.optional`, and into `required` only when the user asks for it explicitly. A closed set of values gets an `attributes.enums` entry. Tracker statuses go into `issues.status_map`, never into `Status`. Arrays replace the defaults when the schema is merged, so when `schema.json` holds only overrides, write the whole array: the default `attributes.optional` entries plus the new one. Never remove or rename a value or column that rows use, and never change ID `prefix` or `digits` once IDs exist. If the user asks for such a change, list the affected rows, explain what breaks, and propose the safe path from the reference. Change nothing until the owner agrees.
4. **Change the lifecycle.** Update `attributes.enums.Status` and `lifecycle.transitions` together, then run the lifecycle checks in `references/attributes-and-lifecycle.md`.
5. **Show, then write.** Show the JSON diff. After confirmation (or directly in non-interactive mode), write `schema.json`: 2-space indent, existing key order, trailing newline. If the user wants the new column filled in `requirements.csv`, add it after the existing columns, propose a value per row, and write after confirmation. Unknown values are `TBD`.
6. **Validate.** Run `re-lint check` (rules `missing-attribute` and `invalid-enum`), or the `requirement-linter` skill. Without either, check by hand that every required cell is filled and every enum cell holds an allowed value or `TBD`. Report the failing rows with `file:line`. Do not change their values without the owner.
7. **Define views.** Turn the audience's need into a view definition: a selective `filter`, projective `columns`, an aggregating `group_by`, and `sort`. Use the format in `references/views-format.md`. Start from a built-in in `assets/views.json` when it is close. Write the definition under `schema.json` → `views.<name>`, with a kebab-case name.
8. **Generate views.** Run `python3 <skill-dir>/scripts/views.py` to write all views, or `python3 <skill-dir>/scripts/views.py --view <name>` for one; `re-lint views` takes the same arguments. Add `--format csv` for spreadsheet users. The output goes to `requirements/views/<name>.md`. Without Python, apply the filter, columns and counts by hand and fill `assets/view.md`; write "built manually" in the Source field.
9. **Report.** List the schema keys you changed, the validation findings, and each view file with its row count.

## Quality checks

- [ ] `schema.json` is valid JSON. `lifecycle.initial` and every transition target are `Status` values, every `Status` has a transitions entry, and `withdrawn` has no outgoing transitions.
- [ ] No enum value or column that rows use was removed or renamed without an agreed migration. ID prefixes and digits are unchanged.
- [ ] Every view names only columns that exist in the register or in the schema, and every view file matches `assets/view.md`.
- [ ] Validation findings are reported, not silently fixed.

## Hand-offs

- **Next:** `re-ids` and `requirement-linter` pick up the new schema on their next run. Suggest `/spec-assembler` to put the views into the specification, and `/baseline` to record the new attribute values.
- **Feeds back to:** suggest `/re-setup` when the request is really about process facets or which work products to keep. Suggest `/issue-sync` for tracker status mapping.

## References

- `references/views-format.md`: the exact `views` format (filter conditions, columns, group-by, sort), the built-in views, and the output shape. Read it at steps 7 and 8.
- `references/attributes-and-lifecycle.md`: where each kind of change goes, changes that need a migration, and the lifecycle checks. Read it at steps 3 and 4.
- `assets/views.json`: the built-in `po`, `architect` and `qa` definitions, ready to copy into `schema.json`.
- `references/ireb-anchor.md`: the handbook sections and glossary terms this skill applies.
- `examples/`: adding a `Component` attribute and an architect view on the loyalty-points sample.
