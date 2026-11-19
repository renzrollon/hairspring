# Expected reply: lint explained

`python3 <skill-dir>/scripts/lint_requirements.py` exited **1**: `re-lint: 8 errors, 4 warnings, 2 info in 14 rows (1 file)`. The run fails on the 8 errors; warnings and info do not fail it at the default `--fail-on error`. Full report: `expected-output.txt`.

| ID | Rule | Match | Why it matters | Suggested rewrite |
| --- | --- | --- | --- | --- |
| R-018 | universal-quantifier (warning) | all | "All members" claims no exceptions; closed or fraud-held accounts are probably exceptions | The loyalty service shall show a member with an active account their points history in the customer mobile app. (Q1: which account states are excluded? owner SH-01) |
| R-020 | weak-word (error) | quickly | "Quickly" cannot be tested; two testers will pick two numbers | WHEN the member completes login, the customer mobile app shall display the points balance within TBD seconds. (Q2: target in seconds? owner SH-01) |
| R-021 | passive-voice (warning) | be validated | Nobody is responsible: the POS, the loyalty service, or both? | WHEN the POS sends a voucher validation request, the loyalty service shall validate the voucher code before the POS applies the discount. (Q3: confirm the loyalty service validates; owner SH-09) |
| R-022 | missing-obligation (error), future-tense (warning) | will | "Will" states an intention, not a requirement, so nobody is bound to build it | WHEN the loyalty service posts points, the loyalty service shall send the member a push notification. (Source says "could": keep Priority `could`) |
| R-025 | incomplete-condition (error) | IF | An unwanted-behavior requirement without THEN reads as a condition with no clear response | IF the fraud engine places a hold on a purchase, THEN the loyalty service shall keep the points of that purchase in pending state. |
| R-026 | compound-requirement (warning) | and email the | Two actions under one `shall`: one can pass while the other fails | Split: R-026 "The loyalty service shall export the daily points extract to the data warehouse." and a new ID from `re-ids`: "WHEN the daily points extract is exported, the loyalty service shall email the finance controller." (Q4: is the email needed, or is the warehouse report enough? owner SH-03) |
| R-040 (line 11) | duplicate-id (error) | R-040 | Two rows share an ID, so traces and decisions point at the wrong one | Keep R-040 on line 10; give the redemption-rejection row the next free ID from `re-ids` (for example `re-lint ids next`). Never renumber the first row. |
| R-064 | nominalization (info) | the handling of | "Handling" hides what agents actually do | The admin console shall let support agents adjust a member's points. |
| R-065 | missing-attribute (error) | Source | No source, so nobody can confirm the 5,000-point limit | Source: `S-01` if the programme terms state it, else `TBD` and Q5 to SH-01. |
| R-082 | invalid-enum (error) x2 | NFR, high | `NFR` and `high` are not schema values; views and filters miss the row | Type `Q`; Priority `TBD` until SH-01 says `must`, `should`, `could` or `wont` (`high` is not automatically `must`). |
| R-082 | open-tbd (info) | TBD | Visible open value; fine for a draft, blocks a release only with `--fail-on info` | Answer Q2 (same target as R-020?) and keep the ID. |
| REQ12 | invalid-id (error) | REQ12 | Tools and traces only recognize `R-nnn` | Allocate the next free `R-` ID from `re-ids` for this row. |

Open questions: Q1 to Q5 above, each with its owner.

Next: apply the rewrites you accept with `requirement-phrasing` (same IDs; new IDs only for the split in R-026 and the duplicate R-040), then rerun `python3 <skill-dir>/scripts/lint_requirements.py --only-ids R-018,R-020,R-021,R-022,R-025,R-026,R-040,R-064,R-065,R-082`. I changed no file.
