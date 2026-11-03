# Use case form guide

The form follows the structure of Alistair Cockburn's fully dressed use case (*Writing Effective Use Cases*, 2001), in our own words. Examples are on the loyalty-points sample.

## Fields

| Field | What to write | Test | Example |
| --- | --- | --- | --- |
| Use case | Verb and object, from the primary actor's view. | Would the actor say "I want to ..." with these words? | Redeem voucher |
| Primary actor | The role that wants the goal and starts the use case. One role. | Is it a role from `stakeholders.md` or `context.md`, not a person's name or a screen? | Member (via the customer mobile app) |
| Supporting actors | Roles and systems the system under design needs to reach the goal. | Does the scenario name them in a step? | Cashier (via TillPoint POS); fraud engine |
| Goal in context | One sentence: what the primary actor wants and why. | Does it name the outcome, not the steps? | The member pays part of a purchase with points. |
| Scope | The system under design, as a black box. | Is it the system in `context.md`, not "the app and everything"? | Loyalty-points service |
| Level | Summary, user goal or subfunction (see the level tests). | Do the steps match the level? | User goal |
| Trigger | The event that starts the use case. | Is it an event, not a state? | The member chooses to redeem points. |
| Stakeholders and interests | Each stakeholder and what the use case must protect for them. | Does every interest show up in a step, an extension or a guarantee? | SH-03 Finance: voucher value matches the points deducted. |
| Preconditions | What the system can rely on at the start; it does not check these again. | Would the use case be wrong to start without it? | The member is identified to the loyalty service. |
| Minimal guarantee | What holds even when the goal fails. | Does every exception end with it true? | The points balance changes only when a voucher is issued. |
| Success guarantee | What is true for every stakeholder after success. | Does the last step make it true? | The voucher is applied; the balance is reduced by the redeemed points. |
| Main success scenario | 3 to 9 numbered steps, no conditions. | Can you read it aloud as one story without "if"? | see step patterns |
| Alternatives | Extensions after which the goal is still reached. | Does it end with "resume at step N" or "ends in success"? | 2a. Requested points exceed the redeemable balance |
| Exceptions | Extensions after which the goal is abandoned. | Does it end with "ends in failure", and does the minimal guarantee hold? | 4a. The fraud engine places a hold |
| Business rules | Rules the steps apply, numbered `BR1`, `BR2` (labels local to this file), each with a source. | Is every rule cited by at least one step? | BR2: minimum redemption 500 points (S-01) |
| Open issues | Questions that block a field or an extension, numbered `Q1`, `Q2` (local to this file), with an owner. | Does every `TBD` point to one? | Q4: voucher expiry period |

## Level tests

| Level | Test | Example |
| --- | --- | --- |
| Summary | The goal spans several sittings or several user goals; its steps are use cases themselves. | Take part in the loyalty programme |
| User goal | One sitting or one visit, after which the primary actor can walk away with what they came for; a person would do it for its own sake. | Redeem voucher; Adjust member points |
| Subfunction | Part of other use cases; nobody does it for its own sake. Write one only when several use cases share it, and link it with «include». | Validate voucher code; Look up member |

If the steps of a "user goal" read like clicks and fields, it is too low. If each step is a whole process, it is too high.

## Step patterns

| Pattern | Form | Example |
| --- | --- | --- |
| Actor action | `<Actor> <verb> <object>.` | Member asks to redeem a number of points. |
| System check | `<System> checks that <condition> (BRn).` | Loyalty service checks that the amount is at least the minimum (BR2) and within the member's redeemable balance (BR3). |
| System action | `<System> <verb> <object>.` | Loyalty service issues a single-use voucher worth SGD 1 per 100 points (BR1), deducts the points and returns the voucher code. |
| Request to a supporting actor | `<System> sends <what> to <supporting actor> for <purpose>.` | Loyalty service sends the redemption to the fraud engine for scoring. |
| Supporting actor answer | `<Supporting actor> returns <what>.` | Fraud engine returns a score with no hold. |

Rules:

- Present tense, one intention per step, the acting role first.
- Name the system as `context.md` does ("Loyalty service"), and data with glossary terms.
- A step may cover one request and its response; a step does not hide a decision.
- No user-interface or technology words. They are design decisions: route them to the architect or the UX designer and keep the intention.

## Extensions

- **Number** each condition with its step and a letter (`2a`, `2b`), its sub-steps with a number (`2a1`, `2a2`). `*a` applies at any step; `3-5a` to a range.
- **Condition** is something the system or an actor can detect: "The requested points exceed the redeemable balance", not "error" or "invalid input".
- **End** every extension with one of: `resume at step N`, `use case ends in success`, `use case ends in failure`.
- **Alternative or exception:** if the goal is still reached, it is an alternative; if not, an exception, and the minimal guarantee must hold at its end.
- **Find them** by asking at every step: invalid or missing input? the supporting actor says no, or does not answer? the thing is already used, expired or unknown? the actor cancels or goes away? the system cannot reach another system?
- **Unknown response:** write the condition under Exceptions with the action `TBD (Qn); use case ends in failure` until the answer says otherwise (without an answer the goal cannot be reached safely). A known condition with an unknown response is still a finding worth recording.

## Requirement links

| Step kind | Requirement form | Example |
| --- | --- | --- |
| System step in the main scenario | `WHEN <trigger>, the <system> shall <response>.` | WHEN the fraud engine returns no hold for a redemption, the loyalty service shall issue a single-use voucher to the member. |
| System step in an exception | `IF <condition>, THEN the <system> shall <response>.` | IF the fraud engine places a hold on a redemption, THEN the loyalty service shall leave the member's points balance unchanged without issuing a voucher. |
| System check | Often already covered by a business-rule requirement; link it | R-040 (minimum 500 points) |
| Actor step (primary or supporting actor) | none | `none: actor step` |
| System step whose response is `TBD` | none yet | `none until Qn` |

One requirement per sentence and one `shall`. If a step needs two requirements, link both.
