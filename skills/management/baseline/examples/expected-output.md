# Requirement release notes: v1.0-contract → v1.1

| Field | Value |
| --- | --- |
| From | v1.0-contract (created 2026-10-15, commit 13a30be) |
| To | v1.1 (created 2026-11-03, commit 1f5327f) |
| Purpose of v1.1 | January release scope, approved by Mei Tan (SH-01) 2026-11-03 |
| Generated | 2026-11-03 |
| Command | `re-lint baseline notes v1.0-contract v1.1` |

## Summary

| Class | Count |
| --- | --- |
| Added | 1 |
| Changed | 2 |
| Status changed | 1 |
| Withdrawn | 1 |
| Removed | 0 |
| Uncontrolled changes | 1 |

## Added

| ID | Type | Priority | Status | Text | Decision / CR |
| --- | --- | --- | --- | --- | --- |
| R-064 | F | must | agreed | IF a support agent submits an adjustment above 5,000 points, THEN the admin console shall require approval by the support lead before posting the adjustment. | RDR-003 |

## Changed

| ID | What changed | Version | Text now | Decision / CR |
| --- | --- | --- | --- | --- |
| R-020 | text | 1 → 2 | WHEN a member requests the balance, the loyalty service shall return the posted points balance and the pending points as two separate values. | none found |
| R-041 | text | 1 → 2 | IF a member requests a redemption of fewer than 300 posted points, THEN the loyalty service shall reject the redemption with the reason "below minimum". | CR-001 |

## Status changed

| ID | Status | Decision / CR | Note |
| --- | --- | --- | --- |
| R-004 | proposed → agreed | none found | Agreed by Mei Tan (SH-01) 2026-10-28 (Rationale); no CR needed to agree a proposed requirement |

## Withdrawn

| ID | Reason | Decision / CR |
| --- | --- | --- |
| R-063 | Replaced by R-064 (RDR-003) | RDR-003 |

## Removed

None.

## Uncontrolled changes

Changes to requirements that were agreed or later in v1.0-contract and have no change request or decision record.

| ID | Class | Status in v1.0-contract | Next step |
| --- | --- | --- | --- |
| R-020 | changed (text) | agreed | Ask SH-01 Mei Tan who approved the rewording; document it with `/change-impact` before v1.1 is shared with TillPoint |
