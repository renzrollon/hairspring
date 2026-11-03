# EARS patterns and natural-language pitfalls

EARS (Easy Approach to Requirements Syntax) is by Alistair Mavin et al. (Rolls-Royce, 2009); see https://alistairmavin.com/ears/. The templates below are the public EARS patterns; the examples are on the loyalty-points sample.

## The six patterns

| Pattern | Use when | Template | Example |
| --- | --- | --- | --- |
| Ubiquitous | Always true, no trigger | `The <system> shall <response>.` | The loyalty service shall record the member ID, store ID and timestamp of each points transaction. |
| Event-driven | A trigger starts the behavior | `WHEN <trigger>, the <system> shall <response>.` | WHEN the POS sends a completed purchase event, the loyalty service shall create a pending points transaction. |
| State-driven | Behavior holds while a state lasts | `WHILE <state>, the <system> shall <response>.` | WHILE a member account is on fraud hold, the loyalty service shall reject redemption requests for that account. |
| Optional feature | Behavior exists only where a feature or configuration is present | `WHERE <feature is included>, the <system> shall <response>.` | WHERE the store's POS supports voucher printing, the loyalty service shall return the voucher text with the validation result. |
| Unwanted behavior | Errors, failures, abuse | `IF <unwanted condition>, THEN the <system> shall <response>.` | IF the fraud engine does not respond within TBD ms, THEN the loyalty service shall accept the earn event and flag it for later scoring. |
| Complex | Combinations | `WHILE <state>, WHEN <trigger>, the <system> shall <response>.` | WHILE the POS is in offline mode, WHEN the cashier scans a member QR code, the POS shall queue the purchase event for later delivery. |

Order of clauses in complex requirements: `WHERE`, `WHILE`, `WHEN` or `IF ... THEN`. A state that comes and goes at run time (a campaign is active, a member is on fraud hold) is `WHILE`; `WHERE` is for a feature or configuration that a given installation has or lacks.

## Obligation verbs

| Verb | Meaning | Note |
| --- | --- | --- |
| shall | Binding requirement | Default for requirements |
| should | Expected; deviation needs a reason | Use for strong wishes, not to soften a binding one |
| may | Optional, permitted | Use for features the system is allowed but not required to have |
| will | A fact or an intention of someone else | Not a requirement. "The POS vendor will deliver v2.2 in March" is context |
| must | Treated as `shall` by many teams | `re-lint` accepts it. Keep it only when the existing register already uses `must` as its binding verb; otherwise rewrite to `shall` |

## Pitfalls to remove

| Pitfall | Example | Rewrite |
| --- | --- | --- |
| Weak word | "show the balance quickly" | "within {n} s of login completion", with {n} from a stakeholder; else `TBD` + open question |
| Universal quantifier | "all users can redeem" | "the loyalty service shall accept a redemption request from a member with at least 500 posted points" |
| Passive, no actor | "points are reversed" | "the loyalty service shall reverse the points" |
| Nominalization | "validation of vouchers" | "the loyalty service shall validate the voucher code" |
| Incomplete condition | "when the POS is offline, the purchase" | complete the response clause |
| Compound | "shall export the file and email the member" | two requirements |
| Solution in disguise | "shall use Redis for sessions" | ask for the quality behind it; route to the architect as a design decision |
| Pronoun with unclear referent | "it shall be logged" | name the thing and the actor |
| Open-ended list | "card, QR, etc." | list every accepted option |

## Measurability prompts

When a statement carries a quality word, ask for: the metric, the target value, the condition (load, data size, environment), and how it will be measured. Write the requirement only with confirmed values; otherwise `TBD`.
