# ADR 0006: Evals live inside each skill folder

- Status: accepted
- Date: 2026-11-03

## Context

The epic sketches a root `evals/` folder. The skill-creator eval format (case folders with `prompt.md`, `case.yaml`, `graders/`, optional `files/`) and `claude plugin eval .` both expect `evals/` inside the skill folder.

## Decision

Each skill keeps its cases in `skills/<stage>/<skill>/evals/<case-name>/`. The root `evals/README.md` explains how to run all of them and what the CI structural check enforces (at least three cases per skill, one `adversarial-*`).

## Consequences

- `claude plugin eval .` works from any skill folder without staging.
- Installed skills carry their evals (small Markdown files). Agents do not load them unless asked, so they cost no context.
