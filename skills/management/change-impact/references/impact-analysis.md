# Impact analysis: following links, sizing, routing

## 1. From trace links to an impact set

`re-lint trace impact R-041 [R-060 ...] --format md` (vendored: `scripts/trace_matrix.py impact ...`) reads `requirements/trace/trace.csv` and lists every node linked to the given IDs, in both directions. Turn each one into a row of the CR impact table:

| `trace.csv` type | Impact kind in the CR | Usual impact |
| --- | --- | --- |
| `requirement` (seed) | requirement | text change, new, or withdraw |
| `requirement` (via `linked-to`) | requirement | review: does it still hold after the change? |
| `source`, `stakeholder`, `interview` | source | the source document must change (terms, contract), or the person must be informed |
| `decision`, `adr` | decision | review: is the decision still valid? A superseded decision needs a new record |
| `code` | code | re-implement |
| `test` | test | update the expected values, or add a test |
| `commit` | (evidence only) | shows where the old behavior was built; not an impact row of its own |
| `change` | change | an earlier CR on the same requirement; read it, because it may hold a constraint |

Then add what the trace cannot show. Search for the seed IDs in these places and confirm each hit:

- Work products: `requirements/stories/`, `verification.csv`, `quality-requirements.md`, `constraints.csv`, `models/`, `openspec/changes/`.
- Interfaces and external parties: `context.md` (on the sample: the POS vendor, the CRM, the app team).
- Configuration and data: config files, feature flags, migrations, seed data, and copy texts in the app or on receipts.
- Communication: programme terms, help pages, support scripts, training.

## 2. Fallback search (no trace matrix, or no Python)

Search the whole repository (code, tests, config, docs, `requirements/`) for:

1. Each seed ID in every citation form: `R-041`, `r_041`, `R041`, `R-041.AC`.
2. The values in the before/after table, in the forms code uses. On the loyalty-points sample, that means `500`, `500.0`, `"500"`, constant names (`MIN_REDEMPTION`, `minRedemption`), and config keys (`min_points`).
3. The domain terms in the request and their glossary synonyms (on the sample: `minimum redemption`, `redeem threshold`).

For every hit, open the line and keep it only if it is about this behavior. A bare number like `12` or `500` matches unrelated code. Record kept hits as `path:line` with `Found by` = `search`. Write in the CR header: "Trace coverage: search only (lower coverage). Run `traceability-matrix` to improve it."

## 3. Effort: relative sizes only

Size each option on this scale. Write the assumptions that put it there. If the team estimates in their own unit (points, days), record their figure with its source next to the size. Never convert a size into hours yourself.

| Size | Shape of the work (qualitative) |
| --- | --- |
| XS | A wording or attribute change only; no code, test or interface change |
| S | One component and its existing tests change; no interface, data or document change |
| M | Several components, or new tests, or a data change inside our service, or a source document to update |
| L | An external interface, a data migration, or a change that other teams or vendors must schedule |
| XL | Too big to size as one change: split the CR into options or phases |

Assumptions are concrete statements someone can confirm or reject. Examples from the loyalty-points sample: "The minimum is read from config in one place (`config/redemption.yaml:4`)", or "The app shows the minimum from the API, not hard-coded text". Ask the team to confirm the size. Until they do, write "proposed by the agent".

## 4. Risk: named factors, highest one wins

| Level | Any of these factors |
| --- | --- |
| high | The change touches a constraint (`Type=C`) or a requirement sourced from a regulation or contract; it changes an external interface; a stakeholder conflict about it is open |
| medium | A source document must be updated (terms, policy); it reopens `implemented` or `verified` requirements; impacted requirements have no tests (trace gaps); trace coverage is search only; a requirement's `Stability` is `volatile` |
| low | None of the above |

Write the factors that apply, not only the level.

## 5. Who decides: the change authority

Read `requirements/schema.json` → `process.change_authority` and the process section of `requirements/README.md`.

| `change_authority` | Route | Section 7 of the CR is drafted as |
| --- | --- | --- |
| `product-owner` (default) | The product owner decides and orders the backlog | A backlog item: title `CR-nnn: <title>`, the problem, the change, acceptance criteria, the impacted IDs, the size, and links |
| `ccb` | A Change Control Board decides (typical for linear, customer-specific or contract-bound work) | A board request: summary, reason, impact, options, recommendation, the decision needed, and by when |
| `customer` | The customer or contract owner decides | As for `ccb`, plus the contract reference and who signs |
| any other value | Ask who decides and how they want to receive it | Ask |
| missing | Use `product-owner`, and say so in the CR | As for `product-owner` |

When `README.md` describes a linear, customer-specific process but `change_authority` says `product-owner`, ask which one applies. Write the name of the person or board in the CR header, not only the role. The decision recorded in section 8 is valid only when the decider matches this authority. If someone else decided, flag the mismatch and ask.

## 6. What "applied" means

A CR is `applied` when the register reflects the approved option. The implementation work (code, tests, documents) is tracked by the backlog item or the board's action list, not by the CR status. CR statuses: `draft` → `submitted` → `approved` | `rejected` | `deferred`; `approved` → `applied`.
