# ReqIF mapping used by `reqif-bridge`

**Checked:** 2026-11-03, against the OMG ReqIF 1.2 schema (namespace `http://www.omg.org/spec/ReqIF/20110401/reqif.xsd`, the XSD bundled with strictdoc `reqif` 0.1.0). Both files in `examples/` pass `reqif validate --use-reqif-schema` with reqif 0.1.0.

**Sources:**

- OMG Requirements Interchange Format 1.2: <https://www.omg.org/spec/ReqIF/1.2>
- strictdoc `reqif` library (parser, validator, bundled XSD, real DOORS and Polarion samples in its test corpus): <https://github.com/strictdoc-project/reqif>
- ProSTEP iViP ReqIF Implementation Guide v1.10 (January 2024), source of the `ReqIF.*` attribute name conventions: <https://www.prostep.org/fileadmin/prod-download/ProSTEP_iViP_ImplementationGuide_ReqIF_V1-10_aw.pdf>

The XML namespace stays `.../20110401/reqif.xsd` and `REQ-IF-VERSION` stays `1.0` in ReqIF 1.0.1, 1.1 and 1.2; that is correct, not an old version.

## Element structure (export)

```text
REQ-IF  xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"  xml:lang="en"
  THE-HEADER
    REQ-IF-HEADER  IDENTIFIER="rs-header-<title-slug>-<YYYYMMDDTHHMMSSZ>"
      COMMENT          (optional)  export note: keep IDENTIFIERs unchanged
      CREATION-TIME    xsd:dateTime, UTC
      REPOSITORY-ID    (optional)  <workspace>/requirements.csv
      REQ-IF-TOOL-ID   re-lint reqif <version>
      REQ-IF-VERSION   1.0 (fixed by the schema)
      SOURCE-TOOL-ID   re-skills
      TITLE            --title
  CORE-CONTENT
    REQ-IF-CONTENT                 children in this order:
      DATATYPES
        DATATYPE-DEFINITION-STRING  IDENTIFIER="rs-dt-string"  LONG-NAME="String"  MAX-LENGTH (required)
      SPEC-TYPES
        SPEC-OBJECT-TYPE  IDENTIFIER="rs-sot-requirement"  LONG-NAME="Requirement"
          SPEC-ATTRIBUTES
            ATTRIBUTE-DEFINITION-STRING  IDENTIFIER="rs-ad-<column, lower case>"  LONG-NAME="<column>"
              TYPE / DATATYPE-DEFINITION-STRING-REF  rs-dt-string
            ... one per exported CSV column, in schema column order
        SPECIFICATION-TYPE  IDENTIFIER="rs-st-specification"  LONG-NAME="Requirements specification"
      SPEC-OBJECTS
        SPEC-OBJECT  IDENTIFIER="<R-ID>"
          VALUES
            ATTRIBUTE-VALUE-STRING  THE-VALUE="<cell>"
              DEFINITION / ATTRIBUTE-DEFINITION-STRING-REF  rs-ad-<column>
            ... one per non-empty cell
          TYPE / SPEC-OBJECT-TYPE-REF  rs-sot-requirement
      SPEC-RELATIONS               (empty)
      SPECIFICATIONS
        SPECIFICATION  IDENTIFIER="rs-spec-<title-slug>"  LONG-NAME="<title>"
          TYPE / SPECIFICATION-TYPE-REF  rs-st-specification
          CHILDREN
            SPEC-HIERARCHY  IDENTIFIER="rs-sh-<R-ID>"
              OBJECT / SPEC-OBJECT-REF  <R-ID>
            ... one per exported row, register order, flat
      SPEC-RELATION-GROUPS         (empty)
```

Every element that has an `IDENTIFIER` also needs `LAST-CHANGE` (`xsd:dateTime`). The bridge writes the export time, in UTC, everywhere.

## Identifier rules

- `IDENTIFIER` is an `xsd:ID`: unique in the file, starting with a letter or `_`, then letters, digits, `-`, `_`, `.`. Default R-IDs (`R-040`) qualify. A custom requirement prefix that starts with a digit does not; the bridge then has to refuse (exit `2`) rather than invent a different identifier.
- The `SPEC-OBJECT` `IDENTIFIER` is the requirement ID, and the `ID` attribute repeats it, because many tools show attribute values but hide identifiers.
- Type, attribute and specification identifiers are fixed (`rs-...`), so two exports of the same set differ only where requirements differ.

