# Expected output: LOY-118 phrased

## Before / after

| Original | Rewritten | Pattern | Requirement |
| --- | --- | --- | --- |
| "the app should quickly show the new balance" | WHEN the loyalty service posts points for a purchase, the customer mobile app shall display the updated points balance on the member's next balance request. | Event-driven | R-023 |
| ("quickly") | WHEN the loyalty service posts points for a purchase, the updated balance shall be available to the customer mobile app within TBD seconds. | Event-driven, quality | R-024 |
| "Points will be added once the purchase is processed" | Not a requirement as written (`will` = fact). Covered by existing earning requirements R-001..R-019; no row added. | n/a | n/a |
| "If something goes wrong with the fraud check the points are held" | IF the fraud engine places a hold on a purchase, THEN the loyalty service shall keep the points of that purchase in pending state until the fraud engine releases the hold. | Unwanted behavior | R-025 |
| "All members should get a push notification and an email" | Split into R-026 (push) and R-027 (email); "All" removed (universal quantifier; opt-out rules are open question Q3). | Event-driven ×2 | R-026, R-027 |
| "Use Redis to cache balances" | Not a requirement: a design decision. Routed to the platform tech lead (SH-08); the quality behind it is R-024. | n/a | n/a |

Rows appended to `requirements/requirements.csv`: see `expected-output.csv`.

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| Q1 | How many seconds after posting must the new balance be visible in the app? | SH-01 Mei Tan | R-024 |
| Q2 | Push, email, or both? Is one a fallback for the other? | SH-01 Mei Tan, SH-07 Priya Raman | R-026, R-027 |
| Q3 | Do members who opted out of marketing messages still get transactional points notifications? | SH-04 Farid Osman | R-026, R-027 |

## Lint

`python3 scripts/lint_requirements.py --only-ids R-023,R-024,R-025,R-026,R-027`: 0 errors, 1 info (`open-tbd` on R-024).
