from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys

import pytest

from relint_helpers import SRC, make_row, run_cli
from re_lint import baseline

HEADER = ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale", "Title", "Version", "Links"]


def _register(ws, rows):
    ws.register(rows, header=HEADER)


def _v1_rows():
    return [
        make_row("R-001", Status="agreed", Version="1", Title="Earn points"),
        make_row("R-002", text="The loyalty service shall round points down per transaction.", Status="agreed",
                 Version="1", Title="Round down"),
        make_row("R-003", text="The app shall show the balance.", Status="proposed", Version="1"),
        make_row("R-005", text="The POS shall print vouchers.", Status="draft", Version="1"),
    ]


@pytest.fixture
def repo(workspace, git_available):
    _register(workspace, _v1_rows())
    workspace.git("init", "-q")
    workspace.git("add", "-A")
    workspace.git("commit", "-qm", "requirements v1")
    return workspace


def test_create_writes_the_manifest(repo, capsys):
    result = run_cli(baseline, ["create", "v1.0", "--message", "contract"], capsys)
    assert result.code == 0, result.err
    manifest = json.loads((repo.ws / "baselines" / "v1.0.json").read_text(encoding="utf-8"))
    assert list(manifest) == ["name", "created", "git_commit", "message", "requirements"]
    assert manifest["name"] == "v1.0" and manifest["message"] == "contract"
    assert manifest["git_commit"] == repo.git("rev-parse", "HEAD").strip()
    assert manifest["created"].endswith("Z")
    first = manifest["requirements"][0]
    assert list(first) == baseline.MANIFEST_FIELDS
    expected = hashlib.sha256(" ".join(make_row()["Text"].split()).encode("utf-8")).hexdigest()
    assert first == {"ID": "R-001", "Version": "1", "Status": "agreed", "Type": "F", "Priority": "must",
                     "text_sha256": expected}
    assert [r["ID"] for r in manifest["requirements"]] == ["R-001", "R-002", "R-003", "R-005"]
    assert "warning" not in result.err


def test_text_hash_ignores_whitespace_only_changes():
    assert baseline.text_sha256("The app  shall\nshow it. ") == baseline.text_sha256("The app shall show it.")
    assert baseline.text_sha256("The app shall show it.") != baseline.text_sha256("The app shall hide it.")


def test_create_refuses_to_overwrite_and_validates_names(repo, capsys):
    assert run_cli(baseline, ["create", "v1"], capsys).code == 0
    again = run_cli(baseline, ["create", "v1"], capsys)
    assert again.code == 2 and "immutable" in again.err
    assert run_cli(baseline, ["create", "v1", "--force"], capsys).code == 0
    for bad in ("../x", "v 1", "a..b", "working", "v1.lock", "v1."):
        assert run_cli(baseline, ["create", bad], capsys).code == 2, bad


def test_tag_only_when_asked(repo, capsys):
    run_cli(baseline, ["create", "v1"], capsys)
    assert repo.git("tag", "-l").strip() == ""
    result = run_cli(baseline, ["create", "v2", "--tag"], capsys)
    assert result.code == 0 and "req-v2" in result.out
    assert repo.git("tag", "-l").split() == ["req-v2"]
    assert repo.git("rev-parse", "req-v2^{commit}").strip() == repo.git("rev-parse", "HEAD").strip()
    clash = run_cli(baseline, ["create", "v2", "--force", "--tag"], capsys)
    assert clash.code == 2 and "already exists" in clash.err


def test_dirty_workspace_warns(repo, capsys):
    _register(repo, _v1_rows() + [make_row("R-006")])
    result = run_cli(baseline, ["create", "v1"], capsys)
    assert result.code == 0 and "uncommitted changes" in result.err


def test_tag_needs_git(workspace, capsys):
    _register(workspace, _v1_rows())
    result = run_cli(baseline, ["create", "v1", "--tag"], capsys)
    assert result.code == 2 and "git repository" in result.err
    plain = run_cli(baseline, ["create", "v1"], capsys)
    assert plain.code == 0
    assert json.loads((workspace.ws / "baselines" / "v1.json").read_text())["git_commit"] is None
    notes = run_cli(baseline, ["notes", "v1", "working"], capsys).out
    assert "(no git commit)" not in notes and ", no git commit)" in notes and "no git commi)" not in notes


def test_notes_show_the_short_commit(repo, capsys):
    run_cli(baseline, ["create", "v1"], capsys)
    head = repo.git("rev-parse", "HEAD").strip()
    notes = run_cli(baseline, ["notes", "v1", "working"], capsys).out
    assert f", git {head[:12]})" in notes


