# Input: `/re-setup` on the loyalty-points repo (Harbourline sample)

Run by Wei Jie Chua (SH-08, platform team tech lead) on 2026-11-03. No `requirements/` folder exists yet.

## Evidence found in step 2

| File | Line | Text |
| --- | --- | --- |
| `README.md` | 5 | "Process: Scrum, two-week sprints, board in Jira project LOY." |
| `README.md` | 7 | "Product owner: Mei Tan, Head of Loyalty." |
| `docs/compliance.md` | 3 | "The service stores member personal data (PDPA). Finance must keep transaction data for 7 years for audit (policy DRP-2024)." |

No contract, tender or vendor-build documents were found.

## Batch A, as asked

> 1. **A1 Time.** Are requirements refined sprint by sprint? Recommended: **iterative** (README.md:5, two-week sprints).
> 2. **A2 Purpose.** Are you still finding out what is needed, rather than handing a binding spec to someone else? Recommended: **explorative** (no contract or tender documents).
> 3. **A3 Target.** Is there one known customer who accepts the system? Recommended: **customer-specific**, the loyalty team led by Mei Tan (README.md:7).
> 4. **A4 Criticality.** Does a regulation or audit need evidence of where each requirement came from? Recommended: **PDPA and DRP-2024** (docs/compliance.md:3).
>
> Reply `yes` to take all four, or correct the ones that are wrong.

**Answer (Wei Jie Chua, 2026-11-03):** "Yes to all four."

## Batch B, as asked (prefilled from the decision rules)

> 1. **B1 Change authority.** Product owner. Who is it? Recommended: Mei Tan (SH-01).
> 2. **B2 Work products.** Keep the set below? (table shown: 18 `yes`, 4 `later`, 1 `no`)
> 3. **B3 IDs and attributes.** Default prefixes and the seven required attributes, plus a `Verification` column (criticality named). Add any other column?
> 4. **B4 Definition of Ready.** Base items plus: story with an unwanted-behavior AC (iterative); assumption stated (explorative); agreed by a named customer representative (customer-specific); regulation cited and personal-data review (criticality). Add or drop anything?

**Answers (Wei Jie Chua, 2026-11-03; B1 confirmed by Mei Tan the same day):**

- B1: "Mei Tan. Anything already in a release baseline needs a CR she approves."
- B2: "Yes."
- B3: "Defaults, plus a Links column."
- B4: "Drop the explorative item, Mei tracks assumptions on her discovery board. Add: member-facing text is reviewed by Marketing (SH-07)."

Two points came up that nobody could answer on the spot: whether the data protection officer must co-approve changes to requirements on personal data, and how often to cut a baseline.
