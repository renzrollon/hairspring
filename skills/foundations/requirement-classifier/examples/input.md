# Input: PRD section 4 of the loyalty-points service (Harbourline sample)

Prompt: "Sort these into requirements before we phrase them." The section is `docs/prd-earning.md`, written by Mei Tan (SH-01, Head of Loyalty) on 2026-10-30. Line numbers below are the file's.

```markdown
1  ## 4. Earning and balance
2
3  Members earn 1 point per SGD 1 spent, rounded down per purchase.
4  Today members collect points with a plastic card at the till.
5  The app shows the member's points balance and the last 12 months of history.
6  The balance must update within a few seconds after a purchase.
7  Use Redis to cache balances so the app is fast.
8  Transaction data must be kept for 7 years (Finance, policy DRP-2024).
9  The service has to run on the platform team's Kubernetes cluster.
10 TillPoint will deliver POS release 2.2 with the voucher call in March.
11 Support agents shall adjust points with a reason code, and adjustments above 5,000 points need a second approver.
12 Members get bonus points on their birthday.
13 Make collecting points fun so members engage more with the app.
14 The admin console must be easy to use for support agents.
15 Points data must not leave Singapore.
16 Members should be able to see why their points are still pending.
```

Workspace: `requirements/glossary.md` defines Member, Points, Purchase, Admin console and Support agent. `requirements/stakeholders.md` lists SH-01 Mei Tan, SH-03 Grace Lim (Finance), SH-04 Farid Osman (data protection officer), SH-06 Daniel Ng (support lead), SH-08 Wei Jie Chua (platform tech lead). No `classification.md` exists yet.
