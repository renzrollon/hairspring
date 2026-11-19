---
tags: [re-skills, traceability-matrix]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our trace report says R-021 has no test, but there is one in web/__tests__/history.ts, and our TypeScript code lives in web/client/. Rebuild the trace matrix so it sees them, and tell me what is really missing.

Input files: requirements/requirements.csv, web/, internal/
