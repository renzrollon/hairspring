# Workshop techniques

The techniques are public, general-purpose methods, described here in our own words: brainstorming (Osborn), brainstorming paradox (also called reverse brainstorming), the 6-3-5 method (brainwriting, Rohrbach), six thinking hats (de Bono), the morphological matrix (Zwicky's morphological analysis) and user story mapping (Patton). Dot voting and affinity clustering are the convergence steps.

## Selection table

| Technique | Use when the goal is | Group | Remote fit | Time box (typical) | Output | Avoid when |
| --- | --- | --- | --- | --- | --- | --- |
| Brainstorming | Many new ideas fast; the group trusts each other | 4 to 10 | good on a shared board | 15 to 25 min | Sticky notes, unclustered | One or two voices dominate; hierarchy is steep |
| Brainstorming paradox | Find dissatisfiers and risks; break a stuck group | 4 to 10 | good | 15 to 20 min | "How to make it fail" list, inverted into needs | The group is already negative about the product |
| 6-3-5 brainwriting | Many ideas with equal voice; quiet or senior-heavy groups; building on others' ideas | exactly 6 per sheet (run several sheets for bigger groups) | very good (one shared sheet per person) | 6 rounds of 5 min, about 30 min | Up to 108 ideas per sheet set, already built on each other | Fewer than 4 people; people unfamiliar with the domain |
| Six thinking hats | Look at one proposal from all sides before deciding to pursue it | 4 to 8 | fair | 5 to 10 min per hat | Facts, feelings, risks, benefits, alternatives, next steps per proposal | You need many new ideas rather than an assessment |
| Morphological matrix | Combine options systematically when the solution has several independent dimensions | 3 to 8 | good on a shared table | 30 to 45 min | Matrix of dimensions by options, plus chosen combinations | The dimensions are not yet known |
| Story mapping | Structure a user journey, find gaps, cut a first release | 3 to 8, including someone who knows the users | good on a shared board | 60 to 120 min | Backbone of activities, steps, stories, release slices | The users' journey is not the question (for example, back-office rules) |

Decision rules:

1. Pick one **diverge** technique for the main goal: new ideas or delighters → brainstorming, or 6-3-5 when voices are unequal or the session is remote; dissatisfiers and risks → brainstorming paradox; a journey or release scope → story mapping; combinations of options → morphological matrix.
2. Add **six thinking hats** only to assess a few shortlisted ideas, never as the first step.
3. Always end with **converge**: cluster, dot vote, Kano-tag the top ideas.
4. Add a second diverge technique only if the agenda still has its full time box; a cut-short technique gives half-formed ideas.
5. If participants cannot attend at the same time, 6-3-5 can run asynchronously over a day with one sheet per person.

## How to run each

### Brainstorming

1. Write the question on the board as "How might we ...?" in the objective's words.
2. Rules read aloud: quantity over quality, no criticism, build on others, one idea per note.
3. Silent writing for a few minutes first, then share round-robin, then open calling.
4. Facilitator writes down ideas exactly as said, including odd ones.

### Brainstorming paradox

1. Ask the inverted question: "How could we make redeeming points as frustrating as possible?"
2. Collect answers as in brainstorming; humor is welcome.
3. Invert each answer into a need: "Voucher only works in the issuing store" becomes "A voucher works in every store".
4. The inverted needs are usually dissatisfiers: their absence causes complaints.

### 6-3-5 brainwriting

1. Six participants, each with a sheet (or a shared document tab) with three columns and six rows.
2. Each round: write three ideas in the first free row in five minutes, then pass the sheet on.
3. Read what is above before writing; build on, vary or combine it.
4. After six rounds, each sheet holds up to 18 ideas. Mark duplicates during clustering, not during writing.

### Six thinking hats

Go through the hats in order for one proposal, everyone wearing the same hat at the same time: white (facts and data we have or need), red (gut feeling, no justification needed), black (risks, why it may fail), yellow (benefits, why it may work), green (alternatives, improvements), blue (process: what did we learn, what next). The facilitator keeps everyone on the same hat.

### Morphological matrix

1. List the independent dimensions of the problem as rows (for redemption: where, what, how much, how proven, when).
2. Fill each row with options as columns.
3. Each participant draws one path through the matrix; compare and discuss paths.
4. Capture each chosen path as one idea, naming its options.

### Story mapping

1. Backbone: the user's activities left to right, in the order they happen.
2. Under each activity: the steps, then the stories (things the user does), most important on top.
3. Walk the map end to end with the group; add missing steps and exceptions.
4. Draw release lines: the thinnest end-to-end slice first.

## Converge

| Step | How | Time box (typical) |
| --- | --- | --- |
| Cluster | Group notes silently by similarity, then name each cluster | 10 min |
| Dot voting | Each participant places a fixed number of dots (say how many before voting) on ideas, not clusters; votes are visible only when everyone has finished | 5 min |
| Kano tagging | For each top idea, ask the two questions below and agree a tag | 1 to 2 min per idea |

## Kano tagging in the room

Ask two questions per idea and tag from the pattern of answers. It is a first guess for `requirement-classifier`, not a survey result.

| "How would members feel if we had it?" | "How would they feel if we did not?" | Tag |
| --- | --- | --- |
| Take it for granted | Complain | `dissatisfier` |
| Pleased, more is better | Disappointed | `satisfier` |
| Delighted, surprised | Would not miss it | `delighter` |
| Don't care | Don't care | `indifferent` |
| No agreement in the room | | `TBD` |

## Remote sessions

- One shared board per technique, prepared before the session, with the question and rules on it.
- Cameras on for the opening and the close; a facilitator and a separate timekeeper.
- Breakout rooms only with a named note-taker per room.
- Export the board (CSV or image) right after the session: it is the source for the capture table.
