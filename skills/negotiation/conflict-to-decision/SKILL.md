---
name: conflict-to-decision
description: >-
  Runs a resolution session for one requirements conflict (a CF-nn from requirements/conflicts.md,
  or a described disagreement) with an agreed technique (agreement, compromise, voting, variants,
  overruling), prepared with consider-all-facts, plus-minus-interesting or a decision matrix whose
  weights are agreed before scoring. Writes a Requirements Decision Record,
  requirements/decisions/RDR-nnn-{slug}.md, with MADR-style headings (constraints, assumptions,
  options, chosen resolution and reasons, decision-makers, affected R-IDs and their updates) so it
  can sit next to ADRs, and updates the affected requirements only after the user confirms. Started
  explicitly by the user: /conflict-to-decision CF-01. Use when stakeholders must choose between
  conflicting requirements ("12 or 18 months?"), after conflict-detector registered a conflict, or
  to record a decision taken in a meeting. Not for finding conflicts (conflict-detector), technology
  choices (an ADR), or changing baselined requirements (change-impact).
license: MIT
disable-model-invocation: true
argument-hint: "[CF-ID, R-IDs or a short description of the disagreement]"
metadata:
  stage: negotiation
  invocation: user
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §4.3.3, §4.3.4"
  inputs-from: "conflict-detector, stakeholder-map, prioritization, re-interview"
  outputs-to: "requirement-phrasing, requirement-linter, traceability-matrix, change-impact, requirements-review"
  work-product: "requirements/decisions/RDR-nnn-<slug>.md"
  version: "0.1.0"
---

# Conflict to decision

A conflict is resolved when the people with authority have chosen, for reasons others can read later, and the requirements say what was chosen. This skill facilitates that choice with one resolution technique, records it as a Requirements Decision Record (RDR) whose headings match MADR-style architecture decision records, and then, only after confirmation, updates the affected requirements. The agent prepares, asks and records. It never votes, sets a weight, scores an option or picks the outcome.

## When not to use

