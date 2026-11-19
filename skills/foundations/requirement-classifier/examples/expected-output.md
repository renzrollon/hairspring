# Requirement classification: loyalty-points

Each batch sorts statements as they were given; nothing here is a requirement yet. Rows with Verdict `requirement` go to the skill in Next. The Kano column is a first guess from wording and domain; confirm it with stakeholders before it influences priority.

## Batch 2026-11-03: PRD section 4, Earning and balance

Input: `docs/prd-earning.md` (Mei Tan, SH-01, 2026-10-30).

| # | Statement | Source | Ref | Verdict | Type | Concern | Kano (guess) | Flags | Next |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | "Members earn 1 point per SGD 1 spent, rounded down per purchase." | docs/prd-earning.md:3 | - | requirement | F | F: points calculation per purchase | dissatisfier | rule, no-obligation | requirement-phrasing |
| 2 | "Today members collect points with a plastic card at the till." | docs/prd-earning.md:4 | - | fact | - | Describes today's process | - | current-state | none |
| 3 | "The app shows the member's points balance and the last 12 months of history." | docs/prd-earning.md:5 | - | requirement | F | F: balance and history shown in the customer mobile app | dissatisfier | compound, no-obligation | requirement-phrasing |
| 4 | "The balance must update within a few seconds after a purchase." | docs/prd-earning.md:6 | - | requirement | Q | Q: performance efficiency (time behavior) of the balance update | satisfier | weak-word, missing-value | quality-requirements |
| 5 | "Use Redis to cache balances so the app is fast." | docs/prd-earning.md:7 | - | solution | Q | Design choice (Redis) with no mandate; the need behind it is balance response time | - | weak-word | SH-08 (architect); clarifying-questions |
| 6 | "Transaction data must be kept for 7 years (Finance, policy DRP-2024)." | docs/prd-earning.md:8 | - | requirement | C | C: retention period set by Finance policy DRP-2024 | - | - | constraints-register |
| 7 | "The service has to run on the platform team's Kubernetes cluster." | docs/prd-earning.md:9 | - | requirement | C | C: hosting platform, if the platform team mandates it; otherwise a design choice | - | mandate-unconfirmed | constraints-register |
| 8 | "TillPoint will deliver POS release 2.2 with the voucher call in March." | docs/prd-earning.md:10 | - | fact | - | The POS vendor's delivery plan | - | will, dependency | system-context |
| 9 | "Support agents shall adjust points with a reason code, and adjustments above 5,000 points need a second approver." | docs/prd-earning.md:11 | - | requirement | F | F: points adjustment by support agents, with a second approver above a limit | dissatisfier | compound | requirement-phrasing |
| 10 | "Members get bonus points on their birthday." | docs/prd-earning.md:12 | - | requirement | F | F: birthday bonus | delighter | no-obligation, missing-value | requirement-phrasing |
| 11 | "Make collecting points fun so members engage more with the app." | docs/prd-earning.md:13 | - | goal | - | Desired outcome with no checkable result | - | weak-word | clarifying-questions |
| 12 | "The admin console must be easy to use for support agents." | docs/prd-earning.md:14 | - | requirement | Q | Q: interaction capability (usability) of the admin console for support agents | satisfier | weak-word, missing-value | quality-requirements |
| 13 | "Points data must not leave Singapore." | docs/prd-earning.md:15 | - | requirement | C | C: data residency; the law or policy that imposes it is not named | - | mandate-unconfirmed | constraints-register |
| 14 | "Members should be able to see why their points are still pending." | docs/prd-earning.md:16 | - | requirement | F | F: reason for pending points shown to the member | satisfier | - | requirement-phrasing |

Summary: 14 statements: 5 F, 2 Q, 3 C requirements; 1 solution; 2 fact; 1 goal; 0 unclear.

### Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | How many seconds after a purchase must the new balance be visible in the app? | SH-01 | 4 |
| 2 | Which balance response time, at which load, is the cache meant to achieve? | SH-08 | 5 |
| 3 | Is running on the platform team's Kubernetes cluster a platform policy, or this team's design choice? | SH-08 | 7 |
| 4 | Which law or company policy requires points data to stay in Singapore? | SH-04 | 13 |
| 5 | How many bonus points does a member get on their birthday? | SH-01 | 10 |
| 6 | Which measurable outcome stands for "fun" and "engage more", for example a usage measure in the app? | SH-01 | 11 |
| 7 | For which support tasks must the admin console be easy, and how would we measure it (time per task, errors)? | SH-06 | 12 |
