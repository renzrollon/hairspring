# Views: the `views` section of `schema.json`

A view is a saved query on the requirement register for one audience. It has three parts, which can be combined:

- **Selective**: a row filter (`filter`). Example: only quality requirements and constraints.
- **Projective**: a column subset (`columns`). Example: ID, Text and Status only.
- **Aggregating**: counts per group (`group_by`). Example: how many requirements per Status.

`re-lint views` (vendored: `scripts/views.py`) reads `schema.json` → `views` plus the built-in views, and writes `<workspace>/views/<name>.md` (or `.csv` with `--format csv`).

## Shape

```json
{
  "views": {
    "architect": {
      "title": "Architect: agreed quality requirements and constraints",
      "audience": "SH-05 Lena Koh, SH-08 Wei Jie Chua",
      "filter": { "Type": ["Q", "C"], "Status": ["agreed", "implemented", "verified"] },
      "columns": ["ID", "Type", "Title", "Text", "Source", "Status", "Risk", "Rationale"],
      "group_by": ["Type"],
      "sort": ["Type", "ID"]
    }
  }
}
```

| Key | Part | Type | Default when omitted | Meaning |
| --- | --- | --- | --- | --- |
| `title` | none | string | the view name | Heading of the view file |
| `audience` | none | string | empty | Who reads it (names, SH-IDs) |
| `filter` | selective | object: column → condition | every row | All conditions must hold (AND) |
| `columns` | projective | array of column names | `attributes.columns` | Output columns, in order. `ID` is put first when it is not listed |
| `group_by` | aggregating | array of 1 or 2 column names | no counts section | Count table over the filtered rows |
| `sort` | none | array of column names; a `-` prefix means descending | `["ID"]` | Row order of the detail table |

View names are kebab-case (`po`, `architect`, `finance-retention`). The name is also the file name.

## Filter conditions

| Form | Matches when the cell ... | Example |
| --- | --- | --- |
| `"value"` | equals the value | `"Type": "Q"` |
| `["a", "b"]` | equals one of the values | `"Status": ["agreed", "implemented"]` |
| `{"not": ["a", "b"]}` | equals none of the values (empty cells match) | `"Status": {"not": ["withdrawn", "rejected"]}` |
| `{"empty": true}` | is empty, or the column does not exist | `"Owner": {"empty": true}` |
| `{"empty": false}` | is not empty | `"Links": {"empty": false}` |
| `{"regex": "<pattern>"}` | contains a match (Python `re.search`, case-sensitive) | `"Source": {"regex": "\\bS-05\\b"}` |

Rules:

- Cells are compared after trimming whitespace. Comparison is case-sensitive.
- `TBD` is a value, not an empty cell. To catch "no verification method", empty and `TBD` alike, use `{"not": [<allowed values>]}`.
- A filter on a column the register does not have treats every cell as empty.
- There are no implicit filters. Withdrawn and rejected rows appear unless the view excludes them.

## Columns, counts and order

- **Missing columns.** A listed column that the register lacks is left out of the table and named in the header field "Columns not in the register". That way an optional column that is not in use yet does not produce an empty column.
- **One group-by column.** The counts table has the rows `| <column> | Count |` plus a final `Total` row. Enum columns list every enum value in enum order, including zero counts. Other columns list the values found, in sorted order, with `(empty)` for empty cells.
- **Two group-by columns.** The counts table has one row per combination that occurs, `| <col1> | <col2> | Count |`, sorted by the first column and then the second, plus `Total`.
- **Sorting.** Enum columns sort in enum order (`must`, `should`, `could`, `wont`); other columns sort as text. Ties fall back to `ID`.
- **Rows read.** The script reads every requirement row of `requirements.csv` and `stories/*.md`, the same files `re-lint check` reads.

## Built-in views

These apply when `schema.json` has no view of the same name. A view in `schema.json` with a built-in's name replaces that built-in completely; nothing is merged. Copy the definition from `assets/views.json` and edit it.

| Name | Audience | Filter | Columns | Group by | Sort |
| --- | --- | --- | --- | --- | --- |
| `po` | Product owner | Status not `withdrawn`, `rejected` | ID, Title, Text, Priority, Status, Owner | Status | Priority, ID |
| `architect` | Architects | Type `Q` or `C`; Status `agreed`, `implemented`, `verified` | ID, Type, Title, Text, Source, Status, Risk, Rationale | Type | Type, ID |
| `qa` | Testers | Status not `withdrawn`, `rejected`; Verification not one of `test`, `inspection`, `analysis`, `demonstration` | ID, Type, Text, Status, Priority, Verification | Type | Priority, ID |

## Output

- `--format md` (default): `<workspace>/views/<name>.md` in the shape of `assets/view.md`. It has a header table (audience, definition, the filter as text, columns, group-by, source files, generated date), then `## Counts` (only with `group_by`), then `## Requirements` with the detail table.
- `--format csv`: `<workspace>/views/<name>.csv`, holding the projected columns of the filtered rows, sorted, without counts.
- Views are generated files. Change the definition in `schema.json` and regenerate; never edit a view file by hand.
