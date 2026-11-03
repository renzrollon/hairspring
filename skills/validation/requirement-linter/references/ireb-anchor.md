# IREB anchor: `requirement-linter`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §3.2.1 Natural-language pitfalls (in §3.2, natural-language-based work products) |
| CPRE FL Syllabus 3.2 | Chapter 3 (Work products and documentation practices) |
| IREB Glossary 2.2 terms | Requirement; Requirements template; Ambiguity; Attribute |
| Quality criteria touched | unambiguous, verifiable, complete (single requirement); conformant, traceable (set) |
| Other standards | EARS (Mavin et al., 2009); ISO/IEC/IEEE 29148:2018, clause "Requirements language criteria" (title only) |

## How this skill applies the practice

- Turns the known natural-language pitfalls (vague qualifiers, absolute quantifiers, passive voice without an actor, nominalizations, incomplete conditions, missing or wrong obligation verbs, compound statements) into deterministic rules that give the same answer every run.
- Adds the structural checks a register needs before anyone reads it: unique and well-formed IDs, required attributes present, attribute values from the agreed lists, sources that resolve, and detail registers that still match the register.
- Keeps judgment out of the verdict: the script decides pass or fail, so the check can gate CI; the model explains each finding and proposes a rewrite that never invents a value.
- Lets a team tune the rules in `schema.json` as a recorded decision, instead of silencing findings ad hoc.

## What this skill deliberately leaves out

- Judging adequacy, necessity, completeness and consistency of the set: `requirements-review`.
- Rewriting statements into phrase templates: `requirement-phrasing`.
- Measurable acceptance criteria and verification methods: `testability-check`.
