---
name: questionnaire-builder
description: >-
  Designs a questionnaire that confirms or quantifies findings across many stakeholders: one
  hypothesis per question, closed or open by rule, labeled scales, a pilot, and an analysis plan
  whose cut-offs are agreed before fielding. Writes
  requirements/elicitation/questionnaire-<slug>/ with questionnaire.md, form-import.csv (a
  tool-neutral item list, with an Apps Script path for Google Forms and a Quick import path for
  Microsoft Forms) and analysis.csv, which a bundled script fills from the response export. Use
  when interview or observation findings must be checked with a larger group ("survey the
  cashiers", "validate these findings with 100 agents", "make a Google Form for this"), or when a
  survey export must be analyzed. Not for discovering needs nobody has voiced (use interview-guide
  or observation-protocol), for a quick batch of questions before implementing (use
  clarifying-questions), or for coding free-text feedback into candidates (artifact-mining).
license: MIT
compatibility: Python 3.9+ optional for scripts/analyze_responses.py; works without it.
disable-model-invocation: true
argument-hint: "[findings or hypotheses, population, form tool] or [response export]"
metadata:
  stage: elicitation
  invocation: user
  priority: P2
  ireb-anchor: "CPRE FL Handbook 1.2 §4.2.2"
  inputs-from: "interview-guide, observation-protocol, artifact-mining, stakeholder-map"
  outputs-to: "requirement-phrasing, artifact-mining, prioritization, requirement-classifier"
  work-product: "requirements/elicitation/questionnaire-<slug>/ (questionnaire.md, form-import.csv, analysis.csv)"
  version: "0.1.0"
---

# Questionnaire builder

A survey answers only the questions it asks, and a badly built one answers them wrongly: double questions, leading wording, cut-offs chosen after the data came in. This skill turns findings into hypotheses, writes one neutral question per hypothesis, fixes the analysis before anyone answers, and produces a form definition and an analysis sheet. Everything lives in `requirements/elicitation/questionnaire-<slug>/`.

## When not to use

- Nobody has voiced the needs yet: run `/interview-guide` or `/observation-protocol` first; a questionnaire confirms, it rarely discovers.
- One task needs a few answers before coding: `clarifying-questions`.
- The input is a pile of free-text feedback (tickets, reviews, open answers): `artifact-mining` with feedback analysis.
- The items exist and need a ranking by stakeholders: `/prioritization`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Findings or hypotheses to test, population, form tool | yes (asked if missing) | the user, `interview-guide`, `observation-protocol` |
| `requirements/candidates.csv`, `requirements.csv`, interview and observation files | no | `artifact-mining`, `interview-guide`, `observation-protocol` |
| `requirements/stakeholders.md` (owner, data protection owner) | no | `stakeholder-map` |
| Response export as CSV (phase B) | for phase B | Google Forms, Microsoft Forms |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `questionnaire-<slug>/questionnaire.md` | `assets/questionnaire.md` | the owner, reviewers |
| `questionnaire-<slug>/form-import.csv` | `assets/form-import.csv`; format in `references/form-import-format.md` | Google Forms (Apps Script), Microsoft Forms (by hand or Quick import) |
| `questionnaire-<slug>/analysis.csv` | `assets/analysis.csv` | `scripts/analyze_responses.py`, `requirement-phrasing`, `prioritization` |

All three sit under `requirements/elicitation/`.

## Procedure

### Phase A: build

1. **Read the workspace.** Load `requirements/schema.json` (else defaults), `stakeholders.md`, and the candidates, requirements, interview and observation files the findings come from, so every hypothesis can cite its source.
2. **Frame it.** If the purpose, population, recruitment, owner or form tool is missing, ask in one batch through the `re-interview` primitive. If the population size is unknown, write `TBD`; never estimate it.
3. **Write the hypotheses.** One testable statement per finding (`H1`, `H2`, ...) with its source (I-nn, CAN-nnn, R-nnn, S-nn). Split any finding that holds two topics. An exploratory open question gets its own `H` marked "Explore".
4. **Agree the analysis before fielding.** For each hypothesis ask the owner for the metric, the threshold that counts as support, and the minimum number of answers (MinN), using `references/question-design.md`. Record who agreed and when. Whatever is not agreed stays `TBD`; never fill a threshold yourself.
5. **Write the questions.** One question per row, each serving exactly one hypothesis; closed when the options are known, open when the respondents' words matter; scales labeled and in one direction per scale type; no double-barrelled, leading, loaded or absolute wording; no jargon. Make items optional where "don't know" is a legitimate answer.
6. **Check privacy.** Collect no personal data unless a hypothesis needs it. If the request asks for identifiers (national ID, staff or card numbers) or contact data, leave them out, say why, and name the data protection owner who would have to approve them.
7. **Write the three files.** `questionnaire.md` from `assets/questionnaire.md` (hypotheses, questions, introduction text, privacy, pilot, analysis plan, empty results); `form-import.csv` with one row per item in the column format of `references/form-import-format.md`; `analysis.csv` with one row per closed item (and one `themes` row per open item), plan columns filled and result columns empty. Show them and tell the user how to build the form in their tool, including that neither tool imports the CSV natively.
8. **Pilot.** Recommend the pilot steps in the file; after the pilot, update wording in both `questionnaire.md` and `form-import.csv` and set `Status=piloted`.

### Phase B: analyze

9. **Compute.** Place the export in the repo and run `python3 <skill-dir>/scripts/analyze_responses.py requirements/elicitation/questionnaire-<slug> --responses <export.csv>`. It fills N, Missing, Distribution, Value, Result and Notes in `analysis.csv`. Exit code 1 lists items it could not match or compute: fix the title or metric and re-run. Without Python, count by hand per item with the same rules (blank = missing; `top2` = share of the two highest scale points among answers).
10. **Report.** Fill *Results* in `questionnaire.md`: per hypothesis the result, value, N and the agreed cut-off, and what changes (the candidate or requirement it is evidence for). A value below the threshold is `not supported`, even if it is a majority; `TBD` thresholds stay `inconclusive`. For open items, code themes with counts, or run `artifact-mining` (feedback analysis) on the open-answer column to land them as candidates. Set `Status=analyzed`.

## Quality checks

- [ ] Every closed question cites exactly one hypothesis; every hypothesis has a source.
- [ ] No question is double-barrelled, leading, loaded or absolute; scales are labeled.
- [ ] Thresholds and MinN were agreed by a named person before fielding, or are `TBD`; none was invented.
- [ ] No personal data is collected without a named approval.
- [ ] `form-import.csv` and `analysis.csv` have exactly the asset headers; titles are unique; IDs match across the three files.
- [ ] Results quote values from `analysis.csv` and claim no significance that was not tested.

## Hand-offs

- **Next:** `requirement-phrasing` for supported hypotheses, citing the result in the rationale; suggest `/prioritization` when results rank needs.
- **Feeds back to:** `artifact-mining` with open-answer columns; `requirement-classifier` when results change a Kano or F/Q/C guess; the owner of each `not supported` hypothesis.

## Non-interactive mode

Build all three files with `TBD` for every threshold, MinN and frame fact nobody gave, list them as open questions in `questionnaire.md`, and say the questionnaire must not be fielded until they are agreed. Phase B runs unchanged.

## References

- `references/question-design.md`: hypothesis to question, closed vs open, scales, wording anti-patterns, sample and pilot, privacy, reporting rules. Read it at steps 3 to 6.
- `references/form-import-format.md`: the CSV columns, what the tools cannot import, the Google Forms Apps Script, the Microsoft Forms path, response exports, and optional `.xlsx` conversion. Read it at step 7.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: a cashier survey validating four interview findings on the loyalty-points sample: the three files as built, a 48-row response export, and the analysis it produced.
