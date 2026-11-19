# Splitting patterns and vertical slices

The patterns below follow Richard Lawrence's story-splitting patterns (Humanizing Work), reduced to the seven that cover most backlogs. Examples are on the loyalty-points sample project.

## Rules for every slice

1. **Vertical.** A slice reaches an outcome the role can observe: a screen, a receipt, a balance, an API response a partner system uses. "Build the voucher API", "create the database table" and "do the app screen" are layers, not slices.
2. **Valuable on its own.** If nobody would notice the slice shipped, merge it with its neighbor. Write the reason in the *Slicing* table column "Valuable on its own because".
3. **Thinnest end-to-end path first.** The first slice crosses every layer once with the simplest rule, one data variant and one interface. Later slices add rules, variants and interfaces.
4. **Every slice keeps an unwanted-behavior criterion.** Deferring the unhappy path means deferring the *recovery variants*, never the safe failure (refuse, show why, change nothing).
5. **Unknowns become spikes, not guesses.** A spike is a time-boxed question with a stated output. It has no R-ID; it is a work item.

## When to split

- *Small* fails by the team's sizing rule.
- The goal joins two goals with "and" / "or", or the story has two roles.
- The acceptance criteria cover several business rules, data variants or interfaces that could ship separately and each still be valuable.
- *Estimable* fails because of one unknown: split that unknown out as a spike.

## The seven patterns

| # | Pattern | Use when | How | Loyalty-points example |
| --- | --- | --- | --- | --- |
| 1 | Workflow steps | The story describes a sequence (create, use, cancel) | First slice: the simplest path from start to end. Later slices: the extra steps or the steps done manually today | Epic "Redeem points at checkout": (1) member spends a fixed voucher at the till, end to end; (2) support cancels an unused voucher |
| 2 | Business rule variations | The same action follows different rules | Slice per rule; the simplest rule goes first | Fixed SGD 5 voucher first; "any amount from 500 points" later |
| 3 | Data variations | The same action works on different kinds or sources of data | Slice per data variant; the most common first | Member-created vouchers first; campaign vouchers from Marketing later |
| 4 | Interfaces | The same capability is reached through several channels or devices | Slice per interface; the channel with most users first. Or a plain interface first, a richer one later | Earning at the POS first; earning in the app later |
| 5 | Happy / unhappy path | Error handling is large (retries, queues, manual recovery) | Happy path plus a safe failure first; recovery variants later | Voucher validation fails: first slice completes the sale without the discount; a later slice adds an offline voucher queue |
| 6 | Defer performance | Making it work and making it fast are both big | Functional slice first; the quality target becomes a quality requirement (Type Q) and its own slice | "Make voucher checks fast" goes to `/quality-requirements`; the story ships with a functional AC only |
| 7 | Spike | One unknown blocks estimating | Time-box a question; its output is a decision, a note or a story draft; the story follows the spike | "How are campaign vouchers issued in the legacy module (S-04)?" |

## Slicing table

Record the proposal in the stories file:

| Order | Slice | Pattern | Valuable on its own because |
| --- | --- | --- | --- |
| 1 | R-040 Spend 500 points as an SGD 5 voucher at the till | Workflow steps, business rule variation | A member can spend points at the till for the first time |
| later | Campaign vouchers | Data variation, after the spike | Waits for the spike "Campaign vouchers" |

## Anti-patterns

| Don't | Why | Instead |
| --- | --- | --- |
| Slice by layer (API, database, UI) | No slice delivers value; integration risk moves to the end | Thin end-to-end slice through all layers |
| "As a developer, I want ..." | A task, not a requirement | List it as a task under *Not stories*; find the user need it serves |
| Split by acceptance criterion count alone | Produces stories that cannot ship separately | Split by a pattern; keep criteria with their behavior |
| Defer the unwanted behavior entirely | The first release fails unsafely | Keep a safe failure in every slice |
| Hide a performance target in a criterion | It escapes the quality walkthrough and the architecture review | A Type Q requirement via `/quality-requirements` |
| Guess a size, time box or limit | Creates false precision | `TBD` and ask the team |
