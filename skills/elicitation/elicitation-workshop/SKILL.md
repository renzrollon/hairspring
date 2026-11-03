---
name: elicitation-workshop
description: >-
  Designs an elicitation workshop and captures its results: objective, participants with a role
  gap check, a time-boxed agenda, technique selection from a table (brainstorming, brainstorming
  paradox, 6-3-5 brainwriting, six thinking hats, morphological matrix, story mapping),
  facilitation notes, a parking lot, and a capture template that lands ideas as classified
  candidates with Kano tags in requirements/candidates.csv. Writes
  requirements/elicitation/workshop-<slug>.md. Use when several stakeholders should generate,
  combine or structure ideas together ("plan a workshop to find delighters", "run a story mapping
  session", "brainstorm what members want") or when a workshop board export must be captured. Not
  for one-to-one interviews (use interview-guide), validating findings at scale
  (questionnaire-builder), choosing between technical designs (conflict-to-decision or an ADR), or
  ranking an existing backlog (prioritization).
license: MIT
disable-model-invocation: true
argument-hint: "[objective, duration, participants, remote or on-site] or [board export]"
metadata:
  stage: elicitation
  invocation: user
  priority: P2
  ireb-anchor: "CPRE FL Handbook 1.2 §4.2.2, §4.2.3"
  inputs-from: "stakeholder-map, system-context, glossary, interview-guide, artifact-mining"
  outputs-to: "requirement-classifier, requirement-phrasing, prioritization, conflict-detector, glossary"
  work-product: "requirements/elicitation/workshop-<slug>.md, requirements/candidates.csv"
  version: "0.1.0"
---

# Elicitation workshop

A workshop without a clear objective and a chosen technique becomes a meeting where the loudest idea wins. This skill fixes the objective, checks who is missing, picks the technique that fits the goal and the group, writes a time-boxed agenda with facilitation notes, and afterwards lands every idea from the board as a candidate with a Kano tag. Plan, capture and parking lot live in `requirements/elicitation/workshop-<slug>.md`.

## When not to use

- One stakeholder at a time, or sensitive topics: `/interview-guide`.
- Many people should confirm or quantify findings: `/questionnaire-builder`.
- The question is which technical solution to build (queue product, database, framework): that is a design decision. Use `/conflict-to-decision` or an ADR; this skill can at most elicit the quality requirements behind the choice.
- The items exist and need ranking: `/prioritization`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Objective, duration, format (remote or on-site), participants | yes (asked if missing) | the user |
| `requirements/stakeholders.md` | no | `stakeholder-map` |
| `requirements/context.md`, `glossary.md`, `candidates.csv`, `requirements.csv` for the topic | no | `system-context`, `glossary`, `artifact-mining`, `requirement-phrasing` |
| Board export, photos transcribed, or notes (phase B) | for phase B | the facilitator |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/elicitation/workshop-<slug>.md` | `assets/workshop-plan.md` | the facilitator, `requirement-classifier` |
| `requirements/candidates.csv` (appended rows, `Technique=workshop`) | `assets/candidates.csv` | `requirement-classifier`, `requirement-phrasing`, `prioritization` |

## Procedure

### Phase A: design

1. **Read the workspace.** Load `requirements/schema.json` (else defaults), `stakeholders.md`, `context.md`, `glossary.md`, and the candidates and requirements on the topic, so the workshop does not re-collect what is known.
2. **Check that it is elicitation.** Write the objective as one sentence: "By the end we have <ideas, a map, a set of candidates> about <topic> for <decision or owner>." If the request is to choose between technical solutions, say it is a design decision, offer to reframe the session around the quality requirements and constraints behind the choice, and recommend `/conflict-to-decision` or an ADR for the choice itself. If the request is to rank existing items, recommend `/prioritization` and stop.
3. **Pin down the frame.** If duration, format, participants or the decision owner are missing, ask in one batch through the `re-interview` primitive. Never invent participant names; use roles and `TBD`.
4. **Check the participants.** List each participant with role, SH-ID and why they are needed. Name the decision owner. Flag missing roles that the topic needs (users or their voice, operations or support, data protection or security when personal data or fraud is in scope), using `stakeholders.md`.
5. **Select the technique.** Use the selection table and rules in `references/techniques.md`: one diverge technique for the main goal, always a converge step (cluster, dot vote, Kano tag). In the plan's *Technique selection* table, list at least two techniques you considered, why each fits or does not fit this goal and group, and mark the chosen ones.
6. **Build the agenda.** Time-boxed blocks that add up to the duration: opening (objective, rules, how Kano tagging works), diverge, break if longer than an hour, cluster, dot vote, Kano tagging of the top ideas, parking lot review, close (next steps and owners). For each block, write facilitation notes: the exact instruction to read out, materials or board, and what to do if the group stalls or one voice dominates.
7. **Write and show the plan.** Fill `assets/workshop-plan.md` with the capture table and parking lot empty, `Status=planned`, and show it to the user for edits.

### Phase B: capture

8. **Capture the ideas.** From the board export, transcribed photos or notes, one row per idea (`W1`, `W2`, ...) in the participants' words, with technique and round, cluster, votes and the Kano tag agreed in the room (`TBD` if none was agreed). Merge duplicates into one row and note which notes were merged. Ideas outside the objective, and ideas that contradict an existing requirement, go to the parking lot with an owner, not to candidates. Count discarded noise in one line; do not list it.
9. **Land the candidates.** For each idea row, append a row to `requirements/candidates.csv` (create it from `assets/candidates.csv` if missing): IDs from `re-ids` (`--kind candidate`), a *Statement* of the need in domain words (a tool or product named on a note becomes the need behind it), `Type` guess, `Technique=workshop`, `Source=workshop-<slug> <YYYY-MM-DD>`, `Location=requirements/elicitation/workshop-<slug>.md#W<n>`, `Quote` from the capture row, `Kano` from the capture row. Ideas are proposals: `Disposition=confirm` with the decision owner as `Owner`; `drop` when an existing requirement already covers it (its ID in `Requirement`). Put each CAN-ID in the capture table. Show the rows, then write. If `artifact-mining` is installed, run its `check_candidates.py` on the file.
10. **Close.** Set `Status=captured`; list the top-voted ideas, the parking-lot owners, and the next steps.

## Quality checks

- [ ] The objective names a work product and a decision owner; the session is elicitation, not a technical design choice.
- [ ] Agenda blocks add up to the duration; every block has facilitation notes; a converge step is present.
- [ ] The selection table shows at least two options considered and a one-line reason for each choice.
- [ ] Missing roles are flagged, not ignored.
- [ ] Every captured idea has a Kano tag or `TBD`, votes, and either a CAN-ID or a parking-lot entry; nothing was added that is not on the board.
- [ ] Candidates cite `workshop-<slug>` and a `#W<n>` location whose quote is in the capture table; every `confirm` has an owner.

## Hand-offs

- **Next:** `requirement-classifier` on the new CAN-IDs (it refines the Kano tags and F/Q/C), then suggest `/prioritization` for the top ideas and `requirement-phrasing` for the ones the owner accepts.
- **Feeds back to:** `conflict-detector` with parking-lot ideas that contradict existing requirements; `glossary` with new terms from the board; `system-context` with ideas that move the system boundary; `source-inventory` to register the workshop as a source.

## Non-interactive mode

Phase A: use `TBD` for missing frame facts, list them as open questions at the top of the plan, and still produce the full agenda for the stated duration. Phase B: capture and land directly, then list the CAN-IDs written, the parking lot and the open questions.

## References

- `references/techniques.md`: selection table, decision rules, how to run each technique, converge steps, Kano tagging questions, remote tips. Read it at steps 5 and 6.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: a 90-minute remote workshop on redemption delighters for the loyalty-points sample: the plan, the captured board and the candidates it produced.
