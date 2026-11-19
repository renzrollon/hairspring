# Unknowns by ticket shape

Use this at step 2 to list candidate unknowns fast. It is a checklist, not a questionnaire: every unknown still has to pass the design test, and anything the repository already answers is recorded under *Already answered*, not asked.

## The design test

Ask a question only if **two plausible answers would lead to different code, data model, interface, permission or test**. Examples on the loyalty-points sample:

| Unknown | Plausible answers | Different design? | Ask? |
| --- | --- | --- | --- |
| How large can one points-history export get? | "a few hundred rows" / "the whole member base" | Direct download vs background job with a file store | yes |
| Should the CSV header row be in English? | "yes" / "yes" | No | no |
| Who may trigger a points adjustment? | "any agent" / "team leads above 5,000 points" | Different permission check and approval flow | yes |
| Which shade of green is the confirm button? | anything | Not a requirement of this task | no |

## Unknowns per shape

Groups: **B** boundary, **F** functional, **Q** quality, **C** constraint. "Check first" lists where the answer often already is.

| Shape (typical wording) | Design-changing unknowns | Check first |
| --- | --- | --- |
| Export / report / download ("add export to CSV", "download as PDF") | B: who may export, from which screen or API. F: which entities and fields; which filter or period. Q: largest export and acceptable wait (direct download vs background job). Q: which personal data may leave the system, masked or not. C: audit of who exported what; where the file goes and how long it is kept. | Existing export helpers (encoding, delimiter, date format), role model, the screen it mirrors |
| Import / bulk upload ("let ops upload a CSV of adjustments") | B: who uploads, from which source system. F: validation rules; reject the whole file or skip bad rows; duplicates and re-uploads (idempotency). Q: largest file; time to result. C: approval for bulk changes; audit trail. | Existing parsers and validators, domain model constraints |
| "Make it faster" / performance | F: which operation exactly (screen load, API call, batch). Q: current value and target, at which percentile, measured where (device, server, network). Q: under which load or data size. F: may results be stale, and for how long (allows caching). | Existing metrics, dashboards, load tests, quality requirements with Type Q |
| Notifications ("notify members when points expire") | F: trigger event and timing (immediate, digest, quiet hours). B: recipients; opt-out and consent rules. F: channel and fallback (push, SMS, email). Q: what happens when delivery fails; duplicates. C: personal data in the message; legal content (marketing vs transactional). | Notification provider client, consent flags in the member model |
| Search / list / filter ("support needs to search members") | F: search keys (phone, card, email, name) and match type (exact, prefix, fuzzy). B: who sees which results. Q: result size, paging, response time. C: masking of personal data in results. | Existing indexes, list endpoints, role checks |
| Delete / archive / retention ("let members delete their account") | F: soft or hard delete; undo window; what happens to related records (points, vouchers, transactions). C: legal retention that forbids deletion (audit, tax) vs privacy law that requires it. B: who may delete. Q: audit evidence. | Retention policy docs, foreign keys, existing deletion jobs |
| Roles / login / SSO ("support SSO for agents") | B: which users and identity provider. F: role mapping; what happens to existing accounts and sessions; fallback when the provider is down. C: mandated protocol or MFA. Q: session lifetime, lockout. | Auth middleware, identity config, security requirements |
| Integration / new endpoint ("expose balance to the CRM") | B: consumer and provider; who owns the contract. F: request and response fields; errors. Q: volume, rate, latency, freshness. F: sync or async; retries and idempotency. C: authentication; versioning; who must change the other side. | API specs (OpenAPI, event schemas), `context.md` interfaces |
| New field / form ("add date of birth to the profile") | F: required or optional; validation; default for existing records. B: who can see and edit it. C: personal data classification and retention. | Model and migration conventions, form components |
| Rule or calculation change ("double points on weekends") | C: who decides the rule (program terms, marketing, finance). F: rounding; effective date; retroactive or not; returns and reversals. F: interaction with other multipliers. Q: audit of which rule applied. | Program terms (S-01), existing rule engine and tests |
| Scheduled job / batch ("expire points nightly") | B: is the job ours or another team's. F: schedule and time zone; what one run covers. Q: run time window; what happens on failure or overlap; re-run safety. C: notification of finance or operations. | Existing schedulers, runbooks, `context.md` grey zones |
| Bug with unclear expected behavior ("balance is sometimes wrong") | F: the expected behavior and who states it; which records are affected; whether existing data must be repaired. | Reproduction steps, logs, tests, requirements for the area |

## Skip examples

| Task | Ask? | One-line reason to write |
| --- | --- | --- |
| "Rename `calc_pts` to `calculate_points` everywhere, no behavior change" | no | "No clarifying questions: pure rename, behavior unchanged." |
| "Bump the HTTP client to the next patch release" | no | "No clarifying questions: dependency bump, no behavior change." |
| "Fix: points are not reversed when a purchase is returned within 24 h; expected: reversed (see R-061)" | no | "No clarifying questions: expected behavior stated by R-061." |
| A ticket that states inputs, outputs, rules, error cases, limits and tests | no | "No clarifying questions: fully specified." |
| "Add export to CSV" | yes | |
| "Make the balance screen faster" | yes | |
| "Fix: balance is sometimes wrong" | yes, after reading logs and tests | |

## Recommended answers without invented numbers

| Situation | Write | Don't write |
| --- | --- | --- |
| The repo or ticket gives the number | "Up to 2,000 transactions, the largest history in `fixtures/members.json`" | |
| No source for a number, but a design avoids needing it | "Stream the file so size does not matter; no limit needed" | "Limit to 10,000 rows" |
| The number is a business decision | "No recommendation: needs a business value" | "Within 2 seconds" |
