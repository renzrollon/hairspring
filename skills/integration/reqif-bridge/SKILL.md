---
name: reqif-bridge
description: >-
  Exports requirements/requirements.csv as a ReqIF 1.2 file that a customer's DOORS, Polarion or
  Jama can import, and brings their annotated ReqIF back as a requirement-level diff you review
  before anything is merged. One SPEC-OBJECT per requirement with the R-ID as IDENTIFIER, so
  round-trips match cleanly; customer edits land only through import --diff, then --apply after
  review, and nothing is deleted. Started explicitly with /reqif-bridge. Use when a customer, vendor
  or tender asks for ReqIF (.reqif or .reqifz), when someone says "export for DOORS", "send the
  requirements to Polarion", "merge the customer's comments back", or when a contract baseline must
  be exchanged with another requirements management tool. Not for a coding-agent hand-off
  (to-openspec), for issue trackers (issue-sync), or for a readable specification document
  (spec-assembler).
license: MIT
compatibility: Python 3.9+ for scripts/reqif_bridge.py (minimal ReqIF 1.2, stdlib only). The strictdoc reqif package is optional, for schema validation and full-fidelity exchange. A manual procedure works without either.
disable-model-invocation: true
argument-hint: "[export [--ids R-001,R-002] [--title TEXT] | import FILE]"
metadata:
  stage: integration
  invocation: user
  priority: P2
  ireb-anchor: "CPRE FL Handbook 1.2 §7"
  inputs-from: "requirement-phrasing, attribute-schema, baseline, requirements-review"
  outputs-to: "requirements-review, change-impact, conflict-detector"
  work-product: "requirements/exports/<name>.reqif and requirements/exports/import-diff-<date>.md"
  version: "0.1.0"
---

# ReqIF bridge

Customers in regulated sectors keep their requirements in DOORS, Polarion or Jama and exchange them as ReqIF, the OMG XML interchange format. This skill sends the register out as ReqIF and brings the customer's edits back as a diff, so the register stays the source of truth and every accepted change is a decision someone made, not a side effect of an import. The work products are a `.reqif` export and an import diff report with a decision per row.

## When not to use

- Handing requirements to a coding agent: `to-openspec`. Creating tickets: `issue-sync`.
- A readable document for procurement (Markdown, docx): suggest `/spec-assembler`.
- The customer needs rich text, enumerations, chapters, relations or `.reqifz` with attachments preserved: the minimal bridge exports plain strings only. Read `references/limitations.md` and use the strictdoc `reqif` library for that exchange.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` | yes | `requirement-phrasing` |
| `requirements/schema.json` (columns, enums, lifecycle) | no (defaults apply) | `re-setup`, `attribute-schema` |
| A named baseline to export (`requirements/baselines/<name>.json`) | no; recommended for contract exchanges | `baseline` |
| The customer's returned `.reqif` file | for import | the customer |
| The receiving tool, its attribute names and what the customer will change | yes (ask) | the customer's tool admin |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/exports/<title-slug>-<YYYY-MM-DD>.reqif` | `assets/export-skeleton.reqif`, structure in `references/reqif-mapping.md` | the customer's RM tool |
| A hand-over note for the customer's tool admin | `assets/handover-note.md` | the customer |
| `requirements/exports/import-diff-<YYYY-MM-DD>.md` | `assets/import-diff.md` | the user, `requirements-review`, `change-impact` |
| `requirements/requirements.csv` rows changed by an approved import | schema columns | every skill |

## Procedure

