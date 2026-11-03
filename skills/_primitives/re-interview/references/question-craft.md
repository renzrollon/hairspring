# Question craft

## Patterns by type

| Type | Ask about | Pattern | Example (loyalty-points) |
| --- | --- | --- | --- |
| Boundary | What is inside the system, what is outside, what is a grey zone | "Is `<X>` something our system does, something it talks to, or out of scope?" | "Is the points-expiry batch job part of the loyalty service, or does the data platform own it?" |
| Actor | Who triggers, who receives, who is affected | "Who starts `<action>`? Who else sees the result?" | "Who can reverse a points transaction: the cashier, the store manager, or support?" |
| Data | Which entities, which fields, how much | "Which `<entities>` and which fields? How many at most?" | "How many transactions can one member have per day at most?" |
| Behavior | Normal flow, alternatives, errors | "What should happen when `<event>` and `<condition>`?" | "What happens when the POS is offline at checkout?" |
| Quality | Performance, reliability, security, usability, compatibility, maintainability, portability, safety | "How fast / how often / how available, measured how, under which load?" | "How quickly must a balance update be visible in the app after a purchase?" |
| Constraint | Mandates from outside the team | "Who requires `<X>`? What happens if we don't?" | "Is the 12-month expiry a legal requirement or a marketing choice?" |
| Rationale | Why it matters | "What problem does `<X>` solve? What breaks without it?" | "Why must support see the full transaction history?" |
| Priority | What can wait | "If we could only ship one of these this quarter, which one?" | "Earn at POS or redeem in the app first?" |

## Probes

- **Quantify:** "What number would make you say it is too slow?"
- **Example:** "Walk me through the last time this happened."
- **Exception:** "And when it goes wrong?"
- **Boundary:** "Where does this stop being our problem?"
- **Absolute words:** when you hear *all*, *always*, *never*, ask "Are there any exceptions?"
- **Vague words:** when you hear *fast*, *easy*, *secure*, ask "How would we test that?"

## Anti-patterns

| Don't | Why | Instead |
| --- | --- | --- |
| Ask two things in one question | Half the answer gets lost | Split into two questions |
| Ask "Do you want X?" | The answer is always yes | Ask what X is worth against something else |
| Ask for a solution ("Should we use Redis?") | That is a design decision, not a requirement | Ask for the quality needed ("How many sessions at peak? How fast?") |
| Lead the witness | Confirms your assumption | Offer options including "none of these" |
| Ask what the code or docs already answer | Wastes the person's time | Read first, then confirm |
| Fill a gap with a plausible number | Creates a false requirement | Write `TBD` and log the question |

## Recording format

Inside the calling skill's work product:

```markdown
| # | Group | Question | Recommended answer | Answer | Source | Becomes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Boundary | Is the points-expiry batch in scope? | Yes, we own it | Out of scope; data platform owns it | PO 2026-11-03 | D-01 closed |
| 2 | Quality | How fast must a new balance show in the app? | Within 5 s | TBD | owner: PO | open |
```
