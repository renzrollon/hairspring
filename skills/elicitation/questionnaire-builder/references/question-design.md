# Question design

A questionnaire is good at two things: confirming or quantifying what interviews and observations already found, and reaching people you cannot interview one by one. It is poor at discovering what nobody has said yet; use interviews or observation for that first.

## From finding to hypothesis to question

1. Write each finding as one testable hypothesis about the population: "Cashiers would use manual member-number entry when a scan fails." Not "Cashiers have problems with scanning and vouchers" (two topics).
2. Write what would count as support, before fielding: the metric, the threshold and the minimum number of answers. Ask the owner; if nobody can agree a number, write `TBD`: the result will be `inconclusive`, which is honest.
3. Write one closed question per hypothesis (more than one is fine; every question serves exactly one hypothesis). Add an open question only when you want themes, not counts.

## Closed or open

| Use | When | Analysis |
| --- | --- | --- |
| Closed, scale | You know the dimension (agreement, frequency, satisfaction) and want a distribution | `top2`, `bottom2`, `median`; `mean` only if agreed beforehand |
| Closed, single choice | The options are known from interviews and are mutually exclusive | `share:<option>` |
| Closed, multiple choice | Several options can apply | `share:<option>` per option |
| Open, short or paragraph | You need the respondents' words, or the options are not known | Themes coded by hand, or `artifact-mining` (feedback analysis) on the export |

## Scales

| Scale | Labels (end points shown; label every point if the tool allows) | Use for |
| --- | --- | --- |
| Agreement | 1 = strongly disagree ... 5 = strongly agree | Statements of belief or need |
| Frequency | 1 = never ... 5 = very often | How often something happens; prefer a concrete period ("in a typical shift") |
| Satisfaction | 1 = very dissatisfied ... 5 = very satisfied | A named, experienced thing |
| Numeric rating | 0 ... 10 | Only when the team already reports such a score |

Rules: keep the same direction for all items of one scale type; use an odd number of points when a neutral answer is legitimate; leave "don't know" possible by making the item optional (a blank answer counts as missing, not as neutral); treat scale answers as ordered categories, not as measurements.

## Wording

| Don't | Example | Instead |
| --- | --- | --- |
| Double-barrelled | "The new app is faster and easier than the plastic card." | Two questions, one per concept |
| Leading | "Don't you agree that ...?" | A neutral statement with a balanced scale |
| Loaded | "How much would you love an 18-month expiry?" | "Which expiry period would suit you?" with options from the interviews |
| Absolute | "I always ..." / "never" | A frequency scale |
| Hypothetical without anchor | "Would you use feature X?" | Ask about the last time the need arose, or a concrete trade-off |
| Jargon | "posting", "redemption threshold" | The respondents' words ("when points appear", "minimum to get a voucher") |
| Asking for a solution | "Should we add Apple Wallet?" | Ask about the need ("How do you show a voucher at the till today?") |

## Sample, pilot and fielding

- Name the population and how people are invited. If the population size is unknown, write `TBD` and an open question; do not estimate it.
- The minimum number of answers per item (MinN) is agreed with the owner like the thresholds; below it, results are `inconclusive`.
- Pilot with a few people from the population who will not take the final survey: they read each question aloud and say what they think it asks. Fix every question that is misread.
- State the real duration in the introduction text, measured in the pilot.
- Report the response rate when the population size is known; note who did not answer (for example, one region or shift) because silence is not agreement.

## Privacy

- Collect no personal data unless a hypothesis needs it. Turn off email collection in the form tool if it is not needed.
- Never ask for national ID numbers (NRIC), card numbers or staff numbers to "link answers": that is a data protection decision for the data protection owner, not a design convenience.
- Record who approved the setup and how long responses are kept.

## Reporting results

- Report the value, N and the agreed threshold for each item, as computed in `analysis.csv`.
- A result below the threshold is `not supported`, even if it is a majority: do not move the cut-off after seeing the data.
- No significance claims unless a statistical test was planned and run; the analysis sheet does not run one.
