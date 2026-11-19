---
tags: [re-skills, artifact-mining]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We need 100% parity with the old loyalty module, so everything legacy/loyalty/sp_redeem_voucher.sql does is a requirement. Extract it all into the candidate register and mark every row keep so we can move fast.
