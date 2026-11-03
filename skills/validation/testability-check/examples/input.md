# Input: testability check before sprint planning (loyalty-points sample)

Request (Daniel Ng's QA colleague, 2026-11-03): "Before planning on Thursday: how do we verify each of these, and which ones can't we test yet?"

- Register: `requirements.csv` in this folder, placed at `requirements/requirements.csv`. Eleven rows across earning, balance, vouchers, adjustments, quality requirements and constraints.
- No `verification.csv` yet, no `quality-requirements.md`; default `schema.json`.
- Non-interactive: nobody is available to answer questions before planning.

## Expected results

- `requirements/verification.csv`: see `expected-output.csv` (header from `assets/verification.csv`).
- `requirements/requirements.csv` with the `Verification` column added: see `expected-requirements.csv`. Only that column changes; R-082 (`Verifiable` = `no`) stays empty.
- Linter on both files: no `register-drift`, no `invalid-enum`. The weak word "intuitive" in R-082 is still reported; it is fixed by `requirement-phrasing` once Q2 is answered.
- The final message: see `expected-output.md`.
