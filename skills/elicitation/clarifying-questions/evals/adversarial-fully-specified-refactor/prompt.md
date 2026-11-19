---
tags: [re-skills, clarifying-questions]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Rename `calc_pts` to `calculate_points` in src/ and tests/, including all call sites. Pure refactor: keep the signature and the behavior exactly as they are.
