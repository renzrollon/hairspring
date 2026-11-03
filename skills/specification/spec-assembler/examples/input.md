# Input: SRS for the procurement review (loyalty-points sample)

Command: `/spec-assembler 29148 for the procurement review`.

Workspace: the files in `examples/input/requirements/`, assembled from the other specification skills' examples: `requirements.csv` (11 rows, R-026 withdrawn), `stories/redeem-points-at-checkout.md` (from `user-story-refiner`), `quality-requirements.md` (from `quality-requirements`), `constraints.csv` (from `constraints-register`), `context.md`, `glossary.md` and `sources.csv`. There is no `stakeholders.md`, no `models/`, no `verification.csv` and no `trace/trace.csv`. pandoc 3.1 is installed.

## Question batch and answers (Mei Tan, SH-01, 2026-11-03)

| # | Question | Recommended answer | Answer |
| --- | --- | --- | --- |
| 1 | Which structure? | 29148 SRS, because procurement reads it | 29148 SRS |
| 2 | Who reads it, and what for? | | The procurement review on 2026-11-10: Finance (Grace Lim, SH-03) and the POS vendor TillPoint (SH-09) price the integration work from it. |
| 3 | Which statuses are in scope? | Only `agreed` for a contract baseline | Everything except withdrawn and rejected; nothing is agreed yet. |
| 4 | Is there a baseline name? | | None yet: working copy. |
| 5 | Do you need a Word file? | Yes, if pandoc is installed | Yes. |

Expected result: `requirements/spec/spec.md` as in `expected-output.md`, `spec_tool.py check` clean, and `requirements/spec/spec.docx` written with `pandoc requirements/spec/spec.md -f gfm -t docx --toc -o requirements/spec/spec.docx`.
