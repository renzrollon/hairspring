# Question funnel

An interview moves from wide to narrow: open questions let the stakeholder show what matters to them, closed questions then pin down what you need to write a requirement. Starting closed gets you answers to your assumptions and nothing else.

## Blocks

| Block | Purpose | Question patterns | Watch for |
| --- | --- | --- | --- |
| 1 Warm-up | Consent, context, rapport | "Is it all right if I take notes?" "What does a normal day look like for you?" "Where does `<topic>` come into your work?" | Write the consent answer in the header before anything else |
| 2 Open | Goals, pains, stories | "What are you trying to achieve with `<topic>`?" "What goes wrong today?" "Tell me about the last time `<problem>` happened." | Let them talk; capture their words; do not propose solutions |
| 3 Narrow | Scenarios, exceptions, volumes, actors | "Who does that, and who else is involved?" "What happens when `<exception>`?" "How often? How many at most?" "What do you do when the system is down?" | Exceptions and edge cases; absolute words (*all*, *never*): ask for exceptions |
| 3b Closed | Confirm what the register holds | "R-062 says adjustments above 5,000 points need a second approver. Is that still right?" "Which of these three matters most?" | One fact per question; offer "none of these" |
| 4 Quality | Quality requirements | See `quality-and-constraint-probes.md`: 3 to 5 characteristics for the role | Vague words: ask "How would we test that?" and "What number would be too slow / too often?" |
| 5 Constraints | Mandates from outside the team | "Who requires that? What happens if we don't? Until when does it apply?" | Separate a constraint (someone outside decides) from a preference |
| 6 Confirm | Shared understanding | "Let me read back the main points: ... Did I get that right? What did I miss?" | Correct the capture sheet live; mark confirmed points |
| 7 Close | Gaps and follow-ups | "What should I have asked and didn't?" "Who else should I talk to?" "Which documents or reports should I read?" "May I come back with follow-up questions?" | Write names and documents into *Follow-ups* |

## Default time split

A starting point; move time to the blocks that matter for the goals. Always keep blocks 6 and 7.

| Block | Share | 30 min | 45 min | 60 min |
| --- | --- | --- | --- | --- |
| 1 Warm-up | 10% | 3 | 5 | 6 |
| 2 Open | 30% | 9 | 13 | 18 |
| 3 Narrow and closed | 20% | 6 | 9 | 12 |
| 4 Quality | 15% | 5 | 7 | 9 |
| 5 Constraints | 10% | 3 | 4 | 6 |
| 6 Confirm | 10% | 3 | 5 | 6 |
| 7 Close | 5% | 1 | 2 | 3 |

## Topics per role (loyalty-points sample and similar systems)

| Role | Open with | Narrow on | Quality focus | Constraint focus |
| --- | --- | --- | --- | --- |
| Product owner / head of program | Goals, members, success measures | Program rules, campaigns, priorities | Interaction capability, flexibility | Contracts, marketing rules |
| Store or field operations | A shift, the checkout, peaks | Offline cases, cashier steps, training | Performance efficiency, reliability, interaction capability | Store hardware and network, vendor release windows |
| Finance | Month-end, liability, audits | Calculation rules, reconciliations, corrections | Functional suitability (correctness), security (accountability) | Accounting and audit rules, retention |
| Customer support | Typical contacts, lookups, adjustments | Reasons, approvals, escalations | Interaction capability, performance efficiency, security (who sees what) | Data protection, approval policies |
| Security architect | Threats, fraud cases | Authentication, roles, logging | Security, reliability | Security standards, certification scope |
| Data protection officer | Personal data in scope | Purposes, retention, deletion, access requests | Security (confidentiality) | Data protection law, retention policy |
| Platform / operations lead | Running the service, incidents | Deployments, monitoring, capacity | Reliability, maintainability, performance efficiency, flexibility | Platform standards, cost limits |
| End user (member, cashier) | What they do and why | Moments of frustration, workarounds | Interaction capability, performance efficiency | Devices, languages, accessibility needs |
| External partner (vendor) | Their interface and release process | Data formats, errors, change windows | Compatibility, reliability | Contracts, interface versions |

## Question rules

- One question, one topic. Split "how often and how fast" into two.
- Ask for the need, not the solution: not "Should we use push notifications?" but "How do members need to learn that points are about to expire?"
- No leading questions: not "Wouldn't 18 months be better?" but "What expiry period works for you, and why?"
- When the interviewee proposes a solution, ask "What would that let you do?" and capture the need.
- When a number comes up, ask how it is measured and where it comes from.
