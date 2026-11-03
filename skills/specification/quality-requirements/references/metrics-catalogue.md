# Metrics catalogue

Metric ideas per sub-characteristic (ISO/IEC 25010:2023 names, US spelling elsewhere). This catalogue gives **what to measure and how**, never a target value: targets come from a named person or a source. Pick a metric, then confirm it with the owner of the concern.

## Performance efficiency

| Sub-characteristic | Metric (scale) | Typical condition | Measurement method (meter) |
| --- | --- | --- | --- |
| time behaviour | Response time of a named operation in ms at a stated percentile (p95, p99); end-to-end latency from event to visible result | Load level, payload size, network (store network, mobile data), time window | Load test with a production-like profile before release; latency percentiles from production monitoring |
| resource utilization | CPU, memory, storage, battery or mobile data used per operation or per hour | Device class, OS version, background or foreground | Profiling on reference devices; resource dashboards |
| capacity | Maximum sustained rate (events per minute, requests per second) or volume (members, transactions) with no loss and the time-behaviour target still met | Duration of the peak, data volume, growth period | Load test ramping to the rate and holding it; intake rate and backlog during real peaks |

## Reliability

| Sub-characteristic | Metric | Typical condition | Measurement method |
| --- | --- | --- | --- |
| faultlessness | Defects or failed operations per period; calculation errors found in reconciliation | Normal operation | Defect tracking; reconciliation reports |
| availability | Share of time or of requests that succeed in a calendar period | Service hours, excluded maintenance windows | Synthetic probes from the users' network; monthly report |
| fault tolerance | Share of operations still completed while a named dependency is down or slow | Which dependency, how long | Fault-injection test (block or slow the dependency) under load |
| recoverability | Recovery time (failure to resumed service); recovery point (data that may be lost) | Kind of failure (instance, data store, site) | Recovery drill with timed restore; reconciliation after the drill |

## Security

| Sub-characteristic | Metric | Typical condition | Measurement method |
| --- | --- | --- | --- |
| confidentiality | Data classes readable by roles or channels that should not read them; interfaces without transport encryption | Data classes, environments, interfaces | Inspection of access rules and configuration; endpoint scans |
| integrity | Unauthorized write or delete paths on protected records | Roles, records, channels | Permission inspection; negative tests per role |
| non-repudiation | Actions that cannot be proven to have happened | Which actions | Inspection of signed or logged evidence |
| accountability | Share of protected actions traceable to one actor | Which actions, retention of the trace | Audit-trail inspection on a sample |
| authenticity | Requests accepted without valid credentials | Callers, endpoints | Automated negative tests in the pipeline; penetration test |
| resistance | Attack scenarios the system withstands; time to detect an attack | Named threats (credential stuffing, voucher forgery) | Penetration test; red-team exercise; detection drill |

## Interaction capability

| Sub-characteristic | Metric | Typical condition | Measurement method |
| --- | --- | --- | --- |
| appropriateness recognizability | Share of first-time users who identify whether the product fits their task | User group, first contact | Usability test with think-aloud |
| learnability | Time or attempts until a new user completes a named task without help | User group, amount of training | Usability test with a stated number of participants and success criterion |
| operability | Steps or time to complete a frequent task | Task, device, experienced users | Task timing in a usability test; analytics |
| user error protection | Share of invalid inputs caught with an explanation before harm | Task, input kinds | Test with error-prone inputs; support ticket analysis |
| user engagement | Return visits, completion rates, satisfaction score | User group, period | Analytics; survey with a named instrument |
| inclusivity | Conformance level against a named accessibility guideline (for example WCAG 2.2) | Screens, assistive technology | Accessibility audit |
| user assistance | Share of tasks completed with the built-in help only | Task, user group | Usability test |
| self-descriptiveness | Share of error responses or screens that state cause and next step | Endpoints or screens | Inspection; API review |

## Maintainability

| Sub-characteristic | Metric | Typical condition | Measurement method |
| --- | --- | --- | --- |
| modularity | Components affected by a typical change | Change kind | Change-impact analysis on recent changes |
| reusability | Parts used by more than one product | Named parts | Inspection |
| analysability | Time to locate the cause of a failure | Failure kinds, available telemetry | Incident review; diagnosis drill |
| modifiability | Effort, lead time or releases needed for a named kind of change | Change kind (a new campaign, a new rule) | Demonstration; lead-time tracking per change |
| testability | Share of rules covered by automated tests; time to run the regression suite | Scope of the suite | Coverage report; pipeline timing |

## Flexibility

| Sub-characteristic | Metric | Typical condition | Measurement method |
| --- | --- | --- | --- |
| adaptability | Platforms, devices or environments supported without code changes | Named OS versions, browsers, regions | Compatibility test matrix |
| scalability | Load handled after adding resources, with the time-behaviour target still met | Growth period, resource added | Scaling test; cost per unit of load |
| installability | Time or steps to install, update or roll back in a target environment | Environment, update channel (store, firmware) | Timed installation; deployment pipeline records |
| replaceability | Effort to replace a named product or component | Product replaced | Migration rehearsal |

## Compatibility, functional suitability, safety

| Sub-characteristic | Metric | Typical condition | Measurement method |
| --- | --- | --- | --- |
| co-existence | Degradation of other products sharing the environment | Shared device, network or host | Test on the shared environment |
| interoperability | Messages accepted and correctly interpreted per partner interface | Interface version, partner system | Contract tests against the partner's examples |
| functional completeness | Specified functions implemented | Release scope | Inspection against `requirements.csv` |
| functional correctness | Wrong results per period or per sample | Data set, rule | Reconciliation; property-based tests |
| functional appropriateness | Steps users need that the function does not support | Task | Usability test; task analysis |
| operational constraint, risk identification, fail safe, hazard warning, safe integration | Hazards identified, mitigated and tested; reaction to a hazardous state | Operating modes, hazard list | Hazard analysis; safety test; independent assessment |

## Writing the condition

A target without a condition cannot be tested. Always state at least one of: the load or volume, the environment (network, device, region), the time window (store trading hours, a calendar month, the year-end sale), and what is excluded (announced maintenance). Values in the condition need a source too; a past measurement is labelled "baseline".
