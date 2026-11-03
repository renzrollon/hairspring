# Process facets: signals and decision rules

`re-setup` reads this file before batch A. The rules below turn four answers (time, purpose, target, criticality) into the configuration written to `requirements/README.md` and `requirements/schema.json`. They are defaults: the user can override any of them in batch B, within the guard rails of step 6.

## 1. Signals per facet

Evidence sets the recommended answer. Quote it with `file:line` in the question. A signal is never an answer.

| Facet | Value | Signals in the repo or in what people say |
| --- | --- | --- |
| Time | `linear` | One specification signed before build; phase gates; "requirements freeze"; a waterfall plan; hardware or a fixed release date with no increments |
| Time | `iterative` | Sprints, iterations, a backlog, refinement meetings, a tracker board, stories, frequent releases |
| Purpose | `prescriptive` | Contract, tender, RFP, SOW, fixed price, outsourced or vendor build, acceptance testing by a customer, certification against the specification |
| Purpose | `explorative` | "We are still figuring out ...", prototypes, experiments, MVP, discovery, goals known but features open |
| Target | `customer-specific` | One named client or internal department orders and accepts the system; a sponsor who signs off; internal tooling |
| Target | `market-oriented` | App store, SaaS, many customers or tenants, personas, product analytics, market research, competitors |
| Criticality | named | A regulation (data protection, financial reporting, payments, health, safety), an audit trail requirement, a contract clause on acceptance evidence, a safety case |

## 2. Common combinations

| Preset | Time | Purpose | Target | Typical case |
| --- | --- | --- | --- | --- |
| participatory | iterative | explorative | customer-specific | An internal service built with its users, such as the loyalty-points service for the Head of Loyalty |
| contract-style | linear | prescriptive | customer-specific | A tender, an outsourced build, a fixed-price contract |
| product-oriented | iterative | explorative | market-oriented | An app or SaaS product sold to a market |

Mixed cases are normal. Take the stricter rule wherever two rules disagree, and write one sentence in the README on why.

| Mix | What to do |
| --- | --- |
| Iterative delivery, prescriptive contract | Keep stories and a backlog; also keep baselines per release and change requests for anything inside the signed scope. Change authority: the change control board for the signed scope, the product owner inside it |
| Market-oriented product with one launch customer | Treat the launch customer as customer-specific for this release; log "when do we switch to market-oriented?" as an open question |
| Explorative discovery inside a linear program | Explorative until the program's requirements gate, then prescriptive; record the gate date as an open question if unknown |

## 3. Work products kept

`yes` = start now. `later` = start when the trigger happens. `no` = skip; re-run `/re-setup` to change. Paths and owners come from `re-templates/references/workspace-layout.md`.

| Work product | Path | Owning skill | Keep |
| --- | --- | --- | --- |
| Workspace README | `requirements/README.md` | `re-setup` | yes |
| Schema | `requirements/schema.json` | `re-setup` | yes |
| Glossary | `requirements/glossary.md` | `glossary` | yes |
| Requirement register | `requirements/requirements.csv` | `requirement-phrasing` | yes |
| System context | `requirements/context.md` | `system-context` | yes |
| Quality requirements | `requirements/quality-requirements.md` | `quality-requirements` | yes |
| Verification | `requirements/verification.csv` | `testability-check` | yes |
| Decision records | `requirements/decisions/` | `conflict-to-decision` | yes (written when a conflict or open decision is settled) |
| Stakeholders | `requirements/stakeholders.md` | `stakeholder-map` | yes; for market-oriented, include user segments with proxy representatives |
| Elicitation records | `requirements/elicitation/` | `clarifying-questions`, `interview-guide`, ... | yes, one file per technique actually used |
| Sources | `requirements/sources.csv` | `source-inventory` | yes if prescriptive or criticality named; else later (trigger: the first requirement cites a document or a system) |
| Constraints | `requirements/constraints.csv` | `constraints-register` | yes if prescriptive or criticality named; else later (trigger: the first constraint is named) |
| Stories | `requirements/stories/` | `user-story-refiner` | yes if iterative; else no |
| Reviews | `requirements/reviews/` | `requirements-review` | yes; prescriptive or linear: before every baseline; iterative: on pull requests that touch `requirements/` |
| Trace matrix | `requirements/trace/` | `traceability-matrix` | yes if prescriptive or criticality named; else later (trigger: tests start citing R-IDs) |
| Baselines | `requirements/baselines/` | `baseline` | yes if linear, prescriptive or criticality named; else later (trigger: someone asks what was agreed at a release) |
| Change requests | `requirements/changes/` | `change-impact` | yes if the change authority is a change control board or baselines are kept; else later |
| Priorities | `requirements/priorities.csv` | `prioritization` | yes if iterative or market-oriented; else later |
| Specification document | `requirements/spec/` | `spec-assembler` | yes if linear or prescriptive; else no |
| Models | `requirements/models/` | `use-case-spec`, `domain-model`, `process-flow`, `state-model` | later (trigger: a flow, structure or state is too complex for sentences) |
| Candidates, classification | `requirements/candidates.csv`, `requirements/classification.md` | `artifact-mining`, `requirement-classifier` | later (working files) |
| Views | `requirements/views/` | `attribute-schema` | later (trigger: an audience asks for its own list) |
| Exports | `requirements/exports/`, `openspec/changes/` | `reqif-bridge`, `to-openspec` | later |

