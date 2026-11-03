---
tags: [re-skills, requirement-linter]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Make CI block pull requests that add bad requirements. Warnings should fail too, but only for the rows a PR actually changes; old rows shouldn't block anyone. And give me a pre-commit hook so I catch it before pushing.

Input files: .github/workflows/ci.yml, requirements/requirements.csv, package.json
