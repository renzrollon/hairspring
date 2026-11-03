from __future__ import annotations

import csv
import io
import json
import shutil
import subprocess
import sys

import pytest

from relint_helpers import SRC, make_row, run_cli
from re_lint import cli, tracing

HEADER = ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale", "Title", "Verification", "Links"]


def _rows(path):
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def _edges(ws):
    return {(r["From"], r["To"], r["Relation"]): r for r in _rows(ws.ws / "trace" / "trace.csv")}


@pytest.fixture
def traced(workspace, git_available):
    """A loyalty-points repo with registers, decisions, code, tests and one commit citing IDs."""
    workspace.register([
        make_row("R-001", Status="agreed", Title="Earn points", Verification="test", Links="RDR-001"),
        make_row("R-002", text="The loyalty service shall round points down per transaction.",
                 Status="implemented", Links="R-001"),
        make_row("R-019", text="The loyalty service shall print vouchers.", Status="withdrawn", Source="TBD"),
        make_row("R-041", text="IF a member redeems fewer than 500 points, THEN the loyalty service shall "
                 "reject the redemption.", Status="agreed", Source="SH-01", Links="docs/adr/0001-minimum.md"),
        make_row("R-080", text="The loyalty service shall post points within 2 seconds.", Type="Q",
                 Source="S-19", Verification="inspection"),
    ], header=HEADER)
    workspace.write("requirements/sources.csv", "ID,Source,Kind\nS-01,Programme T&C draft v3,document\n")
    workspace.write("requirements/decisions/RDR-001-earn-rate.md", "# RDR-001 Earn rate\n\nRequirements: R-001, R-002\n")
    workspace.write("docs/adr/0001-minimum.md", "# ADR 1: minimum redemption\n\nApplies to R-041.\n")
    workspace.write("src/loyalty/earn.py", "# @req R-001\nRATE = 1\n# legacy voucher printing R-019\n")
    workspace.write("tests/test_earn.py", (
        "def test_r_001_credits_one_point_per_dollar():\n"
        '    """R-001: credits."""\n'
        "    assert True\n\n"
        "def test_r_999_unknown_requirement():\n"
        "    pass\n\n"
        "@pytest.mark.R041\n"
        "def test_minimum_redemption():\n"
        '    data = "r080"\n'
    ))
    workspace.write("node_modules/pkg/index.js", "// R-001 vendored\n")
    workspace.write("src/loyalty/blob.bin", "R-001")
    (workspace.root / "src" / "loyalty" / "image.dat").write_bytes(b"\x00\x01R-001\x00")
    workspace.write(".gitignore", "node_modules/\n")
    workspace.git("init", "-q")
    workspace.git("add", "-A")
    workspace.git("commit", "-qm", "feat(earn): credit points (R-001, R-002)")
    workspace.git("commit", "-q", "--allow-empty", "-m", "chore: typo R-777")
    return workspace


def test_build_writes_the_three_files_with_expected_links(traced, capsys):
    result = run_cli(tracing, ["build"], capsys)
    assert result.code == 0, result.err
    out = traced.ws / "trace"
    assert {p.name for p in out.iterdir()} == {"trace.csv", "trace.md", "gaps.json"}
    assert out.joinpath("trace.csv").read_text(encoding="utf-8").splitlines()[0] == ",".join(tracing.TRACE_COLUMNS)
    edges = _edges(traced)
    assert edges[("R-001", "S-01", "derives-from")]["Evidence"] == "requirements/requirements.csv:2"
    assert ("R-001", "RDR-001", "decided-by") in edges
    assert edges[("R-002", "RDR-001", "decided-by")]["Evidence"] == "requirements/decisions/RDR-001-earn-rate.md:3"
    assert ("R-041", "docs/adr/0001-minimum.md", "decided-by") in edges
    assert edges[("R-001", "src/loyalty/earn.py", "implemented-by")]["Evidence"] == "src/loyalty/earn.py:1"
    test_edge = edges[("R-001", "tests/test_earn.py::test_r_001_credits_one_point_per_dollar", "verified-by")]
    assert test_edge["FromType"] == "requirement" and test_edge["ToType"] == "test"
    assert ("R-041", "tests/test_earn.py::test_minimum_redemption", "verified-by") in edges  # marker form R041
    assert not any(k[0] == "R-080" and k[2] == "verified-by" for k in edges)  # "r080" is a fixture string
    head = traced.git("log", "--format=%h", "--grep", "credit points").strip()
    assert edges[("R-001", head, "mentioned-in")]["Evidence"] == head
    assert ("R-002", head, "mentioned-in") in edges
    assert not any("node_modules" in k[1] or k[1].endswith((".bin", ".dat")) for k in edges)
    for row in _rows(traced.ws / "trace" / "trace.csv"):
        assert row["FromType"] in tracing.NODE_TYPES and row["ToType"] in tracing.NODE_TYPES
        assert row["Relation"] in tracing.RELATIONS
    assert "trace: 5 requirements" in result.out