1. **Read the workspace and the exchange.** Load `requirements/schema.json` (else the defaults; say so) and `requirements.csv`. Ask: which tool receives the file, what the customer will do (read, comment, edit text, add requirements), and whether they need rich text, chapters, enumerations or their own attribute names (`ReqIF.Text`, `ReqIF.ForeignID`). If they do, read `references/limitations.md` before going on.
2. **Select what goes out.** Ask which rows to send. For a contract exchange, export the IDs of a named baseline (suggest `/baseline` first). Default advice: send `agreed` and `proposed` rows; leave out `draft`, `rejected` and `withdrawn` unless the user names them.
3. **Export.** Run `python3 <skill-dir>/scripts/reqif_bridge.py export --out requirements/exports/<title-slug>-<YYYY-MM-DD>.reqif --ids <IDs> --title "<title>"` (or `re-lint reqif export ...`). Without Python, write the file by hand from `assets/export-skeleton.reqif` following `references/reqif-mapping.md`.
4. **Check the export.** If the strictdoc `reqif` package is installed, run `reqif validate --use-reqif-schema <file>` (exit `0` means valid). Otherwise run the structure checklist in `references/reqif-mapping.md`. Confirm one `SPEC-OBJECT` per selected row, each `IDENTIFIER` equal to its R-ID. Fill `assets/handover-note.md` (attribute mapping, the round-trip rules for the customer) and give it to the user with the file.
5. **Import as a diff.** When the file comes back, run `python3 <skill-dir>/scripts/reqif_bridge.py import <file> --diff`. Save the result as `requirements/exports/import-diff-<YYYY-MM-DD>.md` in the shape of `assets/import-diff.md`. Compare it with the matching export in `requirements/exports/` so a row the customer dropped (`missing-object`) is told apart from a row that was never sent. Objects the script skips for having no requirement ID are `new-object` candidates: list each one in the diff. Without Python, build the same diff by hand with the rules in `references/reqif-mapping.md`.
6. **Review each change with the user.** Recommend a decision per row and record the user's decision in the diff file:

   | Class | Recommendation |
   | --- | --- |
   | `changed-text` on an `agreed` (or later) row | a change request: suggest `/change-impact`; if accepted, `Status=proposed` (and `Version` + 1 if the column exists) unless the change request approves it |
   | `changed-text` on a `draft` or `proposed` row | accept or reject with the owner; run `requirement-linter` on the new text |
   | `changed-attribute` with a schema value | accept or reject with the owner |
   | `invalid-value` (outside the schema enums, such as `Status=Accepted`) | never written; ask what the customer meant |
   | `new-object` (no R-ID) | a candidate: accept as a new `draft` row with the next ID from `re-ids`, Source = the customer file and object |
   | `missing-object` | never deleted; ask the customer; withdrawing it is a separate decision with a reason |
   | `unmapped-attribute`, `xhtml-flattened` | shown for reading; not imported; check formatting loss in the customer's tool |

   If an accepted edit contradicts another requirement, run `conflict-detector` before applying.
7. **Apply after review.** If the user accepted every change the script would write, and the diff holds no `invalid-value` row and no accepted `new-object` the script skipped, run `python3 <skill-dir>/scripts/reqif_bridge.py import <file> --apply`. If they accepted only some, apply the accepted rows by hand in `requirements.csv` (show the diff first), because `--apply` takes the whole file. Then make sure every accepted text change on an agreed row has `Status=proposed` and, if the column exists, `Version` incremented (unless a change request approved it), and run `requirement-linter` (or `re-lint check --only-ids <changed IDs>`) on the changed rows.
8. **Report.** List the rows changed, added (with their new IDs) and left as they were, the decisions still open with an owner, and the next step.

## Quality checks

- [ ] The export holds only the rows the user chose; each `SPEC-OBJECT` `IDENTIFIER` is its R-ID; there is one `ATTRIBUTE-DEFINITION-STRING` per exported column.
- [ ] The export passes `reqif validate --use-reqif-schema`, or the manual structure checklist.
- [ ] The import diff was saved and reviewed, with a decision per row, before anything was written to `requirements.csv`.
- [ ] No row was deleted; no value outside the schema enums was written; new rows got fresh IDs through `re-ids` and `Status=draft`.
- [ ] Text changes accepted on agreed rows went through a change request or moved back to `proposed` (with `Version` incremented where the column exists).
- [ ] `requirement-linter` reports no new errors on the changed rows.

## Hand-offs

- **Next:** suggest `/requirements-review` on the rows the import changed or added, and `/change-impact` for accepted changes to agreed requirements; `conflict-detector` when a customer edit contradicts another requirement.
- **Feeds back to:** `requirement-phrasing` for customer text that fails lint; suggest `/baseline` before every export, so each exchanged set is a named version you can diff later.

## Non-interactive mode

Run `export` and `import --diff` only; save the diff file and list the decisions it needs. Never run `import --apply` without a person reviewing the diff in the same session.

## References

- `references/reqif-mapping.md`: the ReqIF 1.2 element structure the bridge writes and reads, identifier rules, the attribute mapping, the import diff classes, and a structure checklist. Read it before step 3 when writing by hand, and at step 5.
- `references/limitations.md`: what the minimal bridge does not carry (XHTML rich text, enumerations, hierarchy, relations, tool-specific attribute names, `.reqifz`), and when to use the strictdoc `reqif` library instead. Read it at step 1 if the customer needs more than plain text.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: a three-requirement export, the vendor's annotated return file, and the import diff it produces.
