---
tags: [re-skills, requirement-classifier]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Which of these are actually requirements? Classify these lines from our redemption PRD (author Mei Tan, SH-01) before we phrase them:

1. A member can redeem posted points for a voucher at checkout.
2. Voucher validation at the POS must respond within 300 ms.
3. We will use gRPC between the POS and the loyalty service.
4. TillPoint will release POS 2.2 in March.
5. Redemption records must be kept for 7 years under Finance policy DRP-2024.
6. Today vouchers are printed on paper by the store.
7. Members love surprises, maybe a mystery voucher once a year?
