---
name: quality-requirements
description: >-
  Walks the ISO/IEC 25010:2023 product quality characteristics, tailored to the system type, and
  turns quality concerns into measurable quality requirements (metric, target, condition,
  measurement method). Flags everything unquantified as TBD with an open question, never a
  guessed number, and tags architecture drivers. Leaves requirements/quality-requirements.md and
  Type Q rows in requirements/requirements.csv. Started explicitly with /quality-requirements. Use
  when someone asks "what are the NFRs", "non-functional requirements", "how fast, available or
  secure must it be", at project kick-off, before a design or architecture review, or when tickets
  say fast, scalable, secure, reliable, auditable or user-friendly. Not for one sentence that
  already has its target (use requirement-phrasing), mandates such as regulations, platforms or
  deadlines (constraints-register), checking that existing ones are verifiable
  (testability-check), or functional behavior questions (clarifying-questions).
license: MIT
disable-model-invocation: true
argument-hint: "[system or part, notes file] [planguage]"
metadata:
  stage: specification
  invocation: user
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §1.2, §4.2"
  inputs-from: "system-context, stakeholder-map, interview-guide, clarifying-questions, artifact-mining, requirement-classifier, glossary"
  outputs-to: "requirement-linter, testability-check, constraints-register, conflict-detector, requirements-review, spec-assembler, to-openspec"
  work-product: "requirements/quality-requirements.md"
  version: "0.1.0"
---

# Quality requirements

Quality requirements are the class elicitation under-collects and the one that drives the architecture: nobody writes "must survive the year-end peak" into a ticket until the peak arrives. This skill walks the nine ISO/IEC 25010:2023 product quality characteristics as a checklist, picks the ones that matter for the system type, and turns each concern into a requirement with a metric, a target, a condition and a measurement method. Every missing value stays `TBD` with an open question and an owner. The result is `requirements/quality-requirements.md` plus one Type Q row per requirement in `requirements.csv`.

## When not to use

