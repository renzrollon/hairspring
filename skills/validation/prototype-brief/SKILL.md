---
name: prototype-brief
description: >-
  Writes a brief for a prototype that validates named requirements before they are built:
  hypotheses tied to R-IDs, kind (throwaway or evolutionary) and fidelity (paper, mock-up,
  native), participants, tasks, measures with thresholds agreed in advance, stop criteria, and how
  results flow back as validated, changed or dropped requirements. Writes
  requirements/elicitation/prototype-{slug}.md; run it again after the sessions to record results
  and propose requirement updates, applied only after confirmation. Started explicitly by the
  user: /prototype-brief. Use when stakeholders are unsure a requirement is right, when a UI flow,
  wording or risky integration needs user feedback before it is built, or for "should we prototype
  this?", "validate these requirements with users", "plan a usability test". Not for building or
  designing the prototype, for reviewing written requirements (requirements-review), for
  generating new ideas (elicitation-workshop), or for verifying built software
  (testability-check).
license: MIT
disable-model-invocation: true
argument-hint: "[R-IDs or topic to validate; or 'record <slug>' after the sessions]"
metadata:
  stage: validation
  invocation: user
  priority: P2
  ireb-anchor: "CPRE FL Handbook 1.2 §3.7, §4.4"
  inputs-from: "requirement-phrasing, user-story-refiner, requirements-review, testability-check, stakeholder-map"
  outputs-to: "requirement-phrasing, requirements-review, testability-check, conflict-detector"
  work-product: "requirements/elicitation/prototype-<slug>.md"
  version: "0.1.0"
---

# Prototype brief

Some requirements can only be validated by people using something: a redemption flow, a message, a screen at a busy till. A prototype answers that cheaply, but only if everyone agrees beforehand what it is meant to show, what result counts as yes or no, and when to stop. This skill writes that brief for named requirements, and after the sessions records the evidence and turns it into requirement updates: validated, changed or dropped. It plans what to learn; it does not design or build the prototype.

## When not to use

