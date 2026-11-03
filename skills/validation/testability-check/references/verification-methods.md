# Verification methods and test levels

Read at step 4. Pick the cheapest method that gives a convincing pass/fail answer. One method per requirement; mention a complementary check in the test idea if it matters.

## Method

| Method | Use when | Evidence it produces | Loyalty-points example |
| --- | --- | --- | --- |
| test | Behavior or a measurable quality can be exercised with defined inputs and an expected result | Test run with expected vs actual result | R-002 points rounding; R-065 second approver above 5,000 points; R-083 peak load |
| inspection | The requirement is met by what an artifact contains or omits: code, configuration, schema, document, screen text | Review record against a checklist, with the reviewer named | R-102 no payment card numbers stored (schema, payload mapping, log masking) |
| analysis | Proving it by running the system is impossible or too slow: long periods, rare events, statistics, models | Calculation, model or analysis of operational data | R-084 monthly availability from monitoring data |
| demonstration | The capability is shown working in a realistic setting and observed, without detailed measurement; often across a system you do not control | Witnessed session notes (who, when, what was seen) | R-042 the POS applies the voucher discount on a vendor test till |

Decision rules, in order:

1. Is the requirement about a document, code or configuration property (something present or absent)? Then **inspection**.
2. Can a test reach a pass/fail result within a release cycle, at acceptable cost? Then **test**. A long period is often testable with prepared data: back-dated records test a 7-year retention rule in seconds.
3. Does proof need long observation, statistics or a model (availability over a month, mean time between failures)? Then **analysis**.
4. Is the behavior in a system outside the boundary, or only meaningful when people see it working (vendor POS, store procedure)? Then **demonstration**.

## Level of the first check

| Level | Use when | Example |
| --- | --- | --- |
| unit | Logic inside one component, no I/O | Points calculation: SGD 1.99 earns 1 point |
| integration | The service with one real neighbor or interface: event consumer, database, fraud engine contract, clock | Purchase event in the S-02 format creates a pending transaction |
| e2e | A full user or system flow through the deployed stack: app, admin console, load and performance tests | Two support agents in the admin console approve an adjustment |
| manual | Inspection, analysis, demonstration, usability sessions, exploratory checks | Store-lab demonstration on a test till; monitoring analysis |

## Writing the first test idea

- Name the setup (data, accounts, clock, environment), the action, and the check.
- Put the boundary or failure case that matters most into the idea: exactly 500 points, exactly 5,000, 23 h 59 min vs 24 h, an expired voucher.
- Reuse identifiers from the sources (the S-02 event format, the TillPoint test till) so the test can be built without asking again.
