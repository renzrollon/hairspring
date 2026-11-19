# Mermaid notes

Mermaid is the default diagram language because GitHub, GitLab, Obsidian and most IDE previews render it. GitHub does not publish which Mermaid version it runs, so write for the common subset and check every new diagram in a GitHub preview.

| Diagram | Used by | Pitfalls |
| --- | --- | --- |
| `flowchart LR` (context) | `system-context` | Keep node labels short; quote labels containing parentheses or punctuation: `A["POS (TillPoint)"]`. |
| `flowchart` with `subgraph` lanes | `process-flow` | Long lane titles get clipped; keep them to one or two words. Mermaid 11.4 draws arrowheads on `---`; use `-->` and `-.->` deliberately. |
| `flowchart` as a use case diagram | `use-case-spec` | Mermaid has no use case diagram. The convention: stadium nodes `([Redeem voucher])` inside a `subgraph` for the system boundary, actors outside. PlantUML is the alternative when a true UML diagram is required. |
| `stateDiagram-v2` | `state-model` | Only one self-transition per state is drawn; a second one silently disappears. Model a distinct waiting condition as its own state. Composite states, choice, fork and join are not parsed by `check_states.py`. |
| `classDiagram`, `erDiagram` | `domain-model` | Multiplicity labels go in quotes: `Member "1" --> "*" PointsTransaction`. |
| `quadrantChart` | `stakeholder-map` | Point labels with parentheses break some renderers; use plain names. |

Validate offline with `npx -y @mermaid-js/mermaid-cli -i file.md -o /tmp/out.svg` when Node is available.
