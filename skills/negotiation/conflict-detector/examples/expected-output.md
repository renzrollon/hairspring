# Conflict register

<!-- Owned by conflict-detector. conflict-to-decision updates the Status and Decision columns and the Status line of a detail block. Never delete an entry: set Status to not-a-conflict with the reason. -->

| Field | Value |
| --- | --- |
| Last scan | 2026-11-03 |
| Scanned | requirements/requirements.csv (10 requirements; withdrawn and rejected skipped), refinement notes 2026-10-30, requirements/stakeholders.md |
| Schema | requirements/schema.json |

## Register

| ID | Subject | Kind | Requirements | Stakeholders | Type | Recommended technique | Route | Status | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CF-01 | Points expiry period | contradiction | R-060, R-061 | SH-03, SH-07 | interest | compromise or variants; aid: decision matrix | /conflict-to-decision CF-01 | open | |
| CF-02 | Retention of transaction records vs deletion of personal data | contradiction | R-100, R-101 | SH-03, SH-04 | subject matter | variants or agreement; aid: consider-all-facts | /conflict-to-decision CF-02 | open | |
| CF-03 | Redemption minimum boundary | inconsistent conditions | R-041, R-045 | SH-01, SH-07 | data | agreement; aid: consider-all-facts | /conflict-to-decision CF-03 | open | |
| CF-04 | Points adjustments by support agents | differing level of detail | R-064, R-065 | SH-06, SH-01 | data | agreement; aid: consider-all-facts | /conflict-to-decision CF-04 | open | |
| CF-05 | Manual member-number entry at the POS | priority disagreement | R-008 | SH-02, SH-05 | interest | compromise or variants; aid: plus-minus-interesting | /conflict-to-decision CF-05 | open | |

Kind: `contradiction` | `overlap` | `inconsistent conditions` | `differing level of detail` | `priority disagreement`.
Type: `subject matter` | `data` | `interest` | `value` | `relationship` | `structural`.
Technique: `agreement` | `compromise` | `voting` | `variants` | `overruling` | `none (escalation)`.
Aid: `consider-all-facts` | `plus-minus-interesting` | `decision matrix` | `none`.
Status: `open` | `escalated` | `resolved` | `not-a-conflict`. Decision: `RDR-nnn`, or the escalation outcome and date.

## CF-01: Points expiry period

- **Kind:** contradiction
- **Requirements:** R-060 "expire posted points 12 months after posting" (Source: S-01) vs R-061 "expire posted points 18 months after posting" (Source: SH-07 Priya Raman 2026-10-29)
- **Positions:**
  - SH-03 Grace Lim (Finance controller): 12 months, to limit the points liability (R-060 Rationale; S-01 draft v3)
  - SH-07 Priya Raman (Marketing manager): 18 months, so occasional shoppers reach the redemption minimum (R-061)
- **Why it is a conflict:** posted points can have only one expiry period for the same member population.
- **Type:** interest, because each side protects its own target (liability vs engagement) and the facts are not in dispute.
- **Recommended technique:** compromise or variants (for example, a period per tier), because the disagreement is on a scale and the system could serve more than one period. Analysis aid: decision matrix, with weights agreed before scoring.
- **Route:** /conflict-to-decision CF-01; decision-makers: SH-01 Mei Tan (product owner, change authority), with SH-03 and SH-07 consulted
- **Open questions:** none
- **Status:** open

## CF-02: Retention of transaction records vs deletion of personal data

- **Kind:** contradiction
- **Requirements:** R-100 "retain points transaction records for 7 years after the transaction date" (Source: S-05 DRP-2024) vs R-101 "delete the member's personal data within 30 days" of account closure (Source: S-05 PDPA, SH-04 Farid Osman 2026-10-31)
- **Positions:**
  - SH-03 Grace Lim (Finance controller): transaction records kept 7 years for audit (R-100 Rationale)
  - SH-04 Farid Osman (Data protection officer): personal data deleted 30 days after closure (R-101)
- **Why it is a conflict:** points transaction records carry the member ID, so a closed member's records cannot both be kept 7 years and have their personal data deleted within 30 days.
- **Type:** subject matter, because two obligations (audit policy and data protection) collide on the same data and nobody disputes the facts.
- **Recommended technique:** variants (for example, records kept without direct identifiers after closure) or agreement, because both obligations may be met by changing what is kept, not how long. Analysis aid: consider-all-facts, listing what audit needs from a record and what counts as personal data.
- **Route:** /conflict-to-decision CF-02; decision-makers: SH-01 Mei Tan with SH-03 and SH-04; legal counsel TBD
- **Open questions:** Who represents legal counsel for this decision? (owner: SH-01)
- **Status:** open