- One statement whose target a stakeholder already gave ("balance visible within {n} seconds"): `requirement-phrasing`.
- Mandates from outside the team (regulation, platform standard, interface spec, deadline): `constraints-register`.
- Questions about functional behavior before implementing: `clarifying-questions`.
- Checking whether existing quality requirements are verifiable: `testability-check`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Quality concerns: notes, tickets, interview summaries, or a conversation | yes | the user, `interview-guide`, `clarifying-questions`, `artifact-mining` |
| `requirements/context.md` (system boundary, external systems) | no | `system-context` |
| `requirements/stakeholders.md` (who owns which concern) | no | `stakeholder-map` |
| `requirements/requirements.csv` (existing Q rows, functional conditions) | no | every emitting skill |
| `requirements/schema.json`, `requirements/glossary.md` | no (defaults apply) | `re-setup`, `glossary` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/quality-requirements.md` | `assets/quality-requirements.md` | `spec-assembler`, `requirements-review`, `to-openspec`, the architect |
| `requirements/requirements.csv` (Type Q rows) | `assets/requirements.csv` | `requirement-linter`, `testability-check`, `conflict-detector` |

## Procedure

1. **Read the workspace.** Locate `requirements/` (or the `workspace` in `schema.json`); read `schema.json` (else the default columns `ID,Type,Text,Source,Priority,Status,Rationale`, and say so in the output header), `glossary.md`, `context.md` (the external systems become the interfaces you walk), `stakeholders.md` (who to ask), `requirements.csv` (existing Q rows to update, not duplicate) and `quality-requirements.md` if it exists (update it in place).
2. **Fix the scope and the system type.** Name the system or part under walkthrough. Pick one or more types from `references/system-types.md` (web API or service, mobile app, batch or data pipeline, embedded, internal tool); a service with an admin console is two parts. If unclear, ask one question with a recommended answer taken from `context.md`. Read the tailoring table: each characteristic is `core`, `check` or `rare` for that type.
3. **Collect the concerns.** List every quality statement already made, quoted, with its source: the input, interview notes, tickets, and requirements that contain weak words (fast, scalable, secure, reliable, user-friendly, auditable). `requirement-linter` weak-word findings are a good source.
4. **Walk the nine characteristics.** Cover all nine (functional suitability, performance efficiency, compatibility, interaction capability, reliability, security, maintainability, flexibility, safety), `core` ones first. For `core`, ask the screening questions in `references/system-types.md` and work every concern. For `check`, ask one screening question. For `rare`, record "not relevant" with the reason and who confirmed it. Fill all nine rows of the *Walkthrough* table every run. Follow `re-interview` in batch mode (at most 7 questions per batch, core characteristics first), addressed to the stakeholder who owns the concern. For target values, recommend a reference (a baseline measurement, a vendor or dependency limit, a contract, a policy), never a number you made up. In non-interactive mode, ask nothing: `TBD` plus an open question for every unknown.
5. **Write measurable quality requirements.** One requirement per concern and sub-characteristic (names only; see `references/metrics-catalogue.md` for metric and method ideas). Fill four fields:

   | Field | Holds | Unknown |
   | --- | --- | --- |
   | Metric | What is measured, its unit and statistic (95th percentile response time in ms; events accepted per minute) | Ask; pick from the catalogue and confirm |
   | Target | The value a named person or source gave | `TBD` + open question |
   | Condition | Load, data volume, environment, time window; baselines from sources ("last year's peak: 9,000 purchases per minute, SH-08") | `TBD` + open question |
   | Measurement method | How and when it is measured: load test, synthetic probe, fault injection, inspection, usability test, production monitoring | Propose one from the catalogue; the owner confirms |

   Phrase the `Text` as `[WHEN/WHILE <condition>,] the <system> shall <measurable property> <target>.`, or `IF <failure>, THEN the <system> shall ...` for fault tolerance and recoverability, with one target per requirement. A percentile or other statistic is part of the target: if nobody confirmed it, it is `TBD` too. A baseline is never a target: put it in *Condition*.
6. **Sort out what is not a quality requirement.** Record it in *Unquantified and reclassified concerns*:

   | The concern is really | Example | Do |
   | --- | --- | --- |
   | A function | "Auditable" meaning *record who adjusted points, when and why* | Hand to `requirement-phrasing` (Type F); keep only the quality part here |
   | A mandate | Interface spec, retention period, "stay out of PCI scope" | Run `constraints-register` if installed (Type C); otherwise list it for the user |
   | A design decision | "Use Kafka", "add a cache" | Ask for the quality behind it; list it as an ADR candidate for the architect |
   | Not measurable even after asking | "A great experience" | Keep it with an open question; no row |

7. **Tag architecture drivers.** `yes` when meeting the target needs a structural choice (synchronous or asynchronous flow, replication, partitioning, caching, isolation, identity infrastructure, a configuration model) or is expensive to change after go-live; `no` when platform defaults or local code meet it the same way everywhere; `TBD` when it depends on an open target. Give the reason for every `yes` and `TBD` in *Architecture drivers*. If `requirements.csv` has a `Tags` column, add `arch-driver`.
8. **Planguage, if asked.** When the user passes `planguage` or prefers Gilb's format, add one block per requirement to *Planguage specifications* following `references/planguage.md` (Scale = Metric, Meter = Measurement method, Must = Target). Otherwise write "Not used." in that section.
9. **Allocate IDs and attributes.** Use `re-ids` (or `re-lint ids next --kind requirement --count <n>`). Each row: `Type=Q`, the `Text` from step 5, `Source` (person and date, interview or source ID), `Priority` from the stakeholder (else `TBD`), `Status=draft`, a one-sentence `Rationale` (the concern and who raised it). Rewriting an existing Q row keeps its ID (increment `Version` if present; an `agreed` row moves back to `proposed`).
10. **Show, then write.** Show the *Walkthrough* table and the requirement tables; get confirmation. Write `requirements/quality-requirements.md` from `assets/quality-requirements.md` (same sections, same order, `none` in empty ones) and append the rows to `requirements.csv` in schema column order. In non-interactive mode, write directly.
11. **Lint.** Run the `requirement-linter` skill on the new IDs (or `re-lint check --only-ids <IDs>`). `open-tbd` info findings are expected; fix every error.
12. **Report.** End with: requirements per characteristic, the architecture drivers, every `TBD` with its owner, the reclassified concerns and where they went, and the next steps from *Hand-offs*.

## Quality checks

- [ ] The *Walkthrough* has all nine 2023 characteristics (including interaction capability, flexibility and safety), each with a decision and a reason; "usability" and "portability" are not used as characteristic names.
- [ ] Every requirement has metric, target, condition and measurement method; every unknown is `TBD` with an open question and owner.
- [ ] Every number in a *Target* came from a named person or source; baselines sit in *Condition*, labeled as baselines.
- [ ] One target and one `shall` per requirement; no weak words left in `Text`.
- [ ] Every requirement has a *Driver* value; every `yes` and `TBD` has a reason.
- [ ] `requirements.csv` rows are Type Q, `draft`, with `Source`; the target in each `Text` matches the *Target* column.
- [ ] Functions, mandates and design decisions are routed, not written as quality requirements.
- [ ] No ISO text: characteristic and sub-characteristic names only.

## Hand-offs

- **Next:** `constraints-register` for the mandates found; `requirement-linter` on the new rows; `testability-check` to confirm verification methods; share *Architecture drivers* with the architect; suggest `/requirements-review` with the architect and tester perspectives.
- **Feeds back to:** `clarifying-questions` with every `TBD`; `requirement-phrasing` with concerns that turned out to be functions; `conflict-detector` when two targets compete (latency against fraud scoring, retention against data minimization); `glossary` with new terms.

## Non-interactive mode

Ask nothing. Run the walkthrough from the input and the workspace, write every requirement with `TBD` where a value is missing, log each open question with an owner role, and list them in the final message.

## References

- `references/system-types.md`: tailoring table (which characteristics matter per system type) and screening questions per characteristic. Read it at step 2.
- `references/metrics-catalogue.md`: metrics, conditions and measurement methods per sub-characteristic, without target values. Read it at step 5.
- `references/planguage.md`: the Planguage keywords, a block template and a worked example. Read it at step 8.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: the loyalty-points walkthrough and the file and rows it produces.