- You want the written requirements checked for defects: suggest `/requirements-review`.
- You need pass/fail criteria and test ideas for software that will be built: `testability-check`.
- You want new ideas rather than validation of named requirements: suggest `/elicitation-workshop`.
- Nothing will be decided differently whatever the result: do not prototype; agree the requirement directly.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| The R-IDs (or topic) to validate | yes | `requirement-phrasing`, `user-story-refiner` |
| `requirements/requirements.csv` | yes | `requirement-phrasing` |
| `requirements/stakeholders.md` | no | `stakeholder-map` |
| Review findings or `Verifiable = no` rows that only users can settle | no | `requirements-review`, `testability-check` |
| Session notes and results (record mode) | record mode only | the facilitator |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/elicitation/prototype-<slug>.md` | `assets/prototype-brief.md` | the team, `requirement-phrasing`, `requirements-review` |
| `requirements/requirements.csv`: `Links`, `Status` (and `Text` through `requirement-phrasing`), record mode, after confirmation | schema columns | `requirement-linter`, `traceability-matrix` |

## Procedure

The skill has two modes. **Plan** (default) writes the brief. **Record** runs when the brief exists and the user brings session results ("/prototype-brief record voucher-redemption").

### Plan

1. **Read the workspace.** Load `requirements/schema.json` (else the defaults, and say so), `glossary.md`, `requirements.csv`, `stakeholders.md`, and any brief already in `requirements/elicitation/prototype-*.md` on the same topic (extend it rather than start a second one).
2. **Pin the requirements.** List the R-IDs with their text. Every hypothesis must name at least one existing R-ID. If the user gives a topic, propose the matching rows and confirm. If a requirement is not written yet, draft it with `requirement-phrasing` (Status `draft`) first. One brief covers one round with a handful of requirements; suggest a second brief rather than a long one.
3. **Name the decision.** Ask with `re-interview`: what will be decided with the results, who decides (a named person), and by when. If no decision depends on the outcome, say so and stop.
4. **Write hypotheses.** One per uncertain requirement or assumption: "We believe {belief} (R-nnn)", plus the observable signal for **validated**, **changed** and **dropped**. Write `n/a` when an outcome cannot happen. Thresholds ("at least TBD of TBD participants complete T1 without help") come from the decision-maker before the first session; until then they are `TBD` with a question. Never invent one.
5. **Choose kind and fidelity** with the tables in `references/prototype-options.md`. Kind: `throwaway` (built to learn, then discarded) or `evolutionary` (becomes product code, so it is built to production standards from the first line). Fidelity: `paper`, `mock-up` or `native`; take the lowest that can produce every signal. A hypothesis the chosen fidelity cannot test moves out of this brief, with where it goes instead (a native spike, a demonstration, another brief).
6. **Plan participants and tasks.** Participants represent the people in the requirements (members, cashiers, support agents); the number and recruiter come from the user, else `TBD`. Note consent and how notes are anonymised (participant codes, no names). Write at least one task per hypothesis, in the participant's words, without hints at the answer.
7. **Define measures and stop criteria.** For each hypothesis: what is captured (task success without help, help requests, misreadings, stated intent, quotes), how, the threshold and who agreed it. Stop criteria always include a time box from the user, when to stop early, and when to stop and escalate (for example the throwaway prototype is being wired to production systems).
8. **Show, then write.** Fill `assets/prototype-brief.md`, Status `planned`, and save it as `requirements/elicitation/prototype-<slug>.md` (slug: topic in kebab-case). Results, flow-back and candidates read `Pending: filled after the sessions.` Change no requirement.

### Record

9. **Load the brief and the results.** Status `running` while sessions continue, `done` when finished, `stopped` if a stop criterion fired.
10. **Score each hypothesis** against the thresholds written in the brief before the sessions, never against new ones. Evidence: counts, and quotes attributed to participant codes. Outcome: `validated`, `changed`, `dropped` or `inconclusive` (threshold never agreed, or evidence mixed). Inconclusive is a valid result; state what would settle it.
11. **Propose the flow back.** One row per requirement in "Flow back to requirements", `Applied: no`:

    | Outcome | Proposed change |
    | --- | --- |
    | validated | `Links` + the brief path; Status unchanged (a named person may now agree it) |
    | changed | new `Text` through `requirement-phrasing`, same ID, `Version` + 1 if present; an `agreed` row returns to `proposed` |
    | dropped | `Status` → `rejected` (never agreed) or `withdrawn` (was agreed); `Links` + the brief path; the row stays |
    | inconclusive | no change; the next step in Notes |

    Things participants needed that no requirement covers go to "New candidate requirements" with their evidence.
12. **Confirm, then apply.** Ask the decision-maker (through the user) which changes to apply. Apply only those, fill `Confirmed by` with name and date and set `Applied: yes`. New candidates become rows through `requirement-phrasing` (Status `draft`, Source = the brief path and session date) only when confirmed. Then run the `requirement-linter` skill on the changed IDs.

## Quality checks

- [ ] Every hypothesis cites an existing R-ID and has a signal for validated, changed and dropped (or `n/a`).
- [ ] Kind and fidelity are set with a reason; hypotheses the fidelity cannot test are moved out and say where to.
- [ ] Participant numbers, thresholds and the time box come from the user or are `TBD` with a question; none is invented.
- [ ] Stop criteria include a time box, an early stop and an escalation trigger.
- [ ] Results are scored only against thresholds written before the sessions; participants appear only as codes.
- [ ] No requirement changed before confirmation; every applied change names who confirmed it and when.

## Hand-offs

- **Next:** run the sessions, then `/prototype-brief record <slug>`. After the flow back: `testability-check` on changed requirements; suggest `/requirements-review` on the changed rows.
- **Feeds back to:** `requirement-phrasing` for changed and new rows; `conflict-detector` when results split stakeholders (one wants to keep a dropped requirement); `clarifying-questions` for the open questions.

## Non-interactive mode

Plan mode: write the brief with every unknown as `TBD` and its question; Status `planned`. Record mode: write Results and the proposed flow back with `Applied: no`, change no requirement, and end with what needs confirmation and by whom.

## References

- `references/prototype-options.md`: throwaway vs evolutionary, the three fidelities, measures, and stop-criteria patterns. Read it at steps 5 to 7.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: a mock-up of the voucher redemption flow, planned and recorded.
