# Requirement release notes: v1.0-contract -> v1.1

- From: `v1.0-contract` (2026-10-15T08:30:00Z, git 13a30be2771a) - Requirements agreed for the TillPoint integration contract, signed by Mei Tan (SH-01) 2026-10-15
- To: `v1.1` (2026-11-03T10:00:00Z, git 1f5327f2352e) - January release scope, approved by Mei Tan (SH-01) 2026-11-03

Summary: 1 added, 2 changed, 1 status changed, 1 withdrawn, 0 removed.

## Added

- **R-064** IF a support agent submits an adjustment above 5,000 points, THEN the admin console shall require approval by the support lead before posting the adjustment. (F, must). Decision: RDR-003

## Changed

- **R-020** WHEN a member requests the balance, the loyalty service shall return the posted points balance and the pending points as two separate values. (F, must): text; Version 1 -> 2
- **R-041** IF a member requests a redemption of fewer than 300 posted points, THEN the loyalty service shall reject the redemption with the reason "below minimum". (F, must): text; Version 1 -> 2. Decision: CR-001

## Status changes

- **R-004** WHERE a bonus campaign is active for the store, the loyalty service shall apply the campaign multiplier to earned points. (F, should): Status proposed -> agreed

## Withdrawn

- **R-063** IF a support agent submits an adjustment above 5,000 points, THEN the admin console shall require approval by a second support agent before posting the adjustment. (F, must): Status agreed -> withdrawn. Rationale: Replaced by R-064 (RDR-003). Decision: RDR-003

<!-- Everything above is written by `re-lint baseline notes`; sections with no entries are left out. The review below is added by the baseline skill. -->

## Review: decision links found in changes/ and decisions/

| ID | Class | Decision / CR | Found in |
| --- | --- | --- | --- |
| R-004 | status changed | none needed: agreed by Mei Tan (SH-01) 2026-10-28 | `Rationale` of R-004 |
| R-020 | changed | none found | searched `requirements/changes/` and `requirements/decisions/` |

## Review: uncontrolled changes

Changes to requirements that were agreed or later in v1.0-contract and have no change request or decision record.

| ID | Class | Status in v1.0-contract | Next step |
| --- | --- | --- | --- |
| R-020 | changed (text, Version 1 -> 2) | agreed | Ask SH-01 Mei Tan who approved the rewording; document it with `/change-impact` before v1.1 is shared with TillPoint |
