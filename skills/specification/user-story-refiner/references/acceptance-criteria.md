# Acceptance criteria in Given/When/Then

Given/When/Then comes from behavior-driven development (Dan North) and the Gherkin language used by Cucumber. Examples are on the loyalty-points sample.

## Shape

```markdown
**R-040.AC3: Not enough posted points** _(unwanted behavior)_
- **Given** a member with 300 posted points and 400 pending points
- **When** the member asks the app for an SGD 5 voucher
- **Then** the app refuses the voucher
- **And** the app shows the posted balance of 300 points and the 500-point minimum
- **Flag:** <only when needed>
```

| Line | Rule |
| --- | --- |
| Label | `<story ID>.AC<n>: <short name>` in bold, then the kind in italics: `_(happy path)_`, `_(alternative)_` or `_(unwanted behavior)_` |
| Given | The state before the trigger, with concrete values (balances, statuses, roles). Several facts may be joined with `And` lines |
| When | Exactly one trigger: one action by one actor, or one event |
| Then | An outcome someone outside the code can observe: what a screen, receipt, API response, message or record shows. No internal method calls |
| And | Further outcomes of the same trigger, checked together |
| Flag | `blocked by Qn (<what is TBD>)` or `untestable: <reason>; routed to testability-check` |

## Which criteria a story needs

1. The happy path (one per distinct outcome).
2. One criterion per business rule the story applies (minimum amounts, limits, rounding, approvals).
3. **At least one unwanted behavior.** Pick from the catalogue below the cases the role would actually meet.

A story that needs many criteria to cover several independent rules or data variants is a split signal (*Small*).

## Unwanted-behavior catalogue

| Case | Ask | Loyalty-points example |
| --- | --- | --- |
| Invalid or incomplete input | What if a field is missing or malformed? | Voucher code that does not exist |
| Rule violated | What if the request breaks a business rule? | Fewer than 500 posted points; adjustment above 5,000 points without a second approver |
| Wrong state | What if the object is in a state that forbids the action? | Voucher already Applied, Cancelled or Expired |
| External system fails or is slow | What if a system in the context does not answer? | Loyalty service does not answer the POS within the POS timeout |
| Duplicate or replayed action | What if the same request arrives twice? | Same voucher scanned at two tills |
| Concurrent change | What if two actors change the same thing? | Support cancels a voucher while a cashier scans it |
| Missing permission | What if the actor is not allowed? | A cashier tries to cancel a voucher |
| Limit reached | What if a quota or limit is hit? | Member reaches the maximum vouchers per day (if a rule says so; otherwise ask) |

Only write a case whose expected outcome you know from the input, a business rule or an answer. If the case matters but the outcome is unknown, write the criterion with `Then TBD (Qn: <options>)` and flag it blocked.

## Testable, blocked, untestable

| Verdict | Means | Example | Do |
| --- | --- | --- | --- |
| testable | A tester can set up the Given, perform the When and decide the Then as pass or fail | "Then the POS deducts SGD 5 from the purchase total" | nothing |
| blocked | Testable once an open question is answered | "Then the POS completes the sale without the discount after TBD seconds" | `**Flag:** blocked by Q2 (POS timeout)` |
| untestable | The outcome is subjective, unobservable or has no pass threshold even with values | "Then the cashier finds it easy", "Then the error is nice", "Then it is fast", "Then the cashier completes it without help" | `**Flag:** untestable: <reason>; routed to testability-check` |

Do not turn an untestable criterion into a measurable one by inventing a threshold ("in under 3 seconds", "8 of 10 cashiers"). `testability-check` proposes the measurable form and the stakeholder confirms it.

## Anti-patterns

| Don't | Instead |
| --- | --- |
| Two triggers in one When ("converts the points and scans the voucher") | Two criteria |
| Then describes implementation ("calls `POST /vouchers`") | Describe what the role or the partner system observes |
| Vague words in Then (quickly, correctly, properly, nice) | A value, a state or a visible element; `TBD` if unknown |
| Values outside the business rules ("Given 750 points worth SGD 9") | Use the sample's rules (100 points = SGD 1) |
| A quality target as a criterion ("Then the response time is under 200 ms") | A Type Q requirement via `/quality-requirements` |
