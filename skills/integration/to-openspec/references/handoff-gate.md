# Hand-off gate

A tool hand-off is where a vague requirement turns into code that does the wrong thing, so nothing crosses by default unless it is agreed and clean. Run the gate on the selected rows before generating any file.

## Selection rules

| Row | Goes across |
| --- | --- |
| `Status=agreed` | yes (the default selection, `--status agreed`) |
| `Status=implemented` or `verified`, named by ID | yes (a re-export, for example after a change request) |
| `Status=draft` or `proposed`, named by ID | only after the user approves that ID; mark it in `proposal.md` → "Traceability" (Status cell `draft; exception: named by ID, approved by <name> <date>`) |
| `Status=deferred`, `rejected`, `withdrawn` | never |
| `Priority=wont` | never |

## Checks

| # | Check | Blocks | How to clear it |
| --- | --- | --- | --- |
| G1 | Lint errors on the row | yes | `requirement-phrasing` rewrites it; or the user approves the ID as is |
| G2 | `TBD`, `TBC`, `??` or `XXX` in Text or any attribute | yes | answer the open question (`clarifying-questions`); or the user approves the ID with its placeholder (the script then needs the override it names in its refusal message) |
| G3 | Obligation verb is `should` or `may` | asks | keep as `SHOULD`/`MAY` (plain `openspec validate` warns, `--strict` fails), or leave the row out |
| G4 | No acceptance criterion and no `WHEN`/`IF`/`WHILE`/`WHERE` clause | yes | write an acceptance criterion (`testability-check`, or suggest `/user-story-refiner`) |
| G5 | Text longer than 500 characters | warns | split with `requirement-phrasing` |
| G6 | Same R-ID already in `openspec/changes/*/` of another open change | warns | finish or archive the other change first; two open changes on one requirement collide at archive |

Lint warnings and infos other than `open-tbd` do not block; list them in the final message.

## Error-level lint checks by hand

Use these only when neither `re-lint check` nor the `requirement-linter` skill is available. They are the `error` rules of the `re-lint` rule registry.

| Rule | Check on `Text` (or attributes) |
| --- | --- |
| `weak-word` | none of: quickly, user-friendly, appropriate, fast, easy, flexible, robust, efficient, adequate, as soon as possible, etc., and/or, if possible, normally, sufficient, state-of-the-art, seamless, intuitive, minimal, optimal, reasonable, several, some, various, approximately |
| `incomplete-condition` | every `WHEN`/`WHILE`/`WHERE`/`IF` clause is followed by a consequence with `shall`/`should`/`may`; every `IF` has a `THEN` |
| `missing-obligation` | the text has `shall`, `should`, `may` or `must`, or is a user story (`As a ..., I want ...`) |
| `duplicate-id` | the ID appears once in the register |
| `invalid-id` | the ID matches the schema pattern (default `R-` and at least three digits) |
| `missing-attribute` | every required attribute (default `ID, Type, Text, Source, Priority, Status, Rationale`) is filled; `TBD` counts as filled but trips G2 |
| `invalid-enum` | `Type`, `Priority`, `Status` and the optional enumerated attributes use schema values only |

## Gate result table (show it before generating)

```markdown
| ID | Check | Finding | Action |
| --- | --- | --- | --- |
| R-050 | G2 | `within TBD ms` | left out; open question to SH-02 |
| R-051 | G1 | weak-word `quickly` | left out; rephrase with requirement-phrasing |
| R-052 | selection | Status=draft | left out; not approved |
| R-053 | - | clean | goes across |
```
