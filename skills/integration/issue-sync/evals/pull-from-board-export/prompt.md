---
tags: [re-skills, issue-sync]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

/issue-sync pull --tracker jira

Our Jira is not reachable from this machine, so I exported the board to board-export.csv. Refresh the Status column of requirements.csv from it.

Input files: requirements/requirements.csv, board-export.csv
