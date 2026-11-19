# Requirements workspace: {system name}

{One sentence: what the system is and who it is for.}

Set up with `re-setup` on {YYYY-MM-DD} by {name or role}. Edit this file freely; re-run `/re-setup` to change the process facets. Tools read `schema.json`; if this file and `schema.json` disagree, correct this file.

## Process facets

| Facet | Choice | Confirmed by | Evidence | What it changes |
| --- | --- | --- | --- | --- |
| Time | {linear / iterative} | {name, YYYY-MM-DD, or assumed} | {file:line, or answer A1} | {one line} |
| Purpose | {prescriptive / explorative} | {...} | {...} | {...} |
| Target | {customer-specific / market-oriented} | {...} | {...} | {...} |
| Criticality | {none / named regulation, audit or contract} | {...} | {...} | {...} |

{If the facets mix: one sentence on which stricter rule was taken and why.}

## Change authority

`schema.json` → `process.change_authority`: {product-owner / product-manager / change-control-board}.

| Requirement status | Who may change it | How the change is recorded |
| --- | --- | --- |
| `draft`, `proposed` | {author} | {edit in place} |
| `agreed`, `implemented`, `verified` | {role: name(s), or TBD} | {`Version` + 1 and `Status` back to `proposed`, or `CR-nnn` via `change-impact`} |
| In a baseline | {role: name(s), or TBD} | {`CR-nnn` via `change-impact`, then a new baseline} |

## Work products kept

`yes` = start now. `later` = start when the trigger happens. `no` = skip; re-run `/re-setup` to change.

| Work product | Path | Owning skill | Kept | Why |
| --- | --- | --- | --- | --- |
| {name} | {`requirements/` path} | {owning skill} | {yes / later / no} | {facet rule or trigger} |

## ID scheme

IDs are opaque: never encode type, component or priority in them, never reuse one (withdrawn and rejected included), never renumber. Allocate with `re-ids` or `re-lint ids next --kind <kind>`.

| Kind | Prefix | Digits | Pattern | Lives in |
| --- | --- | --- | --- | --- |
| {kind} | {prefix} | {n} | {pattern such as R-nnn; never a real ID, or `ids next` counts it as used} | {file} |

## Attribute schema

Columns of `requirements.csv`, in this order: {column list}.

| Attribute | Column | Required | Allowed values |
| --- | --- | --- | --- |
| {name} | {yes / optional} | {yes / no} | {values or format} |

Unknown values are `TBD` plus an open question, never a guess. Lifecycle: `draft` → `proposed` → `agreed` → `implemented` → `verified`, plus `deferred`, `rejected` and `withdrawn` (transitions in `schema.json` → `lifecycle`). Only a named person moves a requirement to `agreed`.

## Definition of Ready

A requirement or story is ready for implementation when:

- [ ] {item}

## Story template

{When stories are kept: this sentence, then the fenced block below with the content of `assets/story-template.md`, copied as is. Otherwise this one line instead: "Not used: stories are not a kept work product."}

`user-story-refiner` writes each story in this shape to `requirements/stories/<epic-slug>.md`, with INVEST and Definition of Ready results below it.

```markdown
{content of assets/story-template.md}
```

## Open questions

| # | Question | Owner | Affects |
| --- | --- | --- | --- |
| {n} | {question} | {role or SH-nn} | {facet, work product or schema key} |

## Setup history

| Date | Change | By |
| --- | --- | --- |
| {YYYY-MM-DD} | {Initial setup / what changed} | {name or role} |
