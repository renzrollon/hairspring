# Views: the `views` section of `schema.json`

A view is a saved query on the requirement register for one audience. It has three parts, which can be combined:

- **Selective**: a row filter (`filter`). Example: only quality requirements and constraints.
- **Projective**: a column subset (`columns`). Example: ID, Text and Status only.
- **Aggregating**: counts per group (`group_by`). Example: how many requirements per Status.

`re-lint views` (vendored: `scripts/views.py`) reads the built-in views plus `schema.json` → `views`, and writes `<workspace>/views/<name>.md` (or `.csv` with `--format csv`).

```text
re-lint views [--view NAME ...] [--out DIR] [--format md|csv] [--stdout] [--list]
```

With no `--view`, every view is written. `--view po architect` and `--view po --view architect` both work. `--list` shows the available views; `--stdout` prints them instead of writing files.

## Shape

```json
{
  "views": {
    "finance-sources": {
      "title": "Finance: requirements from the programme terms and the retention policy",
      "description": "For SH-03 Grace Lim",
      "filter": { "Source": { "has": ["S-01", "S-05"] }, "Status": { "not": ["withdrawn", "rejected"] } },
      "columns": ["ID", "Type", "Title|Text", "Source", "Status", "Priority"],
      "group_by": "Status",
      "sort_by": "Status"
    }
  }
}
```

| Key | Part | Type | Default when omitted | Meaning |
| --- | --- | --- | --- | --- |
| `title` | none | string | `View: <name>` | Heading of the view file |
| `description` | none | string | none | Free text for readers of `schema.json`, such as the audience. It is not rendered |
| `filter` | selective | object: column → condition | every row | All conditions must hold (AND) |
| `columns` | projective | non-empty array of column specs | every column of the register | Output columns, in order. `A|B` shows `A`, or `B` when `A` is empty; the header is `A` |
| `group_by` | aggregating | a column name, or an array of names | no counts section | Count table over the filtered rows, one row per value or per combination |
| `sort_by` | none | one column name | requirement ID order | Row order of the detail table |

Any other key, a wrong type, or a name that is not letters, digits, `-` and `_` makes the script exit with `2` and an exact message. View names become file names; use kebab-case (`po`, `architect`, `finance-sources`).

## Filter conditions

| Form | Matches when the cell ... | Example |
| --- | --- | --- |
| `"value"` or `["a", "b"]` | equals one of the values, ignoring case. `""` in the list matches an empty cell | `"Type": ["Q", "C"]` |
| `{"not": ["a", "b"]}` | equals none of the values (an empty cell matches) | `"Status": {"not": ["withdrawn", "rejected"]}` |
| `{"empty": true}` | is empty, `TBD` or `TBC`, or the column does not exist | `"Verification": {"empty": true}` |
| `{"empty": false}` | holds a real value | `"Owner": {"empty": false}` |
| `{"contains": "text"}` | contains the text, ignoring case | `"Text": {"contains": "voucher"}` |
| `{"has": "tag"}` or `{"has": ["a", "b"]}` | holds at least one of the tokens; the cell is split on spaces, commas and semicolons | `"Source": {"has": ["S-01", "S-05"]}` |

Rules:

- Conditions on different columns are combined with AND. To get an OR within one column, use a value list or `has` with a list.
- `has` is the right test for cells that hold several IDs or tags (`Source` = `SH-07, S-01`, `Links`, `Tags`). `contains` matches substrings, so `S-01` also matches `S-010`.
- `TBD` counts as empty for `{"empty": ...}`, so "no verification method yet" catches both empty cells and `TBD`.
- A column the register does not have reads as empty everywhere. The script warns on stderr when a view names a column that is in neither the register nor the schema, which is how you catch typos.

## Counts, columns and order

- **Counts** (`group_by`): a table `| <column(s)> | Count |`, one row per value or combination that occurs. Rows are sorted by count, highest first, then by value. Empty cells count as `(empty)`. Values with a count of zero are not listed.
- **Columns**: a listed column that the register does not have shows as an empty column (with the warning above).
- **Sorting**: an enum column (`Priority`, `Status`, `Type`, `Risk`, or any column in `attributes.enums`) sorts in schema order (`must`, `should`, `could`, `wont`). Other columns sort as text, ignoring case. Rows with equal values stay in ID order.
- **Rows read**: every requirement row of `requirements.csv` and `stories/*.md`. On a duplicate ID, `requirements.csv` wins.

## Built-in views

These are always available. A view in `schema.json` with a built-in's name replaces that built-in completely; nothing is merged. `assets/views.json` holds the three definitions, ready to copy and edit.

| Name | Filter | Columns | Group by |
| --- | --- | --- | --- |
| `po` | Type `F` or empty | ID, Title (or Text), Status, Priority | Status |
| `architect` | Type `Q` or `C`; Status `agreed` or `proposed` | ID, Type, Text, Status, Priority, Rationale | Type |
| `qa` | Verification empty or `TBD`; Status not `withdrawn` or `rejected` | ID, Type, Text, Status, Priority | Type |

## Output

- `--format md` (default) writes `<workspace>/views/<name>.md` in the shape of `assets/view.md`: the title; a line saying the file is generated; the filter as text; the row count; `## Counts` (only with `group_by`); and `## Requirements` with the detail table, or `None.`.
- `--format csv` writes `<workspace>/views/<name>.csv`: the projected columns of the filtered, sorted rows, without counts.
- Views are generated files. Change the definition in `schema.json` and regenerate; never edit a view file by hand.
