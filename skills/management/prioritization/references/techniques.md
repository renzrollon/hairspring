# Prioritization techniques, scales and rules

## The six steps

| Step | Question to settle | Recorded in `priorities.md` |
| --- | --- | --- |
| 1. Goals and constraints | Which decision does this ranking serve (release scope, next increment, MVP cut)? What is fixed (deadline, capacity in the team's own unit, legal or contractual musts)? | §1 |
| 2. Criteria | By which few criteria do we compare? What does each one mean? | §2 |
| 3. Stakeholders | Who scores which criterion? Who owns the final order? | §3 |
| 4. Items | Which items, at one level of abstraction? What is excluded, and why? | §4 |
| 5. Technique | Which technique, and why? For analytical techniques: which weights, agreed by whom and when? | §5 |
| 6. Run | Scores, computed result, ties, disputed items, cut line, decision | §6 and the sections after it |

Settle steps 1 to 5 before anyone scores. A ranking that comes before its criteria are agreed gets argued about, not used.

## Choosing a technique

| Situation | Technique | Kind |
| --- | --- | --- |
| A release cut with one decision-maker and a short list | MoSCoW | ad hoc |
| A long list and many voters; you need a short list first | Top-10 | ad hoc |
| Product features where customer satisfaction drives value | Kano | ad hoc |
| Several criteria, several stakeholders, and a result that others must accept | Wiegers (weighted benefit, penalty, cost, risk) | analytical |
| A flow-based backlog that is ordered by cost of delay (SAFe teams) | WSJF | analytical |

The techniques combine. Use Kano first to find the dissatisfiers, which are must-haves without scoring, and then run Wiegers on the rest.

## Scales

| Technique | Columns | Scale |
| --- | --- | --- |
| Wiegers | Benefit, Penalty, Cost, Risk | Integers 1 to 9, relative to the other items in this run. 1 is the lowest benefit, penalty, cost or risk. Benefit is the value if the item is present; Penalty is the harm if it is absent; Cost is the effort to build it; Risk is the risk of building it |
| WSJF | BusinessValue, TimeCriticality, RiskReduction, JobSize | The modified Fibonacci values 1, 2, 3, 5, 8, 13, 20, relative. Give the smallest item in each column a 1 and score the others against it (SAFe practice) |
| MoSCoW | MoSCoW | `must`, `should`, `could`, `wont` (the schema's `Priority` values) |
| Kano | Kano | `dissatisfier`, `satisfier`, `delighter`, `indifferent` (the schema's `Kano` values) |
| Top-10 | Top10Votes | Each voter picks up to ten items; the cell is the number of voters who picked the item |

For Kano, ask each item as a pair of questions: "How would you feel if the app had X?" and "How would you feel if it did not?" A member who expects X and is unhappy without it marks a dissatisfier. Someone whose satisfaction grows with how much of X there is marks a satisfier. Someone pleased by X who would not miss it marks a delighter. Someone with no reaction either way marks indifferent. Dissatisfiers rank first, and indifferent items are candidates for `wont`.

## Formulas (computed by `re-lint prioritize`)

Wiegers (Wiegers and Beatty, *Software Requirements*), weights `wb, wp, wc, wr`:

```text
value_i    = wb * Benefit_i + wp * Penalty_i
value%_i   = value_i / sum(value)
cost%_i    = Cost_i  / sum(Cost)
risk%_i    = Risk_i  / sum(Risk)
Score_i    = value%_i / (wc * cost%_i + wr * risk%_i)
```

WSJF (all weights 1 unless the decision-maker sets others):

```text
Score_i = (BusinessValue_i + TimeCriticality_i + RiskReduction_i) / JobSize_i
```

Ranking: sort by full-precision Score, descending; equal scores share a rank. The script writes Score with 3 decimals for Wiegers and 2 for WSJF.

Weights: the decision-maker sets them. When asked for a starting point, offer the weights from Wiegers' worked example (benefit 2, penalty 1, cost 1, risk 0.5) as a proposal to confirm. Record the confirmed values, who confirmed them and the date before any score is collected.

## Ties and pseudo-accuracy

Two neighbours in the ranking are tied when `|Score_a - Score_b| <= tie_band * max(Score_a, Score_b)`. The default `--tie-band` is 0.05, a relative band. Tied items get `tie, do not over-interpret` in `Tie`.

All inputs are ordinal judgments on a coarse scale. The last decimals of a score are noise, and so is the difference between neighbours inside the tie band. Read the result in bands: top, middle and bottom. Let the decision-maker set the cut line against the capacity constraint. Never add decimals beyond what the script writes, and never present a difference in the last decimal, or a rank difference inside a tie group, as a finding.

## Disagreement is a conflict, not an average

When stakeholders score the same item and criterion separately and their scores sit at opposite ends of the scale, do not average them. On the 1–9 scale that means one score in 1–3 and the other in 7–9. For WSJF it means 1–2 against 13–20. For MoSCoW it means `must` against `could` or `wont`. Instead:

1. Record both scores, with the stakeholder IDs, in `priorities.md` § Disputed items.
2. Run `conflict-detector` to register the conflict (`CF-nn`). It is usually an interest or value conflict.
3. Keep the item out of `priorities.csv` until it is resolved. Recommend `/conflict-to-decision`.
4. Optionally, show what is at stake: run the script on a scratch copy once with each score and report whether the item moves across the cut line.

Smaller differences are normal. Let the scorers agree on one value in the session and record it.

## From rank to the `Priority` attribute

`Priority` in `requirements.csv` is `must | should | could | wont`. A rank does not map to a priority by itself. Propose a mapping, for example "above the cut line: must or should; below: could", and change `Priority` only for the items the decision-maker confirms.
