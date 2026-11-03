# Planguage option

Planguage is Tom Gilb's specification language for quality requirements (*Competitive Engineering*, 2005). It separates the scale of measure from the way of measuring and from the levels you plan for, which makes a quality requirement hard to misread. Use it when the user asks for it or when a requirement needs several levels (minimum, planned, wished).

## Keywords used in re-skills

| Keyword | Meaning | Maps to the table column |
| --- | --- | --- |
| Tag | The requirement ID | Requirement |
| Gist | One-line summary in plain words | (none) |
| Scale | The scale of measure, with unit and statistic | Metric |
| Meter | How and when the value is measured | Measurement method |
| Past | A baseline value measured before, with its source | Condition (as baseline) |
| Must | The minimum acceptable level: below it the requirement fails | Target, and the value in `requirements.csv` Text |
| Plan | The level the team plans to reach | (block only) |
| Wish | A desirable level without commitment | (block only) |
| Qualifier | The condition: when, where, under which load (written in square brackets in Gilb's notation) | Condition |
| Source | Who gave each level | `requirements.csv` Source |

Rules:

- `Must` is the binding level, so it is the value in the `requirements.csv` `Text` with `shall`. `Plan` and `Wish` stay in the block.
- Every level needs a source. Unknown levels are `TBD` with an open question, exactly as in the table.
- Keep the table row in *Quality requirements*; the block adds levels, it does not replace the row.

## Block template

```text
Tag: R-nnn
Gist: <one line>
Scale: <unit and statistic of the measured property>
Meter: <how and when it is measured>
Qualifier: [<condition>]
Past: <baseline value> (<source>) | none
Must: <value> | TBD (Qn)
Plan: <value> | TBD (Qn) | none
Wish: <value> | none
Source: <person and date, or source ID, per level>
```

## Worked example (loyalty-points sample)

```text
Tag: R-082
Gist: Accept the year-end sale peak of purchase events without losing any.
Scale: Purchase events accepted per minute, sustained, with zero lost events.
Meter: Load test replaying a peak-day profile before release; intake rate and consumer lag in production during the sale.
Qualifier: [year-end sale peak, all 140 stores, for the peak duration TBD (Q3)]
Past: 9,000 purchases per minute across stores at last year's peak (SH-08, 2026-11-03)
Must: TBD (Q3: planned peak for this year)
Plan: TBD (Q3)
Wish: none
Source: Wei Jie Chua (SH-08), 2026-11-03
```