## 4. Change authority

Who may approve a change to a requirement in status `agreed`, `implemented` or `verified`. Apply the first rule that matches.

| Rule | `process.change_authority` | Typical members | How a change is recorded |
| --- | --- | --- | --- |
| linear or prescriptive | `change-control-board` | customer representative or sponsor, product owner, tech lead; add the compliance role when criticality is named | `CR-nnn` through `change-impact`, then a new baseline |
| market-oriented | `product-manager` | the product manager | edit the row, `Version` + 1, `Status` back to `proposed` until agreed; `CR-nnn` only for baselined requirements |
| otherwise | `product-owner` | the product owner, who represents the customer | as for `product-manager` |

Draft and proposed requirements may be edited by their author at any time. Name the people in the README; `TBD` plus an open question when nobody is named yet.

## 5. Depth before implementation

Ask for the detail the next decision needs, not more.

| Facet value | What must be true before building starts |
| --- | --- |
| linear | The whole set is agreed and baselined |
| iterative | Only the items planned for the next iteration meet the DoR; the rest may stay `draft` with `TBD` values |
| prescriptive | Every requirement is verifiable and agreed; `TBD` blocks the baseline (`re-lint check --fail-on info` on the baseline branch) |
| explorative | Goals and the system boundary are clear; requirements may stay `proposed`; prototypes and feedback replace up-front detail |
| customer-specific | Named customer representatives agree requirements |
| market-oriented | No single sign-off; market sources (feedback, analytics, competitors) and Kano categories guide priority |

## 6. Attribute columns to add

Move the attribute from `attributes.optional` to the end of `attributes.columns`. Do not add it to `attributes.required` unless the user asks.

| Condition | Column | Why |
| --- | --- | --- |
| linear or prescriptive | `Version` | Baselines and change requests compare versions |
| prescriptive or criticality named | `Verification` | Acceptance and audit evidence need the method per requirement |
| market-oriented | `Kano` | Prioritization by satisfaction effect |
| change authority has more than one person | `Owner` | Says who to ask about each requirement |

## 7. Definition of Ready

Start from the base items in `assets/definition-of-ready.md` (identical to the default `definition_of_ready` in `schema.json`), then add the items for each chosen facet value and for a named criticality, in the order of that file. The user may reword or drop facet items in B4. Dropping a base item needs a reason recorded in Setup history.

## 8. Other factors worth one sentence in the README

These are not extra questions. Record them only when the user mentions them.

| Factor | Effect |
| --- | --- |
| Stakeholders are hard to reach | Keep `stakeholders.md` with availability; prefer asynchronous techniques (questionnaires, document analysis) |
| Scope changes often | Prefer iterative; keep less detail per requirement; review more often |
| Several teams, vendors or time zones | Write more down: `sources.csv`, an agreed glossary, a specification document |
| Little RE experience in the team | Keep the DoR short; run `re-lint check` in CI so the rules are enforced by a script |
