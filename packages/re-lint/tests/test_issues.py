from __future__ import annotations

import base64
import csv
import io
import json
import shutil
import subprocess
import sys

import pytest

from relint_helpers import SRC, make_row, run_cli
from re_lint import issues

HEADER = ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale", "Title", "Verification"]


def _row(rid, **attrs):
    return issues.reqio.Row(make_row(rid, **attrs))


class FakeClient(issues.TrackerClient):
    """In-memory GitHub-like tracker: no network, records every write."""

    name = "github"
    body = issues.MarkdownBody()

    def __init__(self, existing=()):
        self.issues = list(existing)
        self.calls = []

    def find_many(self, ids):
        self.calls.append(("find", list(ids)))
        return {rid: [i for i in self.issues if rid in i.title] for rid in ids}

    def create(self, title, body, labels):
        n = len(self.issues) + 1
        issue = issues.GitHubIssue(str(n), title, body, "open", f"https://github.com/o/r/issues/{n}", list(labels))
        self.issues.append(issue)
        self.calls.append(("create", title))
        return issue

    def update(self, issue, title, body, labels):
        issue.title, issue.body = title, body
        issue.labels = sorted(set(issue.labels) | set(labels))
        self.calls.append(("update", issue.key))
        return issue


def _gh(n, title, body="", state="OPEN", reason=""):
    return issues.GitHubIssue(str(n), title, body, state, f"https://github.com/o/r/issues/{n}", [], reason)


class ExplodingClient(FakeClient):
    def find_many(self, ids):  # pragma: no cover - must never be called
        raise AssertionError("plan must not call the tracker")


def _main(argv, capsys, client=None):
    args = issues.build_parser().parse_args(argv)
    code = issues.run(args, client=client)
    out, err = capsys.readouterr()
    return code, out, err


@pytest.fixture
def ws(workspace):
    workspace.register([
        make_row("R-001", Status="agreed", Title="Earn points", Links="RDR-001"),
        make_row("R-002", text="WHEN a member opens the app, the app shall show the posted balance and the pending "
                 "points with their posting date.", Status="agreed"),
        make_row("R-003", Status="verified", Title="Round down"),
        make_row("R-004", Status="implemented", Title="Expire points"),
        make_row("R-005", Status="agreed", Title="Print vouchers"),
        make_row("R-006", Status="withdrawn", Title="Old idea", Links="github:o/r#6 RDR-002"),
        make_row("R-007", Status="draft", Title="Draft idea"),
        make_row("R-008", Status="proposed", Title="Proposed idea"),
    ], header=HEADER + ["Links"])
    workspace.write("requirements/trace/trace.csv", (
        "From,FromType,To,ToType,Relation,Evidence\n"
        "R-001,requirement,tests/test_earn.py::test_r_001_x,test,verified-by,tests/test_earn.py:1\n"
        "R-001,requirement,src/earn.py,code,implemented-by,src/earn.py:1\n"
        "R-001,requirement,openspec/changes/x/specs/y/spec.md,code,mentioned-in,openspec/changes/x/specs/y/spec.md:3\n"
    ))
    workspace.write("requirements/sources.csv", "ID,Source,Kind\nS-01,Programme T&C draft v3,document\n")
    workspace.write("requirements/stories/earn.md", "| ID | Acceptance criterion |\n| --- | --- |\n"
                    "| R-001.AC1 | Given a purchase of SGD 12, when it posts, then the member earns 12 points. |\n")
    return workspace


def _csv(ws):
    return {r["ID"]: r for r in csv.DictReader(io.StringIO((ws.ws / "requirements.csv").read_text(encoding="utf-8")))}


