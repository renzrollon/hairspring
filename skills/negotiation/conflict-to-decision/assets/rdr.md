# RDR-nnn: {decision topic in a few words}

- Status: proposed
- Date: {YYYY-MM-DD}
- Decision-makers: {Name (SH-nn, role)}
- Consulted: {Name (SH-nn, role)}
- Informed: {names or roles}
- Conflict: CF-nn ({type}) | unregistered
- Technique: {agreement | compromise | voting | variants | overruling}; analysis aid: {consider-all-facts | plus-minus-interesting | decision matrix | none}
- Affected requirements: R-nnn, R-nnn
- Supersedes: none

## Context and Problem Statement

{What conflicts, between whom, and why it must be decided now. End with the decision question?}

## Decision Drivers

### Constraints

| Constraint | Source |
| --- | --- |
| {mandate that bounds every option} | {S-nn, policy, contract, person and date} |

### Criteria

| Criterion | Weight | Agreed by | Agreed on |
| --- | --- | --- | --- |
| {criterion} | {weight, or n/a without a decision matrix} | {names} | {YYYY-MM-DD} |

### Facts and assumptions

| # | Statement | Kind | Source or owner to verify |
| --- | --- | --- | --- |
| 1 | {statement} | {fact \| assumption} | {source \| owner} |

## Considered Options

1. **{Option name}**: {one line}. Requirement changes: {R-IDs and how}.
2. **{Option name}**: {one line}. Requirement changes: {R-IDs and how}.

## Decision Outcome

Chosen option: "{Option name}", because {reasons tied to the decision drivers}.

| Decision-maker | Confirmed | Date |
| --- | --- | --- |
| {Name (SH-nn)} | {yes \| pending} | {YYYY-MM-DD} |

Dissent: {Name (SH-nn): reason} | none

### Consequences

- Good, because {effect}.
- Bad, because {effect, including what the losing side gives up}.

### Confirmation

- {How to check the decision was carried out: requirement updates applied, lint clean, verification or trace evidence.}

## Pros and Cons of the Options

### {Option name}

- Plus: {good effects}
- Minus: {bad effects}
- Interesting: {neither, but worth noting}

### Decision matrix

{Only when a decision matrix was used; otherwise write "Not used."}

| Criterion | Weight | {Option} | {Option} |
| --- | --- | --- | --- |
| {criterion} | {w} | {score} ({w x score}) | {score} ({w x score}) |
| **Weighted total** (max {n}) | | **{total}** | **{total}** |

Scale: {agreed scale}. Scored by: {names}, {YYYY-MM-DD}.

## Requirement Updates

| Requirement | Change | Before | After | Applied |
| --- | --- | --- | --- | --- |
| R-nnn | {keep \| rewrite \| new \| reject \| withdraw} | {Status, Links, Text before} | {Status, Links, Text after} | no |

## More Information

- Open questions: {question (owner)} | none
- Follow-ups: {action (owner)} | none
- Review trigger: {date or event} | none
- Related: {CF-nn in requirements/conflicts.md, docs/adr/..., reviews, prototypes}
