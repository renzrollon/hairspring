# Epic: RE Skills — Requirements Engineering Skills for AI-Assisted Engineering Teams

Nov 3, 2026 · @Carl Rollon

## Summary

`re-skills` is an open-source catalogue of about 30 agent skills that give engineering teams IREB-grade requirements engineering without a requirements engineer in the room. Each skill is a small, composable `SKILL.md` procedure anchored to one CPRE Foundation Level practice and produces a concrete work product: an interview guide, a context diagram, a requirements table in template form, a review findings list, a traceability matrix. The catalogue is grouped into eight stages that follow the RE lifecycle from scoping to change management.

Why now: spec-driven development toolkits (spec-kit, OpenSpec, Kiro) have made the spec the unit of work for coding agents, but they all start at "write the spec". The harder part is upstream: finding the right sources, asking the questions that surface quality requirements and constraints, detecting conflicts, and validating before code is written. `mattpocock/skills` covers the engineering loop (grill, spec, tickets, TDD, review); the one direct competitor (RE-Skills: 44 Wiegers-based skills, 22 stars) has no validators, no IREB vocabulary and no bridges to the tools teams run. This epic fills that gap.

Working name `re-skills`; repo `renzrollon/re-skills`; licence MIT. The name avoids the IREB trademark while the content stays aligned with the public CPRE syllabus and glossary (see Risks).

## Goals, non-goals, users

The epic is done when an engineering team with no RE training can run a requirements loop end to end using the P0 skills, and every output is something a reviewer can read, edit and trace.

Goals

1. Ship 12 P0 skills (the MVP) that cover one full pass: scope, elicit, specify, validate, trace.
2. Anchor every skill to a CPRE FL handbook section and glossary term, so the vocabulary is the one in the standard, not invented.
3. Make outputs work products, not chat: Markdown tables, Mermaid/PlantUML diagrams, CSV/XLSX matrices, form and questionnaire templates.
4. Compose with what teams already run: outputs feed spec-kit, OpenSpec, Jira/GitHub issues and ADRs rather than a new tool.
5. Stay agent-agnostic: Agent Skills format (`SKILL.md`), installable with `npx skills add` and as a Claude Code plugin.

Non-goals

- Not a requirements management system or database (no replacement for DOORS, Jama, StrictDoc).
- Not CPRE exam preparation.
- No reproduction of IREB handbook text; the skills reference public syllabus and glossary terms only.
- Not a graphical modelling tool; all diagrams are text-based and diffable.

Target users

| Role | Pain today | First skills they would pull |
| --- | --- | --- |
| Engineering team / tech lead | Vague tickets, rework from missed quality requirements, agents that implement the wrong thing | `clarifying-questions`, `quality-requirements`, `requirements-review`, `traceability-matrix` |
| Product owner / business analyst | Inconsistent story quality, slow refinement, no record of why a requirement exists | `user-story-refiner`, `elicitation-workshop`, `prioritization`, `stakeholder-map` |
| Software architect | Constraints and quality attributes discovered after design | `system-context`, `quality-requirements`, `constraints-register`, `conflict-to-decision` |
| QA / test engineer | Untestable requirements, no verification plan | `testability-check`, `requirements-review`, `traceability-matrix` |
| Coding agent (model-invoked) | Starts implementing before the requirement is clear | `clarifying-questions`, `requirement-classifier`, `requirements-review` |

## Landscape and white space

The high-star agent toolkits treat requirements as one "write the spec" step before coding; the one direct competitor is Wiegers-based, has no validators and 22 stars; nothing maps the CPRE syllabus or bridges agent skills to docs-as-code requirements tools. Star counts are as shown on GitHub on 3 Nov 2026 and are approximate.

Agent-skill repos and spec toolkits (closest competitors)

