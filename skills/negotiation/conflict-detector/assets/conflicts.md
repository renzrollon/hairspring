# Conflict register

<!-- Owned by conflict-detector. conflict-to-decision updates the Status and Decision columns and the Status line of a detail block. Never delete an entry: set Status to not-a-conflict with the reason. -->

| Field | Value |
| --- | --- |
| Last scan | YYYY-MM-DD |
| Scanned | requirements/requirements.csv (<n> requirements; withdrawn and rejected skipped)<, other files> |
| Schema | requirements/schema.json \| defaults (no schema.json found) |

## Register

| ID | Subject | Kind | Requirements | Stakeholders | Type | Recommended technique | Route | Status | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CF-nn | <subject in glossary terms> | <kind> | R-nnn, R-nnn | SH-nn, SH-nn | <type> | <technique>; aid: <analysis aid> | /conflict-to-decision CF-nn \| escalate to <role> | open | |

Kind: `contradiction` | `overlap` | `inconsistent conditions` | `differing level of detail` | `priority disagreement`.
Type: `subject matter` | `data` | `interest` | `value` | `relationship` | `structural`.
Technique: `agreement` | `compromise` | `voting` | `variants` | `overruling` | `none (escalation)`.
Aid: `consider-all-facts` | `plus-minus-interesting` | `decision matrix` | `none`.
Status: `open` | `escalated` | `resolved` | `not-a-conflict`. Decision: `RDR-nnn`, or the escalation outcome and date.

## CF-nn: <subject>

- **Kind:** <kind>
- **Requirements:** R-nnn "<colliding clause>" (Source: <source>) vs R-nnn "<colliding clause>" (Source: <source>)
- **Positions:**
  - <SH-nn Name (role)>: <position in one line> (<where stated>)
  - <SH-nn Name (role)>: <position in one line> (<where stated>)
- **Why it is a conflict:** <one sentence: why both cannot hold for the same scope and time>
- **Type:** <type>, because <answer to the root-cause question>
- **Recommended technique:** <technique>, because <reason>. Analysis aid: <aid>.
- **Route:** /conflict-to-decision CF-nn; decision-makers: <names or roles, or TBD> | escalate to <role>
- **Open questions:** <question> (owner: <role>) | none
- **Status:** open

## Checked, not a conflict

| Requirements | Looked like | Why not a conflict |
| --- | --- | --- |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
