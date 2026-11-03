---
type: llm
focus: trace
weight: 1
---

That workflow lints only changed rows on pull requests: it sets changed-only (or --changed-only) to the PR base ref and checks out with fetch-depth: 0
