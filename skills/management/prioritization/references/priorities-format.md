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
| `Score` | script | 2 decimals; empty for ad hoc techniques |
| `Rank` | script (Top-10: the skill) | 1..n by full-precision Score, descending, then ID. Top-10: by votes, then ID. Empty for MoSCoW and Kano |
| `Tie` | script (Top-10: the skill) | `tie, do not over-interpret` or empty. Top-10: equal votes |

## What the script does with the file

- It reads the score columns of the chosen method. The other columns are kept unchanged, in place.
- It overwrites `Score`, `Rank` and `Tie`, and adds them at the end if they are missing. An input that has only the item and score columns is valid.
- It writes the rows in `Rank` order, with LF line endings and minimal quoting. The `Tie` value contains a comma, so it is quoted.
- It exits with `2` (and writes nothing) on a missing column, a non-integer or out-of-scale score, a duplicate ID, or `JobSize` 0.
- `--weights` applies to `wiegers` only. Pass all four weights every time (`benefit=..,penalty=..,cost=..,risk=..`), so a run never depends on a default nobody agreed.

## Companion record

The goal, criteria, scorers, weights (with who agreed and when), disputed items and the decision go in `requirements/priorities.md` (template `assets/priorities.md`). A CSV cannot hold them, and without them the numbers cannot be reviewed.
