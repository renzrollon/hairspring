# Tailoring by system type

Characteristic names follow the ISO/IEC 25010:2023 product quality model (names only; read the standard for definitions). The levels are re-skills guidance for where quality requirements usually come from, not a rule of the standard:

- `core`: walk it with the screening questions; it usually yields requirements and often architecture drivers.
- `check`: ask one screening question; write requirements only if the answer raises a concern.
- `rare`: record "not relevant" with the reason unless the input raises a concern; any stated concern makes it `core`.

## Tailoring table

| Characteristic | Web API or service | Mobile app | Batch or data pipeline | Embedded | Internal tool |
| --- | --- | --- | --- | --- | --- |
| Functional suitability | check | check | core | core | check |
| Performance efficiency | core | core | core | core | check |
| Compatibility | core | check | core | check | check |
| Interaction capability | check | core | rare | check | core |
| Reliability | core | check | core | core | check |
| Security | core | core | core | check | check |
| Maintainability | core | check | check | core | check |
| Flexibility | core | core | check | check | rare |
| Safety | rare | rare | rare | core | rare |

Where the levels usually come from:

| Type | Typical drivers |
| --- | --- |
| Web API or service | Response time and capacity at peak, availability, fault tolerance toward dependencies, authentication of callers, interoperability with partner systems, scaling with load |
| Mobile app | Response time on a mobile network, resource use (battery, data, storage), interaction capability and inclusivity, confidentiality of data on the device, adaptability to OS versions and screen sizes, installability through the stores |
| Batch or data pipeline | Correctness and completeness of data, throughput inside the batch window, recoverability (rerun, restart from a checkpoint), interoperability of formats, confidentiality and integrity of data in transit and at rest |
| Embedded | Timing deadlines and resource limits, fault tolerance, safety where the device can harm people or property, modifiability across hardware variants, firmware installability |
| Internal tool | Learnability and operability for a small known group, user error protection, accountability of actions, integration with company sign-on |

## Screening questions

Ask the stakeholder who owns the concern. Use the probes in `re-interview/references/question-craft.md` ("What number would make you say it is too slow?", "And when it goes wrong?").

| Characteristic | Screening question | Loyalty-points example |
| --- | --- | --- |
| Functional suitability | Is there a calculation or a data set that must be exactly right, and how would you notice an error? | Points per purchase must match the earn rule; Finance reconciles them |
| Performance efficiency | Which operation is someone waiting for, and at what load is it worst? | Voucher validation while the cashier waits; the year-end sale peak |
| Compatibility | Which systems must exchange data with it, and who defines the format? | TillPoint POS interface spec v2.1 (S-02); nightly CRM feed |
| Interaction capability | Who uses it, how often, with how much training, and what mistake would hurt most? | Support agents adjusting points; a wrong adjustment changes the points liability |
| Reliability | What happens to the business when it is down for an hour at the worst time? What must never be lost? | A sale must never be blocked; no points transaction may be lost |
| Security | Which data or actions would hurt if seen, changed or faked, and by whom? | Member personal data; fake vouchers; adjustments without a trace |
| Maintainability | What will change most often after go-live, and who makes the change? | Marketing launches a bonus campaign almost every month |
| Flexibility | Will it need to run with more load, on other platforms, or replace something? | Member growth; replacing the legacy loyalty module |
| Safety | Can a failure harm a person, property or the environment? | No: the service controls no physical process |

## When a concern does not fit one characteristic

Write one requirement per sub-characteristic. "Must survive the peak" is usually capacity (performance efficiency) plus availability (reliability); "secure" is usually authenticity, confidentiality and integrity (security). Ask which failure the person had in mind, then write one requirement for each.
