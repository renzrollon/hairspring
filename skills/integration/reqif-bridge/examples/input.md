# Input: ReqIF round-trip with the POS vendor (loyalty-points sample)

The POS vendor (SH-09) keeps its interface requirements in its own requirements management tool and asked for the voucher requirements as ReqIF, to review them against TillPoint v2.2.

## Export, 2026-11-03

Command typed by Wei Jie Chua (SH-08):

> /reqif-bridge export --ids R-040,R-041,R-085 --title "Voucher redemption"

Register: `input/requirements/requirements.csv` (4 rows; R-043 is a draft and is not sent). The vendor's tool imports plain strings and maps attributes by name; no rich text or chapters are needed.

```bash
python3 <skill-dir>/scripts/reqif_bridge.py export --out requirements/exports/voucher-redemption-2026-11-03.reqif --ids R-040,R-041,R-085 --title "Voucher redemption"
reqif validate --use-reqif-schema requirements/exports/voucher-redemption-2026-11-03.reqif   # strictdoc reqif, optional
```

Expected file: `expected-output.reqif` (3 SPEC-OBJECTs with IDENTIFIER R-040, R-041, R-085; 8 string attributes; validates with 0 errors).

## Import, 2026-11-12

The vendor returns `vendor-return.reqif`. Their tool turned `Text` into a rich-text attribute, added a `Vendor comment` attribute, set R-085's Status to `Accepted`, added one requirement of their own and left R-040 out.

> /reqif-bridge import vendor-return.reqif

```bash
python3 <skill-dir>/scripts/reqif_bridge.py import vendor-return.reqif --diff
```

Expected report: `expected-import-diff.md`, saved as `requirements/exports/import-diff-2026-11-12.md`. Nothing is written to `requirements.csv` until each row has a decision.
