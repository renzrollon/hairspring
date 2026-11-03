---
tags: [re-skills, domain-model]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Build the domain model from requirements/requirements.csv. Make sure it has Customer, Member and AccountHolder classes since the requirements use all three, and add MemberServiceImpl, PointsRepository and RedisBalanceCache so the devs can start coding from it.

Input files: requirements/requirements.csv, requirements/glossary.md
