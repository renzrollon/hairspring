# Quality requirements: loyalty-points service

| Field | Value |
| --- | --- |
| System | loyalty-points service (REST API and event consumer); the admin console is checked as an internal tool |
| System type | web API or service; internal tool (admin console) |
| Quality model | ISO/IEC 25010:2023 product quality model (characteristic and sub-characteristic names only) |
| Walkthrough | 2026-11-03, Mei Tan (SH-01), Arjun Pillai (SH-02), Lena Koh (SH-05), Wei Jie Chua (SH-08); Grace Lim (SH-03) by email 2026-11-02; quality-requirements |
| Sources | S-06 (I-01), S-07 (I-02), session notes 2026-11-03, SH-03 email 2026-11-02 |
| Schema | requirements/schema.json |

## Walkthrough

| Characteristic | Tailoring | Decision | Reason | Requirements |
| --- | --- | --- | --- | --- |
| Functional suitability | check | relevant | Earn and redemption rules must be exact; Finance reconciles every transaction (SH-08) | covered by functional requirements R-001 to R-079 and their acceptance criteria |
| Performance efficiency | core | relevant | Voucher validation is a new call in the checkout path (SH-02); balance visibility (SH-01); year-end peak (SH-08) | R-080, R-081, R-082 |
| Compatibility | core | relevant | TillPoint interface v2.1 is mandated by the vendor (SH-08) | covered by a constraint, routed to constraints-register |
| Interaction capability | check (service); core (admin console) | TBD | Support lead (SH-06) not present; admin console questions open | none yet; Q9 |
| Reliability | core | relevant | "A sale is never blocked by loyalty" (SH-02); no lost transactions (SH-08); fraud engine outages (SH-05) | R-083, R-084, R-085 |
| Security | core | relevant | Authentication, encryption on the wire (SH-05); adjustment records cannot be edited (SH-03) | R-086, R-087, R-088 |
| Maintainability | core | relevant | Monthly campaigns each need a release today (SH-01 for SH-07) | R-089 |
| Flexibility | core | relevant | Growth in load is part of the capacity question Q3; no other platform or replacement concern raised | covered by R-082 |
| Safety | rare | not relevant | No physical process or hardware is controlled (SH-08, 2026-11-03) | none |

## Quality requirements

### Performance efficiency

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-080 | time behaviour | Server-side response time of voucher validation, 95th percentile (SH-08 reporting convention), ms | TBD | At the planned peak load of R-082 | Load test with the year-end peak profile before each release; daily p95 from production monitoring at the API gateway | yes | Q1 |
| R-081 | time behaviour | Seconds from recording a points transaction to its first appearance in the app's points history | TBD | At the planned peak load of R-082 | Scheduled synthetic end-to-end test; event-to-visible lag from production monitoring | TBD | Q2 |
| R-082 | capacity | Purchase events accepted per minute, sustained; lost events | TBD events per minute for TBD minutes; zero lost events | Year-end sale peak, all stores; baseline: 9,000 purchases per minute at last year's peak (SH-08) | Load test replaying a peak-day profile; intake rate and consumer lag during the sale | yes | Q3 |

### Reliability

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-083 | availability | Share of synthetic probe checks of earn and voucher validation that succeed, per calendar month | TBD % | Store trading hours (TBD); announced maintenance excluded | Synthetic probes from a store network; monthly availability report | yes | Q4 |
| R-084 | fault tolerance | Share of earn events accepted while the fraud engine is unavailable | All earn events accepted (SH-05) | Fraud engine unavailable for up to TBD hours | Fault-injection test blocking the fraud engine during a load test | yes | Q5 |
| R-085 | recoverability | Minutes from a failure to resumed processing; recorded points transactions lost | TBD minutes; zero lost transactions (SH-08) | Any failure that stops processing; whether a site-wide outage is included is TBD | Recovery drill in a test environment with timed restore and reconciliation against POS events | yes | Q6 |

### Security

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-086 | authenticity | API requests accepted without valid client credentials | None accepted (SH-05) | POS and customer mobile app endpoints, every environment reachable from stores or the internet | Automated negative tests in the pipeline; penetration test before go-live | yes | none |
| R-087 | confidentiality | Interfaces carrying member personal data without transport encryption | None (SH-05); minimum protocol version TBD | The six interfaces in context.md | Inspection of interface configuration; endpoint scan before go-live | no | Q7 |
| R-088 | integrity | Change or delete paths open to support console agents on points adjustment records | None (SH-03) | Admin console and API, every support role | Permission inspection; negative tests with a support agent account | no | none |

