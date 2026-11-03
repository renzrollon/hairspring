# ADR 0003: Requirements are stored as CSV + Markdown in the MVP

- Status: accepted
- Date: 2026-11-03

## Context

Options from the epic: CSV + Markdown, strictdoc `.sdoc`, doorstop YAML.

## Decision

- `requirements/requirements.csv` is the single register of requirement statements (F, Q, C), with a fixed column order defined in `schema.json`.
- Detail work products are Markdown with pipe tables and Mermaid diagrams, and reference requirement IDs.
- strictdoc, doorstop and ReqIF are reached through bridges (`reqif-bridge` now; strictdoc/doorstop adapters in v1).

## Consequences

- Diffable in any code review, editable in a spreadsheet, readable by agents without tooling.
- CSV has no hierarchy; hierarchy is expressed by `Links` and by stories/epics files. Accepted for the MVP.
