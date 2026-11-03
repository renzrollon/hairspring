# Volere-structured option: mapping sheet

<!-- The Volere Requirements Specification Template is licensed (commercial license, free for academic use; https://www.volere.org). re-skills does not include its text or its section list. Use this option only with a section list the user takes from their own licensed copy. Delete these comments in the output. -->

## How to use it

1. Ask the user for the section list of their licensed Volere template (numbers and titles, pasted or as a file path). Without it, stop this option and offer the 29148 SRS outline or the arc42 chapter instead. Never reconstruct the sections from memory.
2. Copy the user's section titles into the output in their order, as `## <number> <title>`. Use only the titles; leave out any guidance text their copy contains unless the user tells you their license allows reproduction.
3. Map each work product to the user's sections with the table below. When no section of their copy matches, put the content in the closest section and record the mapping in the header table's `Mapping notes` row.
4. Keep the re-skills header table, contents list, requirement blocks and appendices exactly as in the other outlines.

## Mapping by concern

| Work product | Put it in the section of the user's template whose title is about ... |
| --- | --- |
| `README.md` purpose, epic goals | the purpose or goals of the project |
| `stakeholders.md` | stakeholders, clients, customers, users |
| Type C rows with `constraints.csv` | constraints imposed on the project or product (one group per Category if the template has no finer split) |
| `glossary.md` | naming conventions, terminology, definitions |
| Facts and assumptions recorded as context; open decisions D-nn | facts and assumptions |
| `context.md` diagram and table | the scope of the work and the scope of the product |
| `models/domain-model.md` | the business data model or data dictionary |
| Type F rows and stories with acceptance criteria | functional requirements |
| Type Q rows | the non-functional section whose title matches the row's ISO/IEC 25010:2023 characteristic in `quality-requirements.md` |
| Open questions, TBD requirements, missing work products | open issues |
| Spikes and ADR candidates reported by other skills | ideas for solutions, or open issues if no such section exists |
| `spec_tool.py summary`, `spec_tool.py trace` | appendices (re-skills additions after the user's last section) |

## Header table rows for this option

| Field | Value |
| --- | --- |
| Structure | Volere-structured, from <organization>'s licensed Volere template copy, edition <edition as given by the user> |
| Mapping notes | <work products placed in a closest-match section, or none> |
