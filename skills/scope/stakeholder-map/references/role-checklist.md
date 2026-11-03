# Role checklist for the gap check

Check every role in the first table. Check a role in the second table when its trigger applies to the system. A role is covered only when a row with a named representative (or a named proxy) speaks for it.

## Always check

| Role | Why it matters | Typical requirements from them |
| --- | --- | --- |
| Sponsor or budget owner | Decides whether the system is worth its cost | Goals, scope limits, deadlines |
| Product owner or requirements decision-maker | Agrees requirements and priorities | Priorities, acceptance |
| End users, one row per user group and channel | They use it; each group has different needs | Tasks, usability, error cases |
| Operations or run team | Keeps it running in production | Monitoring, recovery, maintenance windows |
| QA or test | Verifies it | Testability, test data, environments |
| Owners of each external system in `context.md` | Every interface has two ends | Interface formats, change windows, limits |

## Check when the trigger applies

| Role | Trigger | Typical requirements from them |
| --- | --- | --- |
| Support or service desk | Users can contact someone about the system | Lookups, corrections, audit of manual changes |
| Security | Authentication, money or anything convertible to money, internet exposure, personal data | Access control, abuse cases, logging |
| Data protection | The system processes personal data | Purpose, retention, consent, data subject requests |
| Legal | Terms and conditions, contracts, licences, consumer law apply | Terms the system must enforce, notices |
| Compliance or regulator liaison | A licence, a regulator or a reporting duty applies | Reports, record keeping, evidence |
| Finance | Money, value, a liability, billing or accounting | Booking rules, reconciliation, month-end |
| Fraud or risk | Value can be gained by abuse (payments, points, vouchers, credit) | Detection rules, holds, limits, review queues |
| Audit, internal or external | Financial reporting or an audit retention policy applies | Trails, evidence, retention |
| Architecture or platform | It runs on a shared platform or integrates with other systems | Platform constraints, standards |
| Marketing or sales | Campaigns, promotions, customer communication | Campaign rules, messaging |
| Training or change management | Staff must learn a new process | Rollout, training material, fallbacks |
| Vendors and partners | A third party builds, hosts or integrates | Release windows, contract limits |
| Accessibility | People outside the company use a user interface | Accessibility standard, assistive technology |
| Works council or union | The system records staff activity or changes working conditions | Limits on monitoring, consultation |
| People who lose something | A system, team, job or contract is replaced | Migration needs, knowledge of current behavior |

## Recording the result

| Gap value | Meaning | Action |
| --- | --- | --- |
| `no` | Covered by a row with a named representative or proxy | none |
| `yes` | The trigger applies and nobody covers it | Add a row with Representative `TBD`; open question to the person who can name one |
| `unclear` | Nobody can say yet whether the trigger applies or whether an existing row covers it | Open question only |

Below the table, one line: "Not applicable (trigger not found in the inputs): <roles>."
