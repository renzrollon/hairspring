# View: Architect: agreed quality requirements and constraints by component

| Field | Value |
| --- | --- |
| View | architect (schema.json → views.architect) |
| Audience | SH-05 Lena Koh, SH-08 Wei Jie Chua |
| Selective (filter) | Type in Q, C; Status in agreed, implemented, verified |
| Projective (columns) | ID, Type, Component, Text, Source, Status, Risk, Rationale |
| Aggregating (group by) | Component |
| Columns not in the register | none |
| Source | requirements/requirements.csv |
| Generated | 2026-11-03 |

## Counts

| Component | Count |
| --- | --- |
| earn | 1 |
| balance | 0 |
| redeem | 0 |
| expiry | 0 |
| admin | 1 |
| platform | 2 |
| Total | 4 |

## Requirements

| ID | Type | Component | Text | Source | Status | Risk | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-081 | Q | earn | The loyalty service shall accept purchase events at TBD events per minute without loss during the year-end sale. | SH-08 | agreed | high | Last year's peak was about 9,000 purchases per minute (SH-08). |
| R-082 | Q | admin | The admin console shall require multi-factor authentication when a support agent logs in. | SH-05 | agreed | medium | Adjustments move member value (SH-05). |
| R-100 | C | platform | The loyalty service shall retain points transaction records for 7 years. | S-05 | agreed | low | Audit retention under DRP-2024. |
| R-101 | C | platform | The loyalty service shall run on the platform team's Kubernetes platform. | SH-08 | agreed | low | Platform mandate (SH-08). |
