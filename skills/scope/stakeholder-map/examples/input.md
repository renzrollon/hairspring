# Input: `/stakeholder-map` for the loyalty-points service (Harbourline sample)

Run on 2026-11-04 by Wei Jie Chua (SH-08). `requirements/context.md` exists (the `system-context` example): it lists the TillPoint POS, the customer mobile app, Relay CRM, the fraud engine, the notification provider and the data warehouse, and members, cashiers and support agents as persons. The programme terms and conditions (S-01) and retention policy DRP-2024 (S-05) are in its context boundary. No `stakeholders.md` exists yet.

## Roster: `notes/stakeholder-roster.md` (Mei Tan, SH-01, 2026-11-03)

```markdown
1  # Loyalty-points kick-off roster
2
3  | Name | Role | Cares about | Can block or sign off? | Changes their daily work? | Availability |
4  | --- | --- | --- | --- | --- | --- |
5  | Mei Tan | Head of Loyalty, product owner | Programme rules, member growth | Yes, owns the budget | Yes | Daily, Slack #loyalty |
6  | Arjun Pillai | Store operations lead | Checkout must not get slower; cashier training | Yes, can stop the store rollout | Yes | Tue and Thu store visits; 30-minute calls |
7  | Grace Lim | Finance controller | Points liability, month-end close | Yes, signs off liability accounting | Only the month-end report? | Not in month-end week; email otherwise |
8  | Farid Osman | Data protection officer | PDPA compliance, retention | Yes, can veto personal-data processing | No | Fortnightly privacy clinic |
9  | Lena Koh | Security architect | Fraud, authentication, PCI scope | Yes, security sign-off before go-live | No | ? |
10 | Daniel Ng | Customer support lead | Fewer "where are my points" tickets; adjustments | No | Yes | Daily stand-up at 9:15 |
11 | Priya Raman | Marketing manager | Bonus campaigns, longer points expiry | No | Yes | Wednesday afternoons |
12 | Wei Jie Chua | Platform team tech lead | Operability, cost, Kubernetes platform | Yes, runs the platform | Yes | Daily |
13 | (vendor contact) | TillPoint POS integration manager | Interface changes, release windows | Yes, controls POS release windows | No | Vendor ticket portal |
```

## Questions asked in step 4 (one batch) and the answers

> 1. Grace Lim: does the loyalty-points service change Finance's work or measures beyond the month-end report? Recommended: no, so interest `low` (roster line 7).
> 2. Lena Koh: how can we reach her? Recommended: ask her directly.
> 3. Who is the named contact at TillPoint? Recommended: ask Arjun Pillai, who works with the vendor.

**Answers (Wei Jie Chua, 2026-11-04):** "1: I don't know, ask Grace. 2: no idea. 3: Arjun will tell us next week."
