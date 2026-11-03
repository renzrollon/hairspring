# ReqIF import diff: vendor-return.reqif

Reviewed: 2026-11-12 · File: `vendor-return.reqif` · From: Vendor RM tool (sample) / Vendor ReqIF export (sample), created 2026-11-12T14:05:31+08:00 · Compared with: `requirements/requirements.csv` and the export `requirements/exports/voucher-redemption-2026-11-03.reqif`

Command: `reqif_bridge.py import vendor-return.reqif --diff` · Nothing has been written to the register.

## Summary

| Class | Count |
| --- | --- |
| changed-text | 1 |
| changed-attribute | 0 |
| invalid-value | 1 |
| new-object | 1 |
| missing-object | 1 |
| unmapped-attribute | 2 |
| xhtml-flattened | 3 |
| unchanged | 0 |

## Changes to decide

| # | ID or object | Class | Attribute | Register value | File value | Recommendation | Decision (who, date) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | R-041 | changed-text | Text | WHEN the POS sends a voucher validation request for a voucher in state Issued, the loyalty service shall return the voucher value to the POS. | WHEN the POS sends a voucher validation request for a voucher in state Issued, the loyalty service shall return the voucher value and the voucher expiry date to the POS. | Change request: R-041 is agreed. Suggest `/change-impact` with SH-01 (owner) and SH-09; the vendor's reason is in its comment below. If accepted: Status=proposed until the change request is approved (and Version + 1 once the register has a Version column); run `requirement-linter` on the new text | open |
| 2 | R-085 | invalid-value | Status | agreed | Accepted | Not written: "Accepted" is not a Status value. Ask the vendor whether it means they accept the target; if so, record that in Rationale or Links, keep Status=agreed | open |
| 3 | `_9c4f2e1d-7a3b-4c5e-8f60-1b2d3e4f5a6b` | new-object | Type, Text, Title | - | F; "The loyalty service shall log each voucher validation request with the store ID and the result."; "Log voucher validation requests" | Candidate requirement from the vendor. If accepted: new row R-086 (next free ID), Status=draft, Source `reqif:vendor-return.reqif#_9c4f2e1d-7a3b-4c5e-8f60-1b2d3e4f5a6b` (SH-09), Priority and Rationale TBD with an open question to SH-09 | open |
| 4 | R-040 | missing-object | - | exported on 2026-11-03 | not in the file | Never deleted. Ask the vendor whether they left it out on purpose (R-040 is about the customer mobile app, not the POS) | open |

## Read only (not imported)

| # | ID or object | Class | Detail |
| --- | --- | --- | --- |
| 1 | R-041 | unmapped-attribute | `Vendor comment`: "TillPoint v2.2 shows the voucher expiry on the till screen, so we need it in the response." |
| 2 | `_9c4f2e1d-7a3b-4c5e-8f60-1b2d3e4f5a6b` | unmapped-attribute | `Vendor comment`: "Needed for our store reconciliation report." |
| 3 | R-041, R-085, `_9c4f2e1d-...` | xhtml-flattened | `Text` arrived as XHTML. R-041 had "and the voucher expiry date" in bold; the bold is dropped. R-085 is identical after flattening |
| 4 | R-043 | not exported | draft row, never sent; absent as expected |

## Next

- [ ] A decision is recorded for every row in "Changes to decide".
- [ ] Accepted changes applied: `import vendor-return.reqif --apply` only if rows 1 and 3 are both accepted (row 2 and row 4 are never written); otherwise by hand.
- [ ] If row 1 is accepted: R-041 `Status=proposed` (no Version column yet), or the approved change request is cited.
- [ ] `requirement-linter` run on R-041 and on the new row.
