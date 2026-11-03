# Sample project: Harbourline Rewards (loyalty-points service)

Every skill example and eval in `re-skills` uses this fictional project, so outputs can be compared across skills and chained end to end. All names are invented. Numbers below are facts *of the sample project*, not recommendations.

## The organization and the change

**Harbourline** is a fictional grocery and convenience chain in Singapore with 140 stores and a mobile app with about 600,000 registered members. Today points are earned with a plastic card and a 15-year-old on-prem loyalty module inside the POS vendor's back office. The company is replacing it with a **loyalty-points service** run by its own platform team: members earn points at the POS and in the app, see their balance in the app, and redeem points as vouchers at checkout.

## System under development

`loyalty-points` service (REST API + event consumer) and its admin console.

## Context (for `system-context`)

| External element | Kind | Interface / data flow |
| --- | --- | --- |
| Customer (member) | person | Mobile app: view balance, history, redeem voucher |
| Cashier | person | POS: scan member QR, apply voucher |
| POS system (vendor: "TillPoint", fictional) | system | POS → service: purchase events (earn); service → POS: voucher validation |
| Customer mobile app | system | App → service: balance, history, redemption |
| CRM ("Relay CRM", fictional) | system | Service → CRM: member tier and points summary, nightly |
| Fraud engine | system | Service → fraud engine: earn/redeem events for scoring; fraud engine → service: hold/release |
| Notification provider (SMS + push) | system | Service → provider: points earned, points expiring |
| Data warehouse | system | Service → warehouse: daily extract for finance (points liability) |
| Support console agents | person | Admin console: look up member, adjust points with reason |
| Grey zone | | **Points-expiry batch job**: in or out of scope? (owned today by the data platform team) → decision `D-01` |
| Grey zone | | **Voucher printing at the POS**: POS vendor or us? → decision `D-02` |

## Stakeholders (for `stakeholder-map`)

| ID | Role | Name (fictional) | Interest |
| --- | --- | --- | --- |
| SH-01 | Head of Loyalty (product owner) | Mei Tan | Programme rules, member growth |
| SH-02 | Store operations lead | Arjun Pillai | Checkout speed, cashier training |
| SH-03 | Finance controller | Grace Lim | Points liability accounting, month-end |
| SH-04 | Data protection officer | Farid Osman | PDPA compliance, retention |
| SH-05 | Security architect | Lena Koh | Fraud, authentication, PCI scope |
| SH-06 | Customer support lead | Daniel Ng | Lookups, adjustments, complaint volume |
| SH-07 | Marketing manager | Priya Raman | Campaigns, bonus-point promotions |
| SH-08 | Platform team tech lead | Wei Jie Chua | Operability, cost, Kubernetes platform |
| SH-09 | POS vendor integration manager | (vendor) | Interface changes, release windows |
| Gap | Fraud analyst | not yet named | Typically missed; surfaces in the gap check |

## Sources (for `source-inventory`, `artifact-mining`)

| ID | Source | Kind |
| --- | --- | --- |
| S-01 | Harbourline Rewards programme terms and conditions, draft v3 | document |
| S-02 | TillPoint POS loyalty interface spec v2.1 (purchase event JSON, voucher validation call) | document |
| S-03 | Support ticket export, last 6 months (loyalty category, 1,240 tickets) | document |
| S-04 | Legacy loyalty module: stored procedures and nightly batch scripts | system |
| S-05 | Singapore PDPA and the company's data retention policy DRP-2024 | document (regulation) |
| S-06 | Mei Tan (SH-01), kick-off interview I-01 | stakeholder |
| S-07 | Arjun Pillai (SH-02), store visit and interview I-02 | stakeholder |

## Business rules (facts of the sample)

- Members earn 1 point per SGD 1 spent, rounded down per transaction; bonus campaigns can multiply this.
- Points become available 24 hours after purchase (return window), then are **posted**.
- Points expire 12 months after posting (S-01 draft; Finance wants this, Marketing would like 18 months: a real conflict).
- 100 points = SGD 1 voucher; minimum redemption 500 points.
- Returns reverse the points of the original transaction; if already redeemed, the balance may go negative (open question).
- Support can adjust points with a mandatory reason code; adjustments above 5,000 points need a second approver (maker-checker).
- Transaction data must be kept 7 years for audit (Finance, S-05 policy), while PDPA requires personal data not be kept longer than needed (DPO): a subject-matter conflict.

## Entities and states (for `domain-model`, `state-model`)

- Entities: Member, Card/QR token, Purchase, PointsTransaction, Voucher, Campaign, Adjustment, Tier.
- `PointsTransaction` states: Pending → Posted → (Redeemed | Expired | Reversed). Pending → Reversed on return within 24 h.
- `Voucher` states: Issued → Applied | Expired | Cancelled.

## Quality concerns raised so far (for `quality-requirements`)

- "Checkout must not get slower" (SH-02): today voucher validation adds no delay because there is none.
- "The app should show the new balance quickly" (SH-01).
- "Must survive the year-end sale peak" (SH-08): last year's peak was about 9,000 purchases per minute across stores.
- "Secure" (SH-05), "auditable" (SH-03).

## Requirement ID ranges used in skill examples

Skill examples are independent snapshots; use any free IDs, but prefer these ranges so examples read as one project:

| Range | Area |
| --- | --- |
| R-001 to R-019 | Earning points |
| R-020 to R-039 | Balance and history |
| R-040 to R-059 | Redemption and vouchers |
| R-060 to R-079 | Expiry, reversal, adjustments |
| R-080 to R-099 | Quality requirements |
| R-100 to R-119 | Constraints |
