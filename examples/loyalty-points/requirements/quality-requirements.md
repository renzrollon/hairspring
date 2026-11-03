# Quality requirements: loyalty-points service and admin console

| Field | Value |
| --- | --- |
| System | loyalty-points service (REST API and event consumer) and its admin console |
| System type | web API or service (the service); internal tool (the admin console) |
| Quality model | ISO/IEC 25010:2023 product quality model (characteristic and sub-characteristic names only) |
| Walkthrough | 2026-11-03, platform-team engineer (non-interactive: no stakeholder answered), quality-requirements |
| Sources | BRIEF.md:74-77 (SH-01, SH-02, SH-03, SH-05, SH-08); S-06 (LOY-118); S-14 (PRD excerpt); `requirements/context.md` |
| Schema | requirements/schema.json |

## Walkthrough

| Characteristic | Tailoring | Decision | Reason | Requirements |
| --- | --- | --- | --- | --- |
| Functional suitability | check (service), check (console) | relevant | Points must match the earning rule and the points liability (SH-03, BRIEF.md:35); covered by functional requirements; how Finance checks correctness is Q12 | covered by R-002, R-014, R-023 |
| Performance efficiency | core (service), check (console) | relevant | "Checkout must not get slower" (SH-02, BRIEF.md:74); "show the new balance quickly" (SH-01, BRIEF.md:75); year-end peak (SH-08, BRIEF.md:76) | R-027, R-028, R-029 |
| Compatibility | core (service), check (console) | relevant | TillPoint interface spec v2.1 (S-02) is a mandate; CRM and warehouse formats are open (`context.md` question 7) | covered by `constraints-register` (TillPoint interface) |
| Interaction capability | check (service), core (console) | TBD | The member-facing screens belong to the customer mobile app (`context.md` row 4); for support agents in the admin console no concern was raised yet (Q10) | none |
| Reliability | core (service), check (console) | relevant | "Must survive the year-end sale peak" (SH-08, BRIEF.md:76); the fraud engine as a dependency (LOY-118 question 4) is Q11 | R-030 |
| Security | core (service), check (console) | relevant | "Secure" (SH-05, BRIEF.md:77): fake vouchers, member personal data; "auditable" (SH-03, BRIEF.md:77); PCI scope is Q8 | R-031, R-032, R-033 |
| Maintainability | core (service), check (console) | TBD | Bonus campaigns change earning (BRIEF.md:58); how often and who sets them up is Q9 | none |
| Flexibility | core (service), rare (console) | TBD | Member growth is SH-01's goal (BRIEF.md:33) and the legacy module is replaced (BRIEF.md:7); growth figures are Q13 | none |
| Safety | rare (service), rare (console) | not relevant | The service controls no physical process; `assumed` (non-interactive), to be confirmed by SH-08 | none |

## Quality requirements

<!-- One "###" subsection per characteristic that has requirements, in walkthrough order. Text lives in requirements.csv; this table holds the measurable parts. Do not name the first column "ID": re-lint reads Markdown tables with an ID column as requirement registers. -->

### Performance efficiency

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-027 | time behavior | Response time of a voucher validation request, server side, in ms, at a percentile | TBD ms at the TBD percentile | During the year-end sale peak; baseline today: checkout has no voucher validation, so it adds no delay (SH-02, BRIEF.md:74) | Load test of the validation call at peak rate before go-live; production monitoring of the percentile afterwards | yes | Q1 |
| R-028 | time behavior | Time from the POS purchase event to the points of that purchase in the next balance response, in seconds, at a percentile | TBD seconds at the TBD percentile | During the year-end sale peak; whether the points show as pending or in the balance is LOY-118 question 2 | Synthetic purchase event and balance probe in a test environment; production monitoring of event age | TBD | Q2 |
| R-029 | capacity | Purchase events accepted per minute, sustained | at least TBD per minute | While the year-end sale is running; baseline: last year's peak was about 9,000 purchases per minute across stores (SH-08, BRIEF.md:76) | Load test at the target rate for the sale's peak duration (TBD) before the sale | yes | Q3 |

### Reliability

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-030 | availability | Share of minutes in which purchase events and voucher validation requests succeed, in percent | at least TBD percent | While the year-end sale is running (dates TBD) | Synthetic probes against both interfaces every minute; availability report after the sale | yes | Q4 |

### Security

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-031 | authenticity | Voucher validation requests without valid TillPoint POS credentials that the service accepts | none accepted (the requirement rejects every one) | Any time; the credential mechanism is the one S-02 defines (TBD) | Negative tests and a penetration test of the validation interface before go-live | TBD | Q5 |
| R-032 | confidentiality | Member personal data shown in the admin console to a person who is not an authenticated support agent | none shown | Any time; sign-on method TBD | Access tests per role and a penetration test of the admin console | TBD | Q6 |
| R-033 | accountability | Audit trail entries for adjustments changed after they were written | none changed | For the retention period of transaction data (constraints-register) | Inspection of the audit store design; a test that tries to change an entry | yes | Q7 |

## Architecture drivers

