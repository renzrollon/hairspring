# Term patterns

## 1. What counts as a term

| Include | Examples (loyalty-points) | Exclude | Examples |
| --- | --- | --- | --- |
| Business objects | member, voucher, points transaction | Generic technical words | string, server, endpoint, payload |
| Roles | cashier, support agent, product owner | People's names | Mei Tan (goes to `stakeholders.md`) |
| States and events | pending, posted, redeemed; purchase completed | Words used in one sense by everyone, everywhere | store, day |
| Units and measures | point, points liability | Product or library names with no domain meaning | Redis, React |
| Rule and policy names | bonus campaign, return window, maker-checker | The rules themselves | "points expire after 12 months" (a requirement candidate) |
| Abbreviations | POS, CRM, PDPA, QR, SGD | Abbreviations of generic tech | HTTP, JSON |
| Names of external systems in the context | TillPoint POS, Relay CRM | Internal module names | `points-ledger` package |

Keep the candidate when, in addition, at least one holds: a requirement or story uses it, more than one source uses it, two parties use it differently, or it is an abbreviation.

## 2. Writing a definition

| Rule | Bad | Good |
| --- | --- | --- |
| One sentence: broader category, then what sets the term apart | "Voucher: used at checkout." | "A code worth a fixed amount in SGD that a member receives for redeemed points and applies at checkout." |
| No circularity | "Points transaction: a transaction involving points." | "One entry in a member's points ledger that adds or removes points, linked to the purchase, redemption, expiry, reversal or adjustment that caused it." |
| No example as the definition | "Tier: e.g. Silver, Gold." | `TBD` plus an open question, until someone defines tiers |
| No requirement or rule value inside | "Points: expire after 12 months." | "Points: the unit of the program's reward balance." The expiry period goes to a requirement candidate |
| Use other glossary terms, spelled as in their rows | "client", "user", "customer" for the same person | "member" everywhere |
| Say what it is not, when people confuse it | | "Not the POS sale itself; see Purchase." (in `Homonym notes`) |

## 3. Homonyms: one word, several senses

Signals:

- The same word with different attributes or types in different code packages or tables (`Account` in identity, `LedgerAccount` in finance).
- Different qualifiers around the word across sources: "member account", "liability account", "staff account".
- Two sources that would answer "how many X are there?" differently.
- Different owners care about the word for different reasons.

Resolution: one row per sense, each with a qualified term (`Member account`, `Liability account`, `Staff account`). In `Homonym notes` say which sense the bare word means, if any, and which qualifier to use. Ask the owners which sense keeps the bare word; until they answer, require the qualifier.

## 4. Synonyms: two words, one thing

Signals:

- Code uses one name and the docs another (`Customer` class, "member" in the terms and conditions).
- The same identifier or field joins both words (`customer_id` on a member record).
- People use the words interchangeably in one ticket or one meeting.

Resolution: one row for the preferred term. Prefer, in this order: the word in binding documents (contracts, terms and conditions, regulations), the word the domain experts use, the word most sources use. List the others in `Synonyms` with where they occur and "avoid". Renaming code is a change for the tech lead, not a glossary decision: record it as a finding with the tech lead as owner.

## 5. Abbreviations

- Put the abbreviation in the `Abbreviation` column of the expanded term's row (`Point of sale` → `POS`).
- An abbreviation with two expansions in the project (`PO` = product owner and purchase order) is a homonym: one row per expansion, both noting the clash, and the rule "write it out" in `Homonym notes`.
- An abbreviation nobody can expand is a `candidate` with `Definition = TBD`.

## 6. Status values

| Status | Meaning | Who sets it |
| --- | --- | --- |
| `candidate` | Found in the sources; no definition yet (`TBD`) | the skill |
| `proposed` | Definition drafted with a source; waiting for the owner | the skill |
| `agreed` | The named owner confirmed the definition | a person only |
| `deprecated` | No longer used; the row says which term replaces it | the owner |

## 7. Findings kinds

| Kind | Use when |
| --- | --- |
| `homonym` | One word, several senses |
| `synonym` | Several words, one thing |
| `abbreviation clash` | One abbreviation, several expansions |
| `undefined` | A term is used but no source defines it |
| `rule in definition` | A source "defines" a term with a business rule; the rule is routed to `requirement-classifier` |
