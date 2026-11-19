# Input: quality walkthrough for the loyalty-points service

Command: `/quality-requirements loyalty-points service (REST API and event consumer)`.

Workspace state: `requirements.csv` holds R-001 to R-079 (functional requirements and stories). `context.md` lists the POS, customer mobile app, CRM, fraud engine, notification provider and data warehouse as external systems. `stakeholders.md` holds SH-01 to SH-09 from the brief.

## Quality concerns raised before the session (from the brief)

- "Checkout must not get slower." (Arjun Pillai, SH-02, interview I-02; source S-07). Today voucher validation adds no delay because there is none.
- "The app should show the new balance quickly." (Mei Tan, SH-01, interview I-01; source S-06)
- "Must survive the year-end sale peak." (Wei Jie Chua, SH-08): last year's peak was about 9,000 purchases per minute across stores.
- "Secure." (Lena Koh, SH-05) and "Auditable." (Grace Lim, SH-03)

## Notes from the walkthrough session, 2026-11-03

Present: Mei Tan (SH-01), Arjun Pillai (SH-02), Lena Koh (SH-05), Wei Jie Chua (SH-08). Grace Lim (SH-03) answered by email on 2026-11-02.

- Arjun: "If loyalty is down, the till must still sell. A sale is never blocked by loyalty."
- Lena: "Every call from the tills and the app must be authenticated. Member data is encrypted on the wire, to all of our systems. If the fraud engine is down, earning must carry on; we score later. PCI is out of scope because we never see card numbers."
- Wei Jie: "If the service crashes we must not lose a points transaction; Finance reconciles every one. How fast we must be back, Finance has to tell me. We have to integrate through the TillPoint loyalty interface v2.1; the vendor won't change it before v2.2. Safety isn't a topic for us, there is no hardware. We report response times as the 95th percentile everywhere."
- Mei: "Marketing runs a campaign almost every month and today each one needs a release. Priya wants to set them up herself."
- Grace (email): "Auditable means every manual adjustment shows who did it, when and why, and nobody can edit that afterwards. We keep transaction data 7 years (DRP-2024)."
- Nobody had numbers for response times, availability or recovery. Daniel Ng (SH-06, support) was not present.
