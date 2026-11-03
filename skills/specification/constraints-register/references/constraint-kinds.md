# Constraint kinds and the mandate test

## The five categories

| Category | Restricts | Typical mandators | Loyalty-points illustration |
| --- | --- | --- | --- |
| `technical` | Platforms, runtimes, interfaces, protocols, hardware, existing systems the solution must use or fit | Platform or enterprise architecture team, vendors of connected systems, customers' IT | Run on the shared Kubernetes platform; exchange purchase events through the TillPoint POS loyalty interface spec v2.1 (S-02) |
| `legal` | What the law, a regulation, an industry standard the organization is bound to, a contract or a licence allows or demands | Regulators, the data protection officer, legal, Finance (statutory retention), contract owners | Keep personal data in Singapore (DRP-2024, S-05); keep transaction records for the retention period; stay outside the PCI DSS cardholder data environment |
| `organizational` | Dates, budgets, staffing, mandated processes, tools, suppliers, organizational policies | Management, procurement, Finance, PMO, a steering committee | Take over from the legacy module before its contract ends; use the company's change process for releases |
| `cultural` | Conventions and norms of the people who use or are affected by the system: language, script, naming, calendars, formats | Marketing, brand owners, regional management, user representatives | Member communications in the languages the brand guideline names; dates in the local format |
| `environmental` | The physical and operating environment: location, climate, network, power, noise, devices in the field | Store operations, facilities, the hardware vendor | Store network links that can drop; tills that cannot run additional software |

Illustrations are on the sample project; they become constraints only when the named mandator confirms them.

## The mandate test on worked cases

| Statement | 1. Restricts how? | 2. Outside mandator? | 3. Team cannot change it? | Outcome |
| --- | --- | --- | --- | --- |
| "Every new service runs on the shared Kubernetes platform" (SH-08, platform standard) | yes (platform) | yes (platform team) | yes | constraint, `technical` |
| "Member personal data must stay in Singapore" (SH-04, DRP-2024) | yes (location) | yes (data protection officer, policy S-05) | yes | constraint, `legal` |
| "The legacy contract ends 2027-03-31; we will not extend it" (SH-03) | yes (date) | yes (Finance, contract) | yes | constraint, `organizational` |
| "Use Kafka between the POS and the service" (team discussion) | yes | no mandator named | n/a | design decision: ADR candidate; ask whether the platform standard mandates it |
| "We'll write it in Go" (loyalty squad) | yes | no (the team itself) | n/a | design decision: ADR candidate |
| "Voucher validation must not slow down checkout" (SH-02) | no: how well, not how | n/a | n/a | quality requirement: `quality-requirements` |
| "Every adjustment records who, when and why" (SH-03) | no: what it does | n/a | n/a | function: `requirement-phrasing` |
| "The POS will be upgraded to TillPoint v2.2 in March" (vendor) | no: a fact about another system | n/a | n/a | fact: context. It may set the `Review by` of the interface constraint |
| "Legal says we must keep logs" (no document, no person) | yes | unknown | unknown | unconfirmed: ask "Who in Legal, which policy, for how long?"; write no row yet |

## Phrasing

- `The <system> shall <restriction>.`: "The loyalty service shall store member personal data only in data centers located in Singapore."
- Put the reason in `Rationale` and the mandate in `Mandated by` / `Mandate reference`, not in the sentence.
- Name versions only when the mandate names them ("TillPoint POS loyalty interface spec v2.1", not "the latest spec").
- One restriction per row. "Must run on Kubernetes in the Singapore region" is two constraints with possibly two mandators.
- A negative constraint is fine when it is the mandate: "The loyalty service shall stay outside the PCI DSS cardholder data environment."

## Dates

| Column | Rule |
| --- | --- |
| `Expires` | Only a date or event the mandator stated. `none` means the mandator said it does not lapse; unknown is `TBD` |
| `Review by` | When to ask the mandator whether the constraint still holds. Use a stated date, a stated event ("before the v2.2 upgrade"; give the date if the event has one), or `TBD` |
| Overdue | `Review by` earlier than today: report *review overdue*. `Expires` earlier than today: report *expired* and ask the owner whether to withdraw the row |
| Format | ISO 8601 (`2026-12-31`) |

## Constraint, design decision, ADR

A design decision is recorded as an architecture decision record (ADR) by the team that made it, in the ADR folder the repository uses (`docs/adr/` or the folders in `schema.json` → `trace.adr_dirs`). If a design decision later becomes mandated (the platform team publishes a standard), it becomes a constraint with that standard as its mandate reference, and the ADR links to the constraint's R-ID.
