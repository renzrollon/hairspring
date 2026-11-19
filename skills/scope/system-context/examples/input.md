# Input: `/system-context` for the loyalty-points service (Harbourline sample)

Run on 2026-11-03 with Mei Tan (SH-01, Head of Loyalty) and Wei Jie Chua (SH-08, platform tech lead). `requirements/stakeholders.md` and `requirements/sources.csv` already exist (SH-01 to SH-09, S-01 to S-07 from the sample brief). No `context.md` exists yet.

## Kick-off notes: `notes/kickoff-2026-11-03.md`

```markdown
1  # Kick-off: loyalty-points context, 2026-11-03 (Mei Tan SH-01, Wei Jie Chua SH-08)
2
3  - We build the loyalty-points service: REST API, purchase-event consumer, admin console for support.
4  - TillPoint POS sends purchase events (earn) when the cashier scans the member QR, and calls us to validate vouchers (interface spec v2.1, S-02).
5  - The customer mobile app (app team) calls our API for balance, history and redemption.
6  - Relay CRM gets member tier and a points summary from us every night.
7  - The fraud engine scores our earn and redeem events and sends back hold or release. Lena (SH-05) owns it.
8  - The notification provider sends SMS and push for points earned and points expiring; we call its API.
9  - Finance needs a daily extract in the data warehouse for points liability (Grace, SH-03).
10 - Support agents use the admin console to look up members and adjust points.
11 - Points-expiry batch job: today the data platform team runs it on the legacy module. Ours after go-live? Mei: "not decided".
12 - Voucher printing on the receipt: POS vendor or us? Nobody knows.
13 - App purchases are fulfilled by the e-commerce order system, not by the app. Who sends us the earn event?
14 - Payments and card terminals: not our business, the POS sends us the purchase total.
15 - Store network outages: the POS queues purchase events while offline (S-02 section 5).
16 - PDPA and retention policy DRP-2024 apply (S-05).
```

## Questions asked in step 4 (one at a time) and the answers

| # | Question, as asked | Answer | Who |
| --- | --- | --- | --- |
| 1 | "Is the admin console part of the loyalty-points service, or a separate tool? I'd say part of it: notes line 3." | "Part of it, we build it." | Wei Jie Chua |
| 2 | "Does the points-expiry batch job become ours after go-live, or does the data platform team keep it? I'd say ours: expiry follows the programme terms (S-01), which we implement." | "Not decided. I need to agree it with the data platform lead." | Mei Tan |
| 3 | "Who prints the voucher on the receipt: the POS from the data we return, or our service? I'd say the POS: the validation call already returns the voucher (S-02)." | "Probably the POS, but ask the vendor." | Mei Tan |
| 4 | "For app purchases, does the earn event come from the app or from the e-commerce order system? I'd say the order system: notes line 13." | "Depends on the app team's roadmap." | Mei Tan |
| 5 | "Who owns the CRM interface on the CRM side?" | "No idea yet." | Mei Tan |
