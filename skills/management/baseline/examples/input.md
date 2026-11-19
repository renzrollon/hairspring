# Input: cut v1.1 and write release notes against v1.0-contract (loyalty-points sample)

Command: `/baseline create v1.1`, then `/baseline notes v1.0-contract v1.1`. Message from the user: "January release scope, approved by Mei Tan (SH-01) 2026-11-03". No git tag requested.

## `requirements/baselines/v1.0-contract.json` (existing; summary)

Created 2026-10-15T08:30:00Z, commit `13a30be`, message "Requirements agreed for the TillPoint integration contract, signed by Mei Tan (SH-01) 2026-10-15".

| ID | Version | Status | Type | Priority | text_sha256 |
| --- | --- | --- | --- | --- | --- |
| R-001 | 1 | agreed | F | must | `de6db66eba5e…` |
| R-003 | 1 | agreed | F | must | `964227f6caf6…` |
| R-004 | 1 | proposed | F | should | `a43f1b9300e5…` |
| R-020 | 1 | agreed | F | must | `82774f4574e2…` |
| R-041 | 1 | agreed | F | must | `535cf27eddd6…` |
| R-060 | 1 | agreed | F | must | `c75a85c4552d…` |
| R-063 | 1 | agreed | F | must | `7654375bdef7…` |
| R-100 | 1 | agreed | C | must | `6439360df696…` |

## `requirements/requirements.csv` now (committed; working tree clean)

```csv
ID,Type,Text,Source,Priority,Status,Rationale,Version,Links
R-001,F,"WHEN the POS sends a completed purchase event, the loyalty service shall create a pending points transaction for the member.",S-02,must,agreed,Core earning flow.,1,
R-003,F,"WHEN 24 hours have passed since the purchase, the loyalty service shall post the pending points to the member's balance.",S-01,must,agreed,Return window before points become usable.,1,
R-004,F,"WHERE a bonus campaign is active for the store, the loyalty service shall apply the campaign multiplier to earned points.",SH-07,should,agreed,Campaigns drive store visits (I-01). Agreed by Mei Tan (SH-01) 2026-10-28.,1,
R-020,F,"WHEN a member requests the balance, the loyalty service shall return the posted points balance and the pending points as two separate values.",S-06,must,agreed,Members ask why new points are not usable yet (S-03).,2,
R-041,F,"IF a member requests a redemption of fewer than 300 posted points, THEN the loyalty service shall reject the redemption with the reason ""below minimum"".",CR-001,must,agreed,Minimum lowered for the year-end campaign (CR-001).,2,CR-001
R-060,F,"WHEN 12 months have passed since points were posted, the loyalty service shall expire those points.",S-01,must,agreed,Programme terms; Finance (SH-03) needs a bounded points liability.,1,
R-063,F,"IF a support agent submits an adjustment above 5,000 points, THEN the admin console shall require approval by a second support agent before posting the adjustment.",SH-06,must,withdrawn,Replaced by R-064 (RDR-003).,1,RDR-003
R-064,F,"IF a support agent submits an adjustment above 5,000 points, THEN the admin console shall require approval by the support lead before posting the adjustment.",RDR-003,must,agreed,Second agents approved each other's adjustments; the support lead approves instead (RDR-003).,1,RDR-003
R-100,C,The loyalty service shall retain points transaction records for 7 years.,S-05,must,agreed,Audit retention under DRP-2024.,1,RDR-001
```

## Decision records in the workspace

- `requirements/changes/CR-001-lower-minimum-redemption.md`: approved by Mei Tan (SH-01) 2026-11-03, Status `applied`, names R-041.
- `requirements/decisions/RDR-003-adjustment-approval.md`: maker-checker by the support lead instead of a second agent; names R-063 and R-064.
- No CR or RDR names R-020.

## Pre-checks

`re-lint check`: 0 errors. Status mix: every row is `agreed` except R-063 (`withdrawn`). `git status --porcelain -- requirements/`: clean. No ID from `v1.0-contract` is missing.

## Commands run

```sh
python3 <skill-dir>/scripts/baseline.py create v1.1 --message "January release scope, approved by Mei Tan (SH-01) 2026-11-03"
python3 <skill-dir>/scripts/baseline.py notes v1.0-contract v1.1
```

Expected outputs: `expected-output.json` (`requirements/baselines/v1.1.json`) and `expected-output.md` (`requirements/baselines/v1.1-notes.md`).