def _evolve(ws):
    rows = _v1_rows()
    rows[0]["Text"] = rows[0]["Text"].replace("pending", "posted")
    rows[0]["Version"] = "2"
    rows[0]["Status"] = "proposed"
    rows[1]["Status"] = "withdrawn"
    rows[1]["Rationale"] = "Superseded by RDR-004."
    rows[1]["Links"] = "RDR-004"
    rows[2]["Status"] = "agreed"
    rows = rows[:3]  # R-005 deleted (should have been withdrawn)
    rows.append(make_row("R-004", text="The app shall show expiring points.", Title="Expiry notice",
                         Links="RDR-004 CR-002", Version="1"))
    _register(ws, rows)


def test_diff_classes(repo, capsys):
    run_cli(baseline, ["create", "v1"], capsys)
    _evolve(repo)
    result = run_cli(baseline, ["diff", "v1", "working", "--format", "json"], capsys)
    assert result.code == 0
    diff = result.json()
    classes = {e["ID"]: e["class"] for e in diff["entries"]}
    assert classes == {"R-001": "changed", "R-002": "withdrawn", "R-003": "status-changed", "R-004": "added",
                       "R-005": "removed"}
    assert diff["counts"] == {"added": 1, "changed": 1, "status-changed": 1, "withdrawn": 1, "removed": 1}
    r1 = next(e for e in diff["entries"] if e["ID"] == "R-001")
    assert [c["field"] for c in r1["changes"]] == ["Text", "Version", "Status"]
    md = run_cli(baseline, ["diff", "v1", "working"], capsys).out
    assert md.startswith("# Baseline diff: v1 -> working")
    assert "| R-001 | text; Version 1 -> 2; Status agreed -> proposed |" in md
    assert "## Withdrawn" in md and "## Removed" in md


def test_diff_between_two_baselines_and_paths(repo, capsys):
    run_cli(baseline, ["create", "v1"], capsys)
    _evolve(repo)
    run_cli(baseline, ["create", "v2"], capsys)
    by_name = run_cli(baseline, ["diff", "v1", "v2", "--format", "json"], capsys).json()
    by_path = run_cli(baseline, ["diff", str(repo.ws / "baselines" / "v1.json"), "v2.json", "--format", "json"],
                      capsys).json()
    assert by_name["entries"] == by_path["entries"] and len(by_name["entries"]) == 5
    assert run_cli(baseline, ["diff", "v2", "working", "--format", "json"], capsys).json()["entries"] == []


def test_unknown_or_broken_baseline(repo, capsys):
    run_cli(baseline, ["create", "v1"], capsys)
    missing = run_cli(baseline, ["diff", "v9", "working"], capsys)
    assert missing.code == 2 and "existing baselines: v1" in missing.err
    repo.write("requirements/baselines/bad.json", "{not json")
    assert run_cli(baseline, ["diff", "bad", "working"], capsys).code == 2
    repo.write("requirements/baselines/odd.json", json.dumps({"name": "odd"}))
    assert "not a baseline manifest" in run_cli(baseline, ["diff", "odd", "working"], capsys).err


def test_release_notes(repo, capsys):
    run_cli(baseline, ["create", "v1", "--message", "contract"], capsys)
    _evolve(repo)
    result = run_cli(baseline, ["notes", "v1", "working"], capsys)
    assert result.code == 0
    notes = result.out
    assert notes.startswith("# Requirement release notes: v1 -> working")
    assert "Summary: 1 added, 1 changed, 1 status changed, 1 withdrawn, 1 removed." in notes
    assert "- **R-004** Expiry notice (F, must). Decision: RDR-004, CR-002" in notes
    assert "- **R-002** Round down (F, must): Status agreed -> withdrawn. Rationale: Superseded by RDR-004.." not in notes
    assert "- **R-002** Round down (F, must): Status agreed -> withdrawn. Rationale: Superseded by RDR-004. Decision: RDR-004" in notes
    assert "Rows should be withdrawn, not deleted" in notes
    out_file = repo.root / "notes.md"
    assert run_cli(baseline, ["notes", "v1", "working", "--out", str(out_file)], capsys).code == 0
    assert out_file.read_text(encoding="utf-8") == notes


def test_runs_standalone_next_to_reqio(tmp_path):
    shutil.copy(SRC / "re_lint" / "reqio.py", tmp_path / "reqio.py")
    shutil.copy(SRC / "re_lint" / "baseline.py", tmp_path / "baseline.py")
    proc = subprocess.run([sys.executable, str(tmp_path / "baseline.py"), "--help"], cwd=tmp_path,
                          capture_output=True, text=True)
    assert proc.returncode == 0 and "create" in proc.stdout, proc.stderr
