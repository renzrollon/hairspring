# Input: source inventory for the loyalty-points service (Harbourline sample)

Prompt (2026-11-04, Wei Jie Chua, SH-08): "The stakeholder map is done. Complete the source register and plan elicitation for each source."

## `requirements/sources.csv` as registered at kick-off (IDs, names and versions only)

```csv
ID,Source,Kind,Category,Version,Location,Contact,Technique,Relevance,Status,Notes
S-01,Harbourline Rewards programme terms and conditions,document,,draft v3,,,,,,
S-02,TillPoint POS loyalty interface spec,document,,v2.1,,,,,,
S-03,Support ticket export (loyalty category),document,,,,,,,,
S-04,Legacy loyalty module: stored procedures and nightly batch scripts,system,,,,,,,,
S-05,Singapore PDPA and data retention policy DRP-2024,document,,,,,,,,
S-06,Mei Tan (SH-01),stakeholder,,,,,,,,
S-07,Arjun Pillai (SH-02),stakeholder,,,,,,,,
```

## Kick-off notes on where things are

- S-01 is on SharePoint under Loyalty/Terms/draft-v3; Mei Tan owns it.
- S-02 is in the repo at `docs/vendor/tillpoint-loyalty-interface-v2.1.pdf`.
- S-03 is `data/support/loyalty-tickets-2026-05-to-10.csv`: 1,240 tickets from May to October 2026; Daniel Ng exported it.
- S-04 runs in the POS vendor's back office: database `LOYALTY_PROD`, scripts in the repo `pos-backoffice/loyalty-batch`. Nobody knows who maintains it.
- S-05: the PDPA text is on Singapore Statutes Online; DRP-2024 is in the intranet policy library and Finance owns it.

## Workspace state

- `requirements/stakeholders.md` (the `stakeholder-map` example): named representatives for SH-01 to SH-08; representative `TBD` for SH-09 (TillPoint integration manager), SH-10 (members), SH-11 (legal counsel) and SH-12 (fraud analyst). Availability: SH-03 not in month-end week; SH-04 fortnightly privacy clinic; SH-05 TBD; SH-06 daily stand-up; SH-07 Wednesday afternoons.
- `requirements/elicitation/interview-head-of-loyalty.md` records interview I-01 with Mei Tan on 2026-10-27; `requirements/elicitation/interview-store-operations-lead.md` records the store visit and interview I-02 with Arjun Pillai on 2026-10-30.
- `requirements/requirements.csv`: R-023 to R-027 cite `S-06 (LOY-118)` in Source; the rationale of R-023 cites S-03.
- `requirements/context.md` lists Relay CRM, the fraud engine, the notification provider and the data warehouse as neighbouring systems; no documentation for their interfaces is named anywhere.
