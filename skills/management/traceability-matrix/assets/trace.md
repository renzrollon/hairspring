# Trace matrix

| Field | Value |
| --- | --- |
| Generated | YYYY-MM-DD |
| Commit | <short SHA, or "not a git repository"> |
| Command | `re-lint trace build <flags>` (or "built manually") |
| Requirements read | <register files> |
| Code globs | <globs> |
| Test globs | <globs> |

## Coverage summary

| Measure | Count |
| --- | --- |
| Requirements in scope (not withdrawn or rejected) | |
| ... with a source | |
| ... with a decision or ADR | |
| ... with code or a commit | |
| ... with a test | |
| Gaps: requirements without tests | |
| Gaps: requirements without a source | |
| Gaps: tests citing unknown or retired IDs | |
| Gaps: code citing unknown or retired IDs | |
| Gaps: agreed or later requirements without an implementation reference | |
| Informational: tests citing no requirement | |
| Informational: code files citing no requirement | |

## Graph

```mermaid
graph LR
  %% sources --> requirements --> decisions / ADRs, code files, test files
  classDef gap stroke:#d33,stroke-width:3px
  classDef retired stroke-dasharray: 5 5,color:#777
```

## Gaps

### Requirements without tests

| ID | Status | Verification | Text |
| --- | --- | --- | --- |

### Requirements without a source

| ID | Status | Source cell |
| --- | --- | --- |

### Tests citing unknown or retired IDs

| Test | Cited ID | Problem | Evidence |
| --- | --- | --- | --- |

### Code citing unknown or retired IDs

| File | Cited ID | Problem | Evidence |
| --- | --- | --- | --- |

### Agreed or later requirements without an implementation reference

| ID | Status | Text |
| --- | --- | --- |

## Unlinked (informational)

| Kind | Item | Evidence |
| --- | --- | --- |
