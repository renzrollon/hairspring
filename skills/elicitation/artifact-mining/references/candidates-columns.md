# `candidates.csv` columns

`requirements/candidates.csv` is the shared register of candidate requirements: statements that may become requirements once someone classifies, confirms and phrases them. `artifact-mining` owns it; `interview-guide`, `elicitation-workshop` and `observation-protocol` append rows in the same shape. The header is fixed, in this order:

```text
ID,Statement,Type,Technique,Source,Location,Quote,Disposition,Reason,Owner,Kano,Requirement
```

| Column | Required | Values | Rule |
| --- | --- | --- | --- |
| `ID` | yes | `CAN-` + 3 digits (schema `ids.candidate`) | Allocated with `re-ids --kind candidate`. Never reused, never renumbered. |
| `Statement` | yes | One sentence | What the system does or must do, in domain words and glossary terms. No table, column, class or queue names. Numbers only if they are in the quote. |
| `Type` | yes | `F`, `Q`, `C`, `TBD` | First guess. `requirement-classifier` decides when unsure. |
| `Technique` | yes | `document-analysis`, `system-archaeology`, `feedback-analysis`, `interview`, `workshop`, `observation`, `questionnaire` | How the candidate was found. |
| `Source` | yes | `S-nn`, `I-nn`, `SH-nn`, or a person or role and ISO date | The source register ID when there is one. |
| `Location` | yes | See below | Where the quote is. Repo-relative, forward slashes. |
| `Quote` | yes | Verbatim text, a few lines at most | Whitespace may be collapsed; `...` marks a gap; personal data masked as `[name]`, `[email]`, `[phone]`, `[nric]`, `[card]`, `[address]`, `[member]` or `[redacted]`. |
| `Disposition` | yes | `keep`, `drop`, `confirm` | `keep`: carry forward as is. `confirm`: a named owner must confirm before it becomes a requirement. `drop`: do not carry forward; the reason stops anyone re-mining it. |
| `Reason` | yes | One sentence | Why this disposition; cite the backing or conflicting source with its location. |
| `Owner` | for `confirm` | Name with SH-ID, role, or `TBD` | Who confirms. `TBD` needs an open question in the run summary. |
| `Kano` | no | `dissatisfier`, `satisfier`, `delighter`, `indifferent`, `TBD`, empty | A first guess; empty means not assessed. |
| `Requirement` | no | Space-separated `R-nnn` | Filled when the candidate becomes a requirement, or the requirement it duplicates. |

## Location formats

| Form | Example | Checked by `check_candidates.py` |
| --- | --- | --- |
| `path:line` | `legacy/loyalty/sp_post_points.sql:12` | File exists; quote found within `--window` lines of line 12 |
| `path:start-end` | `api/pos-loyalty-v2.1.yaml:40-52` | File exists; quote found in the range plus the window |
| `path#anchor` | `requirements/elicitation/interview-support-lead.md#C3` | File exists; quote found anywhere in the file |
| `S-nn <item>` | `S-03 ticket 48812`, `S-01 p.4 §4.3` | Not verified (artifact outside the repo); reported as info |

A line number in a CSV export (support tickets) is the physical line of the file, header included.

## Moving a candidate on

- `requirement-phrasing` writes the requirement and puts its ID in `Requirement`; the candidate row stays as the trace to its quote.
- A confirmed candidate changes `Disposition` from `confirm` to `keep` (or `drop`), and `Reason` gains who confirmed and when: `Confirmed by Mei Tan (SH-01) 2026-11-04`.
- Never delete a row.
