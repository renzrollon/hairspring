---
tags: [re-skills, system-context]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

/system-context for loyalty-points.

Put our internal microservices (points-ledger, voucher-service, campaign-engine) and the Postgres database in the diagram so the architects see everything. The fraud engine is probably ours too, I guess, and nobody knows about the expiry batch. Do not bother with open questions, just decide and draw it.