## Attribute mapping

| CSV column | `LONG-NAME` written | Usual target in the receiving tool (the customer chooses it in their import mapping) |
| --- | --- | --- |
| `ID` | `ID` | `ReqIF.ForeignID` |
| `Title` | `Title` | `ReqIF.Name` |
| `Text` | `Text` | `ReqIF.Text` (often a rich-text attribute) |
| `Type` | `Type` | an enumeration with `F`, `Q`, `C` |
| `Priority`, `Status`, `Stability`, `Risk`, `Verification`, `Kano` | same name | an enumeration with the schema values |
| `Source`, `Rationale`, `Owner`, `Version`, `Links`, `Tags` | same name | a string attribute |

Values go in the `THE-VALUE` XML attribute, escaped (`&amp;`, `&lt;`, `&gt;`, `&quot;`; line breaks as `&#10;`). Empty cells are left out.

## Import: what the bridge reads

| Item | Rule |
| --- | --- |
| Which object is which requirement | `SPEC-OBJECT` `IDENTIFIER` equal to an R-ID; else the value of an `ID` or `ReqIF.ForeignID` attribute matching the requirement ID pattern; else the object is `new-object` |
| Which attribute is which column | `LONG-NAME` equal to a column name; `ReqIF.ForeignID`, `ReqIF.Name` and `ReqIF.Text` are read as `ID`, `Title` and `Text` |
| String values | read as they are |
| XHTML values | flattened to plain text (tags removed, whitespace collapsed) and flagged `xhtml-flattened` |
| Enumeration values | read as the `LONG-NAME` of the referenced `ENUM-VALUE` |
| Integer, real, boolean, date values | read as the text of `THE-VALUE` |
| An attribute definition absent from the file | the column is left as it is (not cleared) |
| An attribute defined but with no value on one object | the cell is reported as `changed-attribute` (cleared), for review |
| Hierarchy, relations, tool extensions | ignored; the number of `SPEC-RELATION` elements is reported |

## Import diff classes

| Class | Meaning | Written by `--apply` |
| --- | --- | --- |
| `unchanged` | every mapped value equals the register | - |
| `changed-text` | `Text` differs | yes (then the lifecycle rule for agreed rows) |
| `changed-attribute` | another column differs and the new value is valid for the schema | yes |
| `invalid-value` | the new value is outside the schema enums (`Status=Accepted`) | no |
| `new-object` | no R-ID found | yes, as a `draft` row with the next free ID; Source `reqif:<file>#<IDENTIFIER>` |
| `missing-object` | a register row exported earlier is not in the file | no (never deleted) |
| `unmapped-attribute` | an attribute matches no column (`Vendor comment`) | no; shown verbatim |
| `xhtml-flattened` | a value arrived as XHTML; formatting was dropped | flag on the row; the text counts as `changed-text` only if it differs after flattening |

## Structure checklist (without a validator)

- [ ] Root `REQ-IF` with the ReqIF namespace; `THE-HEADER` before `CORE-CONTENT`.
- [ ] Header children in the order `COMMENT`, `CREATION-TIME`, `REPOSITORY-ID`, `REQ-IF-TOOL-ID`, `REQ-IF-VERSION` (`1.0`), `SOURCE-TOOL-ID`, `TITLE`.
- [ ] `REQ-IF-CONTENT` children in the order `DATATYPES`, `SPEC-TYPES`, `SPEC-OBJECTS`, `SPEC-RELATIONS`, `SPECIFICATIONS`, `SPEC-RELATION-GROUPS`.
- [ ] Every `IDENTIFIER` is unique and every element with one has a `LAST-CHANGE` date-time.
- [ ] Every `...-REF` names an existing `IDENTIFIER`.
- [ ] `DATATYPE-DEFINITION-STRING` has `MAX-LENGTH`, and no value is longer.
- [ ] Every `SPEC-OBJECT` has a `TYPE` and is referenced by exactly one `SPEC-HIERARCHY`.
- [ ] The file parses as XML (any XML parser or `python3 -c "import xml.etree.ElementTree as E; E.parse('<file>')"`).
