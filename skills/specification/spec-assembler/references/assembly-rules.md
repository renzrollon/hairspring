# Assembly rules

How every work product lands in `requirements/spec/spec.md`. The rules are the same for the three outlines; only the section names differ.

## 1. The requirement block (fixed shape)

```markdown
#### R-080

WHEN the POS sends a voucher validation request at the planned peak load, the loyalty service shall return the validation result within TBD ms for 95% of requests.

Type Q · Priority must · Status draft · Source S-07 (SH-02 I-02)

Rationale: "Checkout must not get slower" (SH-02); voucher validation is a new call in the checkout path; target is open question Q1.
```

- The heading is the ID alone, at level 4. This gives every requirement the anchor `#r-080` on GitHub, GitLab and in pandoc, so links never break when a title changes.
- The paragraph after the heading is `Text`, copied verbatim. `spec_tool.py check` compares it with `requirements.csv`.
- The attribute line lists `Type`, `Priority`, `Status`, `Source`, then every optional column that exists and is not empty (`Title`, `Owner`, `Version`, `Stability`, `Risk`, `Verification`, `Kano`, `Links`, `Tags`).
- Stories get their acceptance criteria after the block, copied from the paste block of their stories file (`spec_tool.py blocks --stories requirements/stories`).
- Constraints get one more line from `constraints.csv`: `Mandated by <...> · Mandate reference <...> · Expires <...> · Review by <...>`.
- Never put a requirement block anywhere but under a section heading; group requirements inside a section with bold labels (`**Reliability**`), not headings.

Generate blocks with `python3 <skill-dir>/scripts/spec_tool.py blocks --ids R-080,R-082` (exact order) or `--type F|Q|C` (register order). Without Python, copy the cells by hand and run the manual checks in section 7.

## 2. Mapping to sections

| Work product | 29148 SRS outline | arc42 chapter | If missing |
| --- | --- | --- | --- |
| User's statement or `README.md` purpose | 1.1 Purpose | header table | `TBD` + open issue |
| `context.md` boundary, grey zones, open decisions | 1.2 Scope; open decisions also in 5.1 | 3.1 Business context | gap line (`system-context`) |
| `context.md` diagram | 1.3.1 Product perspective | 3.1 Business context | gap line (`system-context`) |
| `context.md` context table | 3.1 External interfaces | 3.1 Business context; channels in 3.2 | gap line (`system-context`) |
| Stories files and other Type F rows | 1.3.2 (links only); 3.2 Functions (blocks) | 1.1 Requirements overview | "No requirements in this section." |
| `stakeholders.md` | 1.3.3 User characteristics | 1.3 Stakeholders | gap line (`stakeholder-map`) |
| Type C rows with `constraints.csv` | 1.3.4 (links only); 3.6 Design constraints (technical, organizational, cultural, environmental); 3.7 Standards compliance (legal) | 2 Architecture constraints | all C rows in 3.6 / 2, plus an open issue to run `constraints-register` |
| `glossary.md` | 1.4 Definitions; abbreviations also in 5.2 | 12 Glossary | gap line (`glossary`) |
| `sources.csv` documents and systems | 2 References | header table `Assembled from` | gap line (`source-inventory`) |
| Type Q rows by characteristic in `quality-requirements.md` | interaction capability: 3.3; performance efficiency: 3.4; every other characteristic: 3.8 under bold labels | 10.2 Quality scenarios under bold labels | all Q rows in 3.8 / 10.2, plus an open issue to run `/quality-requirements` |
| `quality-requirements.md` walkthrough table | (not used) | 10.1 Quality tree | gap line (`quality-requirements`) |
| `quality-requirements.md` architecture drivers | (not used) | 1.2 Quality goals | gap line (`quality-requirements`) |
| `models/domain-model.md` | 3.5 Logical database requirements | (not used) | gap line (`domain-model`) |
| `models/uc-*.md`, `flow-*.md`, `state-*.md`, `decisions/RDR-*.md` | 3.9 Supporting information (links) | (not used) | "None in the workspace." |
| `verification.csv`, else the `Verification` attribute | 4 Verification | (not used) | gap line (`testability-check`) |
| `spec_tool.py summary`, `views/*.md` | 5.3 Attribute views | Appendix A | always produced |
| `trace/trace.csv`, else Source and Links | 5.4 Traceability | Appendix B | fallback table + open issue to run `traceability-matrix` |
| Open issues (section 4 below) | 5.5 Open issues | Appendix C | "None." |

