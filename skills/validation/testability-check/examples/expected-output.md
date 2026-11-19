# Expected final message: testability summary

Wrote `requirements/verification.csv` (11 rows) and set `Verification` in `requirements/requirements.csv` for 10 rows. No requirement text, status or version changed.

| Verifiable | Count | IDs |
| --- | --- | --- |
| yes | 7 | R-001, R-002, R-003, R-042, R-065, R-100, R-102 |
| tbd | 3 | R-024, R-083, R-084 |
| no | 1 | R-082 |

| Method | Count | Level | Count |
| --- | --- | --- | --- |
| test | 8 | unit | 1 |
| inspection | 1 | integration | 3 |
| analysis | 1 | e2e | 3 |
| demonstration | 1 | manual | 4 |

Open questions (non-interactive run, none asked):

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| Q1 | How many seconds after posting must the new balance be visible, at which percentile and under what load? | SH-01 Mei Tan | R-024 |
| Q2 | Which tasks define "intuitive" for the app, how many first-time members, and what completion rate and time count as a pass? | SH-01 Mei Tan | R-082 |
| Q3 | What peak rate must the service accept, and for how long? Last year's peak was about 9,000 purchases per minute; is the target that figure or higher? | SH-08 Wei Jie Chua | R-083 |
| Q4 | What availability target applies, over which hours, and does planned maintenance count as downtime? | SH-08 Wei Jie Chua | R-084 |

Next: R-082 cannot be planned until Q2 is answered and `requirement-phrasing` rewrites it; consider `/prototype-brief` to find the pass criteria with members. Give `requirements/verification.csv` to the test strategy; name tests `test_r_nnn_...` so `traceability-matrix` finds them.
