# Definition of Ready: item menu

`re-setup` copies the base items, then the items for each chosen facet value and for a named criticality, in the order below, into `requirements/README.md` and into `schema.json` → `definition_of_ready`. Teams may reword or drop facet items. Base items stay unless the team records why in Setup history.

## Base (always)

- Has an ID, type, source, priority and rationale
- Passes re-lint check with no errors
- Has a verification method and a measurable acceptance criterion
- Open questions are resolved or explicitly deferred with an owner
- Dependencies and constraints are named

## Time: linear

- Is part of an agreed baseline

## Time: iterative

- Is written as a story with a benefit and acceptance criteria, one of them for unwanted behavior

## Purpose: prescriptive

- Is agreed by the change authority named in requirements/README.md
- Traces to a registered source (S-nn) in sources.csv

## Purpose: explorative

- States the assumption it tests and how the team will learn whether the assumption holds

## Target: customer-specific

- Is agreed by a named customer representative

## Target: market-oriented

- Is linked to a user segment and a market source (feedback, analytics or competitor), with a Kano guess

## Criticality named

- Cites the regulation, policy or contract clause in Source or Links where one applies
- Requirements touching personal data or audit evidence are reviewed by the compliance or data protection role
