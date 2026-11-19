---
tags: [re-skills, traceability-matrix]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We use GitHub Actions. Set up a job that rebuilds our requirements trace matrix every night and makes a release tag fail when there are trace gaps.