def test_plan_is_offline_and_lists_every_row(ws, capsys, tmp_path, monkeypatch):
    monkeypatch.setenv("JIRA_PROJECT", "LOY")
    out = tmp_path / "plan.json"
    code, text, _ = _main(["plan", "--tracker", "github", "--out", str(out)], capsys, ExplodingClient())
    assert code == 0
    assert "| R-001 | create-or-match | - | R-001: Earn points | agreed -> open |" in text
    assert "| R-006 | move-on-board | github:o/r#6 | R-006: Old idea | withdrawn -> (manual) |" in text
    assert "close o/r#6 by hand with the reason (RDR-002)" in text
    assert "| R-007 | skip | - | R-007: Draft idea | draft | Status=draft; name it in --ids to push it |" in text
    assert "Nothing has been written. To apply: `push --tracker github --ids R-001,R-002,R-005 --apply`." in text
    plan = json.loads(out.read_text(encoding="utf-8"))
    assert (plan["command"], plan["network"]) == ("plan", False)
    first = plan["actions"][0]
    assert {k: first[k] for k in ("id", "action", "issue", "title", "status", "tracker_status")} == {
        "id": "R-001", "action": "create-or-match", "issue": None, "title": "R-001: Earn points", "status": "agreed",
        "tracker_status": "open"}
    body = first["body"]
    assert body.startswith(issues.BEGIN + "\n**R-001** · F functional · priority must · register status at last push: agreed")
    assert "| Verification | TBD |" in body and "- R-001.AC1: Given a purchase of SGD 12" in body
    assert "- Sources: S-01 (Programme T&C draft v3)" in body and "- Decisions and links: RDR-001" in body
    assert "`tests/test_earn.py::test_r_001_x` (test), `src/earn.py` (code)" in body and "openspec" not in body
    code, text, _ = _main(["plan", "--tracker", "jira", "--ids", "R-007", "--format", "json"], capsys, ExplodingClient())
    data = json.loads(text)
    assert data["target"] == "LOY" and [a["action"] for a in data["actions"] if a["id"] == "R-007"] == ["create-or-match"]
    assert _main(["plan", "--tracker", "github", "--ids", "R-404"], capsys)[0] == 2


def test_title_uses_title_or_first_80_characters():
    assert issues.issue_title(_row("R-001", Title="Earn points")) == "R-001: Earn points"
    long = _row("R-002", text="x" * 50 + " " + "y" * 60)
    assert issues.issue_title(long) == "R-002: " + ("x" * 50 + " " + "y" * 29)


def test_push_dry_run_then_apply_records_links_and_is_idempotent(ws, capsys):
    client = FakeClient()
    code, text, _ = _main(["push", "--tracker", "github"], capsys, client)
    assert code == 0 and "Summary: 3 create" in text and "Nothing has been written" in text
    assert [c for c in client.calls if c[0] != "find"] == []
    code, text, _ = _main(["push", "--tracker", "github", "--apply", "--label", "requirement"], capsys, client)
    assert code == 0 and "3 created" in text
    assert [i.title for i in client.issues][0] == "R-001: Earn points" and client.issues[0].labels == ["requirement"]
    links = {rid: row["Links"] for rid, row in _csv(ws).items()}
    assert links["R-001"] == "RDR-001 github:o/r#1" and links["R-002"] == "github:o/r#2"
    assert "Links now holds github:o/r#1, github:o/r#2, github:o/r#3" in text
    code, text, _ = _main(["push", "--tracker", "github", "--apply", "--label", "requirement"], capsys, client)
    assert code == 0 and "3 unchanged" in text and len(client.issues) == 3


def test_push_replaces_only_the_managed_block(ws, capsys):
    ctx = {"schema": issues.reqio.DEFAULT_SCHEMA, "register": "x", "trace": {}, "acs": {}, "source_titles": {}}
    stale = issues.MarkdownBody().render(issues.block_data(_row("R-001", text="Old text."), ctx))
    human = "Design notes from the team.\n\n" + stale + "\n\nDiscussion: keep this."
    client = FakeClient([_gh(7, "R-001: Earn points", human)])
    code, text, _ = _main(["push", "--tracker", "github", "--ids", "R-001", "--apply"], capsys, client)
    assert code == 0 and "1 updated" in text
    body = client.issues[0].body
    assert body.startswith("Design notes from the team.") and body.endswith("Discussion: keep this.")
    assert body.count(issues.BEGIN) == 1 and "Old text." not in body and make_row()["Text"] in body


