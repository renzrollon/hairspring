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
    """In-memory tracker: no network, records every write."""

    name = "github"
    body = issues.MarkdownBody()

    def __init__(self, existing=()):
        self.issues = list(existing)
        self.calls = []

    def find_many(self, ids):
        self.calls.append(("find", list(ids)))
        return {rid: [i for i in self.issues if rid in i.title] for rid in ids}

    def create(self, title, body, labels):
        issue = issues.GitHubIssue(str(len(self.issues) + 1), title, body, "open", f"https://x/{len(self.issues) + 1}",
                                   list(labels))
        self.issues.append(issue)
        self.calls.append(("create", title))
        return issue

    def update(self, issue, title, body, labels):
        issue.title, issue.body = title, body
        issue.labels = sorted(set(issue.labels) | set(labels))
        self.calls.append(("update", issue.key))
        return issue


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
        make_row("R-001", Status="agreed", Title="Earn points"),
        make_row("R-002", text="WHEN a member opens the app, the app shall show the posted balance and the pending "
                 "points with their posting date.", Status="agreed"),
        make_row("R-003", Status="verified", Title="Round down"),
        make_row("R-004", Status="implemented", Title="Expire points"),
        make_row("R-005", Status="agreed", Title="Print vouchers"),
        make_row("R-006", Status="withdrawn", Title="Old idea"),
        make_row("R-007", Status="draft", Title="Draft idea"),
    ], header=HEADER)
    workspace.write("requirements/trace/trace.csv", (
        "From,FromType,To,ToType,Relation,Evidence\n"
        "R-001,requirement,tests/test_earn.py::test_r_001_x,test,verified-by,tests/test_earn.py:1\n"
        "R-001,requirement,src/earn.py,code,implemented-by,src/earn.py:1\n"
    ))
    return workspace


def test_plan_is_offline(ws, capsys, tmp_path):
    out = tmp_path / "plan.json"
    code, text, _ = _main(["plan", "--tracker", "jira", "--out", str(out), "--label", "requirement"], capsys,
                          ExplodingClient())
    assert code == 0 and "nothing was sent" in text
    assert "R-001: Earn points" in text and "R-007" not in text  # default selection: agreed
    plan = json.loads(out.read_text(encoding="utf-8"))
    assert [i["id"] for i in plan["items"]] == ["R-001", "R-002", "R-005"]
    body = plan["items"][0]["body"]
    assert body.startswith(issues.BEGIN) and body.endswith(issues.END)
    assert "| Status | agreed |" in body and "`tests/test_earn.py::test_r_001_x`" in body
    code, text, _ = _main(["plan", "--tracker", "github", "--ids", "R-007", "--format", "json"], capsys, ExplodingClient())
    assert [i["id"] for i in json.loads(text)["items"]] == ["R-007"]
    assert _main(["plan", "--tracker", "github", "--ids", "R-404"], capsys)[0] == 2


def test_title_uses_title_or_first_80_characters():
    assert issues.issue_title(_row("R-001", Title="Earn points")) == "R-001: Earn points"
    long = _row("R-002", text="x" * 50 + " " + "y" * 60)
    assert issues.issue_title(long) == "R-002: " + ("x" * 50 + " " + "y" * 29)


def test_push_dry_run_then_apply_is_idempotent(ws, capsys):
    client = FakeClient()
    code, text, _ = _main(["push", "--tracker", "github"], capsys, client)
    assert code == 0 and "3 create" in text and "dry run" in text
    assert [c for c in client.calls if c[0] != "find"] == []
    code, text, _ = _main(["push", "--tracker", "github", "--apply", "--label", "requirement"], capsys, client)
    assert code == 0 and "3 created" in text
    assert [i.title for i in client.issues] == ["R-001: Earn points", "R-002: " + make_row(
        "R-002", text="WHEN a member opens the app, the app shall show the posted balance and the pending points "
        "with their posting date.")["Text"][:80].rstrip(), "R-005: Print vouchers"]
    assert client.issues[0].labels == ["requirement"]
    code, text, _ = _main(["push", "--tracker", "github", "--apply", "--label", "requirement"], capsys, client)
    assert "3 unchanged" in text and len(client.issues) == 3


def test_push_replaces_only_the_managed_block(ws, capsys):
    stale = issues.MarkdownBody().render(issues.block_data(_row("R-001", text="Old text."), {}, "`x`"))
    human = "Design notes from the team.\n\n" + stale + "\n\nDiscussion: keep this."
    client = FakeClient([issues.GitHubIssue("7", "R-001: Earn points", human, "open")])
    code, text, _ = _main(["push", "--tracker", "github", "--ids", "R-001", "--apply"], capsys, client)
    assert code == 0 and "1 updated" in text
    body = client.issues[0].body
    assert body.startswith("Design notes from the team.") and body.endswith("Discussion: keep this.")
    assert body.count(issues.BEGIN) == 1 and "Old text." not in body and make_row()["Text"] in body


def test_push_reports_ambiguous_matches(ws, capsys):
    client = FakeClient([issues.GitHubIssue("1", "Follow-up on R-001 and R-002", ""),
                         issues.GitHubIssue("2", "Question about R-001", "")])
    code, text, _ = _main(["push", "--tracker", "github", "--ids", "R-001", "--apply", "--format", "json"], capsys, client)
    item = json.loads(text)["items"][0]
    assert item["action"] == "ambiguous" and "1, 2" in item["detail"]
    assert not [c for c in client.calls if c[0] in ("create", "update")]
    leading = FakeClient([issues.GitHubIssue("1", "Follow-up on R-001", ""), issues.GitHubIssue("2", "[R-001] Earn", "")])
    issue, candidates = issues.pick_issue("R-001", leading.issues)
    assert issue.key == "2" and len(candidates) == 2
    assert issues.pick_issue("R-001", [issues.Issue("3", "R-0012: other")])[0] is None


