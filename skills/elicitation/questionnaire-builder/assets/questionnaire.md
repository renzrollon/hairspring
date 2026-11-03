# Questionnaire: {title}

| Field | Value |
| --- | --- |
| Slug | {slug} (folder `requirements/elicitation/questionnaire-<slug>/`) |
| Owner | {name (SH-nn)} |
| Purpose | validate \| quantify \| explore |
| Based on | {I-nn, CAN-nnn, R-nnn, S-nn the hypotheses come from} |
| Population | {who can answer} |
| Sample and recruitment | <who is invited, how, how many; TBD if unknown> |
| Channel | Google Forms \| Microsoft Forms \| paper \| other |
| Field period | {YYYY-MM-DD to YYYY-MM-DD, or TBD} |
| Status | draft \| piloted \| fielded \| analyzed |

## Hypotheses

| H | Hypothesis | From | Supported if (agreed before fielding) | Agreed by |
| --- | --- | --- | --- | --- |
| H1 | {one testable statement} | {I-nn, CAN-nnn} | {metric and threshold in words, or TBD} | {name (SH-nn) YYYY-MM-DD, or TBD} |

## Questions

| ID | H | Kind | Type | Question | Options or scale | Required |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 | H1 | closed | scale | {one concept, neutral wording} | <1 = label, 5 = label> | <yes \| no> |

Kind: `closed` or `open`. Type: as in `form-import.csv` (`section`, `scale`, `single`, `multi`, `dropdown`, `short`, `paragraph`).
Form definition: `form-import.csv`. Analysis plan and results: `analysis.csv`.

## Introduction text

> {shown to respondents: purpose, time needed, anonymity, how answers are used, contact person}

## Privacy

| Question | Answer |
| --- | --- |
| Personal data collected | {none, or the list and why} |
| Approved by | {data protection owner (SH-nn) YYYY-MM-DD, or TBD} |
| Retention of responses | {rule, or TBD} |

## Pilot

| Step | What | Who | Done when |
| --- | --- | --- | --- |
| 1 | Think-aloud run with a few people from the population who will not take the final survey | {names or roles} | Every question is understood as intended |
| 2 | Time a full run | {role} | The duration in the introduction text is true |
| 3 | Fix wording; update `form-import.csv` | {role} | Status is `piloted` |

## Analysis plan

- Closed items: metric, threshold and minimum number of answers (MinN) per item in `analysis.csv`, agreed before fielding. `TBD` makes the result `inconclusive`.
- Open items: {who codes the answers into themes, and how disagreements are settled}.
- After fielding, nobody changes a threshold, drops an item or switches the metric.

## Results

| H | Items | Result | Evidence | What changes |
| --- | --- | --- | --- | --- |
| H1 | {Q-IDs} | <supported \| not supported \| inconclusive> | {value, N, from analysis.csv} | {candidate or requirement to update, or none} |

## Open questions

| # | Question | Owner |
| --- | --- | --- |
| OQ1 | {question} | {name (SH-nn) or role} |