@pytest.mark.parametrize("body", ["Written by hand, no block.", issues.BEGIN + "\nx\n" + issues.END + "\n" + issues.BEGIN])
def test_push_leaves_bodies_without_clean_markers_alone(ws, capsys, body):
    client = FakeClient([_gh(7, "R-001: Earn points", body)])
    code, text, _ = _main(["push", "--tracker", "github", "--ids", "R-001", "--apply"], capsys, client)
    assert code == 1 and "| R-001 | markers-missing |" in text
    assert client.issues[0].body == body and not [c for c in client.calls if c[0] == "update"]
    empty = FakeClient([_gh(8, "R-001: Earn points", "")])
    assert _main(["push", "--tracker", "github", "--ids", "R-001", "--apply"], capsys, empty)[0] == 0
    assert issues.BEGIN in empty.issues[0].body


def test_push_reports_ambiguous_missing_and_retired_rows(ws, capsys):
    client = FakeClient([_gh(1, "Follow-up on R-001 and R-002"), _gh(2, "Question about R-001"),
                         _gh(6, "R-006: Old idea")])
    code, text, _ = _main(["push", "--tracker", "github", "--ids", "R-001", "R-006", "--apply", "--format", "json"],
                          capsys, client)
    assert code == 1
    items = {a["id"]: a for a in json.loads(text)["actions"]}
    assert items["R-001"]["action"] == "ambiguous" and "1, 2" in items["R-001"]["reason"]
    assert items["R-006"]["action"] == "move-on-board" and items["R-006"]["issue"] == "github:o/r#6"
    assert not [c for c in client.calls if c[0] in ("create", "update")]
    ws.register([make_row("R-001", Status="agreed", Links="github:o/r#41")], header=HEADER + ["Links"])
    lost = FakeClient()
    code, text, _ = _main(["push", "--tracker", "github", "--apply"], capsys, lost)
    assert code == 1 and "| R-001 | missing-issue | github:o/r#41 |" in text and lost.issues == []
    leading = [issues.Issue("1", "Follow-up on R-001"), issues.Issue("2", "[R-001] Earn")]
    issue, candidates = issues.pick_issue("R-001", leading)
    assert issue.key == "2" and len(candidates) == 2
    assert issues.pick_issue("R-001", [issues.Issue("3", "R-0012: other")])[0] is None


def test_pull_guard_classes(ws, capsys):
    tracker = FakeClient([
        _gh(1, "R-001: Earn points", state="CLOSED", reason="COMPLETED"),   # agreed -> implemented: update
        _gh(2, "R-002: Balance"),                                           # agreed -> agreed: unchanged
        _gh(3, "R-003: Round down", state="CLOSED"),                        # verified -> implemented: coarse map
        _gh(4, "R-004: Expire points"),                                     # implemented -> agreed (reopened): update
        _gh(5, "R-005: Print vouchers", state="CLOSED", reason="NOT_PLANNED"),  # -> rejected: not a transition
        _gh(6, "R-006: Old idea"),                                          # withdrawn + open: conflict-lifecycle
        _gh(7, "R-007: Draft idea", state="CLOSED"),                        # draft -> implemented: conflict
        _gh(8, "R-008: Proposed idea"),                                     # proposed -> agreed: needs a person
    ])
    before = (ws.ws / "requirements.csv").read_bytes()
    code, text, _ = _main(["pull", "--tracker", "github", "--format", "json"], capsys, tracker)
    assert code == 1 and (ws.ws / "requirements.csv").read_bytes() == before
    items = {a["id"]: a for a in json.loads(text)["actions"]}
    assert {rid: a["action"] for rid, a in items.items()} == {
        "R-001": "update", "R-002": "unchanged", "R-003": "skip-coarse-map", "R-004": "update", "R-005": "conflict",
        "R-006": "conflict-lifecycle", "R-007": "conflict", "R-008": "needs-person"}
    assert items["R-005"]["mapped"] == "rejected" and items["R-001"]["issue"] == "github:o/r#1"
    code, text, _ = _main(["pull", "--tracker", "github", "--apply"], capsys, tracker)
    assert "Status changed for R-001, R-004; no other cell changed." in text
    assert {rid: r["Status"] for rid, r in _csv(ws).items()} == {
        "R-001": "implemented", "R-002": "agreed", "R-003": "verified", "R-004": "agreed", "R-005": "agreed",
        "R-006": "withdrawn", "R-007": "draft", "R-008": "proposed"}