def test_build_is_deterministic(traced, capsys):
    run_cli(tracing, ["build"], capsys)
    first = (traced.ws / "trace" / "trace.csv").read_bytes()
    gaps = (traced.ws / "trace" / "gaps.json").read_bytes()
    run_cli(tracing, ["build"], capsys)
    assert (traced.ws / "trace" / "trace.csv").read_bytes() == first
    assert (traced.ws / "trace" / "gaps.json").read_bytes() == gaps
    keys = [(r["From"], r["To"], r["Relation"]) for r in _rows(traced.ws / "trace" / "trace.csv")]
    assert keys == sorted(keys, key=lambda k: (tracing._id_key(k[0]), k[1], k[2]))


def test_gap_kinds_are_status_aware(traced, capsys):
    run_cli(tracing, ["build"], capsys)
    report = json.loads((traced.ws / "trace" / "gaps.json").read_text(encoding="utf-8"))
    found = {(g["kind"], g["id"]) for g in report["gaps"]}
    assert found == {
        ("requirement-without-test", "R-002"),
        ("requirement-without-source", "R-080"),       # cites S-19, not in sources.csv
        ("agreed-without-implementation", "R-041"),
        ("test-cites-unknown-id", "R-999"),
        ("code-cites-retired-id", "R-019"),
    }
    for gap in report["gaps"]:
        assert {"kind", "id", "file", "line", "detail"} <= set(gap)
    retired = next(g for g in report["gaps"] if g["kind"] == "code-cites-retired-id")
    assert (retired["file"], retired["line"]) == ("src/loyalty/earn.py", 3)
    s = report["summary"]
    assert (s["requirements"], s["in_scope"], s["with_test"], s["without_tests"]) == (5, 4, 2, 1)
    assert not any(g["id"] == "R-777" for g in report["gaps"])  # commit history never produces a gap


def test_trace_md_has_summary_graph_and_gap_tables(traced, capsys):
    run_cli(tracing, ["build", "--max-graph-edges", "3"], capsys)
    md = (traced.ws / "trace" / "trace.md").read_text(encoding="utf-8")
    for heading in ("# Trace matrix", "## Coverage summary", "## Graph", "## Gaps", "### Requirements without tests",
                    "### Requirements without a source", "### Tests citing unknown or retired IDs",
                    "### Code citing unknown or retired IDs",
                    "### Agreed or later requirements without an implementation reference", "## Matrix"):
        assert heading in md, heading
    assert "```mermaid\ngraph LR" in md
    assert "Graph truncated: 3 of" in md
    assert '| Requirements in scope (not withdrawn or rejected) | 4 |' in md
    run_cli(tracing, ["build"], capsys)
    md = (traced.ws / "trace" / "trace.md").read_text(encoding="utf-8")
    assert "class R019 retired" in md and "truncated" not in md
    assert 'R001["R-001"]' in md and "commit" not in md.split("```mermaid")[1].split("```")[0]


def test_gaps_command_formats_and_exit_codes(traced, capsys):
    run_cli(tracing, ["build"], capsys)
    assert run_cli(tracing, ["gaps"], capsys).code == 0
    result = run_cli(tracing, ["gaps", "--fail-on-gaps"], capsys)
    assert result.code == 1 and "5 gap(s)" in result.out
    only = run_cli(tracing, ["gaps", "--only", "code-cites-retired-id", "--format", "json", "--fail-on-gaps"], capsys)
    assert only.code == 1 and [g["id"] for g in only.json()["gaps"]] == ["R-019"]
    github = run_cli(tracing, ["gaps", "--format", "github", "--fail-on-gaps"], capsys)
    assert "::error file=src/loyalty/earn.py,line=3,title=code-cites-retired-id::R-019: R-019 is withdrawn" in github.out
    assert run_cli(tracing, ["gaps", "--format", "github"], capsys).out.startswith("::warning ")
    scoped = run_cli(tracing, ["gaps", "--status", "draft", "--only", "requirement-without-source", "--format", "json"], capsys)
    assert [g["id"] for g in scoped.json()["gaps"]] == ["R-080"]
    assert run_cli(tracing, ["gaps", "--only", "bogus"], capsys).code == 2


