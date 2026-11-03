---
name: re-setup
description: >-
  Configures a repository's requirements workspace in one short interview (at most 8 questions,
  each with a recommended answer): picks the RE process facets (linear or iterative, prescriptive
  or explorative, customer-specific or market-oriented), the work products to keep, the change
  authority, the ID scheme, the attribute schema and a Definition of Ready, then writes
  requirements/README.md and requirements/schema.json. Use when a repo has no requirements/
  folder yet, when someone types /re-setup, "set up requirements for this repo" or "how much
  process do we need", when a team starts a new service, tender or product and wants every
  re-skills skill to follow one process, and again when the process changes (for example a
  fixed-price contract becomes an agile product).
  Not for adding attributes, lifecycle states or audience views to an existing schema (use
  attribute-schema), for defining domain terms (glossary) or for scoping the system
  (system-context).
license: MIT
disable-model-invocation: true
argument-hint: "[defaults]"
metadata:
  stage: foundations
  invocation: user
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §5.1–5.3, §3.1.6, §6.5"
  inputs-from: "re-templates"
  outputs-to: "attribute-schema, user-story-refiner, change-impact, requirement-linter, glossary"
  work-product: "requirements/README.md, requirements/schema.json"
  version: "0.1.0"
---

# RE setup

Every other skill writes to `requirements/` and reads `requirements/schema.json`. If nobody decides up front how much process the team needs, the skills produce either ceremony nobody reads or notes nobody can trace. This skill asks about the three process facets and the criticality of the system, derives the work products to keep, who may change an agreed requirement, the ID scheme, the attribute schema and a Definition of Ready (DoR), and writes them to `requirements/README.md` and `requirements/schema.json`. Target: under 10 minutes, at most 8 questions, two rounds.

## When not to use

