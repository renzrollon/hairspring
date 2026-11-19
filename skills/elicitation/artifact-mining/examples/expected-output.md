# Expected summary: legacy points posting mined

Mined `legacy/loyalty/sp_post_points.sql` (S-04, 30 lines) against `docs/programme-terms-v3-excerpt.md` (S-01). Eight candidates, CAN-001 to CAN-008, appended to `requirements/candidates.csv`; `check_candidates.py` reports 0 errors.

| Disposition | Count | IDs |
| --- | --- | --- |
| keep | 2 | CAN-001 (24-hour pending window, S-01 4.3), CAN-003 (1 point per SGD 1, rounded down, S-01 4.1) |
| drop | 2 | CAN-004 (XMAS2019 triple points: probable obsolete rule), CAN-007 (CRM staging table: implementation detail) |
| confirm | 4 | see below |

## To confirm, by owner

| Owner | Candidate | Question to ask |
| --- | --- | --- |
| Mei Tan (SH-01) | CAN-002 | Is "available 24 hours after purchase" a maximum, or is posting in the next nightly run acceptable? |
| Mei Tan (SH-01) | CAN-005 | Should earning stay capped at 5,000 points per transaction? Who asked for the cap? |
| Grace Lim (SH-03) | CAN-006 | The legacy job writes off negative balances on the next posting; S-01 6.2 allows them. Keep the write-off or recover from future earnings? |
| Wei Jie Chua (SH-08) | CAN-008 | One failing transaction rolls back the whole night's posting. Is per-transaction failure handling required? |

## Not candidates

- Cursor loop, `loy_txn` status codes `P` and `X`, `COMMIT`: implementation. The status codes go to `glossary` (`P` = pending, `X` = posted).

## Next

- `requirement-phrasing` on CAN-001 and CAN-003 (both F).
- `clarifying-questions` with one batch for Mei Tan (CAN-002, CAN-005) and one each for Grace Lim and Wei Jie Chua.
- `glossary`: legacy status codes `P` and `X`.
