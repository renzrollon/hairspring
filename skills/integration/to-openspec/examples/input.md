# Input: hand off voucher redemption (loyalty-points sample)

Command typed by the tech lead, Wei Jie Chua (SH-08), on 2026-11-03:

> /to-openspec add-voucher-redemption

Workspace: `requirements/requirements.csv` (6 rows, see `input/requirements/requirements.csv`) and the acceptance criteria in `input/requirements/stories/voucher-redemption.md`. No `requirements/schema.json` (defaults apply). The repo has an empty `openspec/` folder and OpenSpec 1.16.0 installed, so the target is OpenSpec.

## Selection (default `--status agreed`)

| ID | Type | Status | Title |
| --- | --- | --- | --- |
| R-040 | F | agreed | Issue voucher on redemption request |
| R-041 | F | agreed | Validate voucher at checkout |
| R-042 | F | agreed | Reject redemption below minimum |
| R-085 | Q | agreed | Voucher validation response time at peak |
| R-100 | C | agreed | Use TillPoint voucher validation interface v2.1 |

R-043 (`draft`, owner of voucher printing is open decision D-02) is not selected.

## Gate result

| ID | Check | Finding | Action |
| --- | --- | --- | --- |
| R-040 | - | clean; scenario from R-040.AC1 | goes across |
| R-041 | G4 | no acceptance criterion; WHEN clause present | goes across with a derived scenario |
| R-042 | - | clean; scenario from R-042.AC1 | goes across |
| R-085 | - | clean (Q: proposal) | goes across |
| R-100 | - | clean (C: proposal) | goes across |

`re-lint check --only-ids R-040,R-041,R-042,R-085,R-100 --fail-on error`: 0 errors.

## Commands

```bash
python3 <skill-dir>/scripts/to_openspec.py add-voucher-redemption --ids R-040,R-041,R-042,R-085,R-100 --target openspec --skip-blocked
openspec validate add-voucher-redemption --strict --no-interactive
```

Capability: no `cap:` tags, so the script uses the change name without `add-`: `voucher-redemption`. In step 6 the user confirmed the `## Why` text, the capability bullet, `## Purpose` and `## Impact`; every other line of the expected files is script output (`--date 2026-11-03` reproduces them).

Expected result: `expected-output/openspec/changes/add-voucher-redemption/`. The same selection with `--target spec-kit` and the name `001-voucher-redemption` gives `expected-output/specs/001-voucher-redemption/spec.md`.
