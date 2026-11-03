# Limitations of the minimal bridge, and when to use the strictdoc `reqif` library

The vendored `scripts/reqif_bridge.py` is stdlib-only so it runs anywhere. That buys portability and costs fidelity: it writes plain strings in one flat specification and reads back only what maps onto the register's columns. Say so to the customer before the first exchange, not after the first failed import.

| Area | What the minimal bridge does | What you lose | What to do |
| --- | --- | --- | --- |
| Rich text (XHTML) | Exports strings only. On import, flattens `ATTRIBUTE-VALUE-XHTML` to plain text and flags `xhtml-flattened` | Bold, lists, tables, images and links in the customer's edits. Tools often keep the main text as XHTML (the Polarion sample in the strictdoc test corpus defines `ReqIF.Text` as XHTML) | Ask the customer to write plain text in the exchanged attributes; open their tool's view of any flagged row before deciding |
| Enumerations | Exports `Type`, `Priority`, `Status` and other enumerated columns as strings. Reads enumeration values back by name | The receiving tool shows free text unless its admin maps the attribute to an enumeration | Send the allowed values (from `schema.json`) in the hand-over note; values outside them come back as `invalid-value` and are never written |
| Specification hierarchy | One `SPECIFICATION`, one flat level of `SPEC-HIERARCHY`. Nesting is ignored on import | Chapters and sections; heading objects (`ReqIF.ChapterName`) the customer adds come back as `new-object` | Reject heading objects in the review; use the strictdoc library or a document export (`spec-assembler`) when structure matters |
| Tool-specific attribute names | Writes the CSV column names. Reads column names plus `ReqIF.ForeignID`, `ReqIF.Name`, `ReqIF.Text` | Other names (for example DOORS Classic's `Object Text` and `Object Heading`, or a project's custom fields) arrive as `unmapped-attribute` | Ask the customer's admin for their import/export mapping; map their attributes to our column names on their side |
| Several object types or specifications | One `SPEC-OBJECT-TYPE`, one `SPECIFICATION` | A customer file with several modules is read as one list of objects | Ask for an export of the one specification you sent |
| Relations | Not exported; ignored on import (the count is reported) | Links between requirements created in the customer's tool | Record the relations they mean in `Links` by hand after review |
| `.reqifz` archives, attachments, OLE objects | Not read or written | Embedded images and files | Unzip the `.reqifz` and import the `.reqif` inside; review attachments separately |
| Identifiers | `IDENTIFIER` = R-ID; matching falls back to the `ID` / `ReqIF.ForeignID` value | Tools that regenerate identifiers and drop the ID attribute make every object `new-object` | Ask the customer to keep the `ID` attribute; check the first round-trip with three objects before sending the full set |
| Timestamps | Writes the export time as `LAST-CHANGE` for everything; does not compare timestamps on import | Which object the customer touched last (values are compared instead) | None needed: value comparison is what the diff reports |
| Validation | Does not validate against the XSD | | Run `reqif validate --use-reqif-schema <file>` |

## When to prefer strictdoc `reqif`

[`strictdoc-project/reqif`](https://github.com/strictdoc-project/reqif) (version 0.1.0 checked, 2026-11-03; Apache-2.0; Python 3.8+; depends on `lxml`, `jinja2` and `xmlschema`, which is why it is not vendored) parses and writes the full ReqIF model. Use it, alone or as a check next to the bridge, when:

- The customer needs XHTML rich text, enumerations, chapters, relations or `.reqifz` archives in the round-trip.
- The file is large (the library reports parsing progress) or comes from a tool that writes unusual but valid ReqIF.
- You need to validate a file: `reqif validate --use-reqif-schema <file>` (exit `0` valid, `1` errors).
- You need to reproduce a problem: `reqif passthrough <in> <out>` shows whether a file survives a parse and write unchanged; `reqif format` pretty-prints it; `reqif anonymize` strips content so the file can be attached to a bug report.

Install it in a virtual environment (`python3 -m venv .venv && .venv/bin/pip install reqif`). Whatever produced or edited the file, merge customer changes into the register only through `import --diff` and a reviewed decision per row.
