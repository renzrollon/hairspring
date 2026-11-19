# Input: a Component attribute and an architect view (loyalty-points sample)

Request from Lena Koh (SH-05, security architect) on 2026-11-03:

> We need to see the agreed quality requirements and constraints per component before the design review: earn, balance, redeem, expiry, admin, platform. Can you add a Component attribute and give us a view?

Wei Jie Chua (SH-08) confirmed the component values for each row in the same thread.

## `requirements/requirements.csv` before

```csv
ID,Type,Text,Source,Priority,Status,Rationale,Risk
R-001,F,"WHEN the POS sends a completed purchase event, the loyalty service shall create a pending points transaction for the member.",S-02,must,agreed,Core earning flow.,
R-041,F,"IF a member requests a redemption of fewer than 500 posted points, THEN the loyalty service shall reject the redemption with the reason ""below minimum"".",S-01,must,implemented,Minimum redemption in the programme terms.,
R-080,Q,"WHEN the POS requests voucher validation, the loyalty service shall respond within TBD ms at the 95th percentile under year-end peak load.",SH-02,must,proposed,Checkout must not get slower (I-02).,high
R-081,Q,The loyalty service shall accept purchase events at TBD events per minute without loss during the year-end sale.,SH-08,must,agreed,"Last year's peak was about 9,000 purchases per minute (SH-08).",high
R-082,Q,The admin console shall require multi-factor authentication when a support agent logs in.,SH-05,must,agreed,Adjustments move member value (SH-05).,medium
R-100,C,The loyalty service shall retain points transaction records for 7 years.,S-05,must,agreed,Audit retention under DRP-2024.,low
R-101,C,The loyalty service shall run on the platform team's Kubernetes platform.,SH-08,must,agreed,Platform mandate (SH-08).,low
```

`requirements/schema.json` is a copy of the default (`assets/schema.json`) with `"views": {}`.

## Steps run

1. Added `Component` to `attributes.optional` and `attributes.enums` (diff in `expected-output.json`). The whole `optional` array is written, because arrays replace the defaults rather than merge.
2. Added the `Component` column to `requirements.csv` with the values Wei Jie Chua confirmed: R-001 earn, R-041 redeem, R-080 redeem, R-081 earn, R-082 admin, R-100 platform, R-101 platform.
3. Replaced the built-in `architect` view with a definition that shows and counts `Component`.
4. `re-lint check`: 0 errors. `python3 <skill-dir>/scripts/views.py --view architect` wrote `requirements/views/architect.md` (`expected-output.md`).
