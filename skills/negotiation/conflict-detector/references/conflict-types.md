# Conflict types, techniques and escalation

The six type names follow CPRE FL Handbook 1.2 §4.3.2; the root-cause questions, techniques and examples below are this catalogue's own working rules. Read at steps 6 and 7.

## Classify by root cause

Ask in order. The first "yes" is the type. If a later question also applies, mention it as `secondary:` in the reason only when it would change the route.

| # | Question | Type | Route |
| --- | --- | --- | --- |
| 1 | Is the disagreement really about the people: history, distrust, tone, "they always block us"? | relationship | escalate |
| 2 | Does it come from the organization: reporting lines, unequal authority, competing mandates or budgets, a role that cannot say no? | structural | escalate |
| 3 | Would it go away if both sides had the same, current information: a different document version, a misread rule, a missing figure, a term used in two senses? | data | `/conflict-to-decision` |
| 4 | Do the sides hold different principles or beliefs about what is right (fairness, openness, brand promise) that no law, policy or contract settles? | value | `/conflict-to-decision` |
| 5 | Do the sides want different outcomes for their own goals, targets, budget or workload? | interest | `/conflict-to-decision` |
| 6 | Otherwise: both sides read the facts the same way, but need different things from the system in that area, often two legitimate obligations colliding. | subject matter | `/conflict-to-decision` |

If a relationship or structural cause sits on top of a content disagreement, route the conflict to escalation and name the content type as secondary, so the content can go to a resolution session once the escalation owner has acted.

### Loyalty-points calibration

| Conflict | Type | Why |
| --- | --- | --- |
| Expiry 12 months (Finance, points liability) vs 18 months (Marketing, member engagement) | interest | Each side protects its own target; the facts are agreed |
| Keep transaction records 7 years (Finance policy DRP-2024) vs delete personal data when no longer needed (PDPA, DPO) | subject matter | Two obligations collide on the same data; nobody disputes the facts |
| R-041 "fewer than 500" vs R-045 "more than 500" | data | One side misread the programme terms (S-01) |
| "Marketing never gets a fair hearing from Finance since the reorg" | relationship | About people, not about the requirement |
| Store operations reports to Finance, so its priority is set by Finance | structural | Comes from the reporting line |

## Technique table

Techniques settle the conflict; analysis aids prepare the decision. Recommend one technique (two at most, in order) and one aid.

| Type | Recommend first | Also consider | Analysis aid | Avoid |
| --- | --- | --- | --- | --- |
| data | agreement, after checking the source together | none | consider-all-facts | voting (facts are checked, not voted) |
| subject matter | variants; agreement | compromise | consider-all-facts, then plus-minus-interesting | overruling, unless a deadline forces it |
| interest | compromise; variants | voting among peers; overruling by the change authority | decision matrix with weights agreed before scoring; plus-minus-interesting | none |
| value | variants; overruling by someone with authority, with reasons recorded | agreement (rare) | plus-minus-interesting | voting and compromise (principles are not traded) |
| relationship | none (escalation) | none | none | any technique run by the requirements engineer |
| structural | none (escalation) | none | none | any technique run by the requirements engineer |

### When each technique fits

| Technique | Fits when | Watch out |
| --- | --- | --- |
| agreement | Few parties, time to talk, and one option all can accept once the facts are on the table | Silence is not agreement; record each decision-maker's yes |
| compromise | The disagreement is on a scale (a period, a limit, a scope) and both sides can give some | Never propose the compromise value yourself; it comes from the parties |
| voting | Several parties of equal standing, well-defined options, and losers who will accept the result | Agree the voters and the rule before the vote |
| variants | The system can serve both needs (configuration per tier, market or store; a feature flag; two product variants) at an acceptable cost | Each variant becomes its own requirement, usually in the `WHERE` pattern |
| overruling | Someone with authority must decide: time pressure, or the other techniques failed | Record who decided, by what authority and why; expect resistance |

### Analysis aids

| Aid | Use it to | Output in the decision record |
| --- | --- | --- |
| consider-all-facts | List every factor (rules, costs, risks, dependencies) before anyone argues for an option | Fact list with sources; assumptions marked |
| plus-minus-interesting | For each option, list what is good, what is bad, and what is neither but worth noting | One P / M / I list per option |
| decision matrix | Compare options on weighted criteria | Criteria and weights agreed and recorded first, then scores, then totals |

## Escalation rule

Relationship and structural conflicts are not the requirements engineer's to resolve, and an agent must not attempt it.

1. Register the conflict with the evidence and both positions, in neutral words. Quote behavior, not character.
2. Route: `escalate to <role>`: the parties' common manager for relationship conflicts; the sponsor, steering group or whoever owns the reporting line or budget for structural ones. If nobody is named, write `TBD` and add an open question for the product owner.
3. Leave every affected requirement as it is. Status of the conflict: `escalated`.
4. When the escalation owner reports back, the content part (if any) can be resolved with `/conflict-to-decision`, and the outcome is recorded there.
