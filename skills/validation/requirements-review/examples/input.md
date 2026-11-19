# Input: `/requirements-review origin/main` on PR #57 "Voucher redemption" (loyalty-points sample)

The PR adds eight rows, R-040 to R-047, to `requirements/requirements.csv`. The base branch already holds R-001, R-003 and R-020 (agreed). Requested by Wei Jie Chua (SH-08), 2026-11-03. No `schema.json` changes; the default schema applies.

## `git diff origin/main -- requirements/`

```diff
@@ -4,0 +5,8 @@ R-020,F,"WHEN the member opens the balance screen, ...
+R-040,F,"WHEN a member with at least 500 posted points requests a voucher in the customer mobile app, the loyalty service shall issue a voucher worth SGD 1 per 100 points redeemed.",S-01,must,draft,Redemption rule from the programme terms.
+R-041,F,"WHEN the loyalty service issues a voucher, it shall deduct the redeemed points from the member's posted balance.",S-01,must,draft,Keeps the balance consistent with issued vouchers.
+R-042,F,"WHEN the POS sends a voucher validation request, the loyalty service shall return the voucher status to the POS.",S-02,must,draft,The POS applies the discount only for valid vouchers.
+R-043,Q,"The loyalty service shall answer voucher validation requests fast enough for checkout.",SH-02 Arjun Pillai 2026-10-30,must,draft,Checkout must not get slower.
+R-044,F,"The customer mobile app shall show the member's recent vouchers.",SH-01 Mei Tan 2026-10-28,could,draft,Members want to find their vouchers at the till.
+R-045,F,"WHEN a member requests a voucher, the loyalty service shall issue a voucher worth SGD 1 per 100 points.",SH-07 Priya Raman 2026-10-29,should,draft,Simple redemption drives app engagement.
+R-046,F,"The loyalty service shall store vouchers in a PostgreSQL table.",SH-08 Wei Jie Chua 2026-10-30,should,draft,Platform standard.
+R-047,F,"Vouchers expire.",S-01,must,draft,TBD
```

## Lint (step 3)

`python3 <skill-dir>/scripts/lint_requirements.py --format json --changed-only origin/main` exits 1. In text form:

```text
requirements/requirements.csv:8: error weak-word R-043: weak word "fast" has no measurable meaning
    hint: Replace with a measurable criterion or a reference to a defined term
requirements/requirements.csv:12: info open-tbd R-047: open placeholder "TBD" in Rationale
    hint: Resolve the open question; keep the ID
requirements/requirements.csv:12: error missing-obligation R-047: no obligation verb (shall/should/may/must) and not a user story
    hint: Add the obligation verb that matches the binding level
re-lint: 2 errors, 0 warnings, 1 info in 11 rows (1 file)
```

## Expected result

- `requirements/reviews/review-2026-11-03.md`: see `expected-output.md`.
- `requirements/requirements.csv` is unchanged. The reply shows the verdict and the blocker and major findings, and asks Wei Jie which findings he accepts.
