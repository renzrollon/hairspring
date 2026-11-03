# Input: legacy points posting (loyalty-points sample)

The user's prompt: "Mine the legacy points-posting procedure for candidate requirements. Check it against the programme terms."

`examples/input/` stands for the repository root. It holds:

| File | Source | Technique |
| --- | --- | --- |
| `legacy/loyalty/sp_post_points.sql` | S-04 Legacy loyalty module: stored procedures and nightly batch scripts | system-archaeology |
| `docs/programme-terms-v3-excerpt.md` | S-01 Harbourline Rewards programme terms, draft v3 | document-analysis (used here to back or contradict the legacy rules) |

`requirements/sources.csv` (not reproduced here) registers S-01 and S-04; `requirements/candidates.csv` does not exist yet, so IDs start at CAN-001. Stakeholders are those of `examples/loyalty-points/BRIEF.md`.

The expected output is `expected-output.csv` (the new `requirements/candidates.csv`) and the summary shown to the user (`expected-output.md`). Check it with:

```bash
python3 scripts/check_candidates.py examples/expected-output.csv --root examples/input
```
