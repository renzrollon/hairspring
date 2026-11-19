# Quality and constraint probes

Stakeholders rarely volunteer quality requirements and constraints; they assume them. Ask on purpose, but only about the characteristics that matter for the role (pick 3 to 5; the role table is in `question-funnel.md`).

The characteristic names below are those of the ISO/IEC 25010:2023 product quality model, cited by name only. Teams on the 2011 edition know *interaction capability* as usability and *flexibility* as portability. The probes are ours.

## Quality probes

| Characteristic | Probe (open) | Quantify follow-up | Loyalty-points example |
| --- | --- | --- | --- |
| Functional suitability | "Which results must be exactly right, and how would you notice a wrong one?" | "How many errors per month would you accept, if any?" | Points per purchase, voucher value |
| Performance efficiency | "Where in your work does waiting hurt?" | "What wait would be too long? At what busy moment?" | Voucher validation at the till during the evening peak |
| Compatibility | "Which other systems or devices must this work with?" | "Which versions? What happens if one of them changes?" | TillPoint v2.1 and v2.2, member phones |
| Interaction capability | "Who uses it, how often, with how much training?" | "How long may a new agent need to learn the task?" | Support agents in their first week |
| Reliability | "What happens to your work when the system is down?" | "During which hours must it work? How long an outage can you bridge?" | Support hours, offline tills |
| Security | "Who must not see or change what?" | "What would be the damage if they did? What must be traceable later?" | Agents seeing card numbers; adjustment audit trail |
| Maintainability | "What changes often in your area?" | "How quickly must a change go live?" | Campaign rules changed by marketing |
| Flexibility | "Where else might this have to run or be used?" | "Which new stores, countries or channels are planned, and when?" | New store formats, a second country |
| Safety | "Could anything here harm a person or property?" | "What must happen when it does?" | Rarely relevant for loyalty points; ask once, record the answer |

### When the answer is vague

| You hear | Ask next | Record |
| --- | --- | --- |
| "Fast", "instant", "quickly" | "What would be too slow? Measured from when to when?" | Their words; target `TBD` unless they give a number |
| "Secure" | "Against whom? What must they not be able to do?" | The threat and the asset, not "secure" |
| "Always available" | "During which hours? What do you do today when it's down?" | Hours and the fallback they use |
| "Easy to use" | "Who struggles today, with which step?" | The user group and the task |
| "Scalable" | "What growth do you expect, by when?" | The expected volume and date, or `TBD` |

## Constraint probes

A constraint restricts the solution because someone outside the team decides it. Ask who decides, why, and until when.

| Category | Probe | Loyalty-points example |
| --- | --- | --- |
| Legal and regulatory | "Which laws, regulations or policies apply to this? Who in the company owns them?" | PDPA; data retention policy DRP-2024 (S-05) |
| Contractual | "Do contracts with vendors, partners or customers fix anything here?" | TillPoint interface spec, vendor release windows |
| Organizational | "Which approvals, roles or processes must stay as they are?" | Maker-checker on large adjustments |
| Technical | "Which platforms, systems or standards are given?" | Company Kubernetes platform |
| Cultural and language | "Which languages, formats or customs must it respect?" | Languages on receipts and in the app |
| Environmental and physical | "Where is it used, on what hardware, with what network?" | Store tills with unreliable network |
| Schedule and budget | "Which dates or budgets are fixed, and by whom?" | A go-live date tied to the year-end sale |

For each constraint, capture: what it is, who mandates it, the document or person to cite, and whether it expires.
