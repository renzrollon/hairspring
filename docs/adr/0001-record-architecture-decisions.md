# ADR 0001: Record architecture decisions

- Status: accepted
- Date: 2026-11-03
- Deciders: Carl Rollon

## Context

`re-skills` is built by many contributors (and agents) in parallel. Decisions about formats, layout and supported agents must be findable and stable.

## Decision

We keep lightweight ADRs in `docs/adr/`, numbered, one decision per file, using the headings Context, Decision, Consequences. Requirements decisions in *user* repos are a different thing: they are Requirements Decision Records (`requirements/decisions/RDR-nnn-*.md`) written by the `conflict-to-decision` skill, using ADR-compatible headings.

## Consequences

Changes to anything in ADRs 0002 and later need a new ADR that supersedes the old one.