def test_gaps_and_impact_need_a_trace(workspace, capsys):
    workspace.register([make_row()])
    result = run_cli(tracing, ["gaps"], capsys)
    assert result.code == 2 and "run `re-lint trace build` first" in result.err
    assert run_cli(tracing, ["impact", "R-001"], capsys).code == 2


def test_impact_follows_links_and_shared_artifacts(traced, capsys):
    run_cli(tracing, ["build"], capsys)
    depth1 = run_cli(tracing, ["impact", "R-002", "--depth", "1", "--format", "json"], capsys).json()
    assert [(r["id"], r["hop"]) for r in depth1["requirements"]] == [("R-002", 0), ("R-001", 1)]  # Links column
    assert [d["name"] for d in depth1["decisions"]] == ["RDR-001"]
    assert depth1["code"] == []
    depth2 = run_cli(tracing, ["impact", "R-002", "--format", "json"], capsys).json()
    assert [c["name"] for c in depth2["code"]] == ["src/loyalty/earn.py"]
    assert depth2["code"][0]["via"] == "R-001" and depth2["code"][0]["hop"] == 2
    md = run_cli(tracing, ["impact", "r_041", "--format", "md"], capsys)
    assert md.code == 0 and md.out.startswith("## Impact of R-041") and "`docs/adr/0001-minimum.md`" in md.out
    text = run_cli(tracing, ["impact", "R-041.AC2"], capsys).out
    assert text.startswith("Impact of R-041 (depth 2)")
    assert run_cli(tracing, ["impact", "R-500"], capsys).code == 2
    assert run_cli(tracing, ["impact", "nonsense"], capsys).code == 2


def test_impact_does_not_expand_through_sources(traced, capsys):
    run_cli(tracing, ["build"], capsys)
    result = run_cli(tracing, ["impact", "R-041", "--depth", "3", "--format", "json"], capsys).json()
    assert [r["id"] for r in result["requirements"]] == ["R-041"]  # SH-01 is not shared further


def test_hand_built_trace_with_reverse_source_rows(workspace, capsys):
    workspace.register([make_row("R-041", Status="agreed"), make_row("R-042", Status="agreed")])
    workspace.write("requirements/trace/trace.csv", (
        "From,FromType,To,ToType,Relation,Evidence\n"
        "S-01,source,R-041,requirement,source-of,requirements/requirements.csv:2\n"
        "R-041,requirement,R-042,requirement,linked-to,requirements/requirements.csv:2\n"
        "R-041,requirement,docs/adr/0002-x.md,adr,decided-by,docs/adr/0002-x.md:1\n"
        "R-041,requirement,3f9c2ab,commit,implemented-by,git:3f9c2ab (#212)\n"
    ))
    result = run_cli(tracing, ["impact", "R-041", "--format", "json"], capsys).json()
    assert [s["name"] for s in result["sources"]] == ["S-01"]
    assert [d["name"] for d in result["decisions"]] == ["docs/adr/0002-x.md"]
    assert [r["id"] for r in result["requirements"]] == ["R-041", "R-042"]
    gaps = run_cli(tracing, ["gaps", "--format", "json"], capsys).json()["gaps"]
    assert not any(g["kind"] == "requirement-without-source" for g in gaps)


def test_build_without_git_walks_the_tree_and_skips_virtualenvs(workspace, capsys):
    workspace.register([make_row("R-001", Status="agreed")])
    workspace.write("src/app.py", "# R-001\n")
    workspace.write("tools/env/pyvenv.cfg", "home = /usr\n")
    workspace.write("tools/env/lib/test_x.py", "# R-001\n")
    workspace.write("src/huge.py", "# R-001\n" + "x = 1\n" * 50)
    result = run_cli(tracing, ["build", "--no-git", "--max-bytes", "100", "--format", "json"], capsys)
    assert result.code == 0 and result.json()["scanned"]["commits_scanned"] == 0
    edges = _edges(workspace)
    assert ("R-001", "src/app.py", "implemented-by") in edges
    assert not any("huge" in k[1] or "env" in k[1] for k in edges)


def test_build_options_and_errors(traced, capsys):
    out_dir = traced.root / "out"
    result = run_cli(tracing, ["build", "--out", str(out_dir), "--code-glob", "lib/**", "--test-glob", "tests/**"], capsys)
    assert result.code == 0 and (out_dir / "trace.csv").is_file()
    edges = {(r["From"], r["To"]) for r in _rows(out_dir / "trace.csv")}
    assert ("R-001", "src/loyalty/earn.py") not in edges  # code globs replaced
    assert run_cli(tracing, ["build", "--since", "no-such-rev"], capsys).code == 2
    since = run_cli(tracing, ["build", "--since", "HEAD~1", "--format", "json"], capsys)
    assert since.code == 0 and since.json()["scanned"]["commits_scanned"] == 1


