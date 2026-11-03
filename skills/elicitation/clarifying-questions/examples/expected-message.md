# Expected messages for LOY-131

## Step 5: the batch, as sent to the user

> Before I implement LOY-131, seven questions whose answers change the design. I wrote them to `requirements/elicitation/questions-loy-131-csv-export.md`. Encoding, delimiter, columns and the 24-month limit are already settled by `src/admin/exports.py`, R-021 and R-020, so I am not asking about them.
>
> **Boundary**
> 1. Who may run the export: support agents only, also team leads, or also Finance or members in the app? *Recommended:* agents and team leads, support console only (Finance has the warehouse extract).
>
> **Functional**
> 2. What does one export contain? *Recommended:* one member, one row per points transaction, the R-021 columns.
> 3. Which period: always 24 months, or a range the agent picks? *Recommended:* agent-chosen range within the 24 months.
>
> **Quality**
> 4. How long may the agent wait for the file while the member is on the phone? *No recommendation: this needs a business value.*
> 5. Which personal data may the file contain: member ID only, or also name, email, phone? *For Farid Osman (DPO).* *Recommended:* member ID only.
>
> **Constraint**
> 6. Must each export be recorded in the audit log (agent, member, period, time)? *Recommended:* yes.
> 7. May the system store or email the file, or browser download only? *Recommended:* download only.
>
> Reply per number: ok, or your answer.

## Step 8: the final message after recording the answers

> Recorded Daniel Ng's answers (2026-11-03) and appended R-030 to R-035 (draft) to `requirements/requirements.csv`; `re-lint check --only-ids R-030,R-031,R-032,R-033,R-034,R-035` reports no errors or warnings; its `open-tbd` notes are the TBD seconds in R-033 and the priorities nobody stated for R-033 to R-035.
>
> Still open:
> - Q5 (blocking, owner Farid Osman, SH-04): personal data in the file. Until answered I build assumption A1: member ID and history columns only.
> - Q8 (owner Daniel Ng, SH-06): the maximum seconds for R-033. I build assumption A2: direct download, no background job.
>
> Next: implementing the export on R-030 to R-035 with A1 and A2 named in the PR description; `testability-check` can add verification methods once Q8 is answered.
