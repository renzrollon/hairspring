# Requirements exchange: {title}

To: {customer tool admin} · From: {name, role} · Date: {YYYY-MM-DD}

**File:** `<file name>.reqif`: ReqIF 1.2, UTF-8, {n} requirements in one specification ("{title}"), one object type "Requirement", every attribute a plain string.

**Attributes** (please map them in your import):

| Attribute in the file | Meaning | Suggested target in your tool | Allowed values |
| --- | --- | --- | --- |
| ID | our requirement ID, also the object IDENTIFIER | ReqIF.ForeignID | do not change |
| Title | short name | ReqIF.Name | free text |
| Text | the requirement statement | ReqIF.Text | plain text |
| {column} | {meaning} | {target} | {values from schema.json enums, or free text} |

**For a clean round-trip, please:**

1. Keep the IDENTIFIER and the ID attribute of every object unchanged.
2. Do not delete objects. To propose removing one, say so in a comment attribute.
3. Add new requirements as new objects and leave ID empty; we assign the ID.
4. Write plain text: bold, lists, tables and images do not survive our import.
5. Use only the allowed values listed above for enumerated attributes.
6. Send back a `.reqif` export of the same specification, with the attributes you received plus any comment attribute.

Every change you send is reviewed one by one before it enters our register; you will get a list of what was accepted.
