---
name: re-ids
description: >-
  Allocates IDs (R-001, S-01, CR-001, ...) and validates that every row has the required attributes
  before a re-skills work product is saved. Use whenever a skill is about to write new requirements,
  sources, stakeholders, candidates, conflicts, decisions, change requests or findings, or when you
  need the next free ID, a list of existing IDs, or a duplicate-ID check. Not for designing the
  attribute schema itself (attribute-schema) or for wording checks (requirement-linter).
license: MIT
compatibility: Python 3.9+ optional for scripts/re_ids.py; manual procedure works without it.
user-invocable: false
metadata:
  stage: primitives
  invocation: primitive
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §6.5"
  inputs-from: "re-templates"
  outputs-to: "requirement-linter, traceability-matrix"
  work-product: "IDs and attribute-complete rows in any register"
  version: "0.1.0"
---

# RE IDs

IDs and attributes from the first requirement: every emitted row gets a unique, never-reused ID and the minimum attribute set, so tracing, review and change impact work later without clean-up.

## When not to use

- Changing ID prefixes, attributes or lifecycle states: use `attribute-schema` (or `re-setup` for a new repo).
- Checking wording quality (weak words, passive voice): use `requirement-linter`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/schema.json` | no (defaults apply) | `re-setup`, `attribute-schema` |
| Existing registers under `requirements/` | no | every emitting skill |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| The calling skill's register, with IDs filled | schema columns | `requirement-linter`, `traceability-matrix` |

## Procedure

1. **Get the next IDs.** Run `python3 <skill-dir>/scripts/re_ids.py next --kind <kind> --count <n>` (or `re-lint ids next ...` if the package is installed). Kinds and default prefixes are in `references/id-scheme.md`.
2. **Manual fallback.** Without Python: search every file under `requirements/` (and commit messages if you can) for the prefix, take the highest number including withdrawn IDs, add one, pad to the schema digits.
3. **Fill the attributes.** Every requirement row needs `ID, Type, Text, Source, Priority, Status, Rationale`. Unknown values are `TBD`, never a guess; add the open question to the calling skill's output.
4. **Validate before saving.** Run `python3 <skill-dir>/scripts/re_ids.py check <file>`. Fix duplicates and pattern errors before handing off.

## Quality checks

- [ ] No ID appears twice; no withdrawn or rejected ID was reused; nothing was renumbered.
- [ ] Every row has all required attributes, using only enum values from the schema.
- [ ] New requirements are `draft` unless a named person agreed them.

## Hand-offs

- **Next:** `requirement-linter` on the rows just written.
- **Feeds back to:** `attribute-schema` when a team needs a new ID kind or attribute.

## References

- `references/id-scheme.md`: ID kinds, prefixes, the attribute set, and the lifecycle. Read it when allocating a kind other than `requirement`.