| Project | Stars | What it covers in RE terms | Gap it leaves |
| --- | --- | --- | --- |
| [jdm4pku/RE-Skills](https://github.com/jdm4pku/RE-Skills) | 22 | 44 SKILL.md skills in 8 phases (foundation, elicitation, analysis and modelling, specification, validation, prioritisation, management, cross-cutting); cites IEEE 29148, ISO 25010, EARS, Cockburn, Gilb, Fagan; built on Wiegers and Beatty. v1.0 Apr 2026, 3 commits. | Direct competitor. No IREB vocabulary, no scripts or validators, no licence named, no bridges to trackers or RM tools, negligible adoption. |
| [adbstyle/requirementsengineer-skill](https://github.com/adbstyle/requirementsengineer-skill) | 0 | Claude Code plugin "following IREB standards": perspective-based review, NFR tables, Jira intake. | Single plugin, validation only; the only IREB-branded entry and it has no users. |
| [zeeshanhanif/agentic-sdlc-kit](https://github.com/zeeshanhanif/agentic-sdlc-kit) | 5 | One `requirements-engineering` skill: interview to `srs.md` with EARS and stable IDs, `use-cases.md`, `rtm.md`. | Monolithic; no technique selection, no review stage. |
| [github/spec-kit](https://github.com/github/spec-kit) | 145k | `specify, plan, tasks, implement`; spec as hand-off to coding agents. | No elicitation discipline, no quality criteria, no traceability beyond the feature folder. |
| [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | 73k | `explore, propose, apply, archive`; Markdown specs with SHALL and WHEN/THEN scenarios. | Delta-spec workflow for coders; no RE practices, no quality model. The natural export target for this catalogue. |
| [obra/superpowers](https://github.com/obra/superpowers) | 311k | `brainstorming` teases a design doc out of a conversation, then `writing-plans`. | Requirements stay implicit inside brainstorming; no templates or standards. |
| [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | 55k | Product brief, PR/FAQ, PRD with an NFR section; a PO agent writes `R<n>` requirements. | PM-flavoured; no stakeholder or interview technique, no validation stage. |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 307k | 27 skills; `grill-me`/`grilling`, `to-spec`, `to-tickets`, `domain-modeling`, `to-questionnaire`. The format and invocation model this epic copies. | No RE standard referenced; spec is a conversation summary. |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | 40k | `skills/prd` interview to PRD; epic and feature breakdown prompts. | PRD-centric, no validation or management. |
| [Kiro specs](https://kiro.dev/docs/specs/concepts/) | n/a | `requirements.md` with user stories and EARS acceptance criteria, `design.md`, `tasks.md`. | Proprietary IDE; specification only. |
| [anthropics/skills](https://github.com/anthropics/skills), [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills), [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | 187k / 79k / 26k | No RE or specification skill; the subagent lists offer `business-analyst` persona prompts only. | A listing slot is open in each. |

Docs-as-code and open-source requirements tooling (integration targets, not competitors)

| Tool | Stars | Purpose | Relevance |
| --- | --- | --- | --- |
| [strictdoc](https://github.com/strictdoc-project/strictdoc) | 380 | Plain-text `.sdoc` requirements, HTML export, web UI; ships `AGENTS.md`. | Export target; its [reqif](https://github.com/strictdoc-project/reqif) library (59) powers `reqif-bridge`. |
| [doorstop](https://github.com/doorstop-dev/doorstop) | 690 | YAML requirement items in git with link-integrity checks. | Alternative storage format for `traceability-matrix`. |
| [sphinx-needs](https://github.com/useblocks/sphinx-needs) | 319 | Need objects in Sphinx, `needs.json`, code links, test-report needs. | Publishing target for `spec-assembler`. |
| [rmtoo](https://github.com/florath/rmtoo) | 232 | Plain-text to HTML/LaTeX, dependency graphs, quality checks. | Prior art for `requirement-linter`. |
| [bmw-software-engineering/trlc](https://github.com/bmw-software-engineering/trlc) and [lobster](https://github.com/bmw-software-engineering/lobster) | 114 / 62 | Requirements-as-code DSL with typed metadata; traceability and coverage into C++/Python/tests. | Prior art for IDs-in-code and coverage reporting. |
| [eclipse-capra](https://github.com/eclipse-capra/capra), [OpenReqEU](https://github.com/OpenReqEU) | 3 / small | Trace links across artefacts; H2020 requirement-quality and similarity services. | Research prior art; both largely dormant. |

Standards the skills anchor to: [IREB CPRE Foundation Level](https://cpre.ireb.org/en/concept/foundationlevel) (syllabus 3.2, handbook 1.2, glossary 2.2), [EARS](https://alistairmavin.com/ears/), [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html), [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html), [Volere](https://www.volere.org/templates/volere-requirements-specification-template/) (paid licence, free academic), Planguage, [Example Mapping and Gherkin](https://cucumber.io/docs/bdd/example-mapping/), [C4 system context](https://c4model.com/diagrams/system-context), and the [agentskills.io specification](https://agentskills.io/specification) for the skill format.

Commercial requirements tools now ship AI features that overlap with Stage 5: Jama Connect Advisor and ReqView score requirements against INCOSE and EARS rules; IBM DOORS Next, Polarion and Codebeamer add ambiguity detection and generation; Visure exposes an MCP server. None of them is open, agent-native or cheap enough for a team that keeps requirements in git.

White space: an IREB-aligned, agentskills.io-conformant catalogue with the mattpocock user/model split, bundled deterministic validators, declared hand-offs between skills, and bridges to OpenSpec, trackers and ReqIF is unoccupied. The risk is not competition but the field moving fast: the scan date matters.

## Design principles and skill anatomy

Every skill is one CPRE practice, packaged in the Agent Skills format, that ends in a work product a reviewer can diff. The conventions below are borrowed from `mattpocock/skills` (small, composable, user-invoked orchestrators over model-invoked primitives) and tightened for RE.

1. One practice per skill. Each skill maps to one handbook section and names its glossary terms in `references/ireb-anchor.md`. No skill reproduces handbook text.
2. Work product out, not advice. Every skill ends in a file with a fixed shape (same columns every run), so outputs can be versioned, diffed and traced.
3. Value-oriented quality (IREB Principle 1). Skills ask for the level of detail the next decision needs. The review skill grades adequacy and understandability before anything else, because without those a requirement is useless whatever else it satisfies.
4. Text-based models only. Mermaid first (renders in GitHub, GitLab, Obsidian), PlantUML or C4 DSL as an option. Diagrams live next to the requirements they illustrate.
5. One interview primitive. A shared `re-interview` primitive (one question at a time, W-questions, confirm understanding, record source) sits under `clarifying-questions`, `interview-guide` and `conflict-detector`, the way `grilling` sits under the grill-\* skills.
6. Deterministic where it can be. Weak words, universal quantifiers, passive voice, nominalisations, incomplete conditions, duplicate IDs and missing attributes are caught by scripts, not by model judgement, so they can run in CI.
7. IDs and attributes from the first requirement. Everything emitted carries `ID, type (F/Q/C), text, source, status, priority, rationale`. The minimum schema is defined once in `re-setup` and consumed by every other skill.
8. Declared hand-offs. Each `SKILL.md` lists what it consumes (and from which skill) and what it emits, so the catalogue composes as a pipeline rather than 35 independent prompts.

Skill anatomy

```markdown
skills/
  specification/
    requirement-phrasing/
      SKILL.md                      # frontmatter + procedure + hand-offs
      references/ireb-anchor.md     # handbook section, glossary terms, quality criteria touched
      references/checklist.md       # EARS patterns, obligation verbs, NL pitfalls
      assets/requirements.csv       # ID,Type,Text,Source,Priority,Status,Rationale
      scripts/lint_requirements.py  # deterministic checks, exit code for CI
```

```markdown
---
name: requirement-phrasing
description: Rewrite requirement-like sentences into ISO 29148 / EARS phrase templates with shall/should/may obligations, one requirement per sentence, with IDs and attributes. Use when a ticket, PRD, transcript or chat contains requirements that must become unambiguous and verifiable.
---
```

Each catalogue entry below follows one card: skill name and invocation mode (user or model), brief, use case, output work product with its IREB anchor, and priority (P0 ships in the MVP).

## Skill map

&#91;embedded content: skill map · 8 stages, 35 skills, 12 in the MVP\]

Stages 0 and 7 are enablers; stages 2 to 6 repeat whenever a change or a new insight arrives, which is why management feeds back into elicitation.

## Stage 0 — Foundations and setup

These three skills make the rest of the catalogue consistent: a configured process, a shared vocabulary, and a reliable way to tell a requirement from a fact or a design decision.

| Skill | Brief | Use case | Output · IREB anchor | Priority |
| --- | --- | --- | --- | --- |
| `re-setup` (user) | One-time per repo. Short interview picks the RE process facets (linear/iterative, prescriptive/explorative, customer-specific/market-oriented), the work products to keep, the ID scheme, the attribute schema and a Definition of Ready. Writes `requirements/README.md` and schema files that every other skill reads. | New payments-reconciliation service, agile team, internal customer. `/re-setup` selects iterative + explorative + customer-specific, creates `requirements/` with `glossary.md`, `requirements.csv` schema, story template and DoR checklist. | `requirements/README.md`, `schema.json` · Handbook §5.1–5.3 process facets, §3.1.6 planning work products, §6.5 attributes | P1 |
| `glossary` (model) | Builds and maintains the project glossary: term, definition, synonyms, homonyms, abbreviations, owner. Mines candidate terms from docs, code and tickets; flags one word used in several senses and two words for one thing. Reuses `domain-modeling` from mattpocock/skills where present. | Agent reads 40 Jira tickets and the domain package, produces `glossary.md` separating Settlement, Clearing and Reconciliation, and flags `account` used in three senses. | `glossary.md` · §3.5 glossary, Principle 3 shared understanding | P0 |
| `requirement-classifier` (model) | Classifies each statement as functional, quality or constraint using the concern test (what concern does it address, not what-vs-how). Flags non-requirements (facts in present tense or `will`), design decisions posing as requirements, and a first Kano guess (dissatisfier / satisfier / delighter). | Paste a PRD section. Table of 23 statements: 14 F, 5 Q, 2 C, 2 statements of fact, 1 solution-in-disguise (`use Redis for sessions`) flagged for the architect. | Classified table with IDs · §1.2 kinds of requirements, §4.2.1 Kano | P1 |

## Stage 1 — Scope and context

Most late requirements are boundary mistakes: something assumed to be outside the system, or a stakeholder nobody asked. These skills make the system boundary, the context boundary and the sources explicit before elicitation starts.

| Skill | Brief | Use case | Output · IREB anchor | Priority |
| --- | --- | --- | --- | --- |
| `system-context` (user) | Interviews for the system boundary and the context boundary, names the grey zones on each, then draws the context diagram (Mermaid flowchart or C4 context; PlantUML optional) and a context table of external actors, systems, interfaces and data flows. Open boundary questions come out as decisions to take, not assumptions. | Loyalty-points service. Diagram shows POS, CRM, fraud engine and customer app as actors; context table lists 6 interfaces; grey zone `points-expiry batch job: in or out of scope?` is logged as decision D-01 for the PO. | `context.md` with diagram + table + open decisions · §1.4 system context and boundaries, §3.4.2 context models | P0 |
| `stakeholder-map` (user) | Stakeholder inventory with role, goals, influence, interest, availability and named representative; power/interest quadrant (Mermaid `quadrantChart`); gap check against a role checklist (operations, security, legal, support, data protection). | KYC rework kick-off. 11 stakeholders mapped; the gap check shows nobody represents the compliance officer and operations support was not invited. | `stakeholders.md` + quadrant · §1.3 stakeholders, §4.1 requirement sources | P1 |
| `source-inventory` (model) | Catalogue of requirement sources: stakeholders, documents (regulations, contracts, legacy specs, runbooks) and systems in operation, each with a source ID and the planned elicitation technique. Source IDs are what backward traceability later points at. | Lists MAS Notice 626, the legacy SOAP WSDL and a Zendesk feedback export; assigns document analysis, system archaeology and feedback analysis respectively; source IDs S-01..S-14. | `sources.csv` · §4.1 sources, §6.6 backward (pre-RS) traceability | P1 |

## Stage 2 — Elicitation

Elicitation turns implicit needs into explicit, verifiable requirements. The handbook splits techniques into gathering (questioning, collaboration, observation, artifact-based) and design/idea-generating; the catalogue covers each family once, plus the one engineering teams use daily: asking the right questions before building.

| Skill | Brief | Use case | Output · IREB anchor | Priority |
| --- | --- | --- | --- | --- |
| `clarifying-questions` (model) | Before implementing, generates the smallest set of questions whose answers would change the design, grouped by functional, quality, constraint and boundary. Uses the `re-interview` primitive (W-questions, one batch, prioritised). Answers are recorded as requirements with the person as source. The RE counterpart of `grill-me`. | Ticket `Add export to CSV`. Seven questions: which entities, maximum rows, PII masking, who triggers it, sync or async, retention of the file, encoding. Answers become R-041..R-047 with source = PO. | Question list + appended requirements · §4.2.2 questioning techniques, Principle 3 shared understanding | P0 |
| `interview-guide` (user) | Role-tailored interview script: goals, warm-up, open-to-closed funnel, probes for quality requirements (ISO 25010 checklist) and constraints, confirmation and close. Ships a capture sheet and a post-interview summary template whose rows feed `requirement-classifier`. | 30-minute interview with the branch operations lead on cash ordering. Guide plus capture sheet; the transcript is fed to `requirement-classifier` the same afternoon. | `interview-<role>.md` + capture sheet · §4.2.2 interviews, ISO 25010 as checklist | P1 |
| `artifact-mining` (model) | Document analysis, system archaeology and feedback analysis in one skill: extracts candidate requirements from specs, code, API contracts, tickets and support logs, each with the source quote and location. Marks legacy behaviour as `keep / drop / confirm` so bad old solutions do not survive by default. | COBOL batch to service migration. Reads JCL, copybooks and two runbooks; produces 64 candidates with `file:line` sources, 9 marked `probable obsolete rule` for the business owner. | `candidates.csv` with source refs · §4.2.2 artifact-based techniques | P0 |
| `elicitation-workshop` (user) | Workshop design: objective, participants, agenda, technique selection (brainstorming, brainstorming paradox, 6-3-5, six thinking hats, morphological matrix, story mapping), facilitation notes, parking lot, and a capture template that lands ideas as classified candidates. | 90-minute remote workshop to find delighters for mobile onboarding. One 6-3-5 round and dot voting; 18 candidate ideas tagged by Kano category. | `workshop-plan.md` + capture template · §4.2.2 workshops, §4.2.3 creativity techniques | P2 |
| `questionnaire-builder` (user) | Designs a quantitative or qualitative questionnaire: one hypothesis per question, closed vs open, scales, pilot and analysis plan. Exports Markdown, a CSV for Google or Microsoft Forms import, and an analysis sheet. | Validate six interview findings with 120 field agents: 12 Likert items and 2 open questions, import file, analysis sheet with agreed cut-offs. | `questionnaire.md`, `form-import.csv`, `analysis.xlsx` · §4.2.2 questionnaires | P2 |
| `observation-protocol` (user) | Field observation or apprenticing plan with a capture template (task, trigger, workaround, dissatisfier, frequency), consent note and debrief script. Observation is the technique that finds what people no longer notice. | Half-day shadowing in a call centre captures five workarounds, which become dissatisfiers and therefore must-haves in the backlog. | `observation-plan.md` + capture template · §4.2.2 observation techniques | P2 |

## Stage 3 — Documentation and specification

This is where generated diagrams and templates pay off. The handbook's three work-product families map directly onto skills: natural language with phrase templates, form templates for use cases, and model-based work products for structure, function and behaviour, plus the quality requirements and constraints that elicitation tends to under-collect.

| Skill | Brief | Use case | Output · IREB anchor | Priority |
| --- | --- | --- | --- | --- |
| `requirement-phrasing` (model) | Rewrites statements into ISO 29148 or EARS phrase templates (ubiquitous, WHEN event-driven, WHILE state-driven, WHERE optional, IF-THEN unwanted behaviour, complex). Fixes the obligation verb (shall / should / may; `will` is a fact, not a requirement), splits compound sentences, assigns IDs and attributes. | `The system should quickly show the balance after login` becomes `WHEN the customer completes login, the system shall display the account balance within 2 s` (R-012, Q, source PO, rationale: usability target from interview I-03). | `requirements.csv` rows · §3.3.1 phrase templates, §3.2 natural-language rules | P0 |
| `user-story-refiner` (user) | Rewrites or splits stories to the Cohn template with a benefit, runs INVEST, writes acceptance criteria (Given/When/Then, always including one unwanted-behaviour case), checks the Definition of Ready, proposes vertical slices. | Epic `Bulk payments` becomes 6 stories with 3–5 ACs each; two ACs are flagged untestable and sent to `testability-check`. | Stories + ACs in the tracker format · §3.3.1.2 user-story template and acceptance criteria | P0 |
| `quality-requirements` (user) | ISO 25010 walkthrough tailored to the system type. Produces measurable quality requirements (metric, target, condition, measurement method), flags anything unquantified, and tags the ones that are architecture drivers. | API gateway: 14 quality requirements across performance efficiency, reliability, security and maintainability. `Should be scalable` becomes `p95 latency < 300 ms at 2,000 req/s sustained for 10 min`. | `quality-requirements.md` · §1.2 quality requirements, §4.2 ISO 25010 as checklist | P0 |
| `use-case-spec` (user) | Cockburn-style form template (actor, goal, pre- and postconditions, trigger, main flow, alternatives, exceptions) plus a use case diagram (Mermaid or PlantUML) and, for complex flows, an activity diagram of the scenarios. | `Approve loan application` with four alternative flows and an activity diagram for the maker-checker path. | `uc-<name>.md` + diagrams · §3.3.2 form templates, §3.4.2.2 use case diagrams | P1 |
| `domain-model` (model) | Class or ER diagram (Mermaid `classDiagram` / `erDiagram`) of business objects, attributes and multiplicities derived from the requirements and the glossary. Flags glossary terms with no class and classes with no glossary entry. | From 40 requirements: 12 entities; finds `Customer` and `Account holder` used for one concept and raises it to `glossary`. | `domain-model.md` · §3.4.3 structure and data | P1 |
| `process-flow` (model) | Activity diagram with swimlanes (Mermaid flowchart with subgraphs, or PlantUML activity) for a scenario or business process: decisions, parallel flows, who is responsible. Exceptions are drawn as separate flows when the main one would stop being readable. | Refund process across customer app, operations and the PSP: three lanes, two decisions; the chargeback exception is its own flow. | `flow-<name>.md` · §3.4.4 function and flow | P1 |
| `state-model` (model) | State machine (Mermaid `stateDiagram-v2`) for an entity: states, events, guards, actions. Checks for unreachable states and missing transitions and emits one EARS `WHILE` requirement per state-dependent behaviour. | Payment: Initiated, Authorised, Captured, Failed, Reversed. Finds no transition from Authorised on timeout; a new requirement R-071 results. | `state-<entity>.md` + requirements · §3.4.5 state and behaviour | P1 |
| `constraints-register` (model) | Technical, legal and regulatory, organisational, cultural and environmental constraints with source, rationale and expiry. Separates constraints from design decisions: a constraint restricts the solution space because someone outside the team says so. | Lists `must run on OpenShift 4.x`, `data residency in Singapore`, `vendor contract ends 2027-03`; flags `use Kafka` as a design decision unless the platform team mandates it. | `constraints.csv` · §1.2 constraints, §4.2 restrictions of the solution space | P1 |
| `spec-assembler` (user) | Assembles the work products into a specification structure (ISO 29148 SRS, Volere, or a lightweight arc42-aligned requirements chapter) in Markdown or docx: table of contents, cross-references, glossary, attribute views, traceability appendix. | Vendor RFP: an SRS with one context diagram, 86 requirements (F/Q/C), glossary and trace matrix, exported to docx for procurement. | `spec.md` / `spec.docx` · §3.6 documentation structures, §6.5 views | P2 |

## Stage 4 — Negotiation and conflict resolution

A requirement set with no conflicts is a sign you missed some. Two skills cover the four conflict tasks in the handbook: identify, analyse, resolve, document the decision.

| Skill | Brief | Use case | Output · IREB anchor | Priority |
| --- | --- | --- | --- | --- |
| `conflict-detector` (model) | Scans a requirement set for contradictions, overlaps, inconsistent conditions and differing levels of detail, and for stakeholders who disagree on priority. Classifies each conflict (subject matter, data, interest, value, relationship, structural) and recommends a resolution technique; relationship and structural conflicts are routed to escalation rather than to the requirements engineer. | R-022 `retain transaction logs 7 years` vs R-035 `delete PII within 30 days`: subject-matter conflict between regulation and privacy; recommends `variants` (pseudonymise before retention) with legal and the DPO in the room. | `conflicts.md` with type and recommended technique · §4.3.1–4.3.2 conflict identification and types | P1 |
| `conflict-to-decision` (user) | Runs a resolution session with the chosen technique (agreement, compromise, voting, variants, overruling; consider-all-facts, plus-minus-interesting or a decision matrix for the analysis) and writes a Requirements Decision Record: assumptions, alternatives considered, constraints, chosen resolution with reasons, decision-makers. ADR-compatible so it can live next to architecture decisions. | Notification channel: SMS vs push vs both. Decision matrix with agreed weights; RDR-007 records `both, SMS as fallback`, links R-050..R-053 as updated. | `decisions/RDR-nnn.md` · §4.3.3–4.3.4 resolution techniques and documentation of decisions | P1 |

## Stage 5 — Validation and quality

Validation is the stage with the best cost ratio for engineering teams: a finding here costs minutes, the same finding in production costs a release. The split follows the handbook: detect first, correct later; check single requirements and the set with different criteria.

| Skill | Brief | Use case | Output · IREB anchor | Priority |
| --- | --- | --- | --- | --- |
| `requirements-review` (user) | Reviews a set against the handbook criteria for single requirements (adequate, necessary, unambiguous, complete, understandable, verifiable) and for the set (consistent, non-redundant, complete, modifiable, traceable, conformant). Perspective-based reading with three subagents (user, architect, tester). Findings list with severity and a proposed fix; detection and correction stay separate steps. | PR adding 30 requirements: 11 findings, among them 4 ambiguous, 2 unverifiable, 1 redundant pair, 1 missing error case. The author fixes in a second pass; the review is re-run on the diff. | `review-<date>.md` findings · §3.8 quality criteria, §4.4 validation techniques | P0 |
| `requirement-linter` (model, script) | Deterministic checks on the requirements CSV and Markdown files: weak words (quickly, user-friendly, appropriate), universal quantifiers (all, always, never), passive voice without an actor, nominalisations, incomplete conditions, missing obligation verb, duplicate IDs, missing attributes. Exit code for CI; the model only explains and suggests rewrites. | CI fails the PR: R-018 `all users` (universal quantifier), R-021 `is validated` (passive, who validates?). Both fixed by `requirement-phrasing`. | Lint report + CI status · §3.2.1 natural-language pitfalls | P0 |
| `testability-check` (model) | For each requirement: verification method (test, inspection, analysis, demonstration), a measurable acceptance criterion and a first test idea. Flags unverifiable requirements and hands the set to `testing-strategy`. | `The UI shall be intuitive` is unverifiable; proposes `a first-time user completes task X in under 3 minutes, 8 of 10 participants` as the measurable form. | `verification.csv` · verifiable criterion in §3.8, acceptance criteria in §3.3.1.2 | P0 |
| `prototype-brief` (user) | Defines a throwaway or evolutionary prototype to validate named requirements: hypotheses, fidelity (paper, mock-up, native), what to measure, stop criteria, how results flow back as validated or changed requirements. | Clickable mock-up to validate five onboarding requirements with six users; three validated, two changed, one dropped. | `prototype-brief.md` · §3.7 prototypes, §4.4 validation by prototyping | P2 |

## Stage 6 — Requirements management

Management is what makes requirements survive contact with change. For engineering teams the two with the highest payoff are traceability (do we have a test for every requirement?) and change impact (what does this request touch?), because both are mechanical once IDs exist and both are usually skipped.

| Skill | Brief | Use case | Output · IREB anchor | Priority |
| --- | --- | --- | --- | --- |
| `traceability-matrix` (model) | Builds and refreshes the trace matrix: source → requirement → decision/ADR → code (paths, PRs) → tests. Reads requirement IDs from commit messages, test names and doc links. Reports coverage gaps: requirements without tests, tests without requirements, orphan code. Outputs CSV and a Mermaid graph. | Nightly job on a service repo: 86 requirements, 71 with tests, 9 without, 6 tests referencing retired IDs. The gaps open as issues. | `trace.csv` + graph + gap report · §6.6 traceability (backward, forward, between requirements) | P0 |
| `change-impact` (user) | Takes a change request and follows the trace links to the impacted requirements, work products, tests and components. Estimates effort and risk, drafts the change request for a Change Control Board or a backlog item for the PO, and records the decision. | `Raise transfer limit to SGD 200k` touches R-012, R-044, three tests, the limits config and one AML rule; CR-014 is drafted with two options and a recommendation. | `changes/CR-nnn.md` · §6.7 handling change, change authority by process type | P0 |
| `prioritization` (user) | Walks the six handbook steps (goals and constraints, criteria, stakeholders, items, technique, run). Ad hoc techniques (MoSCoW, Top-10, Kano) or analytical (weighted benefit, penalty, cost, risk as in Wiegers; WSJF). Produces the matrix, warns about pseudo-accuracy and treats stakeholder disagreement on priority as a conflict for Stage 4. | 28 backlog items. Weights agreed first (benefit 2, penalty 1, cost 1, risk 0.5), matrix computed, ranked list; three items flagged `tie, do not over-interpret`. | `priorities.xlsx` / CSV · §6.8 prioritisation | P1 |
| `attribute-schema` (model) | Defines and validates requirement attributes (ID, title, type, status, priority, source, owner, version, stability, risk, rationale) and the lifecycle states. Generates selective, projective and aggregating views for each audience. | Generates `schema.json` and three saved views: PO (all stories, status, priority), architect (quality requirements and constraints, status agreed), QA (requirements without a verification method). | `schema.json` + views · §6.3–6.5 lifecycle, attributes, views | P2 |
| `baseline` (user) | Cuts a named baseline (git tag plus manifest of requirement IDs and versions), diffs two baselines, and writes requirement release notes. | `v1.0-contract` vs `v1.1`: 4 added, 2 changed, 1 withdrawn, each with its decision record. | `baselines/<name>.json` + diff · §6.3–6.4 versions, configurations, baselines | P2 |

## Stage 7 — Tooling and integration

The catalogue does not replace a requirements tool; it feeds the ones teams already run. Three bridges cover the spec-driven toolkits, the issue trackers and the ReqIF world of DOORS, Polarion and Jama.

| Skill | Brief | Use case | Output · IREB anchor | Priority |
| --- | --- | --- | --- | --- |
| `to-openspec` (user) | Converts RE work products into an OpenSpec change proposal (or a spec-kit `spec.md`): requirements become `SHALL` statements with `WHEN/THEN` scenarios, quality requirements and constraints land in the proposal's constraints section, and requirement IDs are kept as anchors so the trace survives the hand-off to coding agents. | A reviewed set of 14 requirements for `bulk-payments` becomes `openspec/changes/bulk-payments/` with proposal, spec deltas and tasks; each task cites its R-IDs. | OpenSpec change folder / spec-kit spec · §7.1 tool categories (RE process, documentation) | P1 |
| `issue-sync` (user) | Two-way sync between the requirements files and Jira, Azure DevOps or GitHub Issues: creates or updates issues with the requirement ID in the title, maps status both ways, and keeps the trace links in the issue body. | 22 stories pushed to Jira as `R-0xx` issues; a week later the status column of `requirements.csv` is refreshed from the board. | Issues + refreshed status · §7.1 management and collaboration tools | P1 |
| `reqif-bridge` (user) | Imports and exports ReqIF via the `strictdoc-project/reqif` library, so a set written here can be handed to a customer's DOORS or Polarion instance and their edits merged back. | A GovTech tender: requirements exported as ReqIF for the vendor's Polarion; the vendor's annotated ReqIF is re-imported and diffed. | `.reqif` + import diff · §7 tool interoperability | P2 |

Shared primitives (not user-facing): `re-interview` (the questioning primitive), `re-ids` (ID allocation and attribute validation used by every emitting skill), `re-templates` (the asset library: CSV schemas, Markdown templates, Mermaid snippets).

## What matters most to engineering teams, and the roadmap

Eight skills carry most of the value for a delivery team: they run where the team already works (before an agent implements, in a PR, in CI, in a change request) and they catch the defects that otherwise reach production. These eight plus four enablers are the MVP.

| Skill | Why an engineering team pulls it | Where it runs |
| --- | --- | --- |
| `clarifying-questions` | Stops a coding agent (or a developer) from implementing a guess. Cheapest defect prevention in the catalogue. | Model-invoked before implementation; `grill-me` for requirements |
| `requirement-linter` | Deterministic, seconds to run, no judgement calls. Makes requirement quality a CI gate like lint and tests. | CI on `requirements/` changes |
| `requirement-phrasing` | Turns ticket prose into one testable sentence per requirement. The output is what OpenSpec and spec-kit consume. | On ticket intake and in refinement |
| `quality-requirements` | Quality requirements and constraints are the class elicitation under-collects and the one that drives architecture. | Kick-off and before design reviews |
| `requirements-review` | A PR review for requirements, with the tester and architect perspectives the author did not take. | PR review on requirement changes |
| `testability-check` | Every requirement leaves with a verification method and a measurable criterion, so test strategy starts from facts. | After specification, before sprint planning |
| `traceability-matrix` | Coverage gaps and audit evidence from IDs that already exist in commits and tests. Regulated environments ask for exactly this. | Nightly job or release gate |
| `change-impact` | Scopes a change request in minutes by following the trace links instead of memory. | On every change request |

Enablers in the MVP: `glossary` (shared vocabulary every other skill reads), `system-context` (the boundary conversation at kick-off), `artifact-mining` (legacy and migration work), `user-story-refiner` (the format most teams already use). Workshops, questionnaires, observation and document assembly are product-owner and analyst territory and sit in v2.

&#91;embedded content: roadmap · MVP, v1, v2 and the two gates\]

Each gate is evidence of use: the MVP is not done when 12 skills exist but when three teams have run the loop and the validators pass; v1 opens v2 only when the evals are green on two agents and the catalogue is discoverable.

## Repository structure, conventions, licensing

The repo mirrors `mattpocock/skills` (one folder per skill, plugin manifest, changesets) with the stage as the directory and a separate Python package for the deterministic checks.

```markdown
re-skills/
  README.md                  # the 8 stages, install, one end-to-end walkthrough
  AGENTS.md  CLAUDE.md       # how agents use these skills in this repo
  GLOSSARY.md                # IREB terms used across skills (public glossary terms, cited)
  SCOPE.md                   # in / out: no RM tool, no exam prep, no handbook text
  skills/
    foundations/     re-setup  glossary  requirement-classifier
    scope/           system-context  stakeholder-map  source-inventory
    elicitation/     clarifying-questions  interview-guide  artifact-mining
                     elicitation-workshop  questionnaire-builder  observation-protocol
    specification/   requirement-phrasing  user-story-refiner  quality-requirements
                     use-case-spec  domain-model  process-flow  state-model
                     constraints-register  spec-assembler
    negotiation/     conflict-detector  conflict-to-decision
    validation/      requirements-review  requirement-linter  testability-check  prototype-brief
    management/      traceability-matrix  change-impact  prioritization  attribute-schema  baseline
    integration/     to-openspec  issue-sync  reqif-bridge
    _primitives/     re-interview  re-ids  re-templates
  packages/re-lint/          # Python: linter + trace coverage; pip-installable; used by CI and by the skills
  evals/                     # skill-creator eval sets, one per P0 skill
  examples/loyalty-points/   # the sample project every skill is demonstrated on
  docs/                      # stage pages and the hand-off pipeline
  .claude-plugin/plugin.json  .changeset/  CHANGELOG.md  LICENSE (MIT)
```

Conventions

- Format: agentskills.io specification. `name` is kebab-case, at most 64 characters and equal to the folder name; `description` at most 1,024 characters and written as triggers; `SKILL.md` under 500 lines; `skills-ref validate` runs in CI.
- Invocation: user-invoked skills carry `disable-model-invocation: true` and may call model-invoked skills, never another user-invoked skill (the mattpocock rule).
- Spelling in skill names follows the ecosystem (US English): `prioritization`, not `prioritisation`. Prose in this doc keeps British spelling; the repo does not.
- Every emitting skill writes through `re-ids`, so IDs are unique and attributes complete before a file is saved.
- Install: `npx skills@latest add renzrollon/re-skills -a claude-code` (or `-a codex`, `-a copilot`); `claude plugin install re-skills@<marketplace>` once listed. Then `/re-setup` once per repo.

Licensing

- Code and skill text: MIT.
- IREB handbook, syllabus and glossary are copyright IREB: skills cite section numbers and public glossary terms, never paste text, and the README states the project is independent of and not endorsed by IREB.
- Volere templates are licensed: referenced as a structure option in `spec-assembler`, not embedded. EARS is freely usable with attribution to Mavin et al. ISO 29148 and 25010 are cited by clause name only.

## Definition of done and per-skill acceptance criteria

The epic closes when the MVP loop runs end to end on the sample project and on three real teams, with the linter in at least one CI pipeline.

Epic definition of done

- [ ] The 12 P0 skills are merged, each passing `skills-ref validate` and its eval set
- [ ] `packages/re-lint` is published to PyPI with a sample GitHub Actions workflow in the repo
- [ ] `examples/loyalty-points` shows one full loop (scope, elicit, specify, validate, trace) with every output committed
- [ ] Three pilot teams ran the loop on their own repo; their findings are open issues or closed fixes
- [ ] The plugin manifest installs on Claude Code and the skills load on at least one other agent (Codex or Copilot)
- [ ] README states IREB alignment and independence, and the licence position for every referenced standard
- [ ] Submitted to two skills directories (anthropics/skills community list, awesome-claude-skills)

Acceptance criteria for every skill PR

1. Valid frontmatter; the description reads as triggers (when to use, when not to).
2. `references/ireb-anchor.md` names the handbook section, the glossary terms and the quality criteria the skill touches.
3. Inputs and outputs are declared, including which skills produce the inputs and consume the outputs; the output shape is fixed and documented in `assets/`.
4. `examples/` holds one real input and its expected output on the sample project.
5. At least three eval scenarios in `evals/`, including one adversarial input (vague, contradictory, or a design decision in disguise).
6. No handbook text reproduced; no invented numbers in templates.
7. The hand-off to at least one neighbouring skill has been run and the result committed.
8. User-invoked skills carry `disable-model-invocation: true`; model-invoked skills stay under 150 lines.

## Risks, open questions, decisions needed

The two risks that can sink the project are legal (IREB copyright) and speed (a better-funded toolkit adding RE practices). Both are addressed by the same choice: ship validators and bridges, which are hard to copy, and cite rather than copy the standard.

| Risk | Effect | Mitigation |
| --- | --- | --- |
| IREB copyright and trademark | Takedown or reputational damage if handbook text or the IREB mark is used | Cite section numbers and public glossary terms only; `re-skills` name; independence statement; ask IREB in writing whether "aligned with the CPRE syllabus" is acceptable wording |
| Fast-moving field | RE-Skills, BMAD or spec-kit add RE practices and absorb the space | MVP in weeks; differentiate on deterministic validators, hand-off pipeline and OpenSpec / tracker / ReqIF bridges |
| Skill sprawl | 35 skills nobody maintains | Primitives shared, evals per skill, SCOPE.md enforced in review, P2 skills gated on demand |
| Too much ceremony for agile teams | Teams install it and stop using it | `re-setup` tailors depth to the process facets; value-oriented review (adequacy and understandability first); every P0 skill usable in under 10 minutes |
| Model drift | A skill that worked on one model misbehaves on the next | Eval sets run per release; outputs are files so regressions show in diffs |

Decisions needed before the first commit

| Decision | Options | Recommendation |
| --- | --- | --- |
| Repo name | `re-skills` / `ireb-skills` / `cpre-skills` | `re-skills`: no trademark exposure, searchable |
| Requirements storage format | CSV + Markdown / strictdoc `.sdoc` / doorstop YAML | CSV + Markdown in the MVP (diffable, no tooling); strictdoc and doorstop adapters in v1 via `re-templates` |
| First agents supported | Claude Code only / plus Codex and Copilot | Claude Code plus Copilot: Copilot is the enterprise default where the pilot teams work |
| Sample project | Loyalty points / bank transfer limits / public-service booking | Loyalty points: public-safe, has interfaces, rules, states and regulation (data retention) |
| Spelling in skill names | US / UK | US, to match the ecosystem and the agentskills registry |
| Exam-prep skill | Include / exclude | Exclude from the repo; a separate study skill can stay in this project |

Open questions

- Does IREB publish a public list of syllabus educational objectives that can be referenced by ID (EO 3.3.2 etc.) without reproducing the syllabus? The syllabus PDF in this project carries the IDs; confirm reuse terms.
- Which pilot teams: one GovTech, one banking, one product team would cover the three process-facet combinations.
- Does `re-lint` live in this repo or as its own project so non-agent users can adopt it?

## Sources

IREB grounding comes from the files in this project; the landscape was checked on the web on 3 Nov 2026.

- Project files: IREB CPRE Foundation Level Handbook v1.2 (sections 1.2, 1.4, 3.2–3.8, 4.1–4.4, 5.1–5.3, 6.3–6.8, 7.1), Syllabus v3.2, Glossary v2.2, Zühlke CPRE FL course slides and labs
- [mattpocock/skills](https://github.com/mattpocock/skills) · [Agent Skills specification](https://agentskills.io/specification)
- [jdm4pku/RE-Skills](https://github.com/jdm4pku/RE-Skills) · [adbstyle/requirementsengineer-skill](https://github.com/adbstyle/requirementsengineer-skill) · [zeeshanhanif/agentic-sdlc-kit](https://github.com/zeeshanhanif/agentic-sdlc-kit)
- [github/spec-kit](https://github.com/github/spec-kit) · [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) · [obra/superpowers](https://github.com/obra/superpowers) · [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) · [github/awesome-copilot](https://github.com/github/awesome-copilot) · [Kiro specs](https://kiro.dev/docs/specs/concepts/)
- [anthropics/skills](https://github.com/anthropics/skills) · [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) · [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
- [strictdoc](https://github.com/strictdoc-project/strictdoc) · [reqif](https://github.com/strictdoc-project/reqif) · [doorstop](https://github.com/doorstop-dev/doorstop) · [sphinx-needs](https://github.com/useblocks/sphinx-needs) · [rmtoo](https://github.com/florath/rmtoo) · [trlc](https://github.com/bmw-software-engineering/trlc) · [lobster](https://github.com/bmw-software-engineering/lobster) · [eclipse-capra](https://github.com/eclipse-capra/capra) · [OpenReqEU](https://github.com/OpenReqEU)
- [EARS](https://alistairmavin.com/ears/) · [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) · [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) · [Volere template](https://www.volere.org/templates/volere-requirements-specification-template/) · [Example Mapping](https://cucumber.io/docs/bdd/example-mapping/) · [C4 system context](https://c4model.com/diagrams/system-context) · [IREB CPRE Foundation Level](https://cpre.ireb.org/en/concept/foundationlevel)
- LLM-for-RE prior art: [ReqBrain](https://arxiv.org/abs/2505.17632) · [Datasets for LLM-based RE, mapping study](https://arxiv.org/abs/2510.18787) · [jonverrier/RequirementLinter](https://github.com/jonverrier/RequirementLinter)
