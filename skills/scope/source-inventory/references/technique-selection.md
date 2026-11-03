# Technique selection and register values

## 1. Columns and values

| Column | Values |
| --- | --- |
| `ID` | `S-nn` from `re-ids` (kind `source`) |
| `Source` | Title of the document, name of the system, or `Name (SH-nn)` for a stakeholder |
| `Kind` | `stakeholder`, `document`, `system` |
| `Category` | See section 2; several joined with `; ` |
| `Version` | Document version or date, system release, export period; `-` for stakeholders; `TBD` if unknown |
| `Location` | Repo-relative path, URL, system or database name, `requirements/stakeholders.md` for stakeholders. Never credentials |
| `Contact` | `SH-nn` or role who represents, owns or can explain the source; `TBD` if unknown |
| `Technique` | `interview`, `workshop`, `questionnaire`, `observation`, `apprenticing`, `document-analysis`, `system-archaeology`, `feedback-analysis`, `reuse` (section 3); several joined with `; `. The same tokens as `candidates.csv`, where `apprenticing` is recorded as `observation` and `reuse` as `document-analysis` |
| `Relevance` | `high`, `medium`, `low` (section 5) |
| `Status` | `planned`, `in progress`, `elicited`, `unavailable`, `retired` (section 6) |
| `Notes` | One or two sentences: why it matters, access limits, evidence for `elicited` (`I-nn`, IDs citing it) |

## 2. Categories

| Kind | Categories |
| --- | --- |
| `stakeholder` | `individual`, `user group`, `organization` |
| `document` | `regulation`, `policy`, `contract`, `terms`, `standard`, `specification`, `process description`, `runbook`, `ticket export`, `feedback`, `report`, `legacy documentation` |
| `system` | `system in operation`, `predecessor`, `neighboring system`, `competitor product` |

## 3. Technique by source

| Source | Default technique | Choose instead when | Skill that runs it |
| --- | --- | --- | --- |
| Stakeholder who knows the domain and can talk | `interview` | Several must agree or ideas are needed: `workshop`. Many people, spread out, confirming known points: `questionnaire`. They do the work but cannot explain it: `observation` or `apprenticing` | `interview-guide` or `clarifying-questions`; `elicitation-workshop`; `questionnaire-builder`; `observation-protocol` |
| User group with no single representative | `questionnaire` or `observation` with a sample | A proxy speaks for them: `interview` with the proxy | `questionnaire-builder`, `observation-protocol` |
| Regulation, policy, contract, terms, standard | `document-analysis` | none | `artifact-mining` |
| Specification, legacy documentation, process description, runbook | `document-analysis` | none | `artifact-mining` |
| Ticket export, app reviews, survey results, complaint logs | `feedback-analysis` | none | `artifact-mining` |
| System in operation or predecessor: code, database, batch scripts, configuration | `system-archaeology` | Its users can show it in use: add `observation` | `artifact-mining` |
| Competitor product | `system-archaeology` (use and inspect it) | none | `artifact-mining` |
| Requirements from an earlier project | `reuse` | none | `artifact-mining` |

## 4. Kind of knowledge and availability

| Signal | Prefer |
| --- | --- |
| The person can tell you (conscious knowledge) | `interview`, `questionnaire` |
| Routine or tacit work: "we just do it", workarounds nobody mentions | `observation`, `apprenticing`; these find the dissatisfiers people no longer notice |
| Nobody has thought about it yet: new ideas, possible delighters | `workshop` with creativity techniques |
| The stakeholder is hard to reach | `document-analysis` or `feedback-analysis` first; keep the interview for what documents cannot answer |

## 5. Relevance

| Value | When |
| --- | --- |
| `high` | Binding: a law, policy, contract, terms or an interface specification the system must follow; the system being replaced; a stakeholder with high influence |
| `medium` | Shapes requirements but does not bind them: feedback, runbooks, reports; a stakeholder with low influence and high interest |
| `low` | Background only; a stakeholder to monitor |

## 6. Status

| Value | Set when |
| --- | --- |
| `planned` | Registered, technique chosen, nothing elicited yet (the default) |
| `in progress` | Elicitation has started: an interview is scheduled, a document is being analyzed |
| `elicited` | A work product shows it: an `I-nn` record, rows in `candidates.csv` or `requirements.csv` citing the source. Put the evidence in Notes |
| `unavailable` | The person cannot be reached or the document cannot be accessed; say why in Notes |
| `retired` | No longer used (superseded version, left the company); keep the row, give the reason |

## 7. Not a source

| Given | Why not | Instead |
| --- | --- | --- |
| "The internet", "best practice", "industry standard" | Nobody can find it again or check it | Ask which document or standard; register that |
| "Common sense", "obviously" | An assumption, not a source | Write it as an open question to a stakeholder |
| A search result or an assistant's answer | Second-hand; may be wrong | Register the document it points to, after reading it |
| A remark in a corridor or a lift | The person is the source | Register the person (stakeholder), with `interview` planned to confirm |
