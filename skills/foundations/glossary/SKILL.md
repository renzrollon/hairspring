---
name: glossary
description: >-
  Builds and maintains requirements/glossary.md, the project's shared vocabulary: term,
  definition, synonyms, homonym notes, abbreviation, owner, status and source for each domain
  word. Mines candidate terms from docs, code and ticket exports (scripts/mine_terms.py counts
  them), and flags homonyms (one word, several senses, such as "account") and synonyms (two words,
  one thing, such as "customer" and "member"). Use when a repo or domain is new to the team, when
  requirements, stories or tickets use a word nobody has defined, when code and docs name the same
  thing differently, when someone asks "what do we mean by X", "define our terms", "build a
  glossary" or "ubiquitous language", and before writing requirements another team will read.
  Reuses the output of mattpocock's domain-modeling skill when present. Not for class or ER
  diagrams of business objects (use domain-model) or for deciding whether a sentence is a
  requirement (use requirement-classifier).
license: MIT
compatibility: Python 3.9+ optional for scripts/mine_terms.py; works without it.
metadata:
  stage: foundations
  invocation: model
  priority: P0
  ireb-anchor: "CPRE FL Handbook 1.2 §3.5; Principle 3 (shared understanding)"
  inputs-from: "artifact-mining, system-context, stakeholder-map, domain-model, re-interview"
  outputs-to: "requirement-phrasing, domain-model, clarifying-questions, requirements-review, spec-assembler"
  work-product: "requirements/glossary.md"
  version: "0.1.0"
---

# Glossary

Most misunderstandings in requirements are not about logic but about words: "account" means a login to support, a ledger to finance and a points balance to the product owner. A glossary fixes one meaning per term, names the words to avoid, and says who decides. This skill mines candidate terms, finds homonyms and synonyms, drafts definitions with sources, and maintains `requirements/glossary.md`.

## When not to use

- You need entities, attributes and multiplicities as a diagram: `domain-model` (it reads this glossary).
- You are unsure whether a sentence is a requirement, a fact or a design idea: `requirement-classifier`.
- A definition depends on a number nobody has given (tier thresholds, expiry period): ask first with `clarifying-questions`.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| Files to mine: `README*`, `docs/`, domain code, API specs, ticket or support exports | yes (at least one) | the team, `artifact-mining` |
| `requirements/glossary.md` | no | earlier runs |
| `requirements/requirements.csv`, `context.md`, `stakeholders.md` | no | `requirement-phrasing`, `system-context`, `stakeholder-map` |
| Output of the `domain-modeling` skill (mattpocock/skills) | no | that skill |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/glossary.md` | `assets/glossary.md` | `requirement-phrasing`, `domain-model`, `clarifying-questions`, `requirements-review`, `spec-assembler` |

## Procedure

1. **Read the workspace.** Load `requirements/schema.json` (defaults if missing) and the existing `glossary.md`. Keep every existing row; an `agreed` definition changes only after its owner confirms, so propose changes in Findings. Read `stakeholders.md` for owners and `requirements.csv` for the words requirements already use.
2. **Reuse `domain-modeling` output.** If the `domain-modeling` skill from mattpocock/skills is installed, read its `SKILL.md` to find the file it writes; if that file exists, import its terms as rows with `Status=proposed` and `Source=<that file>:<line>` instead of re-deriving them. Do not run that skill yourself.
3. **Mine candidates.** Run `python3 <skill-dir>/scripts/mine_terms.py <paths> --glossary requirements/glossary.md --format md --top 60` over the paths the user named, else `README.md docs src requirements/requirements.csv requirements/stories` and any ticket export (not the whole `requirements/` folder: its work products repeat the catalogue's own vocabulary, such as Rationale or Disposition). Exit code 1 only means new candidates exist. Without Python, search the same files for capitalized nouns, class and table names, enum values and acronyms, and note `file:line` for each.
4. **Select terms.** Keep a candidate when it is a business object, role, state, event, unit or rule name that a newcomer or another team could misread, **and** at least one holds: requirements or stories use it, it appears in more than one source, two parties use it differently, or it is an abbreviation. Drop generic technical words (string, server, request) unless the domain gives them a special meaning. Read `references/term-patterns.md` for the full rules.
5. **Find homonyms and synonyms.** Compare the senses of each kept word across sources (signals and resolutions in `references/term-patterns.md`). A homonym gets one row per sense with a qualified term (`Member account`, `Liability account`) and a note in `Homonym notes`. A synonym set gets one row for the preferred term, the other words in `Synonyms` marked "avoid", and the choice of preferred term proposed to the owner. Record each case in Findings with `file:line` evidence.
6. **Draft definitions.** One sentence: the broader category, then what sets this term apart. No circular definitions, no examples instead of a definition, no requirements or business-rule values inside a definition (move an expiry period or a threshold to a requirement candidate). Unknown meaning: `Definition = TBD`, `Status=candidate`, and an open question to the owner. Every row gets a `Source` (`S-nn`, `I-nn`, `SH-nn` with date, or `file:line`) and an `Owner` (the role or `SH-nn` who decides the meaning; `TBD` if unknown).
7. **Show, then write.** Show the new and changed rows and the findings; after confirmation (or directly in non-interactive mode) write `requirements/glossary.md` from `assets/glossary.md`, rows sorted by `Term` (case-insensitive), all sections present even when empty.
8. **Check.** Re-run step 3 with `--only-new`. It will still list the candidates you dropped on purpose (exit code 1); that is expected. Confirm each remaining one was considered, and name the dropped ones in one line of the final message.

## Quality checks

- [ ] The Terms table has exactly the columns `Term | Definition | Synonyms | Homonym notes | Abbreviation | Owner | Status | Source`.
- [ ] No row is `agreed` unless a named owner confirmed it; existing `agreed` rows are unchanged.
- [ ] Every row has a `Source`; unknown definitions are `TBD` with an open question, never a plausible guess.
- [ ] Every homonym and synonym finding has evidence (`file:line`) and an owner.
- [ ] No term appears in two rows unless the rows are qualified senses of a homonym.
- [ ] No definition contains a requirement or a business-rule value.

## Hand-offs

- **Next:** `requirement-phrasing` and `user-story-refiner` use the preferred terms; `domain-model` checks terms against classes.
- **Feeds back to:** `clarifying-questions` with each `TBD` definition and each open homonym or synonym decision; `requirement-classifier` with business rules found inside definitions.

## Non-interactive mode

Write rows as `candidate` or `proposed`, never `agreed`. Put every unresolved homonym, synonym and unknown definition in Open questions with an owner role, and list in the final message the rows added and the questions left open.

## References

- `references/term-patterns.md`: what counts as a term, definition rules, homonym and synonym signals and resolutions, abbreviations, status values. Read it before step 4.
- `references/ireb-anchor.md`: handbook section and glossary terms this skill applies.
- `scripts/mine_terms.py`: candidate frequency across files; `--help` lists every flag.
- `examples/`: the loyalty-points docs, code and tickets, and the glossary they produce.
