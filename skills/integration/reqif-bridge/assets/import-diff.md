# ReqIF import diff: <file name>

Reviewed: <YYYY-MM-DD> · File: `<path>` · From: <SOURCE-TOOL-ID> / <REQ-IF-TOOL-ID>, created <CREATION-TIME> · Compared with: `<workspace>/requirements.csv` and the export `<workspace>/exports/<export file>` (or "no matching export found")

Command: `reqif_bridge.py import <file> --diff` · Nothing has been written to the register.

## Summary

| Class | Count |
| --- | --- |
| changed-text | <n> |
| changed-attribute | <n> |
| invalid-value | <n> |
| new-object | <n> |
| missing-object | <n> |
| unmapped-attribute | <n> |
| xhtml-flattened | <n> |
| unchanged | <n> |

## Changes to decide

| # | ID or object | Class | Attribute | Register value | File value | Recommendation | Decision (who, date) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | <R-ID or IDENTIFIER> | <class> | <column> | <current value> | <value in the file> | <accept / reject / change request / ask the customer> | <open> |

## Read only (not imported)

| # | ID or object | Class | Detail |
| --- | --- | --- | --- |
| 1 | <R-ID or IDENTIFIER> | <unmapped-attribute / xhtml-flattened / not exported> | <attribute name and value verbatim, or what was dropped> |

## Next

- [ ] A decision is recorded for every row in "Changes to decide".
- [ ] Accepted changes applied: `import <file> --apply` only if every applicable change was accepted; otherwise by hand.
- [ ] Accepted text changes on agreed rows: `Version` + 1 and `Status=proposed`, or the change request is cited.
- [ ] `requirement-linter` run on the changed and new rows.