def test_pull_verified_needs_evidence(ws, capsys):
    ado = FakeClient([issues.Issue("41", "R-001: Earn points", "", "Closed"), issues.Issue("44", "R-004: Expire", "", "Closed")])
    code, text, _ = _main(["pull", "--tracker", "ado", "--format", "json", "--apply"], capsys, ado)
    items = {a["id"]: a["action"] for a in json.loads(text)["actions"]}
    assert items == {"R-001": "conflict", "R-004": "needs-evidence"}  # agreed -> verified skips implemented
    ws.write("requirements/trace/trace.csv", "From,FromType,To,ToType,Relation,Evidence\n"
             "R-004,requirement,tests/t.py::test_r_004,test,verified-by,tests/t.py:1\n")
    code, text, _ = _main(["pull", "--tracker", "ado", "--ids", "R-004", "--apply"], capsys, ado)
    assert _csv(ws)["R-004"]["Status"] == "verified"


def test_pull_uses_schema_status_map_case_insensitively(ws, capsys):
    ws.schema({"issues": {"status_map": {"github": {"closed:not_planned": "deferred"}, "jira": {"done": "implemented"}}}})
    tracker = FakeClient([_gh(5, "R-005: Print vouchers", state="CLOSED", reason="NOT_PLANNED")])
    code, text, _ = _main(["pull", "--tracker", "github", "--ids", "R-005", "--apply"], capsys, tracker)
    assert code == 0 and _csv(ws)["R-005"]["Status"] == "deferred"
    jira = FakeClient([issues.Issue("LOY-1", "R-001: Earn points", None, "DONE")])
    _main(["pull", "--tracker", "jira", "--ids", "R-001", "--apply"], capsys, jira)
    assert _csv(ws)["R-001"]["Status"] == "implemented"
    review = FakeClient([issues.Issue("LOY-2", "R-002: Balance", None, "In Review")])
    code, text, _ = _main(["pull", "--tracker", "jira", "--ids", "R-002", "--format", "json"], capsys, review)
    assert code == 1 and "'In Review' is not in issues.status_map.jira" in text


# ---------------------------------------------------------------- body formats


def _data():
    ctx = {"schema": issues.reqio.DEFAULT_SCHEMA, "register": "requirements/requirements.csv",
           "trace": {"R-001": {"test": ["tests/t.py::test_r_001"]}}, "acs": {}, "source_titles": {}}
    return issues.block_data(_row("R-001", Title="Earn points"), ctx)


def test_html_body_replaces_escaped_markers_and_keeps_the_rest():
    body = issues.HtmlBody()
    escaped = "<p>Intro</p><p>&lt;!-- re-skills:begin --&gt;</p><p>old</p><p>&lt;!-- re-skills:end --&gt;</p><p>Outro</p>"
    assert body.markers(escaped) == (1, 1)
    merged = body.merge(escaped, _data())
    assert merged.startswith("<p>Intro</p><!-- re-skills:begin -->") and merged.endswith("<!-- re-skills:end --><p>Outro</p>")
    assert "old" not in merged and "&lt;!--" not in merged
    assert body.block_text(merged) == body.block_text(body.merge("", _data()))
    ctx = {"schema": issues.reqio.DEFAULT_SCHEMA, "register": "r", "trace": {}, "acs": {}, "source_titles": {}}
    assert "<script>" not in body.render(issues.block_data(_row("R-1", text="<script>x</script>"), ctx))


def test_adf_body_replaces_marker_paragraphs():
    body = issues.AdfBody()
    doc = body.merge(None, _data())
    assert doc["type"] == "doc" and doc["content"][0]["content"][0]["text"] == issues.BEGIN
    human = {"type": "paragraph", "content": [{"type": "text", "text": "Team notes"}]}
    doc["content"].insert(0, human)
    doc["content"].append(human)
    ctx = {"schema": issues.reqio.DEFAULT_SCHEMA, "register": "r", "trace": {}, "acs": {}, "source_titles": {}}
    again = body.merge(doc, issues.block_data(_row("R-001", text="New text."), ctx))
    assert again["content"][0] == human and again["content"][-1] == human
    assert "New text." in body.block_text(again) and body.markers(again) == (1, 1)


