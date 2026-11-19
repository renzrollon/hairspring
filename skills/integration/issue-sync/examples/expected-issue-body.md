Title: R-040: Issue voucher on redemption request
Issue: LOY-81 (created by push --apply on 2026-11-03)

<!-- re-skills:begin -->
**R-040** · F functional · priority must · register status at last push: agreed

> WHEN a member with at least 500 posted points requests a voucher in the customer mobile app, the loyalty service shall issue a voucher worth SGD 1 per 100 points redeemed.

| Attribute | Value |
| --- | --- |
| Source | S-01 (programme T&C draft v3) |
| Rationale | Redemption is why members collect points; the minimum and the rate are programme rules in S-01. |
| Verification | test |
| Owner | SH-01 Mei Tan |

**Acceptance criteria**

- R-040.AC1: Given a member with 1,250 posted points, when the member requests a voucher for 1,000 points in the customer mobile app, then the loyalty service issues a voucher worth SGD 10 and the member's posted balance is 250 points.

**Trace**

- Register: `requirements/requirements.csv` (R-040)
- Sources: S-01
- Decisions and links: none
- Tests and code: not traced yet

_Managed by re-skills issue-sync. Change the requirement in `requirements/requirements.csv` and push again: edits inside this block are overwritten. Discuss outside the block or in comments._
<!-- re-skills:end -->
