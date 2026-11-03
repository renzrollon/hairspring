# Baseline manifest, diff classes and release notes

`re-lint baseline` (vendored: `scripts/baseline.py`) has three commands:

```text
re-lint baseline create NAME [--message TEXT] [--tag]   # writes <workspace>/baselines/NAME.json; --tag adds git tag req-NAME
re-lint baseline diff OLD NEW [--format md|json]        # OLD/NEW: baseline names or manifest files; NEW may be "working"
re-lint baseline notes OLD NEW                          # requirement release notes in Markdown, on stdout
```

## Names

- Use lowercase letters, digits, `.`, `-` and `_`, starting with a letter or digit (`v1.0-contract`, `2026-q1-release`).
- A name is used once. If `baselines/<name>.json` exists, choose another name. A corrected baseline is a new baseline (`v1.0.1-contract`), never an overwrite.
- The git tag, when asked for, is `req-<name>` and is created locally. Pushing it is a separate, explicit step for the user.

## Manifest (`requirements/baselines/<name>.json`)

Template: `assets/baseline.json`.

```json
{
  "name": "v1.0-contract",
  "created": "2026-10-15T08:30:00Z",
  "git_commit": "13a30be2771ab1cfa153a770deb141a64209e037",
  "message": "Requirements agreed for the TillPoint integration contract, signed by Mei Tan (SH-01) 2026-10-15",
  "requirements": [
    {"ID": "R-001", "Version": "1", "Status": "agreed", "Type": "F", "Priority": "must",
     "text_sha256": "de6db66eba5ef61f8f2f8aa486910d6c1c80994d77c1f7bcb2ba6dca455183ce"}
  ]
}
```

| Key | Rule |
| --- | --- |
| `name` | The baseline name |
| `created` | UTC time, ISO 8601 with seconds and `Z` |
| `git_commit` | Full SHA of `HEAD` when the baseline was cut, or `""` outside a git repository |
| `message` | Purpose, who approved it, and the date. Ask for it; do not make it up |
| `requirements` | One entry per requirement row in `requirements.csv` and `stories/*.md`, withdrawn and rejected rows included, sorted by the ID's number |
| `ID`, `Status`, `Type`, `Priority` | The cell values as strings |
| `Version` | The `Version` cell as a string, or `"1"` when the column is missing or the cell is empty |
| `text_sha256` | Lowercase hex SHA-256 of the UTF-8 `Text` cell after trimming leading and trailing whitespace. No other normalization: changing a comma counts as a change |

The file is JSON with 2-space indentation, non-ASCII characters kept as is, and a trailing newline. Once written, it is never edited.

Manual fallback (no Python): compute each hash with `printf '%s' "<text>" | sha256sum`, or `shasum -a 256` on macOS, and fill the template.

## Diff classes

Each ID that differs between OLD and NEW appears in exactly one class. Precedence is top to bottom:

| Class | Rule |
| --- | --- |
| `removed` | The ID is in OLD but not in NEW. The row was deleted, which breaks "never delete a requirement row". Report it as an error |
| `added` | The ID is in NEW but not in OLD |
| `withdrawn` | NEW `Status` is `withdrawn` and OLD `Status` was not |
| `changed` | `text_sha256`, `Type`, `Priority` or `Version` differ. A status change on the same row is shown in the detail |
| `status-changed` | Only `Status` differs |

`working` as NEW means the current register, read the same way as for `create`.

## Release notes (`requirements/baselines/<NEW>-notes.md`)

Template: `assets/release-notes.md`. `notes OLD NEW` prints the notes, and the skill saves them under this name. Notes against `working` are a preview: show them in the message and do not save them.

- **Text shown.** Added and changed rows show the text from the current register. If the current text's hash differs from the NEW manifest's hash, the notes add `(text has changed since <NEW>)`.
- **Decision / CR column.** Every row cites the change request or decision record that allowed the change. Look in this order: the `CR-`/`RDR-` IDs in the row's `Links` cell (the script fills these); then `requirements/changes/CR-*.md` and `requirements/decisions/RDR-*.md` files that name the ID (the skill searches these); otherwise write `none found`. Never invent a link.
- **Uncontrolled changes.** A row is an uncontrolled change when its Decision / CR is `none found`, its OLD status was `agreed`, `implemented` or `verified`, and its class is `changed` or `withdrawn`. Changing an agreed requirement bypassed the change authority. List every such row, and recommend `/change-impact` to document it after the fact.
- **Status changes to `agreed`** do not need a CR. Cite who agreed and when (from `Owner`, `Rationale` or a decision record) in the Note column.
- **Removed rows** are listed with the action "restore the row with Status `withdrawn`".
