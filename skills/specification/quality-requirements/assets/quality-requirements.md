# Quality requirements: {system or part}

| Field | Value |
| --- | --- |
| System | {system under development, or the part walked through} |
| System type | {web API or service \| mobile app \| batch or data pipeline \| embedded \| internal tool; one per part} |
| Quality model | ISO/IEC 25010:2023 product quality model (characteristic and sub-characteristic names only) |
| Walkthrough | {YYYY-MM-DD}, {people and stakeholder IDs}, quality-requirements |
| Sources | {source IDs, interview IDs, people and dates} |
| Schema | requirements/schema.json \| defaults (no schema.json found) |

## Walkthrough

| Characteristic | Tailoring | Decision | Reason | Requirements |
| --- | --- | --- | --- | --- |
| Functional suitability | {core \| check \| rare} | {relevant \| not relevant \| TBD} | {one line with source} | {R-nnn, ... \| covered by ... \| none} |
| Performance efficiency | | | | |
| Compatibility | | | | |
| Interaction capability | | | | |
| Reliability | | | | |
| Security | | | | |
| Maintainability | | | | |
| Flexibility | | | | |
| Safety | | | | |

## Quality requirements

<!-- One "###" subsection per characteristic that has requirements, in walkthrough order. Text lives in requirements.csv; this table holds the measurable parts. Do not name the first column "ID": re-lint reads Markdown tables with an ID column as requirement registers. -->

### {Characteristic}

| Requirement | Sub-characteristic | Metric | Target | Condition | Measurement method | Driver | Open question |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-nnn | {name} | {what, unit, statistic} | {value with source \| TBD} | {load, environment, window; baselines labeled} | {how and when measured} | {yes \| no \| TBD} | {Qn \| none} |

## Architecture drivers

| Requirement | Why it drives the architecture | Decisions it affects | Share with |
| --- | --- | --- | --- |
| R-nnn | {structural choice the target forces, or what it depends on when TBD} | {decision areas} | {role or stakeholder} |

## Unquantified and reclassified concerns

| Concern | Source | Outcome | Routed to |
| --- | --- | --- | --- |
| "{quoted concern}" | {source} | {quality requirement R-nnn \| function \| constraint \| design decision \| not measurable yet} | {skill, person, or Qn} |

## Open questions

| # | Question | Recommended answer | Owner | Affects | Status |
| --- | --- | --- | --- | --- | --- |
| Q1 | {one question} | {a reference to look up or an answer to confirm; never an invented number} | {stakeholder ID and name, or role} | {R-nnn} | {open \| answered \| deferred} |

## Planguage specifications

Not used.
