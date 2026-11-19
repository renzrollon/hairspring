# Completeness check and WHILE requirements

## The state x event matrix

One row per state (final states included), one column per event (the creating event excluded). The first header cell must contain the words "state" and "event", for example `State / event`, so `check_states.py` can find the table. Events that never change this entity but can reach it may get their own column; every cell in that column is then `ignored` or `impossible`.

| Cell | Meaning | When to use it | Needs |
| --- | --- | --- | --- |
| `→ Target` | The diagram has this transition. | Copy the guard: `→ Posted [return window elapsed]`. When every transition in the cell is guarded and none is `[else]`, add `; else ignored (...)` or `; else impossible (...)`. | Nothing more; the diagram is the source. |
| `ignored (reason, source)` | The event can arrive in this state; the entity stays where it is and nothing changes. | Someone with authority said "that is fine, do nothing". | A source: `SH-01 2026-11-02`, an R-ID or a rule. |
| `impossible (reason, source)` | The event cannot arrive in this state. | The reason names what prevents it: a guard elsewhere, a timer that only runs in another state, another system that blocks it. | The reason. If another system prevents it, that is an assumption about that system: cite who confirmed it. |
| `TBD (Qn)` | Nobody knows yet. | Always, rather than guessing. | A matching row in Open questions with an owner. |

Decision rule for a blank cell:

1. Is there a transition in the diagram? Write `→ Target`.
2. Can the event physically reach the entity in this state? If no, and you can name what prevents it, write `impossible (...)`.
3. If yes, does a source say nothing should happen? Write `ignored (...)`.
4. Otherwise write `TBD (Qn)` and ask the owner: "When `<event>` arrives while the `<entity>` is `<State>`, what should happen: a transition to which state, nothing, or can it not happen?"

`-`, `n/a`, `?` and blank cells count as gaps.

## Checker findings

`python3 <skill-dir>/scripts/check_states.py <file>` prints one line per finding: `file:line: kind: message`. Exit code 0 means no findings, 1 findings, 2 a parse or usage error.

| Kind | Meaning | Fix |
| --- | --- | --- |
| `no-initial-state` | No `[*] --> State` line. | Add the creating transition. |
| `unreachable-state` | No path from the initial state reaches it. | Add the missing incoming transition with its source, or ask whether the state still exists. Do not delete it silently. |
| `dead-end` | Not final and no transition to another state (self-loops do not count). | Add the missing exit, or confirm it is final and add `State --> [*]`. |
| `ambiguous-transition` | Several transitions for one state and event, and the guards do not tell them apart. | Give each a distinct guard, one of them `[else]`. |
| `multiple-self-transitions` | A state has more than one self-transition. Mermaid draws only one of them, so readers miss the rest. | A second reaction that does not change the state usually means the entity now reacts differently: model it as its own state (see `OnHold` in the example). |
| `guard-without-else` | Every transition for the cell is guarded; nothing says what happens otherwise. | Add an `[else]` transition, or `; else ignored (...)` / `; else impossible (...)` in the cell. |
| `matrix-gap` | No transition and the cell is not `ignored` or `impossible`. | Ask; keep `TBD (Qn)` until answered. |
| `matrix-mismatch` | Matrix and diagram disagree (wrong target, a transition the other lacks, a blank cell for an existing transition). | Make them agree. The sourced one wins; if neither is sourced, ask. |
| `matrix-unclear-cell` | The cell does not start with `→`, `ignored`, `impossible` or `TBD`. | Rewrite the cell with one of the four forms. |
| `matrix-unknown-state` | A matrix row names a state that is not in the diagram. | Rename the row or add the state. |
| `no-matrix` | No matrix table found. | Add one; `--print-matrix` prints a skeleton. |

Run `--format json` when another tool reads the result.

## Deriving requirements

A behavior is state-dependent when the system must act differently because of the entity's state. Write one requirement per behavior, using the EARS state-driven pattern (Mavin et al., 2009). Use the glossary term for the entity and the system's name from `context.md` (for example "the loyalty service").

| Source in the model | Write | Example (loyalty-points) |
| --- | --- | --- |
| A state changes what the system allows, shows or counts for as long as the entity is in it | `WHILE <entity> is <State>, the <system> shall <response>.` | WHILE a points transaction is Pending, the loyalty service shall exclude its points from the member's redeemable balance. |
| One event column holds different responses in different states | One row per state: `WHILE <entity> is <State>, WHEN <event>, the <system> shall <response>.` | WHILE a points transaction is Posted, WHEN the POS sends a return for its purchase, the loyalty service shall deduct the transaction's points from the member's redeemable balance. |
| An `ignored` cell for an event that another actor or system sends | `WHILE <entity> is <State>, WHEN <event>, the <system> shall <leave ... unchanged / acknowledge ...>.` | WHILE a points transaction is Expired, WHEN the POS sends a return for its purchase, the loyalty service shall leave the member's points balance unchanged. |
| A transition whose event is handled in only one state | Not a `WHILE` requirement. Check that a `WHEN` or `IF ... THEN` requirement covers it; if none does, write `none: Qn` or a candidate in `Covered by` and hand it to `requirement-phrasing`. | `Posted --> Expired : expiryDateReached` needs an event-driven requirement once the expiry period is agreed. |
| An `impossible` cell | No requirement. The reason in the cell documents the dependency. | `impossible (POS blocks a second return, SH-01 2026-11-02)` |
| A `TBD` cell | No requirement until the open question is answered. Then rerun steps 5 to 7. | Redeemed x returnReceived waits for the negative-balance decision. |

Rules:

- One state per `WHILE` clause. If several states share a behavior, either the glossary names the group (then use the group name) or write one row per state.
- One `shall` per row; no `and` joining two actions.
- Do not repeat an existing requirement: link it in `Covered by` instead.
- Values nobody gave you (durations, limits, amounts) are `TBD` in the text, with an open question.
