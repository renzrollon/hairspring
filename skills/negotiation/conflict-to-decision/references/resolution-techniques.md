# Resolution techniques and analysis aids

The five technique names follow CPRE FL Handbook 1.2 §4.3.3; the step lists and examples are this catalogue's working rules. A **technique** settles the conflict. An **analysis aid** prepares the decision and never settles it on its own. Read at step 6.

## Pick or confirm the technique

| Situation | Technique |
| --- | --- |
| Few parties, time to talk, the facts settle it once everyone sees them | agreement |
| The disagreement is on a scale (a period, a limit, a scope) and each side can give some | compromise |
| Several parties of equal standing, well-defined options, losers will accept the result | voting |
| The system can serve both needs (per tier, market, store, channel; a feature flag) at an acceptable cost | variants |
| Time pressure, a deadlock, or a principle at stake that needs someone with authority to decide | overruling |

Do not use voting or compromise for a value conflict (a principle is not traded or out-voted). Do not use any technique for a relationship or structural conflict (escalate).

## Running each technique

### Agreement

1. State the decision question and the facts (consider-all-facts first).
2. Discuss options until one remains that every decision-maker accepts.
3. Ask each decision-maker by name: "Do you agree to option X?" Record each yes with the date. Silence is not a yes.

### Compromise

1. Ask each side what matters most and what it could give up.
2. Let the parties propose the middle ground. The agent may list the dimensions that could move (period, scope, timing), never the value.
3. Record what each side gave up in "Consequences" (Bad, because ...).

### Voting

1. Before any vote: list the voters (named), the options (final wording), and the rule (simple majority, two thirds, unanimity) and what happens on a tie.
2. Collect votes as the user reports them. Record the count per option, not who voted what, unless the participants agree to it.
3. Record the rule and the count in "Decision Outcome".

### Variants

1. Name the variation point: what differs between variants (tier, store format, market, channel, configuration flag).
2. Each variant gets its own requirement, usually `WHERE <feature or configuration>, the <system> shall ...`. The scope of each variant comes from the participants.
3. Record the extra cost or complexity in "Consequences" and the open questions (who configures the variant, default value).

### Overruling

1. Name who decides and by what authority (role in `process.change_authority`, sponsor, regulator's ruling).
2. Hear every position first and record it in "Considered Options" and "Pros and Cons".
3. Record the reasons and the dissent. Plan the follow-up that addresses the losing side's concern, if any.

## Analysis aids

### Consider-all-facts (CAF)

List every factor before anyone argues: rules and their sources, costs, risks, dependencies, deadlines, data. Mark each line as a fact (with source) or an assumption (with who verifies it). Goes into "Facts and assumptions".

### Plus-minus-interesting (PMI)

For each option, list Plus (good effects), Minus (bad effects) and Interesting (neither, but worth knowing: side effects, open questions). Goes into "Pros and Cons of the Options".

### Decision matrix

1. **Criteria first.** Agree the criteria with the decision-makers. Usually the decision drivers.
2. **Weights second.** Agree a weight per criterion and the scale for scores (a 1 to 5 scale, 5 = best on that criterion, is common). Record who agreed and when, in the "Criteria" table, **before** anyone scores.
3. **Scores third.** The participants score each option per criterion. The agent records; it does not score.
4. **Compute.** Weighted total = sum of (weight x score). Show every product in the matrix. The maximum is the sum of weights x the top of the scale.
5. **Read it carefully.** Totals close to each other are a tie: decide on the merits, not on the number. A matrix informs the decision-makers; it does not replace their decision.

Worked example (loyalty-points, CF-01; weights agreed 2026-11-05 by SH-01, SH-03 and SH-07 before scoring; scale 1 to 5):

| Criterion | Weight | A: 12 months | B: 18 months | C: 12 months, 18 for Gold tier |
| --- | --- | --- | --- | --- |
| Points liability | 3 | 5 (15) | 2 (6) | 4 (12) |
| Member engagement | 2 | 2 (4) | 5 (10) | 4 (8) |
| Implementation effort | 1 | 5 (5) | 5 (5) | 2 (2) |
| **Weighted total** (max 30) | | **24** | **21** | **22** |

### An invalid matrix: stop and say so

| Symptom | Why it is invalid | What to do |
| --- | --- | --- |
| Scores exist before weights | Weights can be chosen to produce a wanted winner | Agree weights now, then rescore without looking at the old totals |
| "Change the weights so B wins" | The result is fixed in advance; the matrix becomes decoration | Refuse; offer overruling by the decision-maker with recorded reasons instead |
| The agent is asked to score or weight | The agent is not a stakeholder | Ask the participants; record `TBD` if they are not available |
| Criteria overlap (cost and price) | One concern counted twice | Merge them before weighting |
