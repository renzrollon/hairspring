# Input: change request from Marketing (loyalty-points sample)

Command: `/change-impact` with this email pasted:

> **From:** Priya Raman (Marketing manager, SH-07) · **Date:** 2026-11-02
>
> For the year-end campaign we want members to redeem from 300 points instead of 500. Many members sit between 300 and 500 points and never redeem. The redeem screen in the app says "Redeem from 500 points". Can we have it live by 1 December?

## Workspace state

- No `requirements/schema.json`: the default change authority applies (`product-owner`, SH-01 Mei Tan).
- `requirements/requirements.csv` and `requirements/trace/trace.csv` are the ones in `skills/management/traceability-matrix/examples/` (`input.md` and `expected-output.csv`). This is the hand-off from `traceability-matrix`.
- The register row for R-041 (line 7, no `Version` column):

  ```csv
  R-041,F,"IF a member requests a redemption of fewer than 500 posted points, THEN the loyalty service shall reject the redemption with the reason ""below minimum"".",S-01,must,implemented,Minimum redemption in the programme terms.,test,
  ```

- `requirements/context.md` lists the customer mobile app (App → service: balance, history, redemption) and the POS (service → POS: voucher validation).
- No `conflicts.md`; no earlier CRs.

## Commands run

```sh
python3 <skill-dir>/scripts/trace_matrix.py impact R-041 --format md
```

Linked nodes returned for R-041: `S-01` (source-of), `src/loyalty/redeem.py` (implemented-by, `src/loyalty/redeem.py:12`), `3f9c2ab` (implemented-by, commit), `tests/test_redeem.py::test_r_041_rejects_below_minimum` (verified-by, `tests/test_redeem.py:9`).

A repository search for `500`, `minimum` and `MIN_REDEMPTION` found one more hit about this rule: `src/loyalty/redeem.py:13 MIN_REDEMPTION_POINTS = 500`. Other hits for `500` were unrelated and were discarded.

Expected output: `expected-output.md`, saved as `requirements/changes/CR-001-lower-minimum-redemption.md`. `requirements.csv` is not changed, because no decision has been taken yet.
