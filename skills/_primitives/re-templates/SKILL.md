---
name: re-templates
description: >-
  Shared asset library for the re-skills catalogue: the default requirements/schema.json, the
  requirements.csv header and the workspace layout that says which skill owns which file under
  requirements/. Use when another re-skills skill needs to create a work product, check where a file
  belongs, or fall back to defaults because requirements/schema.json does not exist yet. Not for
  configuring a repo interactively (that is re-setup) or for editing attributes (attribute-schema).
license: MIT
user-invocable: false
metadata:
  stage: primitives
  invocation: primitive
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §3.1.6, §6.5"
  inputs-from: "none"
  outputs-to: "re-setup, attribute-schema, re-ids"
  work-product: "requirements/schema.json"
  version: "0.1.0"
---

# RE templates

The single place where the catalogue's file shapes are defined, so every skill writes the same columns and puts files in the same place.

## When not to use

- Setting up a repository with a tailored process: use `re-setup`.
- Adding attributes, lifecycle states or audience views: use `attribute-schema`.
- Allocating an ID: use `re-ids`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/schema.json` | no | `re-setup`, `attribute-schema` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/schema.json` | `assets/schema.json` | every skill and script |
| `requirements/requirements.csv` | `assets/requirements.csv` header | every emitting skill |

## Procedure

1. **Find the workspace.** Look for `requirements/schema.json` from the repo root. If it names another `workspace`, use that folder.
2. **Resolve defaults.** If `schema.json` is missing, use `assets/schema.json` as is. If it exists, values in it win over the defaults key by key.
3. **Place the file.** Look up the work product in `references/workspace-layout.md`, create parent folders, and start new files from the matching template (`assets/requirements.csv`, or the emitting skill's own `assets/`).
4. **Keep the column order.** When writing CSV, use `attributes.columns` then any optional columns already present, LF line endings, UTF-8, and quote only fields that need it.

## Quality checks

- [ ] The file is at the path the layout gives for its work product.
- [ ] CSV headers match the schema column order exactly.
- [ ] No defaults were silently changed; any deviation is in `requirements/schema.json`.

## Hand-offs

- **Next:** `re-ids` to allocate IDs for the rows you are about to write.
- **Feeds back to:** `re-setup` when the defaults do not fit the team's process.

## References

- `references/workspace-layout.md`: every work product, its path and its owning skill. Read it before creating any file under `requirements/`.
- `assets/schema.json`: the default schema (IDs, attributes, enums, lifecycle, lint, trace, issue mapping, Definition of Ready).