def _statuses(ws):
    rows = csv.DictReader(io.StringIO((ws.ws / "requirements.csv").read_text(encoding="utf-8")))
    return {r["ID"]: r["Status"] for r in rows}


def test_pull_maps_status_and_respects_the_lifecycle(ws, capsys):
    tracker = FakeClient([
        issues.GitHubIssue("1", "R-001: Earn points", "", "CLOSED", state_reason="COMPLETED"),
        issues.GitHubIssue("2", "R-002: Balance", "", "OPEN"),
        issues.GitHubIssue("3", "R-003: Round down", "", "CLOSED"),      # verified -> implemented is a downgrade
        issues.GitHubIssue("4", "R-004: Expire points", "", "OPEN"),     # implemented -> agreed is allowed (reopened)
        issues.GitHubIssue("5", "R-005: Print vouchers", "", "CLOSED", state_reason="NOT_PLANNED"),
        issues.GitHubIssue("6", "R-006: Old idea", "", "OPEN"),          # withdrawn rows never change
    ])
    before = (ws.ws / "requirements.csv").read_bytes()
    code, text, _ = _main(["pull", "--tracker", "github", "--format", "json"], capsys, tracker)
    assert code == 0 and (ws.ws / "requirements.csv").read_bytes() == before
    items = {i["id"]: i for i in json.loads(text)["items"]}
    assert "R-006" not in items
    assert (items["R-001"]["action"], items["R-001"]["mapped"]) == ("update", "implemented")
    assert items["R-002"]["action"] == "unchanged"
    assert items["R-003"]["action"] == "skipped" and "lifecycle does not allow verified -> implemented" in items["R-003"]["detail"]
    assert (items["R-004"]["action"], items["R-004"]["mapped"]) == ("update", "agreed")
    assert items["R-005"]["action"] == "skipped" and "closed:not_planned" in items["R-005"]["detail"]
    assert items["R-007"]["action"] == "no issue"
    code, text, _ = _main(["pull", "--tracker", "github", "--apply"], capsys, tracker)
    assert code == 0 and "2 Status value(s) written" in text
    assert _statuses(ws) == {"R-001": "implemented", "R-002": "agreed", "R-003": "verified", "R-004": "agreed",
                             "R-005": "agreed", "R-006": "withdrawn", "R-007": "draft"}
    forced = _main(["pull", "--tracker", "github", "--ids", "R-003", "--apply", "--ignore-lifecycle"], capsys, tracker)
    assert forced[0] == 0 and _statuses(ws)["R-003"] == "implemented"


def test_pull_uses_schema_status_map_case_insensitively(ws, capsys):
    ws.schema({"issues": {"status_map": {"github": {"closed:not_planned": "deferred"}, "jira": {"done": "verified"}}}})
    tracker = FakeClient([issues.GitHubIssue("5", "R-005: Print vouchers", "", "CLOSED", state_reason="NOT_PLANNED")])
    code, text, _ = _main(["pull", "--tracker", "github", "--ids", "R-005", "--apply"], capsys, tracker)
    assert code == 0 and _statuses(ws)["R-005"] == "deferred"
    jira = FakeClient([issues.Issue("LOY-4", "R-004: Expire points", None, "Done")])
    _main(["pull", "--tracker", "jira", "--ids", "R-004", "--apply"], capsys, jira)
    assert _statuses(ws)["R-004"] == "verified"
    review = FakeClient([issues.Issue("LOY-1", "R-001: Earn points", None, "In Review")])
    _, text, _ = _main(["pull", "--tracker", "jira", "--ids", "R-001", "--format", "json"], capsys, review)
    assert "no mapping for tracker status 'In Review' in issues.status_map.jira" in text


# ---------------------------------------------------------------- body formats


def _data():
    return issues.block_data(_row("R-001", Title="Earn points"), {"R-001": {"test": ["tests/t.py::test_r_001"]}},
                             "`requirements/requirements.csv`")


def test_html_body_replaces_escaped_markers_and_keeps_the_rest():
    body = issues.HtmlBody()
    escaped = "<p>Intro</p><p>&lt;!-- re-skills:begin --&gt;</p><p>old</p><p>&lt;!-- re-skills:end --&gt;</p><p>Outro</p>"
    merged = body.merge(escaped, _data())
    assert merged.startswith("<p>Intro</p><!-- re-skills:begin -->") and merged.endswith("<!-- re-skills:end --><p>Outro</p>")
    assert "old" not in merged and "&lt;!--" not in merged
    assert body.block_text(merged) == body.block_text(body.merge("", _data()))
    assert "<script>" not in body.render(issues.block_data(_row("R-1", text="<script>x</script>"), {}, "r"))


def test_adf_body_replaces_marker_paragraphs():
    body = issues.AdfBody()
    doc = body.merge(None, _data())
    assert doc["type"] == "doc" and doc["content"][0]["content"][0]["text"] == issues.BEGIN
    human = {"type": "paragraph", "content": [{"type": "text", "text": "Team notes"}]}
    doc["content"].insert(0, human)
    doc["content"].append(human)
    again = body.merge(doc, issues.block_data(_row("R-001", text="New text."), {}, "r"))
    assert again["content"][0] == human and again["content"][-1] == human
    assert "New text." in body.block_text(again) and sum(
        1 for n in again["content"] if issues.AdfBody._text(n) == issues.BEGIN) == 1


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
