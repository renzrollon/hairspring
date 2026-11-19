# `priorities.csv`: exact columns

`requirements/priorities.csv` holds the items of the current prioritization. Its header depends on the technique. It is the input and the output of `re-lint prioritize` (vendored: `scripts/prioritize.py`).

| Technique | Header (exact, case-sensitive) | Template |
| --- | --- | --- |
| Wiegers (`--method wiegers`, the default) | `ID,Title,Benefit,Penalty,Cost,Risk,Score,Rank,Tie` | `assets/priorities.csv` |
| WSJF (`--method wsjf`) | `ID,Title,BusinessValue,TimeCriticality,RiskReduction,JobSize,Score,Rank,Tie` | `assets/priorities-wsjf.csv` |
| MoSCoW, Kano, Top-10 (no script) | `ID,Title,MoSCoW,Kano,Top10Votes,Rank,Tie` | `assets/priorities-adhoc.csv` |

## Columns

| Column | Filled by | Rule |
| --- | --- | --- |
| `ID` | the skill | Unique item ID: `R-nnn`, a story or epic key, or a tracker key. Same level of abstraction for every row |
| `Title` | the skill | Short label (requirement `Title`, or the first words of `Text`) |
| `Benefit`, `Penalty`, `Cost`, `Risk` | scorers | Integers 1–9 |
| `BusinessValue`, `TimeCriticality`, `RiskReduction`, `JobSize` | scorers | One of 1, 2, 3, 5, 8, 13, 20. `JobSize` is never 0 |
| `MoSCoW` | decision-maker | `must`, `should`, `could`, `wont` |
| `Kano` | stakeholders | `dissatisfier`, `satisfier`, `delighter`, `indifferent` |
| `Top10Votes` | the skill (counting) | Integer: number of voters who picked the item |
| `Score` | script | 3 decimals for Wiegers, 2 for WSJF; empty for ad hoc techniques |
| `Rank` | script (Top-10: the skill) | By Score, descending; equal scores share a rank (1, 2, 2, 4). Top-10: by votes, the same way. Empty for MoSCoW and Kano |
| `Tie` | script (Top-10: the skill) | `tie, do not over-interpret` or empty. Neighbours within the tie band form a group, chained along the ranking. Top-10: equal votes |

## The weights row

Record the agreed weights in the matrix itself, as the first data row with `ID` = `Weights`:

```csv
ID,Title,Benefit,Penalty,Cost,Risk,Score,Rank,Tie
Weights,,2,1,1,0.5,,,
R-063,Second approver for large adjustments,2,8,2,1,,,
```

The script reads the weights from this row and keeps the row at the top of the output. `--weights` overrides it key by key. Fill all four cells and pass the same four values in `--weights`, so a run never falls back to a default nobody agreed. Who agreed the weights, and when, goes in `priorities.md`.

## What the script does with the file

- It matches headers case-insensitively and ignores spaces, `_` and `-` (`Business Value` is `BusinessValue`). The templates use the exact names above; keep them.
- It reads the score columns of the chosen method. The other columns are kept unchanged, in place.
- It overwrites `Score`, `Rank` and `Tie`, and adds them at the end if they are missing. An input that has only the item and score columns is valid.
- It writes the rows in rank order, after the weights row, with LF line endings and minimal quoting. The `Tie` value contains a comma, so it is quoted. On stdout it prints a Markdown summary with the tie groups.
- It exits with `2` and writes nothing on a missing column, an empty, non-numeric or negative score, a `Cost` or `JobSize` of 0, or bad `--weights`. A duplicate ID only gives a warning, so check IDs yourself.
- It does not check the scale. Make sure every score is an integer on the scale in `techniques.md` before you run it.
- `--weights` keys are `benefit`, `penalty`, `cost`, `risk` for Wiegers. WSJF also takes weights (`business_value`, `time_criticality`, `risk_reduction`, `job_size`, default 1); leave them at 1 unless the decision-maker asks otherwise.

## Companion record

The goal, criteria, scorers, weights (with who agreed and when), disputed items and the decision go in `requirements/priorities.md` (template `assets/priorities.md`). A CSV cannot hold them, and without them the numbers cannot be reviewed.
