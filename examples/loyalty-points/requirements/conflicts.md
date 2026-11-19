# Conflict register

<!-- Owned by conflict-detector. conflict-to-decision updates the Status and Decision columns and the Status line of a detail block. Never delete an entry: set Status to not-a-conflict with the reason. -->

| Field | Value |
| --- | --- |
| Last scan | 2026-11-03 |
| Scanned | requirements/requirements.csv (37 requirements; withdrawn and rejected skipped), constraints.csv, quality-requirements.md, candidates.csv, classification.md, stakeholders.md |
| Schema | requirements/schema.json |

## Register

| ID | Subject | Kind | Requirements | Stakeholders | Type | Recommended technique | Route | Status | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CF-01 | Points expiry period | contradiction | R-019 | SH-03, SH-07 | interest | compromise or variants; aid: decision matrix | /conflict-to-decision CF-01 | open | |
| CF-02 | Retention of points transaction data vs deletion of member personal data | contradiction | R-036, R-037 | SH-03, SH-04 | subject matter | variants or agreement; aid: consider-all-facts | /conflict-to-decision CF-02 | open | |

Kind: `contradiction` | `overlap` | `inconsistent conditions` | `differing level of detail` | `priority disagreement`.
Type: `subject matter` | `data` | `interest` | `value` | `relationship` | `structural`.
Technique: `agreement` | `compromise` | `voting` | `variants` | `overruling` | `none (escalation)`.
Aid: `consider-all-facts` | `plus-minus-interesting` | `decision matrix` | `none`.
Status: `open` | `escalated` | `resolved` | `not-a-conflict`. Decision: `RDR-nnn`, or the escalation outcome and date.

## CF-01: Points expiry period

- **Kind:** contradiction
- **Requirements:** R-019 "WHEN 12 months have passed since points were posted, the loyalty service shall expire those points" (Source: S-01, draft v3) vs the Marketing position "18 months", which has no requirement row (Source: BRIEF.md:60)
- **Positions:**
  - SH-03 Grace Lim (Finance controller): points expire 12 months after posting, as in the programme terms draft v3 (BRIEF.md:60)
  - SH-07 Priya Raman (Marketing manager): points should expire 18 months after posting (BRIEF.md:60)
  - SH-01 Mei Tan (Head of Loyalty, change authority): position not stated (BRIEF.md:60 names only Finance and Marketing)
- **Why it is a conflict:** one expiry period applies to the same posted points, so 12 and 18 months cannot both hold for the same members at the same time.
- **Type:** interest, because each side protects its own goal (Finance its points liability and month-end, BRIEF.md:35; Marketing its campaigns and member engagement, BRIEF.md:39) while the facts are agreed.
- **Recommended technique:** compromise or variants, because the disagreement is on a scale (a period) that both sides could move on, or the period could differ by scope; the compromise value must come from the parties. Analysis aid: decision matrix, with criteria and weights agreed before scoring.
- **Route:** /conflict-to-decision CF-01; decision-makers: Mei Tan (SH-01, product owner and change authority), with Grace Lim (SH-03) and Priya Raman (SH-07)
- **Open questions:** Who runs points expiry after go-live (open decision D-01, owner SH-01)? If the data platform team keeps the job, the period is still decided here but implemented there. (owner: SH-01)
- **Status:** open

## CF-02: Retention of points transaction data vs deletion of member personal data

- **Kind:** contradiction
- **Requirements:** R-036 "keep points transaction data for 7 years" (Source: S-05, DRP-2024) vs R-037 "keep member personal data no longer than TBD" (Source: S-05, PDPA)
- **Positions:**
  - SH-03 Grace Lim (Finance controller): transaction data must be kept 7 years for audit under DRP-2024 (BRIEF.md:64)
  - SH-04 Farid Osman (data protection officer): PDPA requires personal data not be kept longer than needed (BRIEF.md:64)
  - Members: one ticket in the S-03 excerpt asks to delete all data and purchase history (CAN-019, inputs/support-tickets-excerpt.csv:8)
- **Why it is a conflict:** points transactions carry the member they belong to, so keeping every transaction 7 years keeps member personal data 7 years, which may be longer than PDPA allows once the member leaves; the legacy module deletes whole transactions only after 7 years (CAN-014).
- **Type:** subject matter, because two legitimate obligations (a written retention policy and a law) collide on the same data and nobody disputes the facts.
- **Recommended technique:** variants or agreement, because the system can serve both needs, for example by separating what identifies the member from what audit needs; the variant is for the parties to choose. Analysis aid: consider-all-facts, then plus-minus-interesting.
- **Route:** /conflict-to-decision CF-02; decision-makers: Mei Tan (SH-01, change authority), with Grace Lim (SH-03) and Farid Osman (SH-04)
- **Open questions:** Which fields of a points transaction count as personal data, and does DRP-2024 require them for audit? (owner: SH-04, with SH-03)
- **Status:** open

## Checked, not a conflict

| Requirements | Looked like | Why not a conflict |
| --- | --- | --- |
| R-028, R-004, R-010 | Points visible within seconds of the purchase (R-028) vs points posted only after 24 hours (R-004) and added to the balance at posting (R-010) | Both hold if pending points are shown apart from the balance (LOY-118 question 2, option a); it becomes a conflict only if the product owner answers option c |
| R-027, R-009 | Fraud scoring vs fast voucher validation at checkout | Different operations: fraud scoring runs when the member redeems in the app (R-009), not when the POS validates the voucher (R-027) |
| R-019, R-036 | 12 months next to 7 years | Different subjects: points validity vs transaction-data retention |
| R-024, R-025 | A fixed 500-point voucher vs any amount from 500 points | Agreed slices of one epic: R-025 extends R-024 (stories/redeem-points-at-checkout.md, Slicing) |
| R-007, CAN-010 | Negative balance after a reversal vs the legacy rule that sets it to zero | R-007 leaves the response `TBD`; the open rule is a question (BRIEF.md:62), not two positions yet |
| CAN-006, classification row 11 | Legacy module prints a voucher slip at the service desk vs "vouchers will be printed on the receipt by TillPoint" | Neither is a requirement; who prints vouchers is open decision D-02 in `context.md` |
| R-018, CAN-008 | Maker-checker above 5,000 points vs the legacy rule that also covers removals | A detail to confirm with SH-06 (CAN-008), not two positions |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| Q1 | What is Mei Tan's own position on the expiry period, as the change authority? | SH-01 Mei Tan | CF-01 |
| Q2 | Does the service or the data platform team run points expiry after go-live (D-01)? Recommended: the service (see `context.md`). | SH-01 Mei Tan | CF-01 |
| Q3 | Which fields of a points transaction count as personal data, and which of them does DRP-2024 need for audit? | SH-04 Farid Osman, with SH-03 Grace Lim | CF-02 |
