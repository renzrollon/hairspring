# Prototype options: kind, fidelity, measures, stop criteria

Read at steps 5 to 7. The distinctions follow CPRE FL Handbook 1.2 §3.7 by name; the tables are this catalogue's working rules.

## Kind

| Kind | Built to | Choose when | Commit to |
| --- | --- | --- | --- |
| throwaway | Learn, then discard | The question is "is this the right requirement?" and the answer may well be "no" | Discard it after the round; never ship it; write where it is archived or that it was deleted |
| evolutionary | Become part of the product | The requirements are mostly settled and the open question is about details users must try on the real thing | Production standards from the first line: tests, security review, code review, the team's definition of done |

A throwaway prototype that quietly becomes production code is the most common failure. If the team wants to keep it, that is a decision: record it, and switch the brief to evolutionary with its quality bar.

## Fidelity

| Fidelity | What it is | Good for | Cannot show |
| --- | --- | --- | --- |
| paper | Sketches, printed screens, sticky notes, a walkthrough on a whiteboard | Flow, steps, content, what is missing; earliest and cheapest | Timing, interaction details, real data, device behavior |
| mock-up | Clickable screens with fake data, no real backend | Navigation, wording, layout, whether people find and understand things | Performance, integration, scanning, real error behavior |
| native | Running code on the target platform, possibly with real interfaces | Performance, device and hardware behavior (QR scanning at the till), integration, real data | Nothing in principle; costs the most and tempts the team to keep it |

Pick the lowest fidelity that produces every signal in the hypotheses. If one hypothesis needs a higher fidelity than the rest (scanning a QR code on a real phone at a real till), move it to its own native spike or demonstration instead of raising the fidelity of the whole prototype.

## Measures

| Measure | Use for | Capture | Threshold form (values from the decision-maker) |
| --- | --- | --- | --- |
| Task success without help | Can people do it? | Observer marks yes / no per task and participant | At least TBD of TBD participants |
| Help requests and wrong turns | Where does it break? | Observer tally, with the screen where it happened | At most TBD per task |
| Comprehension | Do people understand a message or rule? | Ask the participant to say it in their own words; mark correct / incorrect | At least TBD of TBD restate it correctly |
| Stated intent | Would people use it? | Closing question: "Would you use this in the next month? Why?" | At least TBD of TBD say yes with a concrete reason |
| Quotes | Why it went the way it did | Verbatim, attributed to participant codes | none (qualitative) |
| Time on task | How long it takes | Timer per task | Only if a threshold was agreed; otherwise record without judging |

Stated intent is weak evidence on its own; pair it with an observed task where you can.

## Stop criteria patterns

| Type | Example |
| --- | --- |
| Time box | "Two weeks from the first session" (from the user) |
| Early stop: enough evidence | "Every hypothesis has met its validated or dropped threshold" |
| Early stop: blocker | "The first TBD sessions fail the same task the same way: stop, fix the flow, restart the count" |
| Escalate | "The prototype is being connected to production systems or data: stop and decide throwaway or evolutionary" |
| Escalate | "Participants raise a safety, privacy or fraud concern: stop the task and inform the owner (for example the security architect or DPO)" |

Never "until users like it".
