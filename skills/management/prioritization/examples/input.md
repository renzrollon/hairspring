# Input: January release, loyalty-points sample

Command: `/prioritization R-004 R-021 R-026 R-043 R-061 R-063 R-100`

Notes the user pasted, collected 2026-10-30 to 2026-11-02:

- **Goal (SH-01 Mei Tan):** pick what goes into the January app and console release.
- **Capacity (SH-08 Wei Jie Chua):** "We can build about four of these in January."
- **Fixed:** R-100 (retain transaction records for 7 years) is required by the retention policy (S-05). It is not up for ranking.
- **Technique:** Wiegers. Several stakeholders must accept the result.
- **Weights:** agreed by Mei Tan on 2026-10-30, before scoring: benefit 2, penalty 1, cost 1, risk 0.5.
- **Scorers:** benefit and penalty were scored together by SH-01 Mei Tan, SH-07 Priya Raman and SH-06 Daniel Ng on 2026-11-02. Cost and risk were scored by SH-08 Wei Jie Chua for the platform team on 2026-11-02. All scores are relative, on 1 to 9.

| ID | Title | Benefit | Penalty | Cost | Risk |
| --- | --- | --- | --- | --- | --- |
| R-004 | Bonus campaign multiplier | 7 | 2 | 5 | 4 |
| R-021 | Points history in the app | 6 | 4 | 3 | 2 |
| R-026 | Push notification when points are posted | 4 | 2 | 2 | 2 |
| R-043 | Redeem a voucher in the app | 9 | 7 | 6 | 5 |
| R-061 | Expiry reminder before points expire | 3 | 6 | 3 | 2 |
| R-063 | Second approver for large adjustments | 2 | 8 | 2 | 1 |

Command run after writing `requirements/priorities.csv`:

```sh
python3 <skill-dir>/scripts/prioritize.py requirements/priorities.csv --method wiegers --weights benefit=2,penalty=1,cost=1,risk=0.5 --out requirements/priorities.csv
```

Expected outputs: `expected-output.csv` (`requirements/priorities.csv`) and `expected-output.md` (`requirements/priorities.md`).
