# Expected output: loyalty-points source register

`requirements/sources.csv` after the run: see `expected-output.csv`. S-01 to S-07 kept their IDs and were completed; S-08 to S-13 are new.

## Rows written

| ID | Source | Technique | Relevance | Status | Change |
| --- | --- | --- | --- | --- | --- |
| S-01 | Programme terms and conditions | document-analysis | high | planned | completed |
| S-02 | TillPoint POS loyalty interface spec | document-analysis | high | planned | completed |
| S-03 | Support ticket export | feedback-analysis | medium | planned | completed |
| S-04 | Legacy loyalty module | system-archaeology | high | planned | completed; Version and Contact `TBD` |
| S-05 | PDPA and DRP-2024 | document-analysis | high | planned | completed; Version `TBD` |
| S-06 | Mei Tan (SH-01) | interview | high | elicited (I-01) | completed |
| S-07 | Arjun Pillai (SH-02) | observation; interview | high | elicited (I-02) | completed |
| S-08 to S-13 | Grace Lim, Farid Osman, Lena Koh, Daniel Ng, Priya Raman, Wei Jie Chua | interview, workshop, observation | high or medium | planned | new |

## Not registered

| Item | Why | Next |
| --- | --- | --- |
| SH-09 TillPoint integration manager, SH-10 members, SH-11 legal counsel, SH-12 fraud analyst | No named representative or proxy yet | Register when `stakeholders.md` names one; meanwhile S-03 carries the member voice |
| Relay CRM, fraud engine, notification provider, data warehouse interface documentation | Named in `context.md`, but no document or owner is known | Open questions 1 and 2 |

## Coverage check

| Finding | Detail |
| --- | --- |
| Cited but not registered | none: every S-ID cited in `requirements.csv` is registered |
| Elicited but not cited | S-07: interview I-02 is recorded, but no requirement cites S-07 yet. Run `requirement-phrasing` on the I-02 notes |
| High relevance, still planned | S-01, S-02, S-04, S-05 (documents and the legacy system): run `artifact-mining`; S-08, S-09, S-10, S-13 (interviews): suggest `/interview-guide` |

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| 1 | Is there interface documentation for the Relay CRM nightly summary and the data warehouse extract, and who owns it? | SH-08 | New sources |
| 2 | Is there interface documentation for the fraud engine events and the notification provider API? | SH-05, SH-08 | New sources |
| 3 | Which versions of the PDPA guidance and of DRP-2024 apply? | SH-04, SH-03 | S-05 |
| 4 | Who maintains the legacy loyalty module and can walk us through the batch scripts? | SH-08 | S-04 |
