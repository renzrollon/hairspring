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

Output for R-041 (depth 2): no other requirement at hop 2. Code: `src/loyalty/redeem.py` (`src/loyalty/redeem.py:12`). Tests: `tests/test_redeem.py::test_r_041_rejects_below_minimum` (`tests/test_redeem.py:9`). Sources: `S-01` (`requirements/requirements.csv:7`). Commits: `3f9c2ab`. Decisions: none.

A repository search for `500`, `minimum` and `MIN_REDEMPTION` found one more hit about this rule: `src/loyalty/redeem.py:13 MIN_REDEMPTION_POINTS = 500`. Other hits for `500` were unrelated and were discarded.

Expected output: `expected-output.md`, saved as `requirements/changes/CR-001-lower-minimum-redemption.md`. `requirements.csv` is not changed, because no decision has been taken yet.
