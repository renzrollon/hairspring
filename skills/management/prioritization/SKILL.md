---
name: prioritization
description: >-
  Runs a requirements prioritization in six steps (goals and constraints, criteria, stakeholders,
  items, technique, run) and writes requirements/priorities.csv plus the run record
  requirements/priorities.md. Uses ad hoc techniques (MoSCoW, Top-10, Kano) or analytical ones
  (Wiegers weighted benefit/penalty/cost/risk, WSJF) computed by re-lint prioritize. Weights are
  agreed and recorded before anyone scores, ties are flagged "tie, do not over-interpret", and
  stakeholder disagreement is registered as a conflict instead of being averaged away. Started
  explicitly with /prioritization. Use when a backlog, release scope or MVP cut needs a defensible
  order, when someone asks "what do we build first", "rank these requirements", "MoSCoW this",
  "run WSJF", or when stakeholders argue about priority. Not for contradictions in requirement
  content (conflict-detector), sizing one change request (change-impact), or recording the
  priority someone just stated for a new requirement (requirement-phrasing).
license: MIT
compatibility: Python 3.9+ optional for scripts/prioritize.py; works without it.
disable-model-invocation: true
argument-hint: "[items: IDs, epic, file or list]"
metadata:
  stage: management
  invocation: user
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §6.8"
  inputs-from: "requirement-phrasing, user-story-refiner, stakeholder-map, requirement-classifier, change-impact"
  outputs-to: "conflict-detector, issue-sync, spec-assembler, baseline"
  work-product: "requirements/priorities.csv, requirements/priorities.md"
  version: "0.1.0"
---

# Prioritization

A priority is a decision about order under constraints. It is only as good as the agreement behind it. This skill makes the six decisions of a prioritization explicit: why we prioritize, by which criteria, who scores, which items, which technique, and the run itself. A script does the arithmetic. The skill ends with a matrix and a short record of who agreed what and when.

## When not to use

