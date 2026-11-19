---
name: spec-assembler
description: >-
  Assembles the work products under requirements/ into one specification,
  requirements/spec/spec.md (and spec.docx through pandoc when installed): an ISO/IEC/IEEE 29148
  SRS outline (clause titles only), a lightweight arc42-aligned requirements chapter, or a
  Volere-structured document from the user's own licensed template. Adds a table of contents,
  cross-references, the glossary, attribute views, a traceability appendix and open issues;
  requirement text is copied verbatim from requirements.csv. Started explicitly with
  /spec-assembler. Use when someone needs "an SRS", "a spec document for the vendor, RFP,
  procurement or audit", "one document with all requirements", "export the requirements to
  Word", or a document for a formal review or contract baseline. Not for writing or fixing
  requirements (requirement-phrasing, user-story-refiner), reviewing them (requirements-review),
  building trace links (traceability-matrix), or exporting to OpenSpec (to-openspec) or ReqIF
  (reqif-bridge).
license: MIT
compatibility: Python 3.9+ optional for scripts/spec_tool.py; pandoc optional for .docx; works without either.
disable-model-invocation: true
argument-hint: "[29148 | arc42 | volere] [audience or purpose]"
metadata:
  stage: specification
  invocation: user
  priority: P2
  ireb-anchor: "CPRE FL Handbook 1.2 §3.6, §6.5"
  inputs-from: "requirement-phrasing, user-story-refiner, quality-requirements, constraints-register, glossary, system-context, stakeholder-map, source-inventory, domain-model, use-case-spec, process-flow, state-model, testability-check, traceability-matrix, attribute-schema, baseline"
  outputs-to: "requirements-review, baseline"
  work-product: "requirements/spec/spec.md"
  version: "0.1.0"
---

# Spec assembler