## CF-03: Redemption minimum boundary

- **Kind:** inconsistent conditions
- **Requirements:** R-041 rejects requests "with fewer than 500 posted points" (Source: S-01) vs R-045 shows the Redeem button "when a member has more than 500 posted points" (Source: SH-07 Priya Raman 2026-10-29)
- **Positions:**
  - SH-01 Mei Tan (product owner, owner of S-01): minimum redemption is 500 points (programme terms)
  - SH-07 Priya Raman (Marketing manager): Redeem button above 500 points (R-045)
- **Why it is a conflict:** a member with exactly 500 posted points may redeem under R-041 but sees no Redeem button under R-045.
- **Type:** data, because R-045 most likely misreads the minimum in S-01; checking the source settles it.
- **Recommended technique:** agreement, after checking S-01 together. Analysis aid: consider-all-facts.
- **Route:** /conflict-to-decision CF-03; decision-makers: SH-01 Mei Tan; a short decision record is enough
- **Open questions:** Should the Redeem button show at exactly 500 posted points? Recommended answer: yes, matching S-01. (owner: SH-07)
- **Status:** open

## CF-04: Points adjustments by support agents

- **Kind:** differing level of detail
- **Requirements:** R-064 "let support agents adjust a member's points with a reason code" in the "support console" (Source: S-03) vs R-065 second approver "above 5,000 points" in the "admin console" (Source: S-01)
- **Positions:**
  - SH-06 Daniel Ng (Customer support lead): adjustments as a support tool (S-03 tickets); position on the approval step not recorded
  - SH-01 Mei Tan (product owner, owner of S-01): maker-checker above 5,000 points
- **Why it is a conflict:** read on its own, R-064 lets one agent post any adjustment; R-065 forbids that above 5,000 points, and the two rows name different consoles for what is probably one system.
- **Type:** data, because the gap is missing information (the approval rule and the console name), not a disagreement anyone has stated.
- **Recommended technique:** agreement, after confirming with SH-06. Analysis aid: consider-all-facts.
- **Route:** /conflict-to-decision CF-04; decision-makers: SH-01 Mei Tan with SH-06 consulted
- **Open questions:** Does support expect adjustments above 5,000 points to post without a second approver? Recommended answer: no, R-065 applies. (owner: SH-06). Are "support console" and "admin console" the same system? (owner: SH-08; also raise to `glossary`)
- **Status:** open

## CF-05: Manual member-number entry at the POS

- **Kind:** priority disagreement
- **Requirements:** R-008 "let the cashier enter the member number manually" (Source: I-02, SH-02 Arjun Pillai 2026-10-30)
- **Positions:**
  - SH-02 Arjun Pillai (Store operations lead): `must`, queues build up when the QR scan fails (refinement notes 2026-10-30)
  - SH-05 Lena Koh (Security architect): `wont`, typed member numbers let staff earn points on other members' purchases (refinement notes 2026-10-30)
- **Why it is a conflict:** the requirement cannot be both a must-have and excluded from the release.
- **Type:** interest, because checkout speed and fraud exposure are each side's own goal; neither disputes the other's facts.
- **Recommended technique:** compromise or variants, because a fallback with extra checks may serve both goals. Analysis aid: plus-minus-interesting per option.
- **Route:** /conflict-to-decision CF-05; decision-makers: SH-01 Mei Tan with SH-02 and SH-05 consulted
- **Open questions:** none
- **Status:** open

## Checked, not a conflict

| Requirements | Looked like | Why not a conflict |
| --- | --- | --- |
| R-060, R-100 | Two retention periods (12 months, 7 years) | Different subjects: validity of points vs retention of transaction records |
| R-020, R-045 | Two balance screens | R-020 shows the balance; R-045 adds a button; no overlap in behavior |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | Who represents legal counsel for the retention decision? | SH-01 Mei Tan | CF-02 |
| 2 | Should the Redeem button show at exactly 500 posted points? Recommended: yes, matching S-01. | SH-07 Priya Raman | CF-03 |
| 3 | Do adjustments above 5,000 points post without a second approver today, and should they? Recommended: no. | SH-06 Daniel Ng | CF-04 |
| 4 | Are "support console" and "admin console" one system? | SH-08 Wei Jie Chua | CF-04, glossary |
