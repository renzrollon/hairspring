---
tags: [re-skills, attribute-schema]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Make our requirements match Jira: replace the Status values with To Do, In Progress and Done, and change the requirement ID prefix from R- to LOY- so the IDs look like our Jira keys. Update the schema and the register.

Input files: requirements/requirements.csv, requirements/schema.json, tests/test_redeem.py
