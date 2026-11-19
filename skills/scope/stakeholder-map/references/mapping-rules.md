# Mapping rules

## 1. Influence

`high` when the stakeholder can approve, block, fund or delay the system or its release: sign-off authority, a veto (security, data protection, legal), budget ownership, control of a platform, a release window or a contract. Otherwise `low`. `TBD` when the evidence does not say, plus an open question.

Ask: "Could `<role>` stop or delay go-live?"

## 2. Interest

`high` when the system changes the stakeholder's daily work, their goals or the measures they are judged by, or when they asked to be involved. Otherwise `low`. `TBD` when the evidence does not say, plus an open question.

Ask: "Does the system change how `<role>` works or what `<role>` is measured on?"

There is no `medium`. If a rating is genuinely in between, ask the question above; the answer is yes or no.

## 3. Engagement

| Influence | Interest | Engagement | What it means in practice |
| --- | --- | --- | --- |
| high | high | manage closely | In refinement or workshops; agrees requirements in their area |
| high | low | keep satisfied | Short, targeted check-ins before decisions in their area; sign-off where they hold it |
| low | high | keep informed | Demos, release notes, a feedback channel |
| low | low | monitor | Re-check at each release |
| TBD | any | TBD | Ask the open question first; not plotted |
| any | TBD | TBD | Ask the open question first; not plotted |

## 4. Goals and availability

- **Goals:** what the stakeholder wants from the system or worries about, in one sentence in their words: "No slower checkout during the year-end peak." Not their job description.
- **Availability:** how and when they can be reached, as stated: "Tue and Thu store visits; 30-minute calls", "fortnightly privacy clinic", "via vendor ticket portal". `TBD` when nobody said.

## 5. Representatives and proxies

- The stakeholder is the role; the representative is the named person who speaks for it now. When the person changes, keep the SH-ID and update Representative and Source.
- A user group too large to name (members, cashiers) needs a proxy: a named person who knows the group (the support lead for members, the store operations lead for cashiers) or a source that captures their voice (a ticket export, app reviews). Write the proxy in Representative as `proxy: <name or S-nn>`, or `TBD` with candidate proxies in an open question.
- A role with no named representative is a gap even when it has a row: requirements cannot be elicited from a role.

## 6. Quadrant coordinates

Mermaid `quadrantChart` places quadrant 1 top right, 2 top left, 3 bottom left and 4 bottom right. With x = interest and y = influence, the quadrants are: 1 manage closely, 2 keep satisfied, 3 monitor, 4 keep informed.

Base point of each cell: `high` = 0.75, `low` = 0.25, so a high-interest, low-influence stakeholder sits at `[0.75, 0.25]`.

Stakeholders in the same cell are spread so labels stay readable. Order them by SH-ID; the k-th one gets this offset (x, y) from the base:

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| offset | 0, 0 | 0, +0.08 | 0, -0.08 | 0, +0.16 | 0, -0.16 | +0.12, 0 | +0.12, +0.08 | +0.12, -0.08 | +0.12, +0.16 | +0.12, -0.16 |

Every offset keeps the point inside its quadrant. More than 10 in one cell: split the chart by area (for example internal and external). The position inside a quadrant carries no meaning; say so under the chart.

## 7. Label rules

- Label: `SH-nn <short role>`, for example `SH-04 Data protection`.
- Letters, digits, spaces and hyphens only. Parentheses, colons, commas and quotes break the chart in some renderers.
- Role, not personal name: names are in the table.
