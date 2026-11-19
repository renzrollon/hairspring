# Expected output: constraint candidates for the loyalty-points service

## Mandate test

| # | Statement | Restricts how? | Outside mandator | Outcome | Requirement |
| --- | --- | --- | --- | --- | --- |
| 1 | TillPoint loyalty interface v2.1 | yes (interface) | POS vendor TillPoint (SH-09) | constraint, technical | R-100 |
| 2 | PCI out of scope | yes (data the service may handle) | Security architecture (SH-05), based on PCI DSS | constraint, legal | R-101 |
| 3 | Transaction data kept 7 years | yes (retention) | Finance (SH-03) under DRP-2024 (S-05) | constraint, legal | R-102 |
| 4 | Personal data stays in Singapore | yes (location) | Data protection officer (SH-04), DRP-2024 (S-05) | constraint, legal | R-103 |
| 5 | Shared Kubernetes platform | yes (platform) | Platform team standard (SH-08) | constraint, technical | R-104 |
| 6 | Legacy contract ends 2027-03-31 | yes (date) | Finance (SH-03), vendor contract | constraint, organizational | R-105 |
| 7 | Use Kafka between the POS and the service | yes | none named | unconfirmed: design decision unless a mandator is named | none |
| 8 | Write the service in Go | yes | none (the squad's own choice) | design decision | none |
| 9 | Voucher validation must not slow down checkout | no: how well, not how | n/a | quality requirement | covered by R-080 (`quality-requirements`) |

Rows written: `requirements/requirements.csv` (see `expected-requirements.csv`) and `requirements/constraints.csv` (see `expected-output.csv`), one row each for R-100 to R-105.

## ADR candidates (no requirement rows)

| Statement | Why it is not a constraint | Next |
| --- | --- | --- |
| "Use Kafka between the POS and the service" | Nobody outside the squad mandates it | Ask SH-08: "Does the platform standard mandate an event transport?" If yes, it becomes a constraint citing that standard; if no, record an ADR |
| "We'll write the service in Go" | The squad can change it alone | Record an ADR in `docs/adr/` |

## Hand-offs

- `conflict-detector`: R-102 (keep transaction records 7 years) against the data-minimization concern of the data protection officer (SH-04, S-05). Subject-matter conflict between retention and privacy.
- `source-inventory`: register the legacy loyalty module vendor contract (R-105) and the written platform standard (R-104) and security policy (R-101) once located.
- Review dates: none overdue on 2026-11-03; R-104 is due for review on 2026-12-31.

## Open questions

| Requirement | Question | Owner |
| --- | --- | --- |
| R-100 | When does TillPoint v2.2 go live, and does v2.1 stay supported after the upgrade? | SH-09 |
| R-101 | Which written security policy states this rule, does it have an end or review date, and can it be waived? | SH-05 Lena Koh |
| R-102 | Do the 7 years count from the transaction date or from the end of the financial year, and when is DRP-2024 next reviewed or replaced? | SH-03 Grace Lim |
| R-103 | Does the rule also cover backups and copies held by the notification provider, can the DPO grant exceptions, and when is DRP-2024 next reviewed or replaced? | SH-04 Farid Osman |
| R-104 | Where is the platform standard written down, does it continue after 2026, and what happens to a service that does not comply? | SH-08 Wei Jie Chua |
| R-105 | What is the go/no-go date for the cut-over, and can the contract be registered as a source? | SH-03 Grace Lim |
| statement 7 (Kafka) | Does the platform standard mandate an event transport such as Kafka? | SH-08 Wei Jie Chua |

## Lint

`re-lint check --only-ids R-100,R-101,R-102,R-103,R-104,R-105`: 0 errors.