- The workspace exists and you only need another attribute, lifecycle state or audience view: `attribute-schema`.
- You need shared definitions of domain words: `glossary`.
- You need to decide what the system does and what it talks to: run `/system-context`.
- You need the next free ID or an attribute check on rows: `re-ids`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| The user's answers, or `defaults` | yes | the user |
| Repo files that hint at the process: `README*`, `CONTRIBUTING*`, `docs/`, `.github/`, tracker config, contract, tender or compliance documents | no | the team |
| Existing `requirements/schema.json`, `requirements/README.md` and registers | no | an earlier run, `attribute-schema` |
| `assets/schema.json` (default schema, vendored from `re-templates`) | yes | `re-templates` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/README.md` | `assets/README.md` | people; `change-impact` (change authority) |
| `requirements/schema.json` | `assets/schema.json` with `process`, `ids`, `attributes` and `definition_of_ready` set | every skill and script; `user-story-refiner` reads `definition_of_ready` |
| `requirements/requirements.csv`, header only, only if missing | `re-templates/assets/requirements.csv` | every emitting skill |

## Procedure

1. **Read the workspace.** Look for `requirements/` (or the `workspace` named in an existing `schema.json`). If `schema.json` exists, this is a re-run: load it and apply step 7. List the IDs already in use per kind with the `re-ids` primitive (`re_ids.py list`, or `re-lint ids list`; without either, search the workspace for each prefix). Load the defaults from `assets/schema.json`; if the vendored copy is missing, use `re-templates/assets/schema.json`.
2. **Skim the repo before asking.** Read only the top-level `README*`, `CONTRIBUTING*`, the `docs/` index, `.github/`, tracker config, and files whose names contain contract, tender, rfp, sow, compliance, audit or regulation. Read `references/process-facets.md` and note evidence for each facet with `file:line`. Evidence sets the recommended answer; it never replaces the answer.
3. **Ask batch A: facets (4 questions).** Follow `re-interview` in batch mode: one numbered message, each question with its recommended answer and the evidence behind it, so the user can reply `yes` or `defaults`. If the user started with `/re-setup defaults` or says "use your recommendations", ask nothing: take the recommended answers for batches A and B, record them as `defaults accepted by <name>, <date>`, and list them in the final message for review.

   | # | Question | Options | Default without evidence |
   | --- | --- | --- | --- |
   | A1 | Is the full set of requirements agreed before building starts, or refined iteration by iteration? | linear / iterative | iterative |
   | A2 | Is the requirements set a binding basis for someone else's work (contract, tender, outsourced build, certification), or are you finding out what is needed as you go? | prescriptive / explorative | explorative |
   | A3 | Does one known customer order and accept the system, or is it a product for a market of users nobody can name one by one? | customer-specific / market-oriented | customer-specific |
   | A4 | Does a regulation, audit, safety case or contract require evidence of where each requirement came from and how it was verified? Which one? | none / name it | none |

4. **Derive the configuration.** Apply the decision rules in `references/process-facets.md` to the answers: work products kept (`yes`, `later`, `no`), depth before implementation, change authority, attribute columns to add, and DoR items (from `assets/definition-of-ready.md`). When facets mix, for example iterative delivery against a prescriptive contract, take the stricter rule for change authority and evidence and say so in the README.
5. **Ask batch B: configuration (4 questions),** each answer prefilled from step 4.

   | # | Question | Recommended answer |
   | --- | --- | --- |
   | B1 | Who may approve a change to an agreed requirement? Name the role and the person or people. | derived change authority; person `TBD` if unknown |
   | B2 | Keep this set of work products? (show the derived table) | the derived table |
   | B3 | Keep the default ID prefixes (`R-001`, `S-01`, `SH-01`, ...) and the seven required attributes? Add any optional attribute as a column? | defaults plus the facet columns from step 4 |
   | B4 | Use this Definition of Ready? Anything to add or drop? | base items plus the facet items |

   Stop after B4. Anything else the user raises goes to the README's Open questions; do not add questions.
6. **Check every requested change against the guard rails.** If a request breaks one, say which rule and why in one sentence, offer the nearest allowed option, and log it in Open questions.
   - IDs stay opaque. A prefix may change (`REQ-`), but no ID may encode type, component or priority (`R-F-001`, `LOY-QUAL-0001`); the type lives in `Type`.
   - The seven minimum attributes stay required: `ID, Type, Text, Source, Priority, Status, Rationale`. An unknown value is `TBD`, which `re-lint check` reports as info, not as an error.
   - Prefix or digits of an ID kind may change only while no ID of that kind exists in the workspace or in commit messages. Never renumber an ID.
   - Enum values may be added. A value may be removed or renamed only when no existing row uses it.
   - Only a named person moves a requirement to `agreed`; no facet changes that.
7. **Re-run rules.** When `schema.json` exists: show a key-by-key diff (old → new) and write only after confirmation. Keep every key the user or `attribute-schema` added (`views`, `lint`, `issues`, custom ID kinds). Keep README Open questions that are still open and add a row to Setup history.
8. **Write.** Fill `assets/README.md` exactly (same headings, same columns; the Story template block only when stories are kept, else its one-line "Not used" form) and save it as `requirements/README.md`. Copy the default schema, set `process.lifecycle`, `process.approach`, `process.target`, `process.change_authority`, `ids`, `attributes` and `definition_of_ready`, and save it as `requirements/schema.json` (2-space indent, template key order). Create `requirements/requirements.csv` with the header only if it does not exist (`re-templates`). Create no other files.
9. **Verify.** Parse `schema.json` as JSON (`python3 -m json.tool requirements/schema.json`, or any JSON parser). Then run the `re-ids` check (`python3 <re-ids skill-dir>/scripts/re_ids.py check`, or `re-lint ids check`): exit code 2 means the schema or a register cannot be parsed. Compare the README's DoR list with `definition_of_ready` item by item.
10. **Report.** Final message: the four facet choices in one line, the change authority, the files written, the open questions, and the next step.

## Quality checks

- [ ] At most 8 questions were asked, each with a recommended answer; every answer is recorded with who gave it and the date, or marked `assumed`.
- [ ] `schema.json` parses; `process.*` matches the README's Process facets table.
- [ ] `attributes.required` contains `ID, Type, Text, Source, Priority, Status, Rationale`.
- [ ] No ID prefix or digits changed while IDs of that kind exist; no ID encodes type, component or priority.
- [ ] Every row in Work products kept has the path and owning skill from `re-templates/references/workspace-layout.md` and a reason tied to a facet.
- [ ] The change authority names a role and a person, or `TBD` with an open question.
- [ ] The README's Definition of Ready equals `definition_of_ready` in `schema.json`, item for item.

## Hand-offs

- **Next:** run the `glossary` skill to start `requirements/glossary.md` from the repo; then suggest the user runs `/system-context` and `/stakeholder-map`.
- **Feeds back to:** `attribute-schema` for audience views and extra attributes; re-run `/re-setup` when a facet changes, for example when one customer becomes a market.

## Non-interactive mode

When nobody can answer (CI, an autonomous run, "don't ask"): use the evidence-based recommendation for each question, else the default; mark each facet `assumed` with its evidence; write both files; log every assumption as an open question owned by the product owner (or `TBD`). Never change an ID scheme or the required attributes in this mode.

## Pitfalls

- Choosing `linear` because the team writes documents: the facet is about when requirements are agreed, not about how much is written.
- Choosing `prescriptive` for an internal team because "the PO decides": prescriptive means someone else builds or certifies against the set.
- Keeping every work product "to be safe": each kept file costs upkeep. `later` is a valid answer with a trigger.

## References

- `references/process-facets.md`: facet signals, decision rules for work products, depth, change authority, attribute columns and DoR; mixed facets. Read it before step 2.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `assets/README.md`, `assets/definition-of-ready.md`, `assets/story-template.md`: the fixed output shapes. `assets/schema.json` is vendored from `re-templates` by `tools/vendor_scripts.py`; never edit the copy.
- `examples/`: the Harbourline loyalty-points answers, and the README and schema they produce.