# ---------------------------------------------------------------- real clients with fake transports


def test_github_client_uses_gh_with_stdin_bodies():
    calls = []

    def runner(argv, stdin):
        calls.append((argv, stdin))
        if argv[1:3] == ["issue", "list"]:
            if "stateReason" in ",".join(argv):
                raise issues.TrackerError('gh issue list failed: Unknown JSON field: "stateReason"')
            return json.dumps([{"number": 3, "title": "R-001: Earn points", "body": "b", "state": "OPEN",
                                "url": "https://github.com/o/r/issues/3", "labels": [{"name": "req"}]}])
        if argv[1:3] == ["issue", "create"]:
            return "https://github.com/o/r/issues/9\n"
        return ""

    client = issues.GitHubClient(repo="o/r", runner=runner)
    found = client.find_many(["R-001", "R-002"])
    assert [i.key for i in found["R-001"]] == ["3"] and found["R-002"] == []
    assert found["R-001"][0].labels == ["req"] and calls[-1][0][-2:] == ["--repo", "o/r"]
    created = client.create("R-002: Balance", "BODY", ["requirement"])
    argv, stdin = calls[-1]
    assert created.key == "9" and stdin == "BODY" and argv[:3] == ["gh", "issue", "create"]
    assert ["--body-file", "-"] == argv[argv.index("--body-file"):argv.index("--body-file") + 2]
    assert "--label" in argv
    client.update(created, "R-002: Balance v2", "BODY2", [])
    assert calls[-1][0][:4] == ["gh", "issue", "edit", "9"] and calls[-1][1] == "BODY2"


class FakeHttp:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, method, url, headers, data):
        self.requests.append({"method": method, "url": url, "headers": headers,
                              "body": json.loads(data) if data else None})
        status, payload = self.responses.pop(0)
        return status, json.dumps(payload).encode("utf-8") if payload is not None else b""


def test_jira_client_requests_and_secret_handling(ws, capsys):
    http = FakeHttp([
        (200, {"issues": [{"key": "LOY-7", "fields": {"summary": "R-001: Earn points", "status": {"name": "Done"},
                                                      "description": None, "labels": []}}], "isLast": True}),
        (201, {"key": "LOY-8"}),
        (400, {"errorMessages": ["Field 'labels' cannot be set"], "errors": {}}),
    ])
    client = issues.JiraClient("https://acme.atlassian.net/", "pm@acme.test", "SECRET-TOKEN", "LOY", http=http)
    found = client.find_many(["R-001", "R-002"])
    assert found["R-001"][0].key == "LOY-7" and found["R-001"][0].status == "Done"
    first = http.requests[0]
    assert first["method"] == "GET" and first["url"].startswith("https://acme.atlassian.net/rest/api/3/search/jql?")
    assert first["headers"]["Authorization"] == "Basic " + base64.b64encode(b"pm@acme.test:SECRET-TOKEN").decode()
    assert "R-001" in first["url"] and "project+%3D+%22LOY%22" in first["url"]
    body = client.body.merge(None, _data())
    client.create("R-002: Balance", body, ["requirement"])
    sent = http.requests[1]["body"]["fields"]
    assert sent["project"] == {"key": "LOY"} and sent["issuetype"] == {"name": "Story"}
    assert sent["description"]["type"] == "doc" and sent["labels"] == ["requirement"]
    with pytest.raises(issues.TrackerError) as err:
        client.update(issues.Issue("LOY-7", "R-001: Earn points"), "R-001: Earn points", body, ["x"])
    assert "HTTP 400: Field 'labels' cannot be set" in str(err.value) and "SECRET" not in str(err.value)


