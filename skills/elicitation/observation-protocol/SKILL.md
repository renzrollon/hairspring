---
name: observation-protocol
description: >-
  Plans a field observation or apprenticing session and writes up what was seen: focus questions,
  method choice, site and timing, a consent note, a capture template (task, trigger, steps,
  workaround, dissatisfier, frequency observed vs reported), a same-day debrief script, and a
  synthesis that lands each workaround as a dissatisfier candidate in requirements/candidates.csv.
  Writes requirements/elicitation/observation-<slug>.md. Use when people cannot easily describe
  their work, interviews keep missing steps, or you suspect workarounds ("shadow the cashiers at
  peak", "watch how support handles a dispute", "apprentice with ops for a day"), or when field
  notes must be written up. Not for asking stakeholders directly (use interview-guide), mining
  logs, tickets or code (artifact-mining), or checking findings at scale (questionnaire-builder).
license: MIT
disable-model-invocation: true
argument-hint: "[work to observe, site, time window, roles] or [field notes]"
metadata:
  stage: elicitation
  invocation: user
  priority: P2
  ireb-anchor: "CPRE FL Handbook 1.2 §4.2.2"
  inputs-from: "stakeholder-map, system-context, interview-guide, glossary"
  outputs-to: "requirement-classifier, requirement-phrasing, prioritization, process-flow, glossary"
  work-product: "requirements/elicitation/observation-<slug>.md, requirements/candidates.csv"
  version: "0.1.0"
---

# Observation protocol

Observation finds what people no longer notice: the paper list under the till, the third scan attempt, the supervisor key used every hour. This skill plans a session around a few focus questions, gets consent first, captures each episode with its trigger, workaround and frequency, confirms them in a same-day debrief, and lands every workaround as a dissatisfier candidate. Plan, capture and debrief live in `requirements/elicitation/observation-<slug>.md`.

## When not to use

- The people can tell you what you need and the work has no hidden steps: `/interview-guide`.
- The evidence is in tickets, logs, code or documents: `artifact-mining`.
- You need to know how widespread an observed problem is: `/questionnaire-builder` after this skill.
- You are asked to watch people without their knowledge: do not plan it. Observation here is always announced and consented.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| The work to observe, site, time window, roles, observer | yes (asked if missing) | the user |
| `requirements/stakeholders.md` (process owner, site manager, data protection owner) | no | `stakeholder-map` |
| `requirements/context.md`, `glossary.md`, interview files, candidates for the area | no | `system-context`, `glossary`, `interview-guide`, `artifact-mining` |
| Field notes and debrief notes (phase B) | for phase B | the observer |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/elicitation/observation-<slug>.md` | `assets/observation-plan.md` | the observer, `requirement-classifier`, `process-flow` |
| `requirements/candidates.csv` (appended rows, `Technique=observation`) | `assets/candidates.csv` | `requirement-classifier`, `requirement-phrasing`, `prioritization` |

## Procedure

### Phase A: plan

1. **Read the workspace.** Load `requirements/schema.json` (else defaults), `stakeholders.md`, `context.md`, `glossary.md`, and interviews and candidates on the area, so the session looks for what interviews could not show.
2. **Frame the session.** Write at most three focus questions ("What happens at the till when a member QR scan fails?"). If the site, time window, roles, observer or process owner is missing, ask in one batch through the `re-interview` primitive. Choose the time window when the problem occurs and write down what it will not show. Refer to observed people by role ("Cashier A"); never invent names.
3. **Choose the method** with `references/observation-guide.md`: field observation, apprenticing or mixed, with a one-line reason.
4. **Write the consent note** from the asset: purpose, what is recorded (notes only by default), what is never recorded (customers, screens with personal data), the right to stop at any time, how long notes are kept, and a contact. Name who must agree before the session: the site manager and each observed person; the data protection owner too if photos, audio or video are wanted. If the request asks for hidden or covert observation, or for recording customers or their screens, leave it out, say why, and name the data protection owner.
5. **Prepare capture and debrief.** Keep the capture template as in the asset (one row per episode `O1`, `O2`, ...: time, task, trigger, steps, workaround, dissatisfier, frequency observed, frequency reported, quote, follow-up). Write the debrief script from the guide's question table, adapted to the focus questions.
6. **Show the plan.** Write the file with capture and synthesis empty, `Status=planned`, and show it to the user.

### Phase B: write up

7. **Fill the capture table** from the field notes: one row per kind of episode (repeats raise the observed count), what was seen and said, nothing inferred. Observed frequency is a count with the observation period ("3 in 4 h"); reported frequency comes only from the debrief and says "reported". Mask any customer data in the notes as `[member]`, `[phone]`, `[card]`.
8. **Record the debrief.** Per episode, the person's explanation, the reported frequency, the need in their words, and whether the day was typical. Note any observer effect they mention.
9. **Synthesize and land the candidates.** For each workaround or dissatisfier, name the need it compensates for and append one row per need to `requirements/candidates.csv` (create it from `assets/candidates.csv` if missing): IDs from `re-ids` (`--kind candidate`), domain-word *Statement*, `Type` guess, `Technique=observation`, `Source=observation-<slug> <YYYY-MM-DD>`, `Location=requirements/elicitation/observation-<slug>.md#O<n>`, `Quote` from the capture row, `Kano=dissatisfier` (or `TBD` if the debrief shows nobody minds), `Disposition=confirm` with the process owner as `Owner`, and the observed and reported frequency in `Reason`. Several episodes pointing at one need make one candidate citing all of them. Show the rows, then write. If `artifact-mining` is installed, run `python3 <artifact-mining skill-dir>/scripts/check_candidates.py requirements/candidates.csv --root .` from the repo root and fix every error; otherwise check by hand that each quote is in its capture row.
10. **Close.** Fill the synthesis table, set `Status=written up`, and list open questions with owners and the limits of the sample (one site, one slot).

## Quality checks

- [ ] Focus questions are at most three; the time window says why it was chosen and what it misses.
- [ ] The consent note covers purpose, recording, the right to stop, retention and contact; no covert observation and no recording of customers.
- [ ] The capture template has task, trigger, workaround, dissatisfier and frequency, with observed and reported kept apart.
- [ ] No customer or staff names, phone, card or ID numbers in the file or the candidates.
- [ ] Every workaround leads to a candidate (or a reason why not); every candidate cites an `#O<n>` location whose quote is in the capture table, has a Kano tag and an owner.
- [ ] Nothing in the capture table goes beyond the field and debrief notes.

## Hand-offs

- **Next:** `requirement-classifier` on the new CAN-IDs, then suggest `/prioritization`: dissatisfiers usually rank as must-haves once confirmed.
- **Next:** `process-flow` to draw the observed (as-is) flow from the steps column.
- **Feeds back to:** `glossary` with terms heard on site; `source-inventory` to register the session; suggest `/questionnaire-builder` to check how widespread a workaround is.

## Non-interactive mode

Phase A: use roles and `TBD` for missing frame facts, list them as open questions, and keep the consent note complete; the session must not run until site manager and staff agreed. Phase B: write up and land directly, then list the CAN-IDs written and the open questions.

## Pitfalls

- Judging people instead of describing the work: the workaround is evidence of a system gap, not of a careless cashier.
- Taking one session as the truth: say "seen once at one store" and recommend a second slot.
- Asking for solutions in the debrief: ask what would be different, and capture the need.

## References

- `references/observation-guide.md`: method choice, timing, signals of workarounds, capture rules, the debrief question table, and how a workaround becomes a candidate. Read it at steps 3, 5 and 9.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: a half-day evening-peak shadowing of cashiers at one store on the loyalty-points sample: plan, capture, debrief, and the five candidates it produced.