Procurement, auditors and vendors want one document; engineering keeps requirements as a register and a handful of work products. This skill builds the document from the workspace without rewriting anything: it picks a documentation structure (an ISO/IEC/IEEE 29148-aligned SRS, an arc42-aligned requirements chapter, or a Volere-structured document from the user's licensed copy), copies every in-scope requirement verbatim from `requirements.csv` into a fixed block, links everything, and lists every gap as an open issue. The result is `requirements/spec/spec.md`, and `spec.docx` when pandoc is available.

## When not to use

- Writing, splitting or fixing requirements: `requirement-phrasing`, `user-story-refiner`, `quality-requirements`, `constraints-register`.
- Checking the quality of the set: suggest `/requirements-review` (run it on the register, before or after assembling).
- Building or refreshing trace links: `traceability-matrix`.
- Handing requirements to coding agents or a requirements tool: suggest `/to-openspec` or `/reqif-bridge`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` | yes | `requirement-phrasing`, `user-story-refiner`, `quality-requirements`, `constraints-register` |
| `requirements/stories/*.md`, `quality-requirements.md`, `constraints.csv` | no | `user-story-refiner`, `quality-requirements`, `constraints-register` |
| `requirements/context.md`, `glossary.md`, `stakeholders.md`, `sources.csv` | no | `system-context`, `glossary`, `stakeholder-map`, `source-inventory` |
| `requirements/models/*.md`, `decisions/*.md`, `verification.csv` | no | `domain-model`, `use-case-spec`, `process-flow`, `state-model`, `conflict-to-decision`, `testability-check` |
| `requirements/trace/trace.csv`, `views/*.md`, `baselines/*.json` | no | `traceability-matrix`, `attribute-schema`, `baseline` |
| The user's licensed Volere section list (Volere option only) | for that option | the user |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/spec/spec.md` | `assets/srs-29148.md`, `assets/arc42-requirements.md`, or `assets/volere-mapping.md` | `requirements-review`, `baseline`, readers outside the team |
| `requirements/spec/spec.docx` (optional) | pandoc export of `spec.md` | readers outside the team |

## Procedure

1. **Read the workspace.** Locate `requirements/` (or the `workspace` in `schema.json`) and read `schema.json` (else the defaults, and say so in the final message). `requirements.csv` is required: if it is missing, stop and suggest the skills that create it. List which of the other inputs exist; every missing one becomes a gap line later, not a reason to stop.
2. **Choose structure, scope and version.** Ask in one batch (following `re-interview`): the structure, with a recommendation (29148 SRS for procurement, contracts and audits; arc42 chapter when the team keeps arc42 architecture docs; Volere only when the user's organization holds the template license); the purpose and readers (for section 1.1); the status scope (default: everything except `withdrawn` and `rejected`; for a contract baseline, recommend `agreed` and later); the baseline name if one exists in `baselines/`; and whether a `.docx` is needed. In non-interactive mode use the 29148 SRS, the default scope, `working copy`, and `TBD` for the purpose.
3. **Volere only: get the licensed section list.** Ask the user for the section numbers and titles from their own licensed copy. Without it, do not use this option: say why and offer the other two. Never write Volere sections from memory. Follow `assets/volere-mapping.md`.
4. **Start from the template.** Copy the chosen outline from `assets/` and fill the header table. Keep every section, in order, with the titles exactly as in the template (or the user's Volere list).
5. **Fill the sections.** Read `references/assembly-rules.md` and map each work product to its section. Copy, never author: requirement text, diagrams, tables and glossary entries are copied verbatim. Generate requirement blocks with `python3 <skill-dir>/scripts/spec_tool.py blocks --ids <IDs in section order> --stories requirements/stories`, run from the repository root, taking the IDs only from in-scope rows (`check` in step 10 catches an excluded one); without Python, build each block by hand in the shape of `references/assembly-rules.md` section 1. Group requirements inside a section with bold labels; level-4 headings are only for requirement blocks.
6. **Mark the gaps.** For every section, apply the empty-section rules (section 3 of the rules). Never add, merge, split or rephrase a requirement to fill a gap; if the set has a defect (a `TBD`, a duplicate, a contradiction), it goes into *Open issues* and into the final message.
7. **Link everything.** Link every requirement ID outside its own block as `[R-nnn](#r-nnn)`, and every section reference to its heading slug. Write excluded IDs as plain text with the reason. Fill the contents list.
8. **Add views, traceability and open issues.** Pass the scope's `--status-in` (if not the default) to both commands. Paste the output of `spec_tool.py summary` into the attribute-views section, followed by any `views/*.md`. Paste the output of `spec_tool.py trace` into the traceability section; without `trace/trace.csv` it falls back to Source and Links and you add an open issue to run `traceability-matrix`. Build *Open issues* by the rules (section 4).
9. **Show, then write.** Show the header table, the contents list and the open issues; get confirmation. Write `requirements/spec/spec.md` in full (re-running the skill regenerates it; nobody edits it by hand). In non-interactive mode, write directly.
10. **Check.** Run `python3 <skill-dir>/scripts/spec_tool.py check requirements/spec/spec.md` with the same `--status-in` and fix every error by correcting the assembly, never `requirements.csv`. Without Python, run the manual fallback in section 7 of the rules.
11. **Export to Word if asked.** Run `pandoc --version`. If it works: `pandoc requirements/spec/spec.md -f gfm -t docx --toc -o requirements/spec/spec.docx` (add `--reference-doc=<file>` for company styles; Mermaid diagrams stay as code unless rendered first, see the rules). If pandoc is missing, do not install anything without asking: deliver `spec.md` and give the user the install page and the command.
12. **Report.** End with: structure and scope, requirements included and excluded by type, gaps and open issues with owners, check result, whether `spec.docx` was written, and the next steps from *Hand-offs*.

## Quality checks

- [ ] Every in-scope requirement appears exactly once as a `#### R-nnn` block whose text equals `requirements.csv`; no withdrawn, rejected or out-of-scope requirement has a block.
- [ ] Every section of the chosen outline is present, in order; each empty one carries one of the empty-section lines.
- [ ] Every internal link resolves; excluded IDs are plain text with a reason.
- [ ] No requirement was invented, merged, split or reworded; every gap is an open issue with an owner or `TBD`.
- [ ] No ISO text and no Volere template text: clause and section titles only, Volere titles only from the user's licensed list.
- [ ] No table in `spec.md` has a column named `ID`.
- [ ] `spec_tool.py check` exits 0; `spec.docx` exists only if pandoc ran.

## Hand-offs

- **Next:** suggest `/requirements-review` on the assembled set before the document leaves the team, and `/baseline` to freeze the requirement versions the document shows.
- **Feeds back to:** the skill named in each gap line (suggest `/system-context` or `/stakeholder-map`; `glossary`, `domain-model`, `testability-check` and `traceability-matrix` can run directly); `clarifying-questions` with the open issues; `requirement-phrasing` for defects found while assembling.

## Non-interactive mode

Ask nothing. Use the 29148 SRS outline, the default scope, `working copy` as the version and `TBD` as the purpose (an open issue). Do not use the Volere option. Export to `.docx` only if the request asked for Word and pandoc is installed.

## References

- `references/assembly-rules.md`: the requirement block, the mapping of work products to sections for each outline, empty-section and open-issue rules, anchors, scope, checks and the pandoc export. Read it before step 5.
- `assets/srs-29148.md`, `assets/arc42-requirements.md`, `assets/volere-mapping.md`: the outlines. Copy one at step 4.
- `references/ireb-anchor.md`: handbook sections and glossary terms this skill applies.
- `examples/`: a loyalty-points workspace (`examples/input/requirements/`) and the SRS assembled from it.
