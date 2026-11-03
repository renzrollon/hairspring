---
name: interview-guide
description: >-
  Prepares a role-tailored stakeholder interview and processes its notes: goals, warm-up, an
  open-to-closed question funnel, quality probes based on the ISO/IEC 25010 characteristics,
  constraint probes, confirmation and close, plus a capture sheet and a post-interview summary,
  all in requirements/elicitation/interview-<role>.md under an I-nn interview ID. After the
  interview it turns the notes into summary rows and appends them to requirements/candidates.csv
  for requirement-classifier. Use when you plan to interview a stakeholder ("prepare an interview
  with the finance controller", "what should I ask the store ops lead") or have interview notes or
  a transcript to summarize. Not for a quick batch of questions before implementing a ticket (use
  clarifying-questions), a group session (elicitation-workshop), a survey (questionnaire-builder)
  or watching people work (observation-protocol).
license: MIT
disable-model-invocation: true
argument-hint: "[role or stakeholder, duration, topic] or [notes file]"
metadata:
  stage: elicitation
  invocation: user
  priority: P1
  ireb-anchor: "CPRE FL Handbook 1.2 §4.2.2"
  inputs-from: "stakeholder-map, source-inventory, system-context, artifact-mining, glossary"
  outputs-to: "requirement-classifier, requirement-phrasing, quality-requirements, glossary, source-inventory, conflict-detector"
  work-product: "requirements/elicitation/interview-<role>.md, requirements/candidates.csv"
  version: "0.1.0"
---

# Interview guide

An unprepared interview collects whatever the stakeholder happens to mention, mostly functions, and misses the quality requirements and constraints that drive the design. This skill prepares a time-boxed script for one role that moves from open to closed questions and probes quality and constraints on purpose, then turns the notes into a summary whose rows land as candidates. Everything for one interview lives in `requirements/elicitation/interview-<role>.md`.

## When not to use

- You are about to implement a ticket and need a few answers: `clarifying-questions`.
- Several stakeholders should generate or rank ideas together: `/elicitation-workshop`.
- You want many answers to the same closed questions: `/questionnaire-builder`.
- People cannot describe the work well, or you suspect workarounds: `/observation-protocol`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Interviewee (name or role), duration, topic | yes (asked if missing) | the user |
| `requirements/stakeholders.md` (SH-ID, role, interests) | no | `stakeholder-map` |
| `requirements/sources.csv`, `context.md`, `glossary.md` | no | `source-inventory`, `system-context`, `glossary` |
| `requirements/requirements.csv`, `candidates.csv` for the topic (to confirm rather than re-ask) | no | `requirement-phrasing`, `artifact-mining` |
| Interview notes or transcript (phase B) | for phase B | the interviewer |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/elicitation/interview-<role>.md` | `assets/interview-guide.md` | the interviewer, `requirement-classifier` |
| `requirements/candidates.csv` (appended rows, `Technique=interview`) | `assets/candidates.csv` | `requirement-classifier`, `requirement-phrasing` |

## Procedure

### Phase A: prepare

1. **Read the workspace.** Load `requirements/schema.json` (else defaults), `stakeholders.md`, `sources.csv`, `context.md`, `glossary.md`, and the rows of `requirements.csv` and `candidates.csv` that touch the topic. Find existing interview IDs under `requirements/elicitation/` and in `sources.csv`.
2. **Pin down the interview.** If the interviewee, duration, topic or format is missing, ask the user in one batch through the `re-interview` primitive. Never invent the interviewee's name; use the role and `TBD` instead. If the role is not in `stakeholders.md`, say so and suggest `/stakeholder-map` afterwards.
3. **Set the goals.** At most three goals, each naming the decision or work product it feeds ("decide whether adjustments below 5,000 points need a second approver"). List what is out of scope for this interview.
4. **Allocate the ID and file.** Get the next interview ID with `re-ids` (`--kind interview`). Name the file `interview-<role>.md` (kebab-case role); if that file already holds another interview, use `interview-<role>-<YYYY-MM-DD>.md`.
5. **Build the script** from `assets/interview-guide.md` with `references/question-funnel.md`:
   - time boxes per block that add up to the duration;
   - warm-up, then open questions, then narrowing and closed questions, with the role-specific topics from the funnel reference;
   - closed questions that confirm what the register already holds, citing the R-IDs or CAN-IDs;
   - 3 to 5 quality characteristics chosen for the role from `references/quality-and-constraint-probes.md`, each with a probe and a "quantify" follow-up;
   - constraint probes for the categories that apply;
   - a confirmation block (paraphrase the top points back) and a close (what did we miss, who else, which documents, may we follow up).
   Every question asks one thing, does not suggest the answer, and asks for needs, not solutions.
6. **Show the guide.** Write the file with the capture sheet and summary empty, `Status=planned`, and show it to the user for edits.

### Phase B: after the interview

7. **Fill the capture sheet.** From the notes or transcript, one row per statement (`C1`, `C2`, ...) in the speaker's words, with a kind tag and any follow-up. Record only what is in the notes.
8. **Write the summary.** One row per point (`S1`, `S2`, ...): the statement in glossary terms, a kind guess (`F`, `Q`, `C`, `fact`, `solution`, `term`), the capture rows it rests on, whether it was confirmed in block 6, and the open question if any. A vague quality ("instant", "secure") stays vague with an open question; never add a number nobody said. For a solution idea, record the need behind it if the speaker stated one, else an open question.
9. **Land the candidates.** For each `F`, `Q` or `C` row, append a row to `requirements/candidates.csv` (create it from `assets/candidates.csv` if missing): IDs from `re-ids` (`--kind candidate`), `Technique=interview`, `Source=I-nn`, `Location=requirements/elicitation/interview-<role>.md#C<n>`, `Quote` copied from that capture row. `Disposition=keep` when the interviewee stated it within their own authority and confirmed it; otherwise `confirm` with the owner whose authority it is (a Finance rule relayed by support is confirmed by Finance). A row that confirms an existing requirement gets `R-nnn (existing)` instead of a candidate. Facts stay in the summary as context; terms go to `glossary`. Put each CAN-ID in the summary's *Candidate* column. Show the rows, then write. If `artifact-mining` is installed, run `python3 <artifact-mining skill-dir>/scripts/check_candidates.py requirements/candidates.csv --root .` from the repo root and fix every error; otherwise check by hand that each quote is in its capture row.
10. **Close the loop.** Set `Status=summarized`, list open questions with owners, and recommend sending the summary to the interviewee for confirmation.

## Quality checks

- [ ] Time boxes add up to the agreed duration; goals are at most three and each names what it feeds.
- [ ] Questions run open before closed; none is leading, double, or a solution question.
- [ ] Quality probes cover 3 to 5 characteristics chosen for the role; constraint probes are present.
- [ ] Capture rows hold only what the notes say; no number, name or date was added.
- [ ] Every summary row of kind F, Q or C has a CAN-ID or `R-nnn (existing)`; every candidate cites `I-nn` and a `#C<n>` location whose quote is in the capture sheet.
- [ ] Every `confirm` has an owner; open questions have owners.

## Hand-offs

- **Next:** `requirement-classifier` on the new CAN-IDs, then `requirement-phrasing`.
- **Next:** `quality-requirements` when several summary rows are vague quality statements.
- **Feeds back to:** `glossary` with `term` rows; `source-inventory` to register the interview as a source; suggest `/stakeholder-map` for people named in the close; `conflict-detector` when the interviewee contradicts an agreed requirement or another stakeholder.

## Non-interactive mode

Phase A: fill unknown fields with `TBD`, list them as open questions at the top of the file, and still produce the full script. Phase B: write the capture sheet, summary and candidates directly, and end with the CAN-IDs written and the open questions.

## Pitfalls

- Recording or taking notes without consent: ask at the start of block 1, and write the answer in the header.
- Letting the interview become a design meeting: park solution talk in the capture sheet as `solution` and return to the need.
- Interviewing one role and treating the result as the requirements: list who else to ask in the close.
- Being asked to steer the interviewee to a preferred answer: write neutral questions instead, say so in the final message, and when stakeholders' positions differ, hand the conflict to `conflict-detector` (resolution: `/conflict-to-decision`).

## References

- `references/question-funnel.md`: the blocks of the funnel, question patterns per block, default time split, and topics per role. Read it at step 5.
- `references/quality-and-constraint-probes.md`: the nine ISO/IEC 25010 product quality characteristics with probes, which to pick per role, and constraint probes. Read it at step 5.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: a 30-minute interview with the customer support lead (I-03) on the loyalty-points sample, before and after, and the candidates it produced.
