# Citing requirement IDs in commits, code and tests

The tracer only finds links that someone wrote down. These conventions take seconds per commit or test and make `trace.csv` complete without a spreadsheet. Copy the block at the end of this page into `CONTRIBUTING.md`. Snippets use the re-skills loyalty-points sample project.

## What the tracer recognizes

| Where | Form it finds | Example |
| --- | --- | --- |
| Any scanned file or commit message | The literal ID, word-bounded | `R-041`; `R-041.AC2` links acceptance criterion 2 of R-041 |
| Test function names | `r_041`, `r041` or `R041` inside a name that starts with `test` | `test_r_041_rejects_below_minimum`, `TestR041_RejectsBelowMinimum` |
| Test markers and tags | `R041` (upper case, no underscore), only for registered IDs | `@pytest.mark.R041` |
| Commit messages | The literal ID anywhere in the subject or body | `feat(redeem): reject redemptions below minimum (R-041)` |

It does not recognize `R-41` (the ID has too few digits for the schema), `REQ-041`, `#R041` in a branch name, or ranges such as `R-041..R-045`, which link only the two ends. Write every ID out.

Which files count as code and which as tests comes from `schema.json` → `trace.code_globs` / `trace.test_globs`. A file outside both is not scanned. Add globs there, or pass `--code-glob` / `--test-glob` (these replace the schema globs for that run, so list the existing ones too).

## Commits and pull requests

```text
feat(redeem): reject redemptions below the minimum (R-041)
fix(earn): round down per transaction, not per day (R-002, R-003)

Refs: R-041
```

- Put the ID in the subject in parentheses. When there are several IDs, separate them with commas.
- With squash merges, put the IDs in the PR title. The squash commit takes the title as its subject, and that is what `git log` shows.
- The tracer reads only the commit message. Branch names and PR descriptions are not scanned.
- In CI, check out the full history (`fetch-depth: 0`), or older commits will not be scanned.

## Code annotations

Put one comment next to the code that implements the requirement:

```python
# @req R-041
MIN_REDEMPTION_POINTS = 500
```

```ts
// @req R-041
export const MIN_REDEMPTION_POINTS = 500;
```

Annotate the place a reviewer would look first: the rule, the handler or the config key. Annotating every file that touches the feature is not useful.

## Tests

### Python / pytest

```python
def test_r_041_rejects_redemption_below_minimum():
    """R-041: a redemption of fewer than 500 posted points is rejected."""
```

Optionally add a marker, to run all tests for a requirement with `pytest -m R041`. Register the marker in `pytest.ini` (`markers = R041: tests for R-041`):

```python
@pytest.mark.R041
def test_r_041_rejects_redemption_below_minimum(): ...
```

### JavaScript / TypeScript (jest, vitest)

```ts
describe("R-041 minimum redemption", () => {
  it("R-041 rejects a redemption below the minimum", () => {
    expect(redeem(member, 499)).toEqual({ ok: false, reason: "below minimum" });
  });
});
```

Put the ID in the `it`/`test` title, not only in `describe`, so the link goes to that test. Run one requirement's tests with `npx jest -t "R-041"` or `npx vitest -t "R-041"`.

### Java (JUnit 5)

```java
@Test
@Tag("R-041")
@DisplayName("R-041 rejects a redemption below the minimum")
void rejectsRedemptionBelowMinimum() { ... }
```

`@Tag` lets you run one requirement's tests (`mvn test -Dgroups=R-041`, or Gradle `useJUnitPlatform { includeTags("R-041") }`).

### Go

```go
// TestR041_RejectsBelowMinimum verifies R-041.
func TestR041_RejectsBelowMinimum(t *testing.T) { ... }
```

Run it with `go test ./... -run 'R041'`. For table-driven tests, also put the ID in the case name: `{name: "R-041 below minimum", ...}`.

## Decision records and ADRs

Name the requirement IDs in the record, for example as a line `Requirements: R-041, R-080` under the title. The tracer reads `requirements/decisions/*.md` and the ADR folders (`docs/adr`, `doc/adr`, `adr`, `docs/decisions`).

## Rules that keep the trace honest

- Cite an ID only where the code or test really implements or checks that requirement. The trace is audit evidence, and a citation added just to clear a gap is a false record.
- When a requirement is withdrawn, delete or retarget its tests and annotations in the same PR. The gap report catches the ones that are left behind.
- Never cite IDs in generated or vendored code. Exclude those folders from the globs.

## Block for `CONTRIBUTING.md`

```markdown
### Requirement IDs
- Commits / PR titles: add the requirement ID in parentheses, e.g. `feat(redeem): reject below minimum (R-041)`.
- Code: one `@req R-041` comment at the rule or handler that implements it.
- Tests: the ID in the test name (`test_r_041_...`, `TestR041_...`) or title (`it("R-041 ...")`, `@DisplayName("R-041 ...")`).
- Only cite a requirement your change actually implements or tests. `requirements/trace/trace.md` shows the gaps.
```