### Maintainability

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-089 | modifiability | Software releases needed to launch a campaign that uses an existing multiplier rule; lead time from request to live campaign | No release (SH-01 for SH-07); lead time TBD days | Campaigns using an existing multiplier rule; new rule types excluded | Demonstration by a marketing user in a test environment; lead time tracked per campaign | yes | Q8 |

## Architecture drivers

| Requirement | Why it drives the architecture | Decisions it affects | Share with |
| --- | --- | --- | --- |
| R-080 | A synchronous call inside checkout; the target bounds every hop on the validation path | Voucher validation path, caching, timeouts toward the POS | SH-08 Wei Jie Chua, SH-09 TillPoint |
| R-081 | Depends on Q2: a short target forces synchronous propagation to the app; a longer one allows event-driven updates | Balance read model, event pipeline | SH-08 |
| R-082 | Peak intake decides partitioning and back-pressure of the event consumer | Event intake, scaling, queueing | SH-08 |
| R-083 | The availability target decides redundancy across nodes or zones | Deployment topology, failover | SH-08 |
| R-084 | Earning without the fraud engine needs asynchronous scoring and a pending-scoring state | Fraud integration, PointsTransaction states | SH-05 Lena Koh, SH-08 |
| R-085 | Zero lost transactions decides durable writes and replication of the transaction store | Data store, replication, backup | SH-08, SH-03 Grace Lim |
| R-086 | Credentials for 140 stores' tills and the app need an identity and credential-distribution design | Identity provider, credential rotation | SH-05 |
| R-089 | Campaign set-up without a release needs a configurable rule model | Campaign rule engine, admin console | SH-08, SH-07 Priya Raman |

## Unquantified and reclassified concerns

| Concern | Source | Outcome | Routed to |
| --- | --- | --- | --- |
| "Checkout must not get slower." | SH-02, S-07 | Quality requirement R-080; target unknown | Q1 |
| "Auditable: every manual adjustment shows who did it, when and why" | SH-03 email 2026-11-02 | Function: an adjustment record with agent, timestamp and reason code | `requirement-phrasing` |
| "... and nobody can edit that afterwards" | SH-03 email 2026-11-02 | Quality requirement R-088 (integrity) | none |
| "We keep transaction data 7 years (DRP-2024)" | SH-03 email 2026-11-02, S-05 | Constraint (retention mandated by policy) | `constraints-register` |
| "If loyalty is down, the till must still sell." | SH-02, 2026-11-03 | Function of the POS integration: an unwanted-behavior requirement on the POS side, timeout tied to Q1 | `requirement-phrasing`; SH-09 TillPoint |
| "We have to integrate through the TillPoint loyalty interface v2.1" | SH-08, 2026-11-03, S-02 | Constraint (mandated by the POS vendor) | `constraints-register` |
| "PCI is out of scope because we never see card numbers." | SH-05, 2026-11-03 | Constraint (keep the service outside the cardholder data environment) | `constraints-register` |

## Open questions

| # | Question | Recommended answer | Owner | Affects | Status |
| --- | --- | --- | --- | --- | --- |
| Q1 | What 95th-percentile voucher validation time can the till absorb without checkout getting slower? | Set it below the POS timeout in the TillPoint spec (S-02) minus the store network round trip; measure today's checkout time first | SH-02 Arjun Pillai with SH-09 | R-080 | open |
| Q2 | How many seconds after a purchase must the transaction show in the app's points history? | Ask what members do right after paying; check support tickets about missing points (S-03) | SH-01 Mei Tan | R-081 | open |
| Q3 | What purchase-event rate must we plan for at this year's year-end peak, and how long does the peak last? | Last year's 9,000 per minute (SH-08) plus the growth Marketing plans | SH-08 Wei Jie Chua with SH-07 Priya Raman | R-080, R-081, R-082 | open |
| Q4 | What monthly availability is needed, and what are the store trading hours (are some stores open around the clock)? | Store operations' trading hours; the cost of a lost earn event | SH-02 Arjun Pillai with SH-08 | R-083 | open |
| Q5 | How long may earning continue without fraud scoring before it must stop or be escalated? | The fraud analyst's review window | SH-05 Lena Koh | R-084 | open |
| Q6 | How many minutes may processing stop after a failure, and must a site-wide outage be covered? | Finance's month-end and reconciliation deadlines | SH-03 Grace Lim with SH-08 | R-085 | open |
| Q7 | Which minimum transport encryption protocol version does the security standard require? | The company security standard | SH-05 Lena Koh | R-087 | open |
| Q8 | How many days may pass between a campaign request and the campaign going live? | Marketing's campaign planning calendar | SH-07 Priya Raman | R-089 | open |
| Q9 | Are there time or training targets for support agents using the admin console? | The current onboarding time for new agents | SH-06 Daniel Ng | Interaction capability | open |

## Planguage specifications

Not used.
