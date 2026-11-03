# Questionnaire: cashier checkout findings

| Field | Value |
| --- | --- |
| Slug | cashier-checkout-findings (folder `requirements/elicitation/questionnaire-cashier-checkout-findings/`) |
| Owner | Arjun Pillai (SH-02) |
| Purpose | validate |
| Based on | I-02 (Arjun Pillai), I-03 (Daniel Ng), S-03 (support ticket export) |
| Population | Cashiers in Harbourline's 140 stores |
| Sample and recruitment | All cashiers, invited by their store managers; number of cashiers TBD (OQ1) |
| Channel | Google Forms |
| Field period | 2026-11-17 to 2026-11-19 |
| Status | analyzed |

## Hypotheses

| H | Hypothesis | From | Supported if (agreed before fielding) | Agreed by |
| --- | --- | --- | --- | --- |
| H1 | Scanning a member's QR code fails at the first try often enough to matter at the till. | I-02 | At least 30% answer 4 or 5 on Q01; at least 40 answers | Mei Tan (SH-01), Arjun Pillai (SH-02) 2026-11-10 |
| H2 | Cashiers would use manual entry of the member number when a scan fails. | I-02 | At least 60% answer 4 or 5 on Q02; at least 40 answers. Q05 is descriptive (no cut-off agreed) | Mei Tan (SH-01), Arjun Pillai (SH-02) 2026-11-10 |
| H3 | Cashiers cannot tell members when the points of a purchase will appear. | I-03, S-03 | At least 60% answer 1 or 2 on Q03; at least 40 answers | Mei Tan (SH-01), Arjun Pillai (SH-02) 2026-11-10 |
| H4 | Vouchers are rejected at the till often enough to matter. | I-03, S-03 | At least 30% answer 4 or 5 on Q04; at least 40 answers | Mei Tan (SH-01), Arjun Pillai (SH-02) 2026-11-10 |
| H5 | Explore: other loyalty-related delays at the till that interviews did not surface. | I-02 | n/a: themes coded by hand | n/a |

## Questions

| ID | H | Kind | Type | Question | Options or scale | Required |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 | H1 | closed | scale | In a typical shift, how often does scanning a member's QR code fail at the first try? | 1 = never, 5 = very often | yes |
| Q02 | H2 | closed | scale | When a scan fails, typing the member number by hand would help me finish the sale. | 1 = strongly disagree, 5 = strongly agree | no |
| Q03 | H3 | closed | scale | When a member asks when today's points will appear in the app, I know what to answer. | 1 = strongly disagree, 5 = strongly agree | yes |
| Q04 | H4 | closed | scale | In a typical week, how often is a member's voucher rejected at your till? | 1 = never, 5 = very often | yes |
| Q05 | H2 | closed | single | When a QR scan fails, what do you usually do? | Ask the member to raise screen brightness; Ask for the plastic card; Look up the member by phone number; Finish the sale without points; Other | no |
| Q06 | H5 | open | paragraph | What else slows you down at the till when a member uses the loyalty programme? | free text | no |

Q03 is worded positively on purpose (agreeing means the cashier knows); H3 is supported by disagreement, so its metric is `bottom2`.
Form definition: `form-import.csv`. Analysis plan and results: `analysis.csv`.

## Introduction text

> Six questions, about 3 minutes. Answers are anonymous and used only to improve the loyalty programme at the till. Questions: Arjun Pillai, store operations.

## Privacy

| Question | Answer |
| --- | --- |
| Personal data collected | None: no name, email or staff number; email collection is off in the form settings |
| Approved by | Farid Osman (SH-04) 2026-11-11 |
| Retention of responses | TBD (OQ2) |

## Pilot

| Step | What | Who | Done when |
| --- | --- | --- | --- |
| 1 | Think-aloud run with a few cashiers from one store who will not take the final survey | Arjun Pillai (SH-02) | Every question is understood as intended |
| 2 | Time a full run | Arjun Pillai (SH-02) | The duration in the introduction text is true |
| 3 | Fix wording; update `form-import.csv` | Arjun Pillai (SH-02) | Status is `piloted` |

## Analysis plan

- Closed items: metric, threshold and MinN per item in `analysis.csv`, agreed before fielding. Q05 has threshold `TBD` by agreement: it is reported as a distribution only.
- Open item Q06: Arjun Pillai codes the answers into themes; Daniel Ng (SH-06) checks the coding.
- After fielding, nobody changes a threshold, drops an item or switches the metric.

## Results

48 respondents. Computed with `scripts/analyze_responses.py`; full numbers in `analysis.csv`.

| H | Items | Result | Evidence | What changes |
| --- | --- | --- | --- | --- |
| H1 | Q01 | supported | 33.3% answered 4 or 5 (N 48; cut-off 30%) | Cite as evidence when `requirement-phrasing` writes the scan-failure requirement |
| H2 | Q02, Q05 | supported (Q02); Q05 descriptive | Q02: 70.2% agree (N 47; cut-off 60%). Q05: 14.9% finish the sale without points (N 47) | Manual member-number entry goes to `requirement-phrasing` with this evidence |
| H3 | Q03 | not supported | 54.2% answered 1 or 2 (N 48; cut-off 60%) | Not confirmed at the agreed cut-off; report to Mei Tan (SH-01). The cut-off is not reinterpreted |
| H4 | Q04 | not supported | 20.8% answered 4 or 5 (N 48; cut-off 30%) | Voucher rejection stays a support-ticket finding (S-03) without cashier confirmation |
| H5 | Q06 | manual | 30 answers, 18 blank. Themes: codes that do not scan (13), slow app or scanner (9), balance or pending questions (8) | Run `artifact-mining` (feedback analysis) on Q06 to land the themes as candidates |

## Open questions

| # | Question | Owner |
| --- | --- | --- |
| OQ1 | How many cashiers work across the 140 stores (to state the response rate)? | Arjun Pillai (SH-02) |
| OQ2 | How long are the raw responses kept? | Farid Osman (SH-04) |