def test_build_with_an_empty_register_is_a_usage_error(workspace, capsys):
    result = run_cli(tracing, ["build"], capsys)
    assert result.code == 2 and "no requirements found" in result.err


@pytest.mark.parametrize("line, expected", [
    ("covers R-012 and R-013.AC2", ["R-012", "R-013.AC2"]),
    ("PR-012, CR-012, R-12, R-0123x", []),
    ("def test_r_012_masks_pii():", ["R-012"]),
    ("def test_r012_ac2_masks():", ["R-012.AC2"]),
    ("func TestR012_MasksPii(t *testing.T) {", ["R-012"]),
    ("void testR012ExportMasks() {", ["R-012"]),
    ("@pytest.mark.R012", ["R-012"]),
    ('value = "r012"', []),           # weak lower-case form outside a test name
    ("@pytest.mark.R099", []),        # weak form, unknown ID
    ("def test_r_0123456_x():", []),  # too many digits
    ("def test_parser_r2():", []),
])
def test_id_matcher_forms(line, expected):
    matcher = tracing.IdMatcher(tracing.reqio.DEFAULT_SCHEMA, known=["R-012"])
    assert matcher.test_refs(line) == expected


def test_test_name_forms_can_be_disabled():
    schema = dict(tracing.reqio.DEFAULT_SCHEMA, trace={"test_name_forms": False})
    matcher = tracing.IdMatcher(schema, known=["R-012"])
    assert matcher.test_refs("def test_r_012_x(): # R-012") == ["R-012"]
    assert matcher.test_refs("def test_r_012_x():") == []


@pytest.mark.parametrize("pattern, path, ok", [
    ("src/**", "src/a/b.py", True),
    ("src/**", "srcx/a.py", False),
    ("**/*_test.*", "pkg/a/b_test.go", True),
    ("**/*_test.*", "b_test.go", True),
    ("*.spec.ts", "web/app/x.spec.ts", True),
    ("tests/", "tests/unit/test_a.py", True),
    ("**/test_*.py", "a/test_b.py", True),
    ("**/test_*.py", "a/b_test.py", False),
])
def test_glob_to_regex(pattern, path, ok):
    assert bool(tracing.glob_to_regex(pattern).match(path)) is ok


@pytest.mark.parametrize("lines, index, name", [
    (["def test_r_001_x():", '    """R-001."""'], 1, "test_r_001_x"),
    (["// TestR041_Rejects verifies R-041.", "func TestR041_Rejects(t *testing.T) {"], 0, "TestR041_Rejects"),
    (['  it("R-041 rejects below minimum", () => {'], 0, "R-041 rejects below minimum"),
    (['@Tag("R-041")', '@DisplayName("R-041 rejects")', "void rejects() {"], 0, "R-041 rejects"),
    (["x = 1  # R-001", "y = compute()", "def test_other():"], 0, None),
])
def test_test_name_heuristics(lines, index, name):
    assert tracing._test_name(lines, index) == name


def test_runs_standalone_next_to_reqio(tmp_path):
    shutil.copy(SRC / "re_lint" / "reqio.py", tmp_path / "reqio.py")
    shutil.copy(SRC / "re_lint" / "tracing.py", tmp_path / "trace_matrix.py")
    proc = subprocess.run([sys.executable, str(tmp_path / "trace_matrix.py"), "--help"],
                          cwd=tmp_path, capture_output=True, text=True)
    assert proc.returncode == 0 and "build" in proc.stdout, proc.stderr


@pytest.mark.parametrize("argv, usage", [
    (["trace", "build", "--help"], "usage: re-lint trace build"),
    (["baseline", "notes", "--help"], "usage: re-lint baseline notes"),
    (["reqif", "import", "--help"], "usage: re-lint reqif import"),
    (["issues", "pull", "--help"], "usage: re-lint issues pull"),
    (["views", "--help"], "usage: re-lint views"),
    (["prioritize", "--help"], "usage: re-lint prioritize"),
    (["openspec", "--help"], "usage: re-lint openspec"),
])
def test_subcommand_usage_follows_the_caller(argv, usage, capsys):
    # cli.py sets parser.prog after build_parser(); nested subcommands must follow it.
    result = run_cli(cli, argv, capsys)
    assert result.code == 0 and result.out.startswith(usage), result.out[:80]
