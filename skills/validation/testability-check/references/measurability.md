# Measurability: verdicts, criterion patterns and measurable forms

Read at steps 3, 5 and 6. The rule throughout: propose the **form** of a measurable criterion; take the **values** only from a source. Every other value is `TBD` with a question and an owner.

## Verdict

| Verifiable | When | What to write |
| --- | --- | --- |
| `yes` | The text names an observable result, and every limit it needs is in the text or a register | Criterion from the text; `Basis` `text` (or the register / person it came from) |
| `tbd` | The measurable form is clear, but at least one target, load or period is `TBD` | Criterion with `TBD`; `Question` with an owner; `Basis` `text` |
| `no` | As written it cannot pass or fail: a subjective word, an unbounded claim, nothing observable, or a target nobody could measure | Proposed measurable form with `TBD`; `Question`; `Basis` `proposed` |

A `tbd` row is honest and can go into planning with its question; a `no` row needs its text rewritten before anyone can plan a test.

## Criterion patterns

| Row | Pattern | Example |
| --- | --- | --- |
| Functional, event-driven | Given `<state>`, when `<trigger>`, then `<observable result>` | Given a registered member, when the POS sends one completed purchase event, then a pending points transaction for that purchase and member exists |
| Functional, rule | For inputs `<set incl. boundaries>`, the result is `<outputs>` | For SGD 0.99, 1.00, 1.99 and 150.75 the awarded points are 0, 1, 1 and 150 |
| Functional, unwanted behavior | When `<failure>`, then `<response>` and not `<harm>` | When the fraud engine holds the purchase, the points stay pending and cannot be redeemed |
| Quality | `<metric>` is `<limit>` under `<condition>`, measured by `<method>` | Time from posting to updated balance in the app is at most TBD s at the TBD percentile under TBD requests per minute, measured by load test |
| Constraint | `<artifact>` shows `<property>`, checked by `<who/how>` | The schema, event mapping and log configuration hold no card number field, confirmed in review by the security architect |

The boundary is part of the criterion. "Above 5,000" means 5,000 does not need a second approver and 5,001 does; "at least 500" means 500 qualifies.

## Measurable forms for common unverifiable phrasings

| Phrasing | Why it fails | Proposed form (targets stay TBD) | Question to the owner |
| --- | --- | --- | --- |
| intuitive, easy to use, user-friendly | Subjective | In a moderated usability test with TBD first-time users, at least TBD complete `<task>` without help within TBD minutes | Which tasks, how many users, what completion rate and time count as a pass? |
| fast, quickly, responsive | No limit | `<operation>` completes within TBD ms at the TBD percentile under TBD load | What limit, at which percentile and load? |
| secure | No threat or control named | `<named control>` holds: for example, `<role>` without `<permission>` receives an access-denied response for `<operation>` | Which threats and controls does "secure" mean here? |
| always available, 24/7 | Unbounded | Availability of `<service>` is at least TBD % per calendar month, measured from monitoring, excluding TBD maintenance windows | What target, over which hours, and does maintenance count? |
| never lose data | Absolute, unprovable | Under `<failure scenario>`, at most TBD `<events>` are lost and all others are processed within TBD minutes after recovery | Which failures, and what loss is acceptable (zero is allowed if stated)? |
| all, every, any (unbounded scope) | Scope cannot be tested exhaustively | `<bounded population>`, plus the named exceptions | Which records or users are excluded? |
| scalable | No load or growth figure | Sustains TBD `<units>` per minute for TBD minutes with `<quality limit>` | Which peak, which growth, for how long? |
| support, handle, manage `<X>` | No observable result | When `<trigger>`, the `<system>` shall `<specific action>` with `<result>` | What exactly happens when `<X>` occurs? |

Quoting context is allowed and useful: "Last year's peak was about 9,000 purchases per minute (Rationale of R-083). Is the target that figure or more?" The figure goes in the question, never into the criterion, until the owner confirms it.
