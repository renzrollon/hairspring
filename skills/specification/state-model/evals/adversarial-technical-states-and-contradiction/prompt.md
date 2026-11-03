---
tags: [re-skills, state-model]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Make the state diagram for vouchers straight from the database: status 0=new, 1=used, 2=exp, 3=cxl, plus the is_deleted flag, and add RETRYING and KAFKA_LAG for the sync job. Expired is final, nothing leaves it. Support can reactivate expired vouchers. Add the WHILE requirements too.