- Two requirements contradict each other in content: `conflict-detector`.
- One change request needs sizing and a decision: `/change-impact`.
- A stakeholder just stated the priority of one new requirement: `requirement-phrasing` records it with the source.
- You are ordering implementation tasks inside one story. That is the team's sprint planning, not a requirements prioritization.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Items to rank: R-IDs from `requirements/requirements.csv`, stories, or a list | yes | `requirement-phrasing`, `user-story-refiner` |
| Goal, constraints, and scores from named stakeholders | yes | the user and the stakeholders |
| `requirements/stakeholders.md` | no | `stakeholder-map` |
| `requirements/priorities.csv` and `priorities.md` from an earlier run | no | this skill |
| `requirements/conflicts.md` | no | `conflict-detector` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/priorities.csv` | `assets/priorities.csv` (Wiegers), `assets/priorities-wsjf.csv` or `assets/priorities-adhoc.csv`; exact columns in `references/priorities-format.md` | decision-maker, `issue-sync`, `spec-assembler` |
| `requirements/priorities.md` | `assets/priorities.md` | reviewers, `conflict-detector` |
| `Priority` column in `requirements/requirements.csv` (only for items the decision-maker confirms) | schema enum `must`, `should`, `could`, `wont` | every skill |

## Procedure

1. **Read the workspace.** Read `requirements/schema.json`, `requirements.csv`, `stakeholders.md`, `conflicts.md`, and any earlier `priorities.csv` and `priorities.md`. If an earlier run exists, ask whether this is a re-run with the same criteria and weights or a new prioritization. Start `priorities.md` from `assets/priorities.md`.
2. **Goals and constraints.** Ask which decision the ranking serves (release scope, next increment, MVP cut) and what is fixed: the deadline, the capacity in the team's own unit, and the legal or contractual musts. Fixed musts are not scored: record them in §1 and list them in §4 as excluded, with the reason. Anything unknown is `TBD` plus an open question. Ask with `re-interview`, one question at a time.
3. **Criteria.** Pick the fewest criteria that serve the goal: benefit, penalty, cost, risk for Wiegers; business value, time criticality, risk reduction, job size for WSJF. Write a one-line meaning for each, specific to this run, in `priorities.md` §2.
4. **Stakeholders.** Decide who scores what. Business stakeholders score benefit and penalty, or business value and time criticality. The delivery team scores cost, risk and job size. Use the SH-IDs from `stakeholders.md`. Name one decision-maker who owns the final order; this is usually the product owner or the change authority in `schema.json`.
5. **Items.** List each item with its ID and Title. Keep all items at one level of abstraction: all epics, or all requirements or stories. If the levels are mixed, ask whether to split the epics or to group the stories. Exclude withdrawn, rejected and already implemented items, and list each exclusion with its reason.
6. **Technique.** Choose with the table in `references/techniques.md` and write the reason in one sentence. Use MoSCoW for a quick release cut with one decision-maker. Use Wiegers when several criteria and stakeholders must accept the result. Use WSJF for a flow-based backlog. Use Top-10 for a long list with many voters, and Kano when customer satisfaction drives value.
7. **Agree the weights before scoring (Wiegers only).** Ask the decision-maker for the four weights. Record the value, who agreed and the date in `priorities.md` §5 before you collect any score. If they ask for a starting point, propose the weights from Wiegers' worked example (benefit 2, penalty 1, cost 1, risk 0.5) and get them confirmed. If scores already exist, warn that weights chosen now can steer the result, and record "set after scoring". Never search for weights that produce a wanted order. For WSJF, leave the weights at 1 unless the decision-maker sets others.
8. **Collect the scores.** Use the scale in `references/techniques.md`: one agreed integer per cell. If two stakeholders give scores at opposite ends of the scale for the same item and criterion, do not average them. Record both in `priorities.md` § Disputed items, run `conflict-detector` to register the conflict, and keep the item out of `priorities.csv` until it is resolved. Recommend `/conflict-to-decision`.
9. **Compute.** Write `requirements/priorities.csv` from the matching asset, with one row per item and `Score`, `Rank`, `Tie` empty. For Wiegers, put the agreed weights in a first `Weights` row (`references/priorities-format.md`). Then run:
   - Wiegers: `re-lint prioritize requirements/priorities.csv --method wiegers --weights benefit=<wb>,penalty=<wp>,cost=<wc>,risk=<wr> --out requirements/priorities.csv`
   - WSJF: `re-lint prioritize requirements/priorities.csv --method wsjf --out requirements/priorities.csv`
   - Without the package, run `python3 <skill-dir>/scripts/prioritize.py` with the same arguments. Keep the default `--tie-band 0.05` unless the decision-maker chose another band.
   - Without Python: compute with the formulas in `references/techniques.md`, write `Score` with 3 decimals (Wiegers) or 2 (WSJF), and mark ties by the same rule.
   - Ad hoc techniques: fill `MoSCoW`, `Kano` or `Top10Votes` (and `Rank` and `Tie` for Top-10) by hand, as in `references/priorities-format.md`.
10. **Read the result.** Present the ranking in bands (top, middle, bottom), not as a precise order. Name every item flagged `tie, do not over-interpret`. Say plainly that the scores rest on ordinal judgments: differences in the last decimals, or inside the tie band, mean nothing. Propose a cut line against the capacity constraint and fill §6 of `priorities.md`.
11. **Record the decision.** Record the cut line, who decided and the date in `priorities.md` § Decision. If the decision-maker confirms new `must`/`should`/`could`/`wont` values for R-ID items, show the diff of the `Priority` column and write it to `requirements.csv`. Never derive `Priority` from the rank by yourself.

## Quality checks

- [ ] `priorities.md` records the goal, constraints, criteria, scorers and decision-maker before it records the result.
- [ ] The weights (value, who, date) were recorded before scoring, or the record says they were set after.
- [ ] All items are at one level of abstraction, and every exclusion has a reason.
- [ ] Scores are integers on the stated scale. No cell holds an average of disagreeing scores.
- [ ] `priorities.csv` has the exact header for its technique, and `Score`, `Rank`, `Tie` come from the script or the documented formula.
- [ ] Ties are named in the message. No statement relies on a difference inside the tie band, and no score has more decimals than the script writes.
- [ ] `Priority` in `requirements.csv` changed only for items the decision-maker confirmed.

## Hand-offs

- **Next:** `conflict-detector` for each disputed item, then suggest `/conflict-to-decision`. Suggest `/issue-sync` to carry the order into the tracker, and `/baseline` once the release scope is agreed.
- **Feeds back to:** suggest `/stakeholder-map` when a criterion has no scorer. Suggest `/user-story-refiner`, or use `requirement-phrasing`, when items are at mixed levels or too vague to score. Suggest `/change-impact` for an item whose cost nobody can score because its scope is still changing.

## Non-interactive mode

Never invent scores or weights. If the input contains the weights (with who agreed them) and the scores, compute and write both files. Otherwise fill `priorities.md` §1–5 with what is known, write `TBD` and open questions for the rest, write `priorities.csv` with `ID` and `Title` filled and the score columns empty, and stop.

## Pitfalls

- Scoring first and choosing weights afterwards. The weights then become a lever for a wanted result.
- Mixing epics and stories in one run. The epics win on benefit and lose on cost, and the result says nothing.
- Treating rank 3 against rank 4 as a finding when both sit in the same band.
- Averaging a must against a won't. That hides a conflict that will come back at release time.
- A MoSCoW run where everything becomes must. Ask: "If we could ship only half, which half?"

## References

- `references/techniques.md`: the six steps, technique choice, scales, the Wiegers and WSJF formulas, ties and pseudo-accuracy, the disagreement rule, and mapping rank to `Priority`. Read it at steps 6 to 10.
- `references/priorities-format.md`: the exact `priorities.csv` columns for each technique, and what the script reads and writes. Read it at step 9.
- `references/ireb-anchor.md`: the handbook section and glossary terms this skill applies.
- `examples/`: a Wiegers run on six loyalty-points requirements for the January release.
