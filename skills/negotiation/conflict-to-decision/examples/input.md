# Input: `/conflict-to-decision CF-01` (loyalty-points sample)

## The conflict (from `requirements/conflicts.md`)

| ID | Subject | Kind | Requirements | Stakeholders | Type | Recommended technique | Route | Status | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CF-01 | Points expiry period | contradiction | R-060, R-061 | SH-03, SH-07 | interest | compromise or variants; aid: decision matrix | /conflict-to-decision CF-01 | open | |

## The rows (from `requirements/requirements.csv`)

```csv
ID,Type,Text,Source,Priority,Status,Rationale,Links
R-060,F,"The loyalty service shall expire posted points 12 months after posting.",S-01,must,proposed,Limits the points liability on the balance sheet (SH-03).,
R-061,F,"The loyalty service shall expire posted points 18 months after posting.",SH-07 Priya Raman 2026-10-29,must,draft,Occasional shoppers lose points before they reach the redemption minimum.,
```

## Session facts the user gave (2026-11-05, 30 minutes, Mei Tan chairing)

- Decision question agreed: "Which expiry period applies to posted points?"
- Decision-maker: Mei Tan (SH-01, product owner; `process.change_authority` is `product-owner`). Consulted: Grace Lim (SH-03), Priya Raman (SH-07). Informed: Daniel Ng (SH-06, support), Wei Jie Chua (SH-08).
- Constraint: the expiry period is printed in the programme terms (S-01), which must be final before launch.
- Before scoring, Mei, Grace and Priya agreed the criteria and weights: points liability 3, member engagement 2, implementation effort 1; scale 1 to 5, 5 = best.
- Options: A 12 months (R-060); B 18 months (R-061); C, raised by Priya: 12 months standard, 18 months for Gold-tier members.
- Scores agreed in the room: A 5/2/5, B 2/5/5, C 4/4/2 (liability/engagement/effort).
- Priya: "Occasional shoppers never reach 500 points in 12 months." Nobody had data; Priya will pull it from the data warehouse.
- Mei decided for A: liability carries the highest agreed weight, and C adds a tier rule to expiry, member communication and Finance's liability report for a small group. Priya disagreed and asked for an expiry reminder.
- User, after seeing the draft: "Mei confirmed by email today. Apply the updates."

## Expected results

- `requirements/decisions/RDR-001-points-expiry-period.md`: see `expected-output.md`.
- `requirements/requirements.csv` rows after the confirmed updates: see `expected-requirements.csv`.
- `requirements/conflicts.md`: CF-01 `Status` resolved, `Decision` RDR-001.
- Lint on R-060, R-061: 0 errors.
