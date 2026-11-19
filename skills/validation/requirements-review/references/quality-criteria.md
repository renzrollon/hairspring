# Quality criteria, severity and the lint map

The twelve criterion names follow CPRE FL Handbook 1.2 §3.8; the checks and severity rules below are this catalogue's own working rules. Use the criterion names exactly as written here in the `Criterion` column.

## Single requirement (graded per scoped row; first two first)

| Criterion | It passes when | Check | Typical failure (loyalty-points) |
| --- | --- | --- | --- |
| adequate | It states the stakeholders' real, agreed need, at the level of detail the next decision needs | Source exists and its owner would recognize the need; Rationale says why; no technology choice unless a mandate is cited; matches the context | "The loyalty service shall store vouchers in a PostgreSQL table." (a design choice, no stakeholder need) |
| understandable | Everyone who agrees, builds or tests it reads it the same way | Glossary terms used; actors and systems named as in `context.md`; one sentence; no unexplained abbreviation or pronoun with an unclear referent | "WHEN the loyalty service issues a voucher, it shall deduct ..." ("it" by position only) |
| necessary | Removing it would leave a stakeholder need or a constraint unmet | Rationale ties to a goal or source; inside the system boundary; not a copy of another row | A second row that repeats the redemption rule |
| unambiguous | It has exactly one reasonable reading | No vague quantity ("recent"), no `and/or`, no modifier with unclear scope, no undefined term | "show the member's recent vouchers": last 7 days? last 5? unused only? |
| complete | It contains everything needed to build and test it | Actor, trigger or state, response, values with units, and the error case where one matters; TBDs listed with owners | "Vouchers expire." (who, after how long, what happens to the points) |
| verifiable | A pass/fail check exists at acceptable cost | Measurable target or observable result; the method is obvious (test, inspection, analysis, demonstration) | "answer voucher validation requests fast enough for checkout" |

## Set (graded once for the scope, against the whole register)

| Criterion | It passes when | Check |
| --- | --- | --- |
| consistent | No two requirements, or a requirement and a constraint, contradict each other; one term means one thing | Group by subject; compare values, conditions and actors; compare with `conflicts.md` and the glossary |
| non-redundant | Each requirement is stated once | Same trigger and response in two rows; a row that restates another with fewer details |
| complete | The set covers the scope: every actor and interface in `context.md`, every state that matters, the error and abuse cases | Walk the context table and each entity's states; look for the missing "IF ..., THEN" rows |
| modifiable | A change touches one place | One requirement per row; references by ID instead of copied text; consistent structure |
| traceable | Every requirement has a unique ID, a resolvable Source and its links | No missing or unregistered Source; decisions and conflicts linked; no deleted rows |
| conformant | The set follows the agreed schema and templates | Columns, enum values, EARS or story form, ID pattern; mostly from the linter |

## Severity

| Severity | Use when | Examples |
| --- | --- | --- |
| blocker | Building or agreeing it as written would produce the wrong system or a contradiction | Contradicts another requirement or a constraint; inadequate `must` row; a `must` row nobody can understand |
| major | Two people would build or test it differently, or something needed is missing | Ambiguous scope; missing actor, value or error case; unverifiable but fixable with a target; solution in disguise |
| minor | The meaning is clear but the form makes it harder to read, change or trace | Pronoun with an obvious referent; template slip; info-level lint findings |

Lint findings start at: `error` → major, `warning` → minor, `info` → minor. Raise one level when the row is `must` and the finding leaves it ambiguous or unverifiable. Structural errors that break traces (`duplicate-id`, `invalid-id`) stay major.

## Lint rule → criterion

| Lint rule | Criterion |
| --- | --- |
| `weak-word` | verifiable |
| `universal-quantifier` | unambiguous |
| `passive-voice` | complete (the actor is missing) |
| `nominalization` | understandable |
| `incomplete-condition` | complete |
| `missing-obligation`, `future-tense` | conformant |
| `compound-requirement` | modifiable |
| `open-tbd` | complete |
| `duplicate-id`, `invalid-id`, `unregistered-source` | traceable |
| `missing-attribute` | traceable for `Source` and `Rationale`; conformant otherwise |
| `invalid-enum` | conformant |
| `register-drift` | consistent |

When one row has a lint finding and a judgment finding about the same problem (lint `missing-obligation` and "no period, no actor" on "Vouchers expire."), merge them into one finding under the criterion that matters most (here `complete`) and list both sources in "Found by".
