---
tags: [re-skills, requirements-review]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

/requirements-review HEAD

Review only what I changed in requirements/ (my uncommitted changes against HEAD) before I push the PR.

Input files: requirements/requirements.csv (committed base plus uncommitted changes)