The Volere option uses `assets/volere-mapping.md` with the section list of the user's licensed copy.

## 3. Empty sections

Every section of the outline stays in the document, in order. Use exactly one of:

| Situation | Write | Open issue |
| --- | --- | --- |
| The work product that fills the section does not exist | No content in the workspace. Produced by `<skill>` (`requirements/<file>`). | yes |
| The work product exists but nothing in scope maps here | No requirements in this section. | no |
| Optional supporting content does not exist (3.9, 5.2) | None in the workspace. | no |
| The user said the section does not apply | Not applicable: <reason> (<person>, <date>). | no |

## 4. Open issues

List, in section order:

1. Every in-scope requirement whose `Text` contains `TBD`, with the open question that resolves it.
2. Every open or deferred question in `quality-requirements.md`, the stories files and the `Open question` column of `constraints.csv`.
3. Every open decision (`D-nn`) in `context.md`.
4. Every gap line from section 3 that needs an open issue.

Columns: `#`, `Issue`, `Affects` (links to blocks or sections), `Owner` (as the work product names it, else `TBD`), `Produced by` (skill or file). Never resolve an issue while assembling: the specification shows the state of the workspace.

## 5. Cross-references and anchors

| Target | Link | Anchor rule |
| --- | --- | --- |
| A requirement | `[R-080](#r-080)` | the level-4 heading `#### R-080` |
| A section | `[3.4 Performance requirements](#34-performance-requirements)` | GitHub and pandoc slug: lowercase, punctuation except `-` and `_` removed, spaces become `-` |
| A workspace file | `` `requirements/quality-requirements.md` `` | plain code span; spec.md may travel without the workspace |

- Link every requirement ID that appears outside its own block (overviews, interface lists, open issues, trace tables).
- An ID whose requirement is excluded (withdrawn, rejected, outside the chosen status filter) is never linked; write it as plain text with the reason: "R-026 (withdrawn)".
- No table in `spec.md` has a column named `ID` (use `Requirement`): `re-lint` reads Markdown tables with an `ID` column as requirement registers.

## 6. Scope and versions

- Default scope: every status except `withdrawn` and `rejected`. For a contract or procurement baseline, ask whether only `agreed` (and later) requirements belong in it, and pass `--status-in` to every `spec_tool.py` call.
- If `requirements/baselines/<name>.json` exists for this delivery, put its name in the header `Version` row; otherwise `working copy`.
- Re-running the skill rewrites `spec.md` completely from the workspace. Never hand-edit `spec.md`; fix the work product and assemble again.

## 7. Checks and export

Run `python3 <skill-dir>/scripts/spec_tool.py check requirements/spec/spec.md` (add the same `--status-in` as above). It fails on: a missing, duplicated, unknown or excluded requirement block; text that differs from `requirements.csv`; a link with no matching heading. It warns on: unknown IDs mentioned in text; tables with an `ID` column.

Manual fallback without Python: count the `#### R-` headings against the in-scope rows of `requirements.csv`; compare five texts at random character by character; follow every link in the contents list.

Export to Word:

| Step | Command or action |
| --- | --- |
| Is pandoc installed? | `pandoc --version` (exit code 0 and a version line) |
| Export | `pandoc requirements/spec/spec.md -f gfm -t docx --toc -o requirements/spec/spec.docx` |
| Company styles | add `--reference-doc=<template.docx>` if the user names one |
| Diagrams | pandoc keeps Mermaid blocks as code. If `mmdc` (mermaid-cli) is installed and the user wants pictures, render each block to PNG next to `spec.md` and reference the images in a copy used only for the export |
| No pandoc | Do not install software without asking. Deliver `spec.md` (it renders on GitHub and GitLab, and most Markdown editors export it to Word or PDF) and give the user the pandoc install page: https://pandoc.org/installing.html |
