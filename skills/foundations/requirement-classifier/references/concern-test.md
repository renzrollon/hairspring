# Concern test, Kano guess, flags and routing

Examples come from the loyalty-points sample project; their numbers are facts of that sample, not recommendations.

## 1. The concern test

Classify by the concern a statement addresses, not by whether it reads as "what" or "how". Ask in this order and stop at the first answer.

| # | Question | If yes |
| --- | --- | --- |
| 1 | Does the statement say something the system or the project must make true? | Go on. If it describes the world, today's system or someone else's plan: `fact`. If it names a desired outcome too broad to check as one statement: `goal`. If you cannot tell without asking: `unclear` |
| 2 | Does someone outside the team restrict the solution or the process (law, regulation, contract, company policy, a platform mandate, a physical or organizational limit)? | `requirement`, Type `C`. If it names a technology, component, pattern or algorithm and nobody outside the team mandated it: `solution` |
| 3 | Is the concern how well the system does something: performance efficiency, reliability, security, interaction capability (usability), compatibility, maintainability, flexibility (portability) or safety? | `requirement`, Type `Q`. Name the characteristic in `Concern` |
| 4 | Otherwise: is the concern a behavior or a result (input, output, data, reaction to an event)? | `requirement`, Type `F` |

Quality characteristic names follow ISO/IEC 25010:2023 (names only).

## 2. Tie-breakers

| Situation | Call | Why |
| --- | --- | --- |
| A quality target attached to a function: "the balance updates within 2 s" | `Q` | The concern is how fast; the function is the context |
| A function that exists to achieve a quality: "lock sign-in after repeated wrong passwords" | `F`; Concern "F: security, refined into behavior" | The behavior is checkable on its own |
| A law that requires a function: "members can ask for their data to be deleted" | `F`; Source names the law | The law is the source, not the type |
| A law or policy that restricts how: "keep transaction data 7 years", "data stays in Singapore" | `C` | It narrows the solution space |
| A technology with a named mandate: "PostgreSQL, the only database the platform team operates (platform policy)" | `C` | Someone outside the team restricts the choice |
| A technology without a mandate: "use Kafka", "build it in Go", "cache balances in Redis" | `solution`; Type = the need behind it if clear, else `TBD` | A design decision; ask what quality it is meant to achieve |
| A present-tense rule the system must apply: "members earn 1 point per SGD 1" | `F`, flag `rule` | Product documents state rules as facts |
| A present-tense description of today: "today points are on a plastic card" | `fact`, flag `current-state` | Context, not a requirement |
| `will` about someone else: "the vendor will ship v2.2 in March" | `fact`, flags `will`, `dependency` | An intention of another party |
| `will` that may be meant as an obligation: "the service will log every refund" | `fact`, flag `will`; open question "binding?" | Never upgrade the binding level yourself |
| A process restriction: "acceptance tests decide the final payment" | `C` | It restricts the project, not only the product |
| A wish with no checkable result: "make points fun", "increase engagement" | `goal` | Needs a measurable outcome first |

## 3. Kano first guess

Guess only for `requirement` rows of Type `F` or `Q`; write `-` everywhere else. Take the view of the user group the statement serves (member, cashier, support agent).

| Guess | Signals | Example (loyalty-points) |
| --- | --- | --- |
| `dissatisfier` | Taken for granted; nobody asks for it, but its absence causes complaints; the old system already did it; a legal, safety or security basic | Show the current points balance |
| `satisfier` | Asked for explicitly; more or better is better (faster, fewer steps, more options) | The balance is visible sooner after a purchase |
| `delighter` | Not expected; would surprise users; its absence causes no complaint | Birthday bonus points |
| `indifferent` | No user group cares either way | A theme color for the admin console |

Kano categories drift: delighters become satisfiers and then dissatisfiers as users get used to them. Confirm a guess with stakeholders before it influences priority.

## 4. Flags (fixed list)

| Flag | Meaning |
| --- | --- |
| `will` | Uses `will`: a fact or intention until the source says it is binding |
| `rule` | A business rule stated in the present tense that the system must apply |
| `current-state` | Describes today's system or process |
| `dependency` | Depends on a delivery or decision by another party |
| `compound` | More than one requirement in one statement; `requirement-phrasing` splits it |
| `no-obligation` | No `shall`, `should` or `may`; the binding level is not stated |
| `weak-word` | A vague qualifier: fast, easy, a few, user-friendly, secure, scalable ... |
| `missing-value` | A target, limit or period is needed but absent |
| `no-actor` | Passive voice with no actor |
| `mandate-unconfirmed` | Reads as a constraint, but who imposes it is not named |
| `duplicate:<Ref>` | Repeats another statement or an existing requirement |
| `conflict?` | Seems to contradict another statement or requirement |

## 5. Verdict and Type values

| Verdict | Type |
| --- | --- |
| `requirement` | `F`, `Q` or `C` |
| `solution` | Type of the need behind it (`F`, `Q`, `C`) or `TBD` |
| `fact`, `goal`, `unclear` | `-` |

## 6. Routing (`Next`)

| Row | Next |
| --- | --- |
| `requirement` F | `requirement-phrasing` (or `user-story-refiner` when the team writes stories) |
| `requirement` Q with a target value | `requirement-phrasing` |
| `requirement` Q without a target value | `quality-requirements` (several) or `clarifying-questions` (one) |
| `requirement` C | `constraints-register` |
| `solution` | The architect (role or `SH-nn`), plus `clarifying-questions` for the need behind it |
| `goal` | `clarifying-questions` or `elicitation-workshop` |
| `fact` | `none` (kept here as context); `system-context` when it describes the environment of the system |
| `unclear` | `clarifying-questions` |
| any row flagged `conflict?` | `conflict-detector` as well |
