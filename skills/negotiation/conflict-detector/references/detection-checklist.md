# Detection checklist

Use at step 3. Each candidate gets one **kind** (what you observed). The **type** (why it exists) comes later from `conflict-types.md`. Examples are on the loyalty-points sample.

## The five kinds

| Kind | What it looks like | How to scan | Example |
| --- | --- | --- | --- |
| contradiction | Two rows set different values, or opposite obligations, for the same subject and scope | Inside each subject group, compare numbers, units, durations, `shall` vs `shall not`, and the actor who does it | R-060 expires points 12 months after posting; R-061 says 18 months |
| overlap | Two rows describe the same behavior with partly different details, actors or systems, so both could get built differently | Look for the same trigger or the same result in two rows; check whether one already covers the other | R-064 lets support agents adjust points in the "support console"; R-065 governs adjustments in the "admin console" |
| inconsistent conditions | Same trigger or state, different responses; thresholds that overlap or leave a gap; different time bases | Line up every condition on one value (`< 500`, `>= 500`, `more than 500`) and ask what happens exactly at each boundary | R-041 rejects requests below 500 points; R-045 shows the Redeem button only above 500: at exactly 500 a member can redeem but sees no button |
| differing level of detail | One row is a broad statement, another a detailed rule on the same subject; the person behind the broad one may expect something the detailed one forbids | Pair goal-level rows ("shall let agents adjust points") with rule-level rows on the same subject; check that their owners agree | R-064 (any adjustment) vs R-065 (second approver above 5,000 points) |
| priority disagreement | Stakeholders give the same requirement different priorities | Compare priorities by stakeholder in `priorities.csv`, refinement notes, Rationale and Source; one row with two owners is a signal | R-008 manual member-number entry: SH-02 says `must`, SH-05 says `wont` |

## Where contradictions hide

- **Requirement vs constraint.** A requirement that a law, policy, contract or platform rule limits or forbids. Example: R-100 keeps transaction records 7 years; R-101 deletes personal data 30 days after account closure. Transaction records hold the member ID, so both cannot hold as written.
- **Quality vs quality.** Two quality requirements pulling in opposite directions: fraud scoring before posting vs a balance visible within a fixed time; full audit logging vs storage cost.
- **Quality vs function.** A function that makes a quality target unreachable: synchronous fraud check during checkout vs "checkout must not get slower".
- **Two sources, one rule.** The same business rule taken from two documents or two people (`S-01` draft v3 vs an interview): version drift.
- **Terms.** One word in two senses, or two words for one thing ("support console" / "admin console"). Often a data conflict; also raise it to `glossary`.

## Not a conflict (record under "Checked, not a conflict")

| Looks like | Why it is not | What to write |
| --- | --- | --- |
| Two durations near each other (points expire after 12 months; records kept 7 years) | Different subjects (points validity vs record retention) | "Different subjects: points validity vs record retention" |
| Two values for different scopes (Gold tier vs standard) | Both hold at once; scope is explicit | "Different scopes: {scope A} / {scope B}" |
| A refinement that its owner already agreed to | One row details the other with consent | "R-065 refines R-064; confirmed by {owner, date}" |
| A wording defect only | Nobody disagrees; the text is unclear | Recommend `requirement-linter` or `requirement-phrasing` |

## Evidence to capture for each conflict

1. The requirement IDs, with a short excerpt of each text (quote only the clause that collides).
2. The Source of each row (`S-01`, `SH-07 2026-10-29`, `I-02`).
3. The stakeholders and their positions, each with where you read or heard it.
4. One sentence: why both cannot hold for the same scope and time.
