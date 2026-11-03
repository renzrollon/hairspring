# ADR 0002: Product name `re-skills`, hosted in `renzrollon/hairspring`

- Status: accepted
- Date: 2026-11-03

## Context

The epic recommends the product name `re-skills` (no IREB trademark exposure, searchable) and a repo `renzrollon/re-skills`. The repository that exists is `renzrollon/hairspring`.

## Decision

- The product, the Claude Code plugin and the marketplace entry are named `re-skills`.
- The source lives in `renzrollon/hairspring`. Every install command in the docs uses `renzrollon/hairspring` because that is the URL that works today.
- If the repository is renamed to `re-skills`, GitHub redirects keep old install commands working; update the docs in the same PR.

## Consequences

The marketplace name (`hairspring`, from the repository) and the plugin name (`re-skills`) differ. Docs always show both: `/plugin install re-skills@hairspring`.
