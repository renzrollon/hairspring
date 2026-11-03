# Changesets

Every PR that changes a skill, the `re-lint` package or packaging adds one small Markdown file here, named after the change (`glossary-homonym-check.md`):

```markdown
---
bump: minor            # major | minor | patch
scope: skills/glossary # skills/<name>, re-lint, packaging, docs
---

Flag homonyms that differ only by capitalization.
```

On release, the maintainer folds the changesets into `CHANGELOG.md`, bumps `version` in `.claude-plugin/plugin.json`, `packages/re-lint/pyproject.toml` and the changed skills' `metadata.version`, and deletes the folded files.

Bump rules for skills: a changed output shape (columns, headings, file path) is **major**; a new optional section, rule or check is **minor**; wording and examples are **patch**.
