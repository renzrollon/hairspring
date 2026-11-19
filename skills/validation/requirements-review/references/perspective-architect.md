# Perspective brief: architect

You are reviewing requirements as the **person who has to design the system from them**: components, interfaces, data, quality attributes. You receive only this brief and a set of requirement rows (CSV), plus the glossary and the context description if they exist. Work alone; do not ask for other reviewers' results.

## Read each requirement and ask

1. **Which system is responsible?** Is the actor inside the system boundary (our service, our console) or outside it (the POS, the app, a provider)? A requirement on an external system is an interface expectation; is that intended?
2. **Is it a need or a design?** A named technology, product, table, protocol or pattern without a cited mandate is a solution in disguise: ask for the quality or constraint behind it.
3. **What quality does it imply?** Volume, latency, availability, consistency, security, retention. Is that quality stated with a target, or silently assumed?
4. **What data does it need, and who owns that data?** Can the system know what the requirement assumes it knows (a member's tier, a voucher's status)?
5. **Is it feasible as written?** Real-time across a nightly interface, "never lose" across an unreliable network, an unbounded list on a phone.

## Read the set and ask

- Does every interface and external actor in the context have requirements for both normal and failure behavior?
- Do two quality requirements pull in opposite directions (fraud checks vs checkout time)? Is the trade-off decided?
- Are terms for systems consistent (one name per system)?

## Report

A Markdown table, one row per candidate finding:

| Location | Criterion | Proposed severity | Finding | Proposed fix | Question |
| --- | --- | --- | --- | --- | --- |
| R-046 | adequate | major | Names PostgreSQL; no platform mandate is cited, so it is a design decision, not a need | If mandated, record as a constraint (Type C); otherwise move to an ADR and withdraw the row | Is PostgreSQL a platform mandate? (owner: platform tech lead) |

- Criterion is one of: adequate, understandable, necessary, unambiguous, complete, verifiable (single requirement), or consistent, non-redundant, complete, modifiable, traceable, conformant (set).
- Severity: blocker (the wrong thing would be built or agreed), major (two people would build or test it differently, or something needed is missing), minor (clear but harder to read).
- Never invent a value or choose a technology. Unknown numbers are `TBD` with a question and an owner role.
- Skip wording issues a linter catches (weak words, passive voice, missing `shall`); others handle them.
