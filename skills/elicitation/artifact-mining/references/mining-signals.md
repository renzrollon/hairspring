# Mining signals by artifact type

Read the whole artifact before writing candidates; a rule in line 12 is often undone in line 40. The signals below say where requirements hide. The examples are on the loyalty-points sample.

## Code, stored procedures, scripts (system archaeology)

| Signal | Looks like | Candidate it suggests |
| --- | --- | --- |
| Business constants | `FLOOR(amount_cents / 100)`, `> 5000`, `SYSDATE - 1` | Earning rate, rounding, caps, time windows |
| Conditions on business data | `IF store_id IN (17, 23)`, `if member.tier == 'GOLD'` | Rules per store, tier or campaign (check whether still valid) |
| Validation and rejection | `raise InvalidVoucher`, `RETURN -1` | Input rules and the error behavior |
| State changes | `status = 'P'` to `'X'` | States and transitions (hand to `state-model`) |
| Scheduling | cron entries, "nightly job", batch windows | Timing and freshness (often a quality candidate) |
| External calls | HTTP clients, queue publishers, file drops | Interfaces (hand to `system-context`) |
| Permission checks | `if user.role in (...)` | Who may do what |
| Retention and deletion | `DELETE ... WHERE created < ...`, archive jobs | Retention rules (check against the retention policy) |
| Error handling | `WHEN OTHERS THEN ROLLBACK`, retries, swallowed exceptions | Reliability behavior, often a probable defect |
| Comments | "must", "legal", "audit", "temporary", "hack", "TODO", "do not change" | Intent, or a warning that the code is a workaround |

Usually **not** a candidate: loops, cursors, temp and staging tables, ORM mappings, logging format, framework glue. Drop them as implementation details, and add a `Q` candidate only when a quality need is visible behind them.

## Config and data

- Feature flags: a flag permanently off is a `drop` candidate with "probable obsolete rule"; a flag that differs per store or country is a variability candidate (EARS `WHERE`).
- Lookup tables (reason codes, tiers, store lists): one candidate for the rule the table expresses, not one per row. Mention the table's size or odd entries in `Reason`.
- Data that contradicts the code (a cap of 5,000 in code, transactions of 7,500 in the data) makes the candidate `confirm`.

## API contracts (OpenAPI, WSDL, event schemas)

| Signal | Candidate |
| --- | --- |
| Required fields, formats, enums | What the interface must carry |
| Error responses and codes | Unwanted-behavior candidates |
| Rate limits, timeouts, pagination | Quality candidates (`Q`) and constraints from the provider (`C`) |
| Versioning and deprecation notes | Constraints with an expiry |

A contract owned by another party (the POS vendor's interface spec, S-02) is an authoritative source for what crosses the boundary: candidates backed by it can be `keep`.

## Documents (document analysis)

- Terms and conditions, contracts, regulations, policies: each clause with an obligation ("must", "shall", "may not", "within n days") is a candidate; regulations and contracts often give `C`.
- Specs and PRDs: separate requirements from facts ("the POS will be upgraded in March" is context) and from solutions ("use Redis").
- Runbooks and operating procedures: manual steps people perform to keep the old system right are needs the new system may have to cover; they are `confirm` until an owner says so.
- Drafts: a clause marked draft or "to be confirmed" makes its candidates `confirm`, owner = whoever must confirm it.

## Tickets, support logs, reviews (feedback analysis)

1. Read the whole export, then group tickets by the need behind them, not by their wording.
2. One candidate per group: the need in the member's or agent's terms ("members can see when pending points will be posted"), not the requested fix.
3. Put the count in `Reason`, for example (sample project numbers): "212 of 1,240 tickets (S-03) ask where their points are".
4. Quote one representative ticket with its location (`support/export.csv:88` or `S-03 ticket 48812`), with personal data masked.
5. Disposition `confirm`, owner the product owner; `Kano` `dissatisfier` when the group is complaints about something members take for granted.
6. Single tickets with an unusual wish: one candidate only if it touches safety, security, legal duties or money; otherwise mention them in the summary.

## Personal data

Never copy names, emails, phone numbers, NRIC or card numbers, addresses or free-text personal details from tickets or logs into `Quote` or `Statement`. Replace them with the mask markers in `candidates-columns.md`. If a quote is meaningless without the personal data, cite the location and quote only the non-personal part.
