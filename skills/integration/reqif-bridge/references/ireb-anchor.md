# IREB anchor: `reqif-bridge`

> re-skills is independent of IREB and not endorsed by it. This file cites section numbers and public glossary term names only. It does not reproduce handbook, syllabus or glossary text.

| Field | Value |
| --- | --- |
| CPRE FL Handbook 1.2 | §7 Tool interoperability |
| CPRE FL Syllabus 3.2 | Chapter 7 (Tool support) |
| IREB Glossary 2.2 terms | Requirements management; Attribute; Baseline; Version; Change request; Traceability |
| Quality criteria touched | traceable, conformant, consistent (set); modifiable (set) |
| Other standards | OMG Requirements Interchange Format (ReqIF) 1.2 (title only); ProSTEP iViP ReqIF Implementation Guide v1.10 (title only) |

## How this skill applies the practice

- Uses the open interchange format that requirements management tools share, so a customer or supplier can work in their own tool without re-keying the set.
- Keeps one stable identity per requirement across tools (the requirement ID as the ReqIF identifier), which is what makes a round-trip mergeable and traceable.
- Treats an import as incoming change, not as truth: every difference is classified, reviewed and decided, and edits to agreed requirements go through change control.
- Never deletes on import; removals are explicit decisions with a reason, so the history of the set stays reconstructable.
- States the loss of fidelity up front (rich text, enumerations, structure, tool-specific attributes), because an exchange that silently drops information breaks the shared understanding it was meant to support.

## What this skill deliberately leaves out

- Deciding whether an accepted customer edit is in scope or affordable: `change-impact`.
- Naming and freezing the exchanged set: `baseline`.
- Producing a readable specification document: `spec-assembler`.
