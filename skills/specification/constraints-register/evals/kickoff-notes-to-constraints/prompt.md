---
tags: [re-skills, constraints-register]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We just had the architecture kick-off for the loyalty-points service. Please record the constraints from these notes in our requirements:

1. Wei Jie Chua (platform lead, SH-08): every new service runs on the shared Kubernetes platform, no exceptions this year.
2. Farid Osman (data protection officer, SH-04): member personal data must stay in Singapore, per our data retention policy DRP-2024 (source S-05).
3. Grace Lim (Finance, SH-03): the legacy loyalty module's vendor contract ends on 2027-03-31 and we won't extend it.
4. The squad wants Kafka between the POS and the service.

Today is 2026-11-03.
