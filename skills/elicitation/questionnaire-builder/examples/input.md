# Input: cashier survey on checkout findings (loyalty-points sample)

## Run 1 (build), 2026-11-10

> `/questionnaire-builder Validate four findings from interviews I-02 and I-03 with cashiers in all stores before we write the requirements: (1) QR scans of the member code fail often, (2) cashiers would use manual member-number entry as a fallback, (3) cashiers can't tell members when points will appear, (4) vouchers get rejected at the till often. Plus one open question on what else slows them down. Arjun owns it; we use Google Forms.`

Answers given during the run (one batch through `re-interview`):

- Cut-offs agreed by Mei Tan (SH-01) and Arjun Pillai (SH-02) on 2026-11-10: findings 1 and 4 hold if at least 30% of cashiers answer 4 or 5 ("often" or "very often"); findings 2 and 3 hold if at least 60% agree (for finding 3: disagree that they know the answer); a result counts only with at least 40 answers to the item.
- No cut-off agreed for what cashiers do when a scan fails: descriptive only.
- Number of cashiers across the 140 stores: Arjun does not know; store managers forward the link to every cashier.
- Farid Osman (SH-04) approved on 2026-11-11 that the form collects no names, emails or staff numbers.

Run 1 writes `requirements/elicitation/questionnaire-cashier-checkout-findings/` with `questionnaire.md`, `form-import.csv` (`expected-output-form-import.csv`) and `analysis.csv` (`expected-output-analysis.csv`, plan columns only).

## Run 2 (analyze), 2026-11-20

> `/questionnaire-builder The cashier survey closed yesterday. The Google Forms export is responses.csv. Fill in the analysis.`

The skill runs:

```bash
python3 scripts/analyze_responses.py requirements/elicitation/questionnaire-cashier-checkout-findings --responses responses.csv
```

and fills `analysis.csv` (`expected-output-analysis-results.csv`) and the *Results* section of `questionnaire.md` (`expected-output.md`, shown after run 2).