| Requirement | Why it drives the architecture | Decisions it affects | Share with |
| --- | --- | --- | --- |
| R-027 | A synchronous call inside checkout: the target decides where voucher data is read from and whether a cache is needed (the Redis idea in S-14) | Data store and caching for vouchers; deployment close to the POS network | SH-08 Wei Jie Chua, SH-02 Arjun Pillai |
| R-028 | TBD: a target of minutes allows a plain read of the ledger; a target of seconds at peak needs a balance projection updated from events | Read model for balances; event processing path | SH-08 Wei Jie Chua |
| R-029 | Peak ingestion rate decides asynchronous intake, partitioning of events and scaling | Event consumer design; scaling on the Kubernetes platform | SH-08 Wei Jie Chua |
| R-030 | Availability during the sale needs redundancy for both interfaces and no single point of failure | Replication; deployment topology; release freeze around the sale | SH-08 Wei Jie Chua |
| R-031 | TBD: depends on the credential mechanism the TillPoint interface v2.1 defines | POS credential management | SH-05 Lena Koh, SH-09 |
| R-032 | TBD: depends on the company sign-on the admin console must use | Identity provider integration | SH-05 Lena Koh |
| R-033 | Unchangeable entries need an append-only audit store separate from correctable data | Audit store design and retention | SH-03 Grace Lim, SH-05 Lena Koh |

## Unquantified and reclassified concerns

| Concern | Source | Outcome | Routed to |
| --- | --- | --- | --- |
| "Checkout must not get slower" | SH-02, BRIEF.md:74 | quality requirement R-027 | Q1 |
| "The app should show the new balance quickly" | SH-01, BRIEF.md:75; S-06 (LOY-118) | quality requirement R-028 | Q2 |
| "Must survive the year-end sale peak" | SH-08, BRIEF.md:76 | quality requirements R-029 (capacity) and R-030 (availability) | Q3, Q4 |
| "Secure" | SH-05, BRIEF.md:77 | quality requirements R-031, R-032; staying outside PCI scope may be a mandate | Q5, Q6; Q8 to `constraints-register` |
| "Auditable" | SH-03, BRIEF.md:77 | function: record who adjusted points, when, why and who approved | `requirement-phrasing` (Type F); the quality part is R-033 |
| "Keep issued vouchers in a Redis cluster so the POS gets an answer fast" | S-14 (inputs/prd-redeem-at-checkout.md:19) | design decision | SH-08 Wei Jie Chua (ADR candidate); the quality behind it is R-027 |
| "Use Redis to cache balances" | S-06 (LOY-118) | design decision | SH-08 Wei Jie Chua (ADR candidate); the quality behind it is R-028 |
| "The redemption screen should be easy to use" | S-14 (inputs/prd-redeem-at-checkout.md:18) | not measurable yet; belongs to the customer mobile app | `classification.md` open question 1 (SH-01) |

## Open questions

| # | Question | Recommended answer | Owner | Affects | Status |
| --- | --- | --- | --- | --- | --- |
| Q1 | How many milliseconds may a voucher validation take, at which percentile, during the peak? | Start from the POS timeout in the TillPoint interface spec (S-02) and today's checkout time; no number without them | SH-02 Arjun Pillai | R-027 | open |
| Q2 | How many seconds after the purchase may the points take to appear in the app, at which percentile? | No recommendation: needs a business value (same as LOY-118 question 6) | SH-01 Mei Tan | R-028 | open |
| Q3 | How many purchase events per minute must the service accept during this year's sale, and for how long? | Last year's peak (about 9,000 per minute) plus the growth Finance or Marketing expect; the platform team confirms | SH-08 Wei Jie Chua | R-029 | open |
| Q4 | Which availability must purchase events and voucher validation reach during the sale, and when does the sale run? | No recommendation: needs a business value | SH-08 Wei Jie Chua | R-030 | open |
| Q5 | Which credentials does the TillPoint interface v2.1 define for POS terminals? | Look it up in S-02 | SH-05 Lena Koh, with SH-09 | R-031 | open |
| Q6 | Which company sign-on must support agents use for the admin console? | Ask the security architect for the company standard | SH-05 Lena Koh | R-032 | open |
| Q7 | Who reads the adjustment audit trail, and is it kept as long as transaction data? | Ask Finance; retention follows the transaction-data constraint | SH-03 Grace Lim | R-033 | open |
| Q8 | Must the service stay outside PCI DSS scope, and which written policy says so? | Ask the security architect; it becomes a constraint only with a named mandate | SH-05 Lena Koh | Security | open |
| Q9 | How often does Marketing change bonus campaigns, and must a campaign go live without a release? | Ask Marketing | SH-07 Priya Raman | Maintainability | open |
| Q10 | Which mistake by a support agent in the admin console would hurt most? | Ask the support lead; a wrong adjustment changes the points liability | SH-06 Daniel Ng | Interaction capability | open |
| Q11 | What must the service do when the fraud engine does not answer (LOY-118 question 4)? | Keep the points pending (the most restrictive option) | SH-05 Lena Koh | Reliability | open |
| Q12 | How does Finance check that points per purchase and the points liability are right? | Ask Finance | SH-03 Grace Lim | Functional suitability | open |
| Q13 | How many members does the programme expect in the next years? | Ask the product owner | SH-01 Mei Tan | Flexibility | open |

## Planguage specifications

Not used.
