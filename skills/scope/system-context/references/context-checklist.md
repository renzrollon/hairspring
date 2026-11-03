# Context checklist

## 1. Where to look in a repo

| Look in | What it tells you | Typical evidence |
| --- | --- | --- |
| `README*`, `docs/architecture*`, ADRs | Purpose, named neighbors, decisions about ownership | "The CRM receives a nightly summary" |
| OpenAPI, AsyncAPI, GraphQL, `.proto` files | Interfaces the system offers and their consumers | `paths: /members/{id}/balance` |
| HTTP clients, SDK wrappers, message producers and consumers | Systems the system calls or listens to | `FraudClient`, topic `pos.purchases` |
| Configuration and `.env.example` | External endpoints and credentials by name | `CRM_BASE_URL`, `NOTIFY_API_KEY`, `WAREHOUSE_SFTP_HOST` |
| `docker-compose*`, Helm charts, infrastructure code | Neighboring services and managed services | a `fraud-mock` container, an SFTP bucket |
| Scheduled-job definitions (cron, CronJob, workflow schedules) | Batch flows in and out | `0 2 * * *` export job |
| Identity and access configuration | Who signs in and through which provider | an OIDC client for the admin console |
| Support runbooks, ticket exports | Manual workarounds and the tools people use | "agents adjust points in the back office" |

Evidence from code, configuration or docs alone gives status `assumed` until a person or a specification confirms it.

## 2. External elements to check for

Ask about each line that could apply. A missing element is a requirement source nobody consulted.

| Element | Ask |
| --- | --- |
| Users, one per channel (app, web, store, phone) | Who uses the system directly? Who uses it through another system? |
| Staff tools (admin console, back office, support) | Who corrects data or helps users, and with which tool? |
| Upstream systems | What sends data or events to the system? |
| Downstream systems | What receives data, reports or events from the system? |
| Shared services | Identity provider, notification, payment, email, document generation, address lookup |
| Batch and scheduled jobs | What runs at night, at month-end, at year-end? Who owns it today? |
| Reporting and analytics | Which extracts go to a warehouse, to finance, to a regulator? |
| Legacy system being replaced | What does it do today that nobody wrote down? Does any of it stay? |
| Organizations | Vendors, partners, regulators, auditors that receive or send something |
| Rules from outside | Laws, regulations, contracts, company policies (listed in the context boundary table; detail goes to `constraints-register` and `source-inventory`) |
| Physical and operating conditions | Offline stores, peak periods, devices, locations |

## 3. Boundary question patterns

| Situation | Question (with a recommended answer) |
| --- | --- |
| A capability on the system boundary | "Is `<X>` something our system does, something it talks to, or out of scope? I'd say `<recommendation>` because `<evidence>`." |
| Ownership after go-live | "Who runs `<X>` after go-live, and whose incident is it when `<X>` fails?" |
| Shared responsibility | "Both `<A>` and `<B>` could do `<X>`. Which one does it in release 1?" |
| Relevance on the context boundary | "Does `<element>` change any requirement of ours? If not, I will list it as irrelevant." |
| Data flow | "What does `<element>` send us, and what do we send back? Through which interface?" |
| Indirect actor | "Does `<person>` use our system directly, or only through `<other system>`?" |

Answers that contain "maybe", "probably", "depends", "later", "both", "not decided" or "ask `<someone>`" become open decisions `D-nn`.

## 4. Grey-zone patterns

| Pattern | Example (loyalty-points sample) |
| --- | --- |
| A job another team runs on the legacy system today | Points-expiry batch job, run by the data platform team |
| Output produced on someone else's device | Voucher printing on the POS receipt |
| A second channel with its own back end | App purchases fulfilled by an e-commerce order system |
| Data both teams think the other one keeps | Member consent for marketing messages: CRM or loyalty service? |
| A manual workaround that would become a feature | Support adjusting points in a spreadsheet today |
| Reporting obligations | Points liability extract: our file, or the warehouse team's query? |

For each grey zone write: the question, at least two options (one of them "outside"), the recommended option and why, the owner who decides, and status `open`.
