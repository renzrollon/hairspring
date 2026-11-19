# Pasting stories into a tracker

Each story section in `requirements/stories/<epic-slug>.md` has a paste block between `<!-- paste-start R-nnn -->` and `<!-- paste-end R-nnn -->`. The block uses only bold text and bullet lists so it survives every tracker editor. The INVEST and Definition of Ready tables stay in the stories file; link to it from the issue instead of pasting them.

## Issue title

`<R-ID>: <Title>`, for example `R-040: Spend 500 points as an SGD 5 voucher at the till`. This is the title `issue-sync` uses, so a later sync updates the issue instead of creating a second one.

## Per tracker

| Tracker | How | Notes |
| --- | --- | --- |
| GitHub Issues | Paste the block as is into the issue body | Renders as written. Add the stories file path as a link at the end |
| Jira Cloud | Paste the block into the description | The editor converts Markdown bold and bullets on paste. If your site has Markdown paste switched off, use the Data Center column |
| Jira Data Center / Server (wiki markup) | Convert before pasting: `**text**` becomes `*text*`; `- ` at line start becomes `* `; italics `_(text)_` stay as they are | Or switch the field to the visual editor and paste the rendered text from the Markdown preview |
| Azure DevOps | Paste into the Description (Markdown editor) or the rendered text into the HTML editor | Acceptance criteria may go into the "Acceptance Criteria" field: paste from the first `**R-nnn.AC1` line to the last criterion |

## Keeping the tracker and the files in step

- The files are the source; the tracker is a copy. Edit the stories file, then re-paste or run `/issue-sync`.
- Never renumber criteria in the tracker. A removed criterion stays in the file with the kind `_(withdrawn)_`.
- Keep the R-ID in the title so commits and tests that cite it (`R-040`, `test_r_040_*`) trace back to the story.
