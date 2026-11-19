# Baseline manifest, diff classes and release notes

`re-lint baseline` (vendored: `scripts/baseline.py`) has three commands:

```text
re-lint baseline create NAME [--message TEXT] [--tag] [--force]   # writes <workspace>/baselines/NAME.json
re-lint baseline diff OLD NEW [--format md|json]                  # OLD/NEW: baseline names or manifest files; NEW may be "working"
re-lint baseline notes OLD NEW [--out FILE]                       # requirement release notes in Markdown
```

## Names

- Letters, digits, `.`, `-` and `_`, starting with a letter or digit (`v1.0-contract`, `2026-q1-release`).
- A name is used once. `create` refuses an existing name unless `--force` is given. This skill never passes `--force`: a contract, a release or an audit may already refer to that baseline, and a correction is a new baseline (`v1.0.1-contract`).
- `--tag` also creates the lightweight git tag `req-<name>` on `HEAD`, and refuses when that tag exists. Pushing it is a separate, explicit step for the user.

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
| `git_commit` | Full SHA of `HEAD` when the workspace is in a git repository, otherwise `null`. The script warns when the workspace has uncommitted changes |
| `message` | Purpose, who approved it, and the date. Ask for it; do not make it up |
| `requirements` | One entry per requirement row in `requirements.csv` and `stories/*.md` (withdrawn and rejected included; `requirements.csv` wins on a duplicate ID), sorted by ID |
| `ID`, `Version`, `Status`, `Type`, `Priority` | The cell values as strings. `Version` is empty when the register has no `Version` column |
| `text_sha256` | Lowercase hex SHA-256 of the UTF-8 `Text` after whitespace normalization: runs of spaces, tabs and newlines become one space, and leading and trailing whitespace is dropped. A changed comma counts as a change; reflowed whitespace does not |

The file is never edited after it is written.

Manual fallback (no Python): normalize the whitespace of each `Text`, then hash it with `printf '%s' "<text>" | sha256sum` (or `shasum -a 256` on macOS), and fill the template.

## Diff classes

Each ID that differs between OLD and NEW appears in exactly one class. The first match wins:

| Class | Rule |
| --- | --- |
| `added` | The ID is in NEW only |
| `removed` | The ID is in OLD only. The row was deleted, which breaks "never delete a requirement row". Treat it as an error |
| `withdrawn` | `Status` became `withdrawn` |
| `changed` | `text_sha256`, `Version`, `Type` or `Priority` differ. A status change on the same row is listed with it |
| `status-changed` | Only `Status` differs |

`working` as NEW means the current register, read the same way as for `create`.

## Release notes (`requirements/baselines/<NEW>-notes.md`)

Template: `assets/release-notes.md`. The file has two parts.

**Generated part.** `notes OLD NEW --out <file>` writes this part. It has the From/To lines (name, created time, `git` and the first 12 characters of the commit, or `no git commit`, and the message), a summary of the counts, and one bullet section per class that has entries. Each bullet shows the ID, the `Title` (or `Text`) from the current register, Type and Priority, and what changed. `Decision:` lists the `CR-` and `RDR-` IDs in the row's `Links` cell. Withdrawn rows also show their `Rationale`. If a text changed again after NEW, a note at the end says so. Never edit this part by hand; rerun the command instead.

**Review part.** The skill appends this part:

- **Decision links found in changes/ and decisions/.** For every changed, status-changed or withdrawn row without a `Decision:`, search `requirements/changes/CR-*.md` and `requirements/decisions/RDR-*.md` for the ID. Record what you find, or `none found`, and where you looked. Never invent a link. A status change to `agreed` needs no CR: cite who agreed it and when (from `Owner`, `Rationale` or a decision record).
- **Uncontrolled changes.** List every `changed` or `withdrawn` row that has no decision link and was `agreed`, `implemented` or `verified` in OLD. Changing an agreed requirement bypassed the change authority. Recommend `/change-impact` to document each one after the fact.
- **Removed rows.** List them as errors, with the action "restore the row with Status `withdrawn`".

Notes against `working` are a preview: show them in the message, and do not save them.