def test_jira_push_through_run_never_prints_the_token(ws, capsys):
    http = FakeHttp([(200, {"issues": [], "isLast": True}), (201, {"key": "LOY-1"}), (201, {"key": "LOY-2"}),
                     (500, {"message": "boom"})])
    client = issues.JiraClient("https://acme.atlassian.net", "pm@acme.test", "SECRET-TOKEN", "LOY", http=http)
    code, out, err = _main(["push", "--tracker", "jira", "--apply"], capsys, client)
    assert code == 1  # the third create failed
    assert "SECRET-TOKEN" not in out + err and "HTTP 500: boom" in out
    assert "2 created" in out and "1 error" in out
    assert _csv(ws)["R-001"]["Links"] == "RDR-001 jira:LOY-1" and _csv(ws)["R-005"]["Links"] == ""


def test_ado_client_requests():
    http = FakeHttp([
        (200, {"workItems": [{"id": 41}]}),
        (200, {"value": [{"id": 41, "fields": {"System.Title": "R-001: Earn points", "System.State": "Resolved",
                                               "System.Description": "<p>x</p>", "System.Tags": "req; loyalty"}}]}),
        (200, {"id": 42, "fields": {"System.Title": "R-002: Balance", "System.State": "New"}}),
    ])
    client = issues.AdoClient("https://dev.azure.com/acme", "Loyalty Points", "PAT-SECRET", http=http)
    found = client.find_many(["R-001"])
    issue = found["R-001"][0]
    assert (issue.key, issue.status, issue.labels) == ("41", "Resolved", ["req", "loyalty"])
    wiql = http.requests[0]
    assert wiql["url"] == "https://dev.azure.com/acme/Loyalty%20Points/_apis/wit/wiql?api-version=7.1"
    assert "[System.Title] CONTAINS 'R-001'" in wiql["body"]["query"]
    assert wiql["headers"]["Authorization"] == "Basic " + base64.b64encode(b":PAT-SECRET").decode()
    created = client.create("R-002: Balance", "<p>b</p>", ["requirement"])
    req = http.requests[2]
    assert req["url"].endswith("/_apis/wit/workitems/$User%20Story?api-version=7.1")
    assert req["headers"]["Content-Type"] == "application/json-patch+json"
    assert {"op": "add", "path": "/fields/System.Tags", "value": "requirement"} in req["body"]
    assert created.key == "42"


def test_make_client_configuration_errors(monkeypatch):
    args = issues.build_parser().parse_args(["push", "--tracker", "jira"])
    with pytest.raises(issues.UsageError) as err:
        issues.make_client("jira", args, env={"JIRA_BASE_URL": "https://x", "JIRA_API_TOKEN": "SECRET"})
    assert "JIRA_EMAIL, JIRA_PROJECT" in str(err.value) and "SECRET" not in str(err.value)
    with pytest.raises(issues.UsageError):
        issues.make_client("ado", args, env={"ADO_ORG_URL": "http://dev.example.com", "ADO_PROJECT": "p", "ADO_PAT": "t"})
    assert isinstance(issues.make_client("ado", args, env={"ADO_ORG_URL": "https://dev.azure.com/a",
                                                          "ADO_PROJECT": "p", "ADO_PAT": "t"}), issues.AdoClient)
    monkeypatch.setattr(issues.shutil, "which", lambda name: None)
    with pytest.raises(issues.UsageError) as err:
        issues.make_client("github", args)
    assert "gh CLI is not installed" in str(err.value)


def test_missing_credentials_exit_2(ws, capsys, monkeypatch):
    for name in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT"):
        monkeypatch.delenv(name, raising=False)
    assert run_cli(issues, ["push", "--tracker", "jira"], capsys).code == 2


def test_runs_standalone_next_to_reqio(tmp_path):
    shutil.copy(SRC / "re_lint" / "reqio.py", tmp_path / "reqio.py")
    shutil.copy(SRC / "re_lint" / "issues.py", tmp_path / "issue_sync.py")
    proc = subprocess.run([sys.executable, str(tmp_path / "issue_sync.py"), "--help"], cwd=tmp_path,
                          capture_output=True, text=True)
    assert proc.returncode == 0 and "push" in proc.stdout, proc.stderr