- You are not sure there is a conflict: the `conflict-detector` skill finds and registers it first (this skill runs it for you when you pass R-IDs).
- The conflict is of type relationship or structural: it goes to escalation. This skill only records the escalation owner's decision afterwards (step 2).
- A technology or architecture choice ("Kafka or SQS"): write an ADR in your ADR folder; this skill decides requirements, not designs.
- An agreed requirement in a baseline must change because of a new request: suggest the user runs `/change-impact`, which drafts a change request for the change authority.
- Ranking many backlog items: suggest `/prioritization`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| A CF-ID in `requirements/conflicts.md`, or the conflicting R-IDs or a description | yes | `conflict-detector` |
| `requirements/requirements.csv` | yes | `requirement-phrasing` |
| Session facts the user gives: participants, weights, scores, votes, the decision | no | the session participants |
| `requirements/stakeholders.md` | no | `stakeholder-map` |
| `requirements/decisions/RDR-*.md` (earlier decisions) | no | this skill |
| `requirements/schema.json` (`process.change_authority`) | no (defaults apply) | `re-setup` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/decisions/RDR-nnn-<slug>.md` | `assets/rdr.md` | `traceability-matrix`, `change-impact`, `requirements-review` |
| `requirements/requirements.csv`: `Status`, `Links` (and `Text`, `Version` through `requirement-phrasing`) of affected rows, after confirmation | schema columns | `requirement-linter`, `traceability-matrix` |
| `requirements/conflicts.md`: `Status` and `Decision` of the CF entry | `conflict-detector` template | `conflict-detector` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else the defaults, and say so), `glossary.md`, `requirements.csv`, `conflicts.md`, `stakeholders.md` and every `decisions/RDR-*.md`. If an accepted RDR already covers this topic, the new one supersedes it: both get a `Supersedes` / `superseded by` line.

2. **Load the conflict.**
   - CF-ID given: read its entry (requirements, positions, type, recommended technique, decision-makers). If its Status is `resolved`, stop and point to the RDR in `Decision`.
   - R-IDs or a description given: run the `conflict-detector` skill on those rows so the conflict gets a CF-ID. If it is not installed, write the conflict into the RDR context and set `Conflict: unregistered`.
   - Type `relationship` or `structural`: do not run a session. Tell the user it is routed to escalation and to whom. Continue only when the user reports the escalation owner's decision; record it with technique `overruling` and the escalation owner as decision-maker.

3. **Frame the session.** Settle these with the user through `re-interview`, one question at a time, each with a recommended answer:
   1. The decision question, in one sentence ending with "?".
   2. Decision-makers: named people with the authority to decide. Default: the role in `process.change_authority` (product owner unless the schema says otherwise). Also who is consulted and who is informed.
   3. Constraints that bound every option: laws, policies, contracts, deadlines, budgets, each with its source.
   4. When the decision is needed.

   Without at least one named decision-maker the RDR can be drafted but never `accepted`.

4. **Collect facts and assumptions** (consider-all-facts). List every factor that matters to the decision with its source. Anything nobody can source is an assumption, with the person who will verify it.

5. **List the options.** At least the positions as each side stated them, plus every variant or compromise the participants raise, plus "defer" when waiting is a real choice. For each option: one line, and which requirements change and how. Option parameters (the compromise period, a variant's scope) come from the participants. If one is missing, the option carries `TBD` and a question; never fill it in.

6. **Agree the technique and aid.** Start from the conflict's recommended technique and confirm it with the decision-makers. Run it as described in `references/resolution-techniques.md`. These rules do not bend:
   - **Decision matrix:** criteria, weights and the scale are agreed and recorded (who, when) before any option is scored. If scores came first, or someone asks to change weights after seeing totals, the matrix is invalid: say so, and either re-agree weights and rescore, or drop the matrix and use another aid. Show the arithmetic in the RDR.
   - **Voting:** voters and the rule (majority, unanimity) are fixed before anyone votes.
   - **Overruling:** name who overrules, by what authority, and why. Record dissent.
   - **Compromise and variants:** each side states what it gives up or which scope its variant covers.

7. **Record the outcome.** Write down the outcome as the participants state it: chosen option, reasons tied to the decision drivers, each decision-maker's confirmation and date, and dissent. If no decision was reached, stop here with Status `proposed` and the open points.

8. **Draft the RDR.** Allocate the next number with `re-ids` (kind `decision`, or `re-lint ids next --kind decision`). Name the file `RDR-nnn-<slug>.md`, slug = the decision topic in kebab-case. Fill every heading of `assets/rdr.md` in order; `references/rdr-format.md` says what goes under each. Status `accepted` only when every named decision-maker has confirmed; otherwise `proposed`. Show the whole record.

9. **Draft the requirement updates.** Add one row per affected requirement to the RDR's "Requirement Updates" table, with `Applied: no`:

   | Change | Before → after |
   | --- | --- |
   | `keep` (chosen as written) | `Links` + `RDR-nnn CF-nn`; `Status` → `agreed` only if the RDR is accepted, else unchanged |
   | `rewrite` (compromise value, narrowed scope) | new `Text` through `requirement-phrasing`, same ID, `Version` + 1 if the column exists; an `agreed` row returns to `proposed` unless the RDR is accepted |
   | `new` (a variant needs its own row) | new ID from `re-ids`, usually the `WHERE` pattern, `Source` = `RDR-nnn`, `Status` `draft` (or `agreed` if the RDR is accepted) |
   | `reject` / `withdraw` (losing option) | `Status` → `rejected` if the row was never agreed, `withdrawn` if it was; `Links` + `RDR-nnn CF-nn`; the row stays, `Rationale` unchanged |

10. **Confirm, then apply.** Ask the user which updates to apply (all, some, none). Apply only those to `requirements.csv`, and set `Applied: yes (YYYY-MM-DD)` in the RDR. Set the CF entry in `conflicts.md` to `Status: resolved`, `Decision: RDR-nnn` once the RDR is accepted. Do not apply anything to a requirement that is in a baseline, or when `process.change_authority` is a change control board: suggest `/change-impact` with the RDR as input instead.

11. **Lint the changed rows.** Run the `requirement-linter` skill on the changed IDs (or `re-lint check --only-ids <IDs>`). Fix errors through `requirement-phrasing` and show the result.

## Quality checks

- [ ] The RDR has every heading of `assets/rdr.md` in order, at least two considered options, and Status `proposed` or `accepted`.
- [ ] Decision-makers are named people; the agent appears nowhere as a decision-maker, voter or scorer.
- [ ] An accepted RDR records each decision-maker's confirmation with a date; dissent is recorded or `none`.
- [ ] If a decision matrix was used, the weights were recorded before the scores, and the totals are arithmetically correct.
- [ ] No number in the RDR or in a requirement lacks a source; unknown values are `TBD` with a question.
- [ ] Every affected R-ID has a row in "Requirement Updates"; nothing was applied without confirmation; no row was deleted.
- [ ] `requirement-linter` reports no errors on the changed rows.

## Hand-offs

- **Next:** `testability-check` for rewritten or new requirements; suggest the user runs `/requirements-review` on the changed rows. `traceability-matrix` picks up the RDR from `requirements/decisions/` as trace evidence.
- **Feeds back to:** `conflict-detector` when the session surfaces another conflict; suggest `/change-impact` when baselined requirements are affected; `glossary` when the decision defines or narrows a term.

## Non-interactive mode

Do not facilitate and do not decide. Use only facts, scores and decisions stated in the input. Write the RDR with everything known; if no named decision-maker's decision is in the input, Status stays `proposed` and "Decision Outcome" reads `Pending: decision by <role>`. List the requirement updates with `Applied: no`, leave `requirements.csv` and `conflicts.md` unchanged unless the input explicitly confirms the updates, and end with the questions for the decision-makers.

## Pitfalls

- Treating a loud participant's preference as agreement. Agreement is each decision-maker saying yes.
- Splitting the difference on a principle (privacy, safety). Value conflicts take variants or a decision by authority, not a halfway number.
- Recording the decision but not the losing requirement: it then gets implemented anyway. Always reject or withdraw it in the same RDR.
- Writing the reasons as "best option". Reasons cite drivers: "meets the liability constraint (S-01) at the lowest effort".

## References

- `references/resolution-techniques.md`: how to run each technique and analysis aid, a worked decision matrix, and how to spot an invalid one. Read it at step 6.
- `references/rdr-format.md`: what goes under each RDR heading, status lifecycle, superseding, and how RDRs relate to ADRs. Read it at step 8.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: CF-01 (points expiry) resolved into RDR-001 with a decision matrix and an overruling.
