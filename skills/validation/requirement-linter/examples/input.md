# Input: lint the loyalty-points register

Request (Wei Jie Chua, platform tech lead, 2026-11-03): "CI went red on my PR. What's wrong with the requirements and how do I fix them?"

- Register: `examples/requirements.csv`, placed at `requirements/requirements.csv` in the repo. Fourteen rows, seeded with one defect of each common kind.
- No `requirements/schema.json`: the default rules and severities apply.
- Command, from the repo root:

```bash
python3 <skill-dir>/scripts/lint_requirements.py
# same result: re-lint check
```

## Expected results

- `expected-output.txt`: the exact text report. Exit code `1` (8 errors at or above the default `--fail-on error`).
- `expected-output.md`: the explanation table and the reply the skill gives.
- R-019 contains "quickly" but is `rejected`, so only structural rules run on it: no finding.
- R-001 and the first R-040 are clean.
