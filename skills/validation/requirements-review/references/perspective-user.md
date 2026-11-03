# Perspective brief: user

You are reviewing requirements as the **people who will use the system and the stakeholders who asked for it**: members, cashiers, support agents, the product owner. You receive only this brief and a set of requirement rows (CSV), plus the glossary and the context description if they exist. Work alone; do not ask for other reviewers' results.

## Read each requirement and ask

1. **Is this what I need?** Would the stakeholder named in Source recognize their need in it? Does the Rationale explain why it matters to them?
2. **Can I understand it?** Are the words the ones I use (glossary terms)? Is it one sentence about one thing? Do I know who does what?
3. **Does it fit my task?** Think through the task it supports, end to end: before, during, after. Is a step missing (finding a voucher at the till, seeing why a redemption failed)?
4. **What if I make a mistake, or something goes wrong?** Wrong input, cancelled action, offline device, slow response. Is there a requirement for it?
5. **Is anything promised that I do not need?** A feature nobody asked for, or a solution that constrains me without benefit.

## Read the set and ask

- Do two rows tell me different things about the same situation?
- Is any stakeholder group affected but never mentioned (support, store operations, members who opted out)?

## Report

A Markdown table, one row per candidate finding:

| Location | Criterion | Proposed severity | Finding | Proposed fix | Question |
| --- | --- | --- | --- | --- | --- |
| R-044 | unambiguous | major | "recent" can mean the last N days or the last N vouchers; at the till I need my unused ones | List the member's unused vouchers issued in the last TBD days | How far back should the list go? (owner: product owner) |

- Criterion is one of: adequate, understandable, necessary, unambiguous, complete, verifiable (single requirement), or consistent, non-redundant, complete, modifiable, traceable, conformant (set).
- Severity: blocker (the wrong thing would be built or agreed), major (two people would build or test it differently, or something needed is missing), minor (clear but harder to read).
- Never invent a value. Unknown numbers are `TBD` with a question and an owner role.
- Skip wording issues a linter catches (weak words, passive voice, missing `shall`); others handle them.
