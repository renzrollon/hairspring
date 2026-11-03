---
name: artifact-mining
description: >-
  Extracts candidate requirements from existing artifacts (specs, terms, regulations, legacy code,
  stored procedures, config, API contracts such as OpenAPI, WSDL or event schemas, tickets,
  runbooks, support logs and app reviews) into requirements/candidates.csv. Each candidate gets a
  CAN-nnn ID, a verbatim quote with its location (file:line), a first F/Q/C guess and a keep / drop /
  confirm disposition, so old behavior is confirmed by a person before it survives. Use when
  migrating or replacing a legacy system, when asked "what does the old module actually do",
  "extract requirements from this spec / repo / API", "mine the support tickets", or when
  sources.csv plans document analysis, system archaeology or feedback analysis for a source. Not for
  asking people (use clarifying-questions or interview-guide), listing which sources exist
  (source-inventory), or phrasing confirmed candidates as requirements (requirement-phrasing).
license: MIT
compatibility: Python 3.9+ optional for scripts/check_candidates.py; works without it.
metadata:
  stage: elicitation
  invocation: model
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §4.2.2"
  inputs-from: "source-inventory, system-context, glossary"
  outputs-to: "requirement-classifier, requirement-phrasing, clarifying-questions, glossary, constraints-register"
  work-product: "requirements/candidates.csv"
  version: "0.1.0"
---

# Artifact mining

Legacy code and documents say what a system does or once had to do, not what the new one must do. This skill reads specs, code, contracts, tickets and logs, extracts each candidate requirement with the exact quote and its location, and gives it a disposition, so obsolete rules and old workarounds are dropped or confirmed instead of being rebuilt by default. The work product is `requirements/candidates.csv`.

## When not to use

