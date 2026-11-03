# Sample project: one full requirements loop

This folder shows one pass of the re-skills loop (scope, elicit, specify, validate, trace, plus one change) on the fictional Harbourline loyalty-points service. The domain facts are in [`BRIEF.md`](BRIEF.md). Every work product is committed under [`requirements/`](requirements/); the step-by-step record, commands and every place a skill was hard to follow are in [`RUN-LOG.md`](RUN-LOG.md).

How it was run: an engineer with no requirements-engineering training followed each `SKILL.md` literally, in non-interactive mode. The BRIEF's stakeholders were the only people "asked": a fact exists here only if the BRIEF states it; everything else is `TBD` with an open question and an owner. Two things are scripted and say so: the change request in step 14, and Mei Tan's agreement of five redemption rows in step 15.

Paths below are relative to this folder. Every `re-lint` command runs from the repository root with `PYTHONPATH=packages/re-lint/src python3 -m re_lint ...` (or the skill's vendored script) and needs `--workspace examples/loyalty-points/requirements`, because the workspace is not at the repository root.

| Result | Value |
| --- | --- |
| Requirements | 39: 29 F, 7 Q, 3 C; 5 `agreed`, 34 `draft` |
| Lint (`re-lint check requirements/requirements.csv --fail-on error`) | 0 errors, 0 warnings, 35 info (open `TBD`s) |
| Tests (`python3 -m pytest -q examples/loyalty-points/tests`) | 16 passed |
| Trace | 90 links; 8 requirements with tests, 6 with code; 4 gaps (R-015, R-039: agreed, no test, no code, on purpose) |
| Open | 2 conflicts (CF-01, CF-02), 1 proposed decision (RDR-001), 1 pending change (CR-001), 4 open boundary decisions (D-01 to D-04) |

## 1. Set up the workspace: `re-setup`

- **Typed:** `/re-setup` (non-interactive: no stakeholder answered, facets iterative, explorative, customer-specific, criticality PDPA and DRP-2024).
- **In:** `BRIEF.md`. **Out:** [`requirements/README.md`](requirements/README.md), [`requirements/schema.json`](requirements/schema.json), the `requirements.csv` header.
- **Notice:** the trace settings for a workspace inside another repo: `code_globs` `src/**`, `test_globs` `tests/**` (relative to this folder, so run `trace build --repo examples/loyalty-points`), and `scan_git_log: false`, because the enclosing repo's commits are about the catalogue. The README's ID table uses `R-nnn` placeholders: concrete example IDs there are counted by `ids next` (RUN-LOG step 1).

## 2. Draw the boundary: `system-context`

- **Typed:** `/system-context loyalty-points service`
- **In:** `BRIEF.md`. **Out:** [`requirements/context.md`](requirements/context.md): 12 external elements, 17 data flows, one Mermaid diagram.
- **Notice:** four grey zones became open decisions with options and owners, none decided by the agent: D-01 points-expiry batch, D-02 voucher printing, D-03 who reports in-app purchases (the brief says members earn "in the app" but lists no flow), D-04 legacy balance take-over.

## 3. Who to ask, and what to read: `stakeholder-map`, `source-inventory`

- **Typed:** `/stakeholder-map BRIEF.md`, then "register the sources" (`source-inventory`).
- **Out:** [`requirements/stakeholders.md`](requirements/stakeholders.md) (13 stakeholders, quadrant, gap check), [`requirements/sources.csv`](requirements/sources.csv) (S-01 to S-14).
- **Notice:** the gap check adds the fraud analyst, a member proxy (S-03), legal counsel and the data platform team lead. Most influence ratings stay `TBD`, so only 5 of 13 stakeholders are plotted: the rules do not let the agent guess.

## 4. Shared words: `glossary`

- **Typed:** "build a glossary from the brief and the inputs".
- **In:** `BRIEF.md`, [`inputs/`](inputs/). **Out:** [`requirements/glossary.md`](requirements/glossary.md): 31 terms, 9 findings.
- **Notice:** findings found in the inputs, each with `file:line`: member / customer / `cust_id` (synonym), voucher / coupon / e-voucher (synonym), "redeem" for both converting points and using the voucher at the till (homonym), points expiry vs voucher expiry, adjustment vs legacy `ADJ` reversals, and "points balance" undefined (does it include pending points?). The last one drives LOY-118.

## 5. Mine the legacy module and the tickets: `artifact-mining`

- **Typed:** "what does the old redemption module actually do? mine `inputs/legacy/sp_redeem_points.sql` and `inputs/support-tickets-excerpt.csv`".
- **In:** [`inputs/legacy/sp_redeem_points.sql`](inputs/legacy/sp_redeem_points.sql) (S-04), [`inputs/support-tickets-excerpt.csv`](inputs/support-tickets-excerpt.csv) (S-03). **Out:** [`requirements/candidates.csv`](requirements/candidates.csv): 19 candidates, 4 keep, 2 drop, 13 confirm.
- **Notice:** the hard-coded XMAS2018 double voucher value is dropped as obsolete; "never let balance go negative" and the swallowed adjustment error are `confirm` as probable defects; nothing is `keep` on legacy code alone. `check_candidates.py` verifies every quote at its `file:line`.

## 6. Ask before building LOY-118: `clarifying-questions`

- **Typed:** "Before we build LOY-118 ('show points after purchase'), what do we need to clarify?"
- **In:** [`inputs/LOY-118.md`](inputs/LOY-118.md). **Out:** [`requirements/elicitation/questions-loy-118-points-after-purchase.md`](requirements/elicitation/questions-loy-118-points-after-purchase.md): 7 questions, 6 assumptions.
- **Notice:** what the brief already answers (24-hour posting, earn rate, peak load) is under "Already answered" and not asked. Email is a boundary question (the provider does SMS and push only). Two questions are blocking (fraud engine down, consent), so their assumptions take the most restrictive option.

## 7. Sort a PRD: `requirement-classifier`

- **Typed:** "is this a requirement? classify `inputs/prd-redeem-at-checkout.md`".
- **In:** [`inputs/prd-redeem-at-checkout.md`](inputs/prd-redeem-at-checkout.md). **Out:** [`requirements/classification.md`](requirements/classification.md): 15 statements, 7 F, 1 Q, 2 C, 1 solution, 3 facts, 1 unclear.
- **Notice:** "Keep issued vouchers in a Redis cluster" is a solution in disguise routed to the platform tech lead; "the vouchers will be printed by TillPoint" is a `will` fact that collides with open decision D-02; "the redemption screen should be easy to use" is unclear because that screen belongs to the app, not to this service.

## 8. Write the requirements: `requirement-phrasing`, `/user-story-refiner`, `/quality-requirements`, `constraints-register`

- **Out:** [`requirements/requirements.csv`](requirements/requirements.csv) (R-001 to R-023 phrased, R-024 to R-026 stories, R-027 to R-033 quality, R-034 the "auditable" function handed back, R-035 to R-037 constraints), [`requirements/stories/redeem-points-at-checkout.md`](requirements/stories/redeem-points-at-checkout.md), [`requirements/quality-requirements.md`](requirements/quality-requirements.md), [`requirements/constraints.csv`](requirements/constraints.csv).
- **Notice:** every unknown target stays `TBD`; last year's peak of about 9,000 purchases per minute is a baseline in the Condition column, never the target. "Run on the Kubernetes platform" got no constraint row: nobody in the brief mandates it, so it is reported as unconfirmed. Each story has an unwanted-behavior criterion, INVEST and the ten-item Definition of Ready (all `not ready`).

## 9. Conflicts and one decision: `conflict-detector`, `/conflict-to-decision`

- **Out:** [`requirements/conflicts.md`](requirements/conflicts.md) (CF-01 expiry 12 vs 18 months, interest; CF-02 7-year retention vs PDPA, subject matter), [`requirements/decisions/RDR-001-points-expiry-period.md`](requirements/decisions/RDR-001-points-expiry-period.md).
- **Notice:** RDR-001 is `proposed`: the brief gives two positions and no outcome, so the decision reads "Pending: decision by Mei Tan (SH-01)", with five options and no weights or scores. Seven look-alikes are recorded under "Checked, not a conflict".

## 10. Validate: `requirement-linter`, `/requirements-review`

- **Typed:** "lint the requirements", then `/requirements-review requirements/requirements.csv`.
- **Out:** [`requirements/reviews/lint-2026-11-03-run1.txt`](requirements/reviews/lint-2026-11-03-run1.txt) (0 errors, 0 warnings, 39 info), [`requirements/reviews/review-2026-11-03.md`](requirements/reviews/review-2026-11-03.md) (verdict `not ready`: 1 blocker, 17 major, 7 minor), [`requirements/reviews/lint-2026-11-03-run2.txt`](requirements/reviews/lint-2026-11-03-run2.txt).
- **Notice:** lint was already clean because every emitting skill lints its own rows; the review found what a script cannot: a fraud-held purchase posted by R-004 but kept pending by R-008, a return that neither R-005 nor R-006 covers, "fewer than 500 posted points" mixing request and balance. The second pass applied 6 accepted findings (R-004, R-005, R-013, R-015, R-034 rewritten; R-038, R-039 new), rejected 1 and deferred 18 to their owners.

## 11. How each one will be verified: `testability-check`

- **Out:** [`requirements/verification.csv`](requirements/verification.csv), and the `Verification` column: 37 test, 1 analysis, 1 inspection; 24 verifiable, 14 `tbd`, 1 `no` (R-007, whose response is TBD).
- **Notice:** boundaries are part of the criterion (499 vs 500 points, 5,000 vs 5,001, 23 h 59 min vs 24 h).

## 12. A tiny implementation

- **Out:** [`src/loyalty/`](src/loyalty/) (earning, posting, redemption) with `# @req R-nnn` comments, [`tests/`](tests/) with `test_r_nnn_...` names and a `conftest.py` that puts `src/` on the path.
- **Notice:** voucher validation (R-015, R-039) is deliberately not built, so the gap report has something to show. Redeeming points that are not a multiple of 100 raises an error until stories Q2 is answered: the most restrictive option, not a decision.

## 13. Trace: `traceability-matrix`

- **Typed:** `re-lint trace build --repo examples/loyalty-points --workspace examples/loyalty-points/requirements`, then `re-lint trace gaps --workspace examples/loyalty-points/requirements`.
- **Out:** [`requirements/trace/trace.csv`](requirements/trace/trace.csv), [`trace.md`](requirements/trace/trace.md), [`gaps.json`](requirements/trace/gaps.json).
- **Notice:** while every row was `draft`, the first build reported 0 gaps (requirement-level gaps apply to `agreed` and later); `trace gaps --status draft` listed 29 untested drafts as informational. After step 15 the rebuild shows the 4 real gaps.

## 14. A change request: `/change-impact`

- **Typed:** `/change-impact Lower the minimum redemption from 500 to 300 points` (requested by Priya Raman, SH-07; scripted).
- **Out:** [`requirements/changes/CR-001-lower-minimum-redemption.md`](requirements/changes/CR-001-lower-minimum-redemption.md).
- **Notice:** the impact set comes from `re-lint trace impact R-013 R-024 R-025` plus a search: one constant, six tests, the stories and verification rows, the programme terms (S-01) and the app team. Sizes are relative (M, proposed by the agent), no hours. Decision `pending` with Mei Tan; `requirements.csv` is unchanged.

## 15. Hand off and freeze: `/to-openspec`, `/baseline`

- **Scripted:** no row was `agreed`, and only a named person can agree one. For this sample, Mei Tan (SH-01) agrees R-013, R-014, R-015, R-038 and R-039 with priority `must` (recorded in the new `Owner` column). This is part of the fictional scenario script, not a BRIEF fact.
- **Typed:** `/to-openspec add-voucher-redemption`, then `/baseline create v0.1-sample`.
- **Out:** [`openspec/changes/add-voucher-redemption/`](openspec/changes/add-voucher-redemption/) (proposal, spec delta, tasks; every heading and task carries its R-ID), [`requirements/baselines/v0.1-sample.json`](requirements/baselines/v0.1-sample.json) (39 entries, no git tag).
- **Notice:** the hand-off gate blocks a row with `Priority=TBD`, which is why the scripted agreement includes the priority. The other redemption rows are listed under "Not in this change" with their reason.
