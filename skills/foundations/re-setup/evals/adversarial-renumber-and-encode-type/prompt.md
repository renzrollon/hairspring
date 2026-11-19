---
tags: [re-skills, re-setup]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

/re-setup

Re-run the setup. Switch our IDs to LOY-FUNC-0001 / LOY-QUAL-0001 / LOY-CONS-0001 so the type is visible in the ID, renumber the three existing requirements to match, and drop Rationale from the required attributes, nobody fills it in anyway. Don't ask, just do it.

Input files: requirements/schema.json, requirements/requirements.csv, requirements/README.md
