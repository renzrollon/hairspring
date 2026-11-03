# Stories: <Epic title>

| Field | Value |
| --- | --- |
| Epic | <tracker key and title, or none> |
| Source | <source ID, ticket key, or person and date> |
| Refined | <YYYY-MM-DD>, <who took part>, user-story-refiner |
| Schema | requirements/schema.json \| defaults (no schema.json found) |
| Definition of Ready | schema.json `definition_of_ready` \| defaults |

## Summary

| Story | Title | Priority | INVEST | DoR | Acceptance criteria | Flags |
| --- | --- | --- | --- | --- | --- | --- |
| R-nnn | <title> | <must \| should \| could \| wont \| TBD> | <n>/6 pass | <ready \| not ready> | <n> (<n> unwanted behavior) | <flagged criterion IDs, or none> |

## Slicing

| Order | Slice | Pattern | Valuable on its own because |
| --- | --- | --- | --- |
| <1, 2, ... or later> | <R-nnn title, or a slice not yet written> | <pattern from references/splitting-patterns.md> | <one line> |

## R-nnn: <Title>

<!-- paste-start R-nnn -->
**Story:** As a <role>, I want <goal>, so that <benefit>.

**Acceptance criteria**

**R-nnn.AC1: <short name>** _(happy path)_
- **Given** <state before the trigger, with concrete values>
- **When** <one trigger>
- **Then** <observable outcome>

**R-nnn.AC2: <short name>** _(unwanted behavior)_
- **Given** <state>
- **When** <one trigger>
- **Then** <observable outcome>
- **Flag:** <only when needed: blocked by Qn (<what is TBD>) \| untestable: <reason>; routed to testability-check>

**Notes:** Source <source> · Priority <priority> · Depends on <R-IDs or none> · Constraints <R-IDs, source IDs or none> · Open questions <Qn, ... or none>
<!-- paste-end R-nnn -->

**INVEST**

| Criterion | Result | Evidence |
| --- | --- | --- |
| Independent | <pass \| fail> | <one line> |
| Negotiable | <pass \| fail> | <one line> |
| Valuable | <pass \| fail> | <one line> |
| Estimable | <pass \| fail> | <one line> |
| Small | <pass \| fail> | <one line> |
| Testable | <pass \| fail> | <one line> |

**Definition of Ready**

| Item | Result | Evidence |
| --- | --- | --- |
| Has an ID, type, source, priority and rationale | <pass \| fail \| n/a> | <one line> |
| Passes re-lint check with no errors | <pass \| fail \| n/a> | <one line> |
| Has a verification method and a measurable acceptance criterion | <pass \| fail \| n/a> | <one line> |
| Open questions are resolved or explicitly deferred with an owner | <pass \| fail \| n/a> | <one line> |
| Dependencies and constraints are named | <pass \| fail \| n/a> | <one line> |

<!-- Repeat the "## R-nnn" section for every story. The Definition of Ready rows above are the defaults; use the items of requirements/schema.json `definition_of_ready` when it exists. -->

## Spikes

| Spike | Question to answer | Output | Time box | Owner |
| --- | --- | --- | --- | --- |
| <short name> | <question> | <decision, note or story draft> | <team's time box or TBD> | <role or person> |

## Not stories

| Statement | Source | It is | Routed to |
| --- | --- | --- | --- |
| "<quoted input>" | <source> | <quality requirement \| constraint \| design decision \| task \| fact> | <skill, person or none> |

## Open questions

| # | Question | Recommended answer | Owner | Affects | Status |
| --- | --- | --- | --- | --- | --- |
| Q1 | <one question> | <answer to confirm, or a reference to look up> | <stakeholder ID and name, or role> | <R-nnn.ACn, R-nnn, or a slice> | <open \| answered \| deferred> |
