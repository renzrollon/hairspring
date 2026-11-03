# Modeling rules and the glossary cross-check

## What becomes a class

Ask of each candidate noun, in this order:

| Question | If yes | Example (loyalty-points) |
| --- | --- | --- |
| Does the system have to remember individual instances of it, each with its own identity? | Business object: a class. | Member, Purchase, PointsTransaction, Voucher, Campaign, Adjustment, Store |
| Is it one fact about another object (a value, an amount, a date, a code)? | Attribute of that object. | Points balance (Member), reason code (Adjustment), voucher value (Voucher) |
| Is it a person or system acting on our system from outside? | Actor or role, not a class. It belongs in `context.md` or a use case. If the system must remember facts about the role (an approver's name for audit), model those facts where they belong and ask. | Cashier, support agent, fraud engine |
| Is it a rule, a duration, a calculation or a process step? | Not a class. Link it to the class it constrains, or to `state-model` or `process-flow`. | Return window (24 hours, a rule of PointsTransaction), maker-checker |
| Is it another word for a candidate already listed? | Synonym: one class, and a cross-check finding. | Customer, account holder (for Member) |
| Is it a piece of the implementation? | Technical artefact: leave it out and say so. | `outbox_events`, `MemberServiceImpl`, `RedisBalanceCache`, `id`, `created_at`, `member_id` |

## Attributes

- Name the business fact: `redeemableBalance`, not `bal2` or `posted_pts`.
- Types are business types: `Points`, `Money` (with currency in the meaning column), `Date`, `DateTime`, `Text`, `Code`, `Number`, `Boolean`, or an enumeration class.
- A business identifier the stakeholders use (member number, voucher code) is an attribute; a surrogate key is not.
- A derived value (balance) may be an attribute; say "derived from ..." in the Classes table.
- A status attribute typed with a state enumeration is the hook for `state-model`.

## Multiplicities

- Read each association in both directions: "one Member holds how many PointsTransactions?" and "one PointsTransaction is held by how many Members?".
- Take the number from a requirement, a business rule or the glossary definition, and cite it in the Associations table.
- If no source says, write `"TBD"` and add the open question with an owner. A plausible guess is still a guess.
- Lower bound `0` versus `1` is a real requirement ("can a voucher exist without points behind it?"). Ask it.

## Cross-check finding kinds

`check_glossary.py` finds the first four; the last two need you to read the requirement text.

| Kind | Found by | Meaning | Proposed action (pick one, write it in the table) |
| --- | --- | --- | --- |
| `class-without-term` | script | A class has no glossary entry. | Raise to `glossary` with a draft definition from the requirements; or rename the class to an existing term. |
| `class-named-after-synonym` | script | The class uses a synonym, not the preferred term. | Rename the class to the preferred term; or ask the glossary owner to change the preferred term. |
| `duplicate-concept` | script | Two classes map to one glossary term. | Merge the classes; or raise to `glossary` to split the term into two defined terms. |
| `term-without-class` | script | A glossary term matches no class, display name or attribute. | Model it; or record why it is not a business object (actor, rule, process) and rerun with `--ignore`. |
| `synonym` | you | Requirements use two words for one concept, and the glossary does not list one as a synonym. | Raise to `glossary` (add the synonym or confirm the preferred term) and send the affected R-IDs to `requirement-phrasing` for rewording. |
| `homonym` | you | One word means two things in different requirements, or a requirement distinguishes two concepts the glossary merges. | Raise to `glossary` to define both terms; model both concepts. |

Evidence is always concrete: an R-ID with the word in quotes, a `file:line`, or the glossary row.

## Script usage

```text
python3 <skill-dir>/scripts/check_glossary.py requirements/models/domain-model.md
python3 <skill-dir>/scripts/check_glossary.py requirements/models/domain-model.md --glossary requirements/glossary.md --ignore "Cashier,Return window"
python3 <skill-dir>/scripts/check_glossary.py requirements/models/domain-model.md --format json
```

The glossary must have a Markdown pipe table (or CSV) with a `Term` column; columns whose header contains "synonym" or "abbreviation" are read as alternative names (comma, semicolon or slash separated). Names compare without case, spaces or punctuation, with a naive plural match. Exit 0: no findings; 1: findings; 2: file or parse error.
