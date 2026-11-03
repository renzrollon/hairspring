---
tags: [re-skills, state-model]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Model the lifecycle of a points transaction for the loyalty service and add the requirements it implies to requirements/requirements.csv. A transaction starts Pending when the POS sends a completed purchase. Points stay pending during the 24-hour return window, then they are Posted. Posted points can be Redeemed for a voucher or Expire after the expiry period. A return reverses the points (Reversed), whether the transaction is pending or posted. If the points were already redeemed when the return comes in, we have not decided what happens. Source for all of this: programme terms draft v3 (S-01). I can't answer questions today, so write the file and list what is open.