- The information is in people's heads: `clarifying-questions` for a task, `interview-guide` for a planned interview.
- You need the list of sources and the technique per source first: `source-inventory`.
- The candidates are confirmed and need EARS wording: `requirement-phrasing` (or `requirement-classifier` when F/Q/C is unclear).
- The artifact is a regulation or mandate you are turning into constraints: run this skill, then `constraints-register` on the `C` candidates.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Artifacts to mine: files in the repo, or exports placed in it | yes | the user, `source-inventory` |
| `requirements/sources.csv` (source IDs and planned technique) | no | `source-inventory` |
| `requirements/requirements.csv`, `candidates.csv`, `glossary.md`, `context.md` | no | `requirement-phrasing`, earlier runs, `glossary`, `system-context` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/candidates.csv` (appended rows) | `assets/candidates.csv`; columns in `references/candidates-columns.md` | `requirement-classifier`, `requirement-phrasing`, `clarifying-questions` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (else defaults: candidate IDs `CAN-` plus 3 digits), `sources.csv`, `glossary.md`, `requirements.csv` and `candidates.csv` if they exist. Note which artifact locations were already mined so you do not mine them twice.
2. **Scope the artifacts.** List each artifact with its source ID (from `sources.csv`; if it has none, use its path and recommend `source-inventory`) and its technique: `document-analysis` (specs, terms, contracts, regulations, runbooks), `system-archaeology` (code, stored procedures, config, schemas, API contracts), `feedback-analysis` (tickets, support logs, reviews, survey free text). If an artifact is outside the repo, ask the user to place it in the repo or cite it as `S-nn <item>`. If you can run subagents, mine large artifacts in parallel, one per subagent, then merge; otherwise one after another.
3. **Extract.** Read each artifact in full, using the signals in `references/mining-signals.md`: business constants, conditions, validations, limits, state changes, schedules, external calls, permissions, retention and deletion, error messages, and comments such as "must", "legal", "temporary", "hack". For feedback, cluster recurring complaints and count them. Write one candidate per behavior: a *Statement* in domain words (glossary terms, present tense, no table or class names), a *Type* guess (`F`, `Q`, `C`, or `TBD`), *Source*, *Location* and a verbatim *Quote* of at most a few lines (use `...` for a gap). Mask personal data in quotes as `[name]`, `[email]`, `[phone]`, `[nric]`, `[card]` or `[address]`.
4. **Decide the disposition** with the table below. Code shows behavior, not intent: a candidate whose only evidence is legacy code, config, data or a runbook is never `keep`. A blanket "we need parity" is not evidence for each rule: keep those rows `confirm` and offer the person who wants parity one confirmation batch. Give a one-sentence *Reason* for every row, and an *Owner* (name with SH-ID, or role) for every `confirm`.
5. **Merge and cross-check.** One behavior found in several artifacts is one candidate; list the other locations in *Reason*. A candidate already covered by `requirements.csv` is `drop` with that ID in *Requirement*. Two sources that disagree make the candidate `confirm` with both owners.
6. **Allocate and validate.** Allocate IDs with `re-ids` (`--kind candidate`). Run `python3 <skill-dir>/scripts/check_candidates.py <file> --root <repo root>`: it checks columns, IDs and values and that every quote appears at its cited location. Fix every error. Without Python, re-open each cited line and compare the quote by hand.
7. **Show, then write.** Show counts per disposition and the `confirm` list grouped by owner. After confirmation (or directly in non-interactive mode), append the rows to `requirements/candidates.csv` (create it from `assets/candidates.csv` if missing).

| Evidence | Disposition | Reason starts with |
| --- | --- | --- |
| A current, authoritative source states it (terms in force, regulation, contract, interface spec, a stakeholder's recorded statement) and nothing contradicts it | `keep` | "Backed by S-nn ..." (cite the location) |
| The only evidence is legacy code, config, data, a runbook or a log | `confirm` | "Legacy-only ..." |
| Two sources disagree, or the behavior looks like a defect | `confirm` | "Conflicts with ..." / "Probable defect ..." |
| Hard-coded past dates, stores or campaigns; "temporary", "hack" or "TODO remove"; flags permanently off; references to retired systems | `drop` if obsolescence is evident, else `confirm` | "Probable obsolete rule ..." |
| Implementation detail: table, queue or class names, cursor loops, tuning for old hardware, technology choice | `drop`; add a separate `Q` candidate if a quality need is visible behind it | "Implementation detail ..." |
| Recurring complaint or wish in feedback | `confirm`, owner = product owner; count in *Reason*; *Kano* `dissatisfier` for complaints | "n of N tickets ..." |
| Duplicate of an existing requirement or candidate | `drop` with the ID in *Requirement* or *Reason* | "Covered by ..." |

## Quality checks

- [ ] Every row has a verbatim quote and a location that `check_candidates.py` verifies (or `S-nn <item>` for an artifact outside the repo).
- [ ] No candidate is `keep` on legacy evidence alone; every `confirm` has an owner; every row has a reason.
- [ ] Statements use domain words, not table, column or class names; implementation details are dropped.
- [ ] No personal data from tickets or logs is copied into *Quote* or *Statement*.
- [ ] No value was invented: numbers in statements come from the quote.

## Hand-offs

- **Next:** `requirement-classifier` on the `keep` rows when F/Q/C is unclear, then `requirement-phrasing` to turn them into requirements (it fills *Requirement* with the new R-ID).
- **Next:** `clarifying-questions` with the `confirm` rows, one batch per owner (or `/interview-guide` for an owner with many).
- **Feeds back to:** `glossary` with legacy terms and codes found (`status 'P'` means pending); `system-context` with interfaces found in code; `constraints-register` with `C` candidates; `source-inventory` with artifacts that had no source ID.

## Non-interactive mode

Append the rows directly, never set `keep` beyond the table's rule, and end with the counts per disposition, the `confirm` rows grouped by owner, and any artifact you could not read.

## References

- `references/candidates-columns.md`: every column of `candidates.csv`, its allowed values and location formats. Read it before writing the first row.
- `references/mining-signals.md`: what to look for in code, SQL, config, API contracts, documents, tickets and logs, with loyalty-points examples. Read it at step 3.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `examples/`: the legacy points-posting procedure (S-04) checked against the program terms (S-01), and the eight candidates it yields.
