# Attributes, enums and the lifecycle in `schema.json`

The defaults are in `assets/schema.json`, a vendored copy of the `re-templates` default; never edit that copy. A repository's `requirements/schema.json` is merged over the defaults key by key. Objects merge; arrays and plain values replace. So to add one optional attribute, write the whole `attributes.optional` array.

## Where things go

| You want | Edit | Note |
| --- | --- | --- |
| A new column that is not always filled (`Component`, `Release`) | `attributes.optional` | Rows may leave it empty |
| A new column every row must fill | `attributes.optional` first; move it to `attributes.required` only on explicit request | Every existing row then fails `missing-attribute` until filled. `TBD` is allowed and reported as `open-tbd` |
| A closed set of values for a column | `attributes.enums.<Column>` | `re-lint check` reports `invalid-enum` for other values. `TBD` is always allowed |
| A new lifecycle state | `attributes.enums.Status` **and** `lifecycle.transitions` | Both, in the same change |
| Tracker statuses (To Do, In Progress, Done) | `issues.status_map.<tracker>` | Never as `Status` values. Tracker states describe work, not the requirement's lifecycle |
| Another ID kind | `ids.<kind>` with `prefix` and `digits` | Coordinate with `re-ids` |
| Audience views | `views.<name>` | See `views-format.md` |

`attributes.columns` is the fixed leading column order of `requirements.csv`. Change it only when you are creating a register; on a register that exists, it reorders every row.

## Changes that need a migration first

Never make these changes silently. List the affected rows, propose the migration, and wait for the requirement owner's agreement.

| Change | Why it breaks things | Safe path |
| --- | --- | --- |
| Remove or rename an enum value that rows use | Those rows fail `invalid-enum`; filters and status maps stop matching | Add the new value; migrate the rows (show the diff); remove the old value afterwards |
| Rename or remove a column that rows use | Other skills read it by name (`Verification`, `Links`, `Version`) | Usually do not do it. If you must, add the new column, copy the values, update every view, and then drop the old column |
| Change an ID `prefix` or `digits` after IDs exist | Every trace link, commit message, test name and baseline cites the old IDs | Do not do it. Keep the prefix and put the extra meaning in an attribute (`Component`, `Tags`) |
| Make an attribute required | Every existing row fails until it is filled | Add it as optional first, fill the rows (`TBD` allowed), then make it required |

## Lifecycle checks (run them by hand; there is no script for these)

1. `lifecycle.initial` is a value of `attributes.enums.Status`.
2. Every `Status` value has an entry in `lifecycle.transitions`, and every target in the transitions is a `Status` value.
3. Every state can be reached from `initial`.
4. `withdrawn` has no outgoing transitions. Withdrawn IDs are never reused.
5. Moving a requirement to `agreed` needs a named person (in `Source`, `Owner` or a decision record), and skills never set it on their own (see `re-ids`). Keep that rule when you add states before `agreed`.
6. Every `Status` cell in the register is a valid state. Use `re-lint check` (`invalid-enum`).

To check transitions that actually happened, compare two baselines with the `baseline` skill: its diff lists every status change, and you can match each one against `lifecycle.transitions`.

## Writing `schema.json`

- Keep it valid JSON with 2-space indentation, the existing key order, and a trailing newline.
- Show the change as a diff before writing. In non-interactive mode, write it and list the changed keys.
- After writing, run `re-lint check`. The schema change is done only when the register passes, or when the remaining failures are listed for their owners.
