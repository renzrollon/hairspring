#!/usr/bin/env python3
# VENDORED from packages/re-lint/src/re_lint/issues.py by tools/vendor_scripts.py; do not edit.
# Change the package module, then run `python3 tools/vendor_scripts.py` to refresh this copy.
"""Plan, push and pull requirement issues in GitHub Issues, Jira or Azure DevOps.

Usage::

    re-lint issues plan --tracker github|jira|ado [--ids ...] [--status S ...] [--format text|json] [--out FILE]
    re-lint issues push --tracker github|jira|ado [--ids ...] [--status S ...] [--apply] [--label L ...]
    re-lint issues pull --tracker github|jira|ado [--ids ...] [--apply] [--ignore-lifecycle]

``plan`` shows what ``push`` would send, without any network call. ``push`` and ``pull`` are dry
runs unless ``--apply`` is given: they read the tracker and report what they would change.

* Issue title: ``<ID>: <Title, or the first 80 characters of Text>``. Issues are matched by the ID
  in the title (a title that starts with the ID wins), so re-running ``push`` updates instead of
  duplicating; two candidate issues for one ID are reported as ambiguous and left alone.
* Issue body: a block between ``<!-- re-skills:begin -->`` and ``<!-- re-skills:end -->`` with the
  text, attributes and trace links (from ``<workspace>/trace/trace.csv`` when present). A re-sync
  replaces only that block; the rest of the body is kept. Jira descriptions are Atlassian Document
  Format, so the markers are paragraphs there; Azure DevOps descriptions are HTML.
* Selection: ``--ids``, else ``--status`` (default ``agreed`` for plan and push; every status except
  withdrawn and rejected for pull).
* ``pull`` maps the tracker status through ``schema.json`` -> ``issues.status_map.<tracker>`` (keys
  are case-insensitive; for GitHub, ``closed:not_planned`` is looked up for issues closed as not
  planned and such issues are skipped when the key is missing) and sets ``Status`` in
  ``requirements.csv`` only where it differs. A change must be allowed by
  ``schema.lifecycle.transitions`` or move forward along draft -> proposed -> agreed ->
  implemented -> verified (so a closed issue never moves ``verified`` back to ``implemented``);
  ``--ignore-lifecycle`` skips that check. Withdrawn and rejected rows never change.

Credentials (never printed):

* GitHub: the ``gh`` CLI, logged in (``gh auth login``); ``--repo OWNER/REPO`` or the current repo.
* Jira Cloud (REST v3): ``JIRA_BASE_URL``, ``JIRA_EMAIL``, ``JIRA_API_TOKEN``, ``JIRA_PROJECT``.
* Azure DevOps (REST 7.1): ``ADO_ORG_URL``, ``ADO_PROJECT``, ``ADO_PAT``.

Exit codes: 0 ok, 1 some tracker calls failed, 2 usage, configuration or parse error.
"""
from __future__ import annotations

import argparse
import base64
import copy
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

if not __package__:  # run as a plain script: make the sibling reqio.py importable
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # inside the package
    from . import reqio
except ImportError:  # vendored next to reqio.py in a skill's scripts/
    import reqio

BEGIN = "<!-- re-skills:begin -->"
END = "<!-- re-skills:end -->"
TRACKERS = ("github", "jira", "ado")
RETIRED = {"withdrawn", "rejected"}
PROGRESSION = ["draft", "proposed", "agreed", "implemented", "verified"]
ATTRIBUTES = ["Type", "Priority", "Status", "Source", "Rationale", "Owner", "Verification", "Version",
              "Links", "Tags"]
TIMEOUT = 30


class UsageError(Exception):
    """A problem the user can fix (exit 2)."""


class _Parser(argparse.ArgumentParser):
    """Keeps subcommand usage in step with ``prog``, even when a caller sets it after
    ``build_parser()`` (``re-lint`` does: ``parser.prog = "re-lint <command>"``)."""

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "prog":
            for action in getattr(self, "_actions", []):
                if isinstance(action, argparse._SubParsersAction):
                    action._prog_prefix = value
                    for choice, sub in action.choices.items():
                        sub.prog = f"{value} {choice}"


class TrackerError(Exception):
    """A tracker call failed (reported per item; exit 1)."""


# --------------------------------------------------------------------------- helpers


def _workspace(args: argparse.Namespace) -> Tuple[Path, Dict]:
    schema_path = getattr(args, "schema", None)
    if schema_path and not Path(schema_path).is_file():
        raise UsageError(f"schema file not found: {schema_path}")
    if getattr(args, "workspace", None):
        ws = Path(args.workspace).resolve()
    else:
        base = reqio.load_schema(schema_path) if schema_path else None
        ws = reqio.find_workspace(".", base).resolve()
    return ws, reqio.load_schema(schema_path, workspace=ws)


def _split_list(values: Optional[Sequence[str]]) -> List[str]:
    out: List[str] = []
    for value in values or []:
        out.extend(v for v in re.split(r"[,\s]+", value) if v)
    return out


def _one_line(text: str) -> str:
    return " ".join((text or "").split())


def _md_cell(value: object) -> str:
    return _one_line(str(value if value is not None else "")).replace("|", "\\|")


def issue_title(row: reqio.Row) -> str:
    label = _one_line(row.get_str("Title")) or _one_line(row.get_str("Text"))[:80].rstrip()
    return f"{row.get_str('ID')}: {label}"


def title_pattern(rid: str) -> "re.Pattern[str]":
    return re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(rid)}(?![0-9]|\.AC)")


def pick_issue(rid: str, issues: Sequence["Issue"]) -> Tuple[Optional["Issue"], List["Issue"]]:
    """The issue for ``rid`` and the candidates (more than one candidate means ambiguous)."""
    pattern = title_pattern(rid)
    candidates = [i for i in issues if pattern.search(i.title or "")]
    leading = [i for i in candidates if re.match(rf"^\W*{re.escape(rid)}(?![0-9])", i.title or "")]
    if len(leading) == 1:
        return leading[0], candidates
    if len(candidates) == 1:
        return candidates[0], candidates
    return None, candidates


# --------------------------------------------------------------------------- body blocks


def block_data(row: reqio.Row, trace: Dict[str, Dict[str, List[str]]], register: str) -> Dict:
    rid = row.get_str("ID")
    attrs = [(name, _one_line(row.get_str(name))) for name in ATTRIBUTES if row.get_str(name)]
    links = OrderedDict((label, trace.get(rid, {}).get(kind, [])[:10])
                        for label, kind in (("Tests", "test"), ("Code", "code"), ("Decisions", "decision")))
    return {"id": rid, "text": _one_line(row.get_str("Text")), "attributes": attrs,
            "trace": OrderedDict((k, v) for k, v in links.items() if v), "register": register}


def _footer(data: Dict) -> str:
    return (f"Synced by re-skills issue-sync from {data['register']}. Edit the requirement there; "
            "this block is replaced on every sync.")


class MarkdownBody:
    """GitHub: Markdown with HTML-comment markers."""

    name = "markdown"
    _region = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)

    def render(self, data: Dict) -> str:
        out = [BEGIN, f"> {data['text']}", "", "| Attribute | Value |", "| --- | --- |"]
        out += [f"| {k} | {_md_cell(v)} |" for k, v in data["attributes"]]
        if data["trace"]:
            out += ["", "**Trace**"]
            out += [f"- {label}: " + ", ".join(f"`{v}`" for v in values) for label, values in data["trace"].items()]
        out += ["", f"_{_footer(data)}_", END]
        return "\n".join(out)

    def merge(self, existing: Any, data: Dict) -> str:
        block = self.render(data)
        body = existing or ""
        if self._region.search(body):
            return self._region.sub(lambda _m: block, body, count=1)
        return (body.rstrip() + "\n\n" + block) if body.strip() else block

    def block_text(self, body: Any) -> Optional[str]:
        match = self._region.search(body or "")
        return _one_line(match.group(0)) if match else None


class HtmlBody:
    """Azure DevOps: HTML descriptions (markers as comments, escaped markers also recognized)."""

    name = "html"
    _marker = r"(?:<(?:p|div)[^>]*>\s*)?(?:<!--|&lt;!--)\s*re-skills:{0}\s*(?:-->|--&gt;)(?:\s*</(?:p|div)>)?"
    _region = re.compile(_marker.format("begin") + r".*?" + _marker.format("end"), re.S | re.I)

    def render(self, data: Dict) -> str:
        e = html.escape
        rows = "".join(f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in data["attributes"])
        out = [BEGIN, "<div>", f"<blockquote>{e(data['text'])}</blockquote>",
               f"<table><tr><th>Attribute</th><th>Value</th></tr>{rows}</table>"]
        if data["trace"]:
            items = "".join(f"<li>{e(label)}: {e(', '.join(values))}</li>" for label, values in data["trace"].items())
            out.append(f"<p><strong>Trace</strong></p><ul>{items}</ul>")
        out += [f"<p><em>{e(_footer(data))}</em></p>", "</div>", END]
        return "".join(out)

    def merge(self, existing: Any, data: Dict) -> str:
        block = self.render(data)
        body = existing or ""
        if self._region.search(body):
            return self._region.sub(lambda _m: block, body, count=1)
        return (body + block) if body.strip() else block

    def block_text(self, body: Any) -> Optional[str]:
        match = self._region.search(body or "")
        if not match:
            return None
        text = re.sub(r"<!--.*?-->", " ", match.group(0), flags=re.S)
        return _one_line(html.unescape(re.sub(r"<[^>]+>", " ", text)))


class AdfBody:
    """Jira Cloud: Atlassian Document Format; the markers are their own paragraphs."""

    name = "adf"

    @staticmethod
    def _text(node: Any) -> str:
        if isinstance(node, dict):
            if node.get("type") == "text":
                return str(node.get("text", ""))
            return " ".join(AdfBody._text(c) for c in node.get("content", []) or [])
        if isinstance(node, list):
            return " ".join(AdfBody._text(c) for c in node)
        return ""

    @staticmethod
    def _para(*parts: Dict) -> Dict:
        return {"type": "paragraph", "content": [p for p in parts if p.get("text")]}

    @staticmethod
    def _t(text: str, *marks: str) -> Dict:
        node: Dict[str, Any] = {"type": "text", "text": text}
        if marks:
            node["marks"] = [{"type": m} for m in marks]
        return node

    def nodes(self, data: Dict) -> List[Dict]:
        items = [{"type": "listItem", "content": [self._para(self._t(k, "strong"), self._t(f": {v}"))]}
                 for k, v in data["attributes"]]
        out: List[Dict] = [self._para(self._t(BEGIN)),
                           {"type": "blockquote", "content": [self._para(self._t(data["text"] or " "))]}]
        if items:
            out.append({"type": "bulletList", "content": items})
        if data["trace"]:
            out.append(self._para(self._t("Trace", "strong")))
            out.append({"type": "bulletList", "content": [
                {"type": "listItem", "content": [self._para(self._t(f"{label}: {', '.join(values)}"))]}
                for label, values in data["trace"].items()]})
        out += [self._para(self._t(_footer(data), "em")), self._para(self._t(END))]
        return out

    def _bounds(self, content: List[Any]) -> Optional[Tuple[int, int]]:
        begin = next((i for i, n in enumerate(content) if _one_line(self._text(n)) == BEGIN), None)
        if begin is None:
            return None
        end = next((i for i in range(begin + 1, len(content)) if _one_line(self._text(content[i])) == END), None)
        return (begin, end) if end is not None else None

    def merge(self, existing: Any, data: Dict) -> Dict:
        doc = copy.deepcopy(existing) if isinstance(existing, dict) and existing.get("type") == "doc" else None
        nodes = self.nodes(data)
        if doc is None:
            return {"type": "doc", "version": 1, "content": nodes}
        content = list(doc.get("content") or [])
        bounds = self._bounds(content)
        doc["content"] = content[:bounds[0]] + nodes + content[bounds[1] + 1:] if bounds else content + nodes
        return doc

    def block_text(self, body: Any) -> Optional[str]:
        if not isinstance(body, dict):
            return None
        content = list(body.get("content") or [])
        bounds = self._bounds(content)
        if not bounds:
            return None
        return _one_line(self._text(content[bounds[0]:bounds[1] + 1]))


# --------------------------------------------------------------------------- tracker clients


class Issue:
    def __init__(self, key: str, title: str, body: Any = None, status: str = "", url: str = "",
                 labels: Optional[List[str]] = None, state_reason: str = ""):
        self.key = str(key)
        self.title = title or ""
        self.body = body
        self.status = status or ""
        self.url = url or ""
        self.labels = list(labels or [])
        self.state_reason = state_reason or ""

    def status_keys(self) -> List[str]:
        """Status-map keys to try, most specific first."""
        return [self.status]


class TrackerClient:
    """Interface the sync logic uses; tests inject fakes implementing it."""

    name = "tracker"
    body = MarkdownBody()

    def find_many(self, ids: Sequence[str]) -> Dict[str, List[Issue]]:  # pragma: no cover - interface
        raise NotImplementedError

    def create(self, title: str, body: Any, labels: Sequence[str]) -> Issue:  # pragma: no cover
        raise NotImplementedError

    def update(self, issue: Issue, title: str, body: Any, labels: Sequence[str]) -> Issue:  # pragma: no cover
        raise NotImplementedError


Runner = Callable[[List[str], Optional[str]], str]
Http = Callable[[str, str, Dict[str, str], Optional[bytes]], Tuple[int, bytes]]


def _run_cli(argv: List[str], stdin: Optional[str] = None) -> str:
    try:
        proc = subprocess.run(argv, input=(stdin or "").encode("utf-8"), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise TrackerError(f"{argv[0]} failed to run: {exc}") from exc
    if proc.returncode != 0:
        message = proc.stderr.decode("utf-8", errors="replace").strip().splitlines()
        raise TrackerError(f"{' '.join(argv[:3])} failed: {message[-1] if message else 'exit ' + str(proc.returncode)}")
    return proc.stdout.decode("utf-8", errors="replace")


class GitHubIssue(Issue):
    def status_keys(self) -> List[str]:
        state = self.status.lower()
        if state == "closed" and self.state_reason.upper() == "NOT_PLANNED":
            return ["closed:not_planned"]  # never falls back to "closed" (that usually means implemented)
        if state == "closed":
            return ["closed:completed", "closed"]
        return [state]


class GitHubClient(TrackerClient):
    name = "github"
    body = MarkdownBody()
    FIELDS = "number,title,body,state,stateReason,url,labels"

    def __init__(self, repo: Optional[str] = None, runner: Optional[Runner] = None, bulk_limit: int = 1000):
        self.repo = repo
        self.runner = runner or _run_cli
        self.bulk_limit = bulk_limit

    def _gh(self, args: List[str], stdin: Optional[str] = None) -> str:
        argv = ["gh", *args] + (["--repo", self.repo] if self.repo else [])
        return self.runner(argv, stdin)

    def _list(self, extra: List[str], limit: int) -> List[Issue]:
        fields = self.FIELDS
        try:
            out = self._gh(["issue", "list", "--state", "all", "--limit", str(limit), "--json", fields, *extra])
        except TrackerError as exc:
            if "stateReason" not in str(exc):
                raise
            fields = fields.replace(",stateReason", "")  # older gh releases
            out = self._gh(["issue", "list", "--state", "all", "--limit", str(limit), "--json", fields, *extra])
        try:
            items = json.loads(out or "[]")
        except json.JSONDecodeError as exc:
            raise TrackerError(f"gh returned unexpected output: {exc}") from exc
        return [GitHubIssue(str(i.get("number", "")), i.get("title", ""), i.get("body", ""), i.get("state", ""),
                            i.get("url", ""), [l.get("name", "") for l in i.get("labels") or []],
                            i.get("stateReason", "") or "") for i in items]

    def find_many(self, ids: Sequence[str]) -> Dict[str, List[Issue]]:
        result: Dict[str, List[Issue]] = {rid: [] for rid in ids}
        if not ids:
            return result
        recent = self._list([], self.bulk_limit)
        for rid in ids:
            pattern = title_pattern(rid)
            result[rid] = [i for i in recent if pattern.search(i.title)]
        if len(recent) >= self.bulk_limit:  # more issues than one listing: search the ones not found
            for rid in ids:
                if not result[rid]:
                    pattern = title_pattern(rid)
                    found = self._list(["--search", f'"{rid}" in:title'], 50)
                    result[rid] = [i for i in found if pattern.search(i.title)]
        return result

    def create(self, title: str, body: Any, labels: Sequence[str]) -> Issue:
        args = ["issue", "create", "--title", title, "--body-file", "-"]
        for label in labels:
            args += ["--label", label]
        out = self._gh(args, body)
        url = out.strip().splitlines()[-1] if out.strip() else ""
        number = re.search(r"/issues/(\d+)", url)
        return GitHubIssue(number.group(1) if number else url, title, body, "open", url, list(labels))

    def update(self, issue: Issue, title: str, body: Any, labels: Sequence[str]) -> Issue:
        args = ["issue", "edit", issue.key, "--title", title, "--body-file", "-"]
        for label in labels:
            args += ["--add-label", label]
        self._gh(args, body)
        return GitHubIssue(issue.key, title, body, issue.status, issue.url, sorted(set(issue.labels) | set(labels)))


def _urllib_http(method: str, url: str, headers: Dict[str, str], data: Optional[bytes]) -> Tuple[int, bytes]:
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except urllib.error.URLError as exc:
        raise TrackerError(f"cannot reach {urllib.parse.urlsplit(url).netloc}: {exc.reason}") from exc


def _check_base_url(name: str, url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    local = parts.hostname in ("localhost", "127.0.0.1", "::1")
    if parts.scheme not in ("https", "http") or not parts.netloc or (parts.scheme == "http" and not local):
        raise UsageError(f"{name} must be an https:// URL (got {parts.scheme or 'no scheme'}://{parts.netloc})")
    return url.rstrip("/")


class RestClient(TrackerClient):
    """Shared JSON-over-HTTP plumbing; the Authorization header is never printed."""

    def __init__(self, base: str, auth_header: str, http: Optional[Http] = None):
        self.base = base
        self._auth = auth_header
        self.http = http or _urllib_http

    def request(self, method: str, path: str, body: Any = None, content_type: str = "application/json") -> Any:
        url = path if path.startswith("http") else self.base + path
        headers = {"Authorization": self._auth, "Accept": "application/json"}
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = content_type
        status, payload = self.http(method, url, headers, data)
        text = payload.decode("utf-8", errors="replace") if payload else ""
        if status >= 400:
            try:
                parsed = json.loads(text)
            except ValueError:
                parsed = None
            detail = text
            if isinstance(parsed, dict):  # Jira: errorMessages/errors; Azure DevOps: message
                messages = [str(m) for m in parsed.get("errorMessages") or []]
                errors = parsed.get("errors") or {}
                detail = "; ".join(messages) or (json.dumps(errors) if errors else str(parsed.get("message") or text))
            path_only = urllib.parse.urlsplit(url).path
            raise TrackerError(f"{method} {path_only} -> HTTP {status}: {_one_line(str(detail))[:300]}")
        if not text.strip():
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise TrackerError(f"{method} {urllib.parse.urlsplit(url).path}: response is not JSON") from exc


class JiraClient(RestClient):
    name = "jira"
    body = AdfBody()

    def __init__(self, base_url: str, email: str, token: str, project: str, issue_type: str = "Story",
                 http: Optional[Http] = None):
        auth = "Basic " + base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
        super().__init__(_check_base_url("JIRA_BASE_URL", base_url), auth, http)
        self.project = project
        self.issue_type = issue_type

    def _issue(self, item: Dict) -> Issue:
        fields = item.get("fields") or {}
        return Issue(item.get("key", ""), fields.get("summary", ""), fields.get("description"),
                     (fields.get("status") or {}).get("name", ""), f"{self.base}/browse/{item.get('key', '')}",
                     fields.get("labels") or [])

    def find_many(self, ids: Sequence[str]) -> Dict[str, List[Issue]]:
        result: Dict[str, List[Issue]] = {rid: [] for rid in ids}
        project = self.project.replace('"', '\\"')
        for start in range(0, len(ids), 20):
            chunk = list(ids)[start:start + 20]
            terms = " OR ".join(f'summary ~ "\\"{rid}\\""' for rid in chunk)
            jql = f'project = "{project}" AND ({terms})'
            token: Optional[str] = None
            issues: List[Issue] = []
            for _ in range(50):  # pages
                params = {"jql": jql, "fields": "summary,status,description,labels", "maxResults": "100"}
                if token:
                    params["nextPageToken"] = token
                data = self.request("GET", "/rest/api/3/search/jql?" + urllib.parse.urlencode(params))
                issues += [self._issue(i) for i in data.get("issues") or []]
                token = data.get("nextPageToken")
                if not token or data.get("isLast", True):
                    break
            for rid in chunk:
                pattern = title_pattern(rid)
                result[rid] = [i for i in issues if pattern.search(i.title)]
        return result

    def create(self, title: str, body: Any, labels: Sequence[str]) -> Issue:
        fields: Dict[str, Any] = {"project": {"key": self.project}, "summary": title,
                                  "issuetype": {"name": self.issue_type}, "description": body}
        if labels:
            fields["labels"] = list(labels)
        data = self.request("POST", "/rest/api/3/issue", {"fields": fields})
        key = data.get("key", "")
        return Issue(key, title, body, "", f"{self.base}/browse/{key}", list(labels))

    def update(self, issue: Issue, title: str, body: Any, labels: Sequence[str]) -> Issue:
        payload: Dict[str, Any] = {"fields": {"summary": title, "description": body}}
        if labels:
            payload["update"] = {"labels": [{"add": label} for label in labels]}
        self.request("PUT", f"/rest/api/3/issue/{urllib.parse.quote(issue.key)}", payload)
        return Issue(issue.key, title, body, issue.status, issue.url, sorted(set(issue.labels) | set(labels)))


class AdoClient(RestClient):
    name = "ado"
    body = HtmlBody()
    API = "api-version=7.1"

    def __init__(self, org_url: str, project: str, pat: str, work_item_type: str = "User Story",
                 http: Optional[Http] = None):
        auth = "Basic " + base64.b64encode(f":{pat}".encode("utf-8")).decode("ascii")
        super().__init__(_check_base_url("ADO_ORG_URL", org_url), auth, http)
        self.project = project
        self.work_item_type = work_item_type
        self.prefix = f"/{urllib.parse.quote(project)}/_apis/wit"

    def _issue(self, item: Dict) -> Issue:
        fields = item.get("fields") or {}
        tags = [t.strip() for t in str(fields.get("System.Tags") or "").split(";") if t.strip()]
        wid = str(item.get("id", ""))
        return Issue(wid, fields.get("System.Title", ""), fields.get("System.Description") or "",
                     fields.get("System.State", ""),
                     f"{self.base}/{urllib.parse.quote(self.project)}/_workitems/edit/{wid}", tags)

    def find_many(self, ids: Sequence[str]) -> Dict[str, List[Issue]]:
        result: Dict[str, List[Issue]] = {rid: [] for rid in ids}
        for start in range(0, len(ids), 20):
            chunk = list(ids)[start:start + 20]
            terms = " OR ".join(f"[System.Title] CONTAINS '{rid.replace(chr(39), chr(39) * 2)}'" for rid in chunk)
            query = f"SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = @project AND ({terms})"
            data = self.request("POST", f"{self.prefix}/wiql?{self.API}", {"query": query})
            wids = [str(w.get("id")) for w in data.get("workItems") or [] if w.get("id") is not None]
            issues: List[Issue] = []
            for batch in range(0, len(wids), 200):
                fields = "System.Id,System.Title,System.State,System.Description,System.Tags"
                got = self.request("GET", f"{self.prefix}/workitems?ids={','.join(wids[batch:batch + 200])}"
                                          f"&fields={fields}&{self.API}")
                issues += [self._issue(i) for i in got.get("value") or []]
            for rid in chunk:
                pattern = title_pattern(rid)
                result[rid] = [i for i in issues if pattern.search(i.title)]
        return result

    def _ops(self, title: str, body: Any, tags: Sequence[str]) -> List[Dict]:
        ops = [{"op": "add", "path": "/fields/System.Title", "value": title},
               {"op": "add", "path": "/fields/System.Description", "value": body}]
        if tags:
            ops.append({"op": "add", "path": "/fields/System.Tags", "value": "; ".join(tags)})
        return ops

    def create(self, title: str, body: Any, labels: Sequence[str]) -> Issue:
        kind = urllib.parse.quote("$" + self.work_item_type, safe="$")
        data = self.request("POST", f"{self.prefix}/workitems/{kind}?{self.API}", self._ops(title, body, labels),
                            content_type="application/json-patch+json")
        return self._issue(data) if data else Issue("", title, body)

    def update(self, issue: Issue, title: str, body: Any, labels: Sequence[str]) -> Issue:
        tags = sorted(set(issue.labels) | set(labels)) if labels else []
        data = self.request("PATCH", f"{self.prefix}/workitems/{urllib.parse.quote(issue.key)}?{self.API}",
                            self._ops(title, body, tags), content_type="application/json-patch+json")
        return self._issue(data) if data else issue


def make_client(tracker: str, args: argparse.Namespace, env: Optional[Dict[str, str]] = None) -> TrackerClient:
    env = dict(os.environ if env is None else env)
    if tracker == "github":
        if shutil.which("gh") is None:
            raise UsageError("the gh CLI is not installed; see https://cli.github.com and run `gh auth login`")
        return GitHubClient(repo=getattr(args, "repo", None))
    if tracker == "jira":
        names = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT"]
        missing = [n for n in names if not env.get(n)]
        if missing:
            raise UsageError(f"set {', '.join(missing)} for Jira (values are never printed)")
        return JiraClient(env["JIRA_BASE_URL"], env["JIRA_EMAIL"], env["JIRA_API_TOKEN"], env["JIRA_PROJECT"],
                          issue_type=getattr(args, "issue_type", None) or "Story")
    names = ["ADO_ORG_URL", "ADO_PROJECT", "ADO_PAT"]
    missing = [n for n in names if not env.get(n)]
    if missing:
        raise UsageError(f"set {', '.join(missing)} for Azure DevOps (values are never printed)")
    return AdoClient(env["ADO_ORG_URL"], env["ADO_PROJECT"], env["ADO_PAT"],
                     work_item_type=getattr(args, "issue_type", None) or "User Story")


# --------------------------------------------------------------------------- workspace data


def _load_rows(ws: Path, schema: Dict) -> "OrderedDict[str, reqio.Row]":
    out: "OrderedDict[str, reqio.Row]" = OrderedDict()
    try:
        rows = reqio.read_requirements(reqio.requirement_files(ws), schema)
    except UnicodeDecodeError as exc:
        raise UsageError(f"cannot read the requirement registers as UTF-8: {exc}") from exc
    for row in rows:
        out.setdefault(row.get_str("ID"), row)
    return out


def _trace(ws: Path) -> Dict[str, Dict[str, List[str]]]:
    path = ws / "trace" / "trace.csv"
    out: Dict[str, Dict[str, List[str]]] = {}
    if not path.is_file():
        return out
    try:
        table = reqio.read_table(path)
    except (OSError, UnicodeDecodeError, ValueError):
        return out
    for row in table.rows:
        rid = row.get_str("From").split(".AC", 1)[0]
        kind = row.get_str("ToType")
        target = row.get_str("To")
        values = out.setdefault(rid, {}).setdefault(kind, [])
        if target and target not in values:
            values.append(target)
    return out


def _select(rows: "OrderedDict[str, reqio.Row]", args: argparse.Namespace, default_statuses: Optional[List[str]]
            ) -> List[reqio.Row]:
    ids = _split_list(getattr(args, "ids", None))
    if ids:
        unknown = [i for i in ids if i not in rows]
        if unknown:
            raise UsageError(f"unknown requirement ID(s): {', '.join(unknown)}")
        keep = set(ids)
        return [r for rid, r in rows.items() if rid in keep]
    statuses = {s.lower() for s in _split_list(getattr(args, "status", None))}
    if statuses:
        return [r for r in rows.values() if r.get_str("Status").lower() in statuses]
    if default_statuses is None:
        return [r for r in rows.values() if r.get_str("Status").lower() not in RETIRED]
    return [r for r in rows.values() if r.get_str("Status").lower() in default_statuses]


def _register_name(ws: Path) -> str:
    return "`" + os.path.relpath(ws / "requirements.csv", reqio.find_repo_root(ws)).replace(os.sep, "/") + "`"


def map_status(tracker: str, issue: Issue, schema: Dict) -> Tuple[Optional[str], str]:
    """(requirement status, the key that matched or a reason it did not)."""
    status_map = ((schema.get("issues") or {}).get("status_map") or {}).get(tracker) or {}
    lowered = {str(k).strip().lower(): str(v) for k, v in status_map.items()}
    for key in issue.status_keys():
        if key.strip().lower() in lowered:
            return lowered[key.strip().lower()], key
    keys = issue.status_keys()
    return None, f"no mapping for tracker status {keys[0]!r} in issues.status_map.{tracker}"


def transition_allowed(current: str, target: str, schema: Dict) -> bool:
    transitions = ((schema.get("lifecycle") or {}).get("transitions") or {})
    if target in (transitions.get(current) or []):
        return True
    return current in PROGRESSION and target in PROGRESSION and PROGRESSION.index(target) > PROGRESSION.index(current)


# --------------------------------------------------------------------------- commands


def _print_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) if rows else len(str(h)) for i, h in enumerate(headers)]
    print("  ".join(str(h).ljust(w) for h, w in zip(headers, widths)).rstrip())
    for row in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)).rstrip())


def cmd_plan(args: argparse.Namespace, client: Optional[TrackerClient] = None) -> int:
    ws, schema = _workspace(args)
    rows = _select(_load_rows(ws, schema), args, ["agreed"])
    trace = _trace(ws)
    register = _register_name(ws)
    labels = _split_list(args.label)
    items = []
    for row in rows:
        data = block_data(row, trace, register)
        items.append({"id": row.get_str("ID"), "title": issue_title(row), "labels": labels,
                      "action": "create, or update the issue whose title holds the ID",
                      "body": MarkdownBody().render(data)})
    plan = {"tracker": args.tracker, "count": len(items), "items": items}
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    if args.format == "json":
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    else:
        _print_table(["ID", "Title", "Labels"], [(i["id"], i["title"], ", ".join(labels) or "-") for i in items])
        print(f"\n{len(items)} requirement(s) for {args.tracker}; nothing was sent (plan never calls the tracker)."
              + (f" Plan written to {args.out}." if args.out else ""))
    return 0


def cmd_push(args: argparse.Namespace, client: Optional[TrackerClient] = None) -> int:
    ws, schema = _workspace(args)
    rows = _select(_load_rows(ws, schema), args, ["agreed"])
    if not rows:
        print("no requirements selected")
        return 0
    client = client or make_client(args.tracker, args)
    trace = _trace(ws)
    register = _register_name(ws)
    labels = _split_list(args.label)
    try:
        matches = client.find_many([r.get_str("ID") for r in rows])
    except TrackerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    report = []
    errors = 0
    for row in rows:
        rid = row.get_str("ID")
        title = issue_title(row)
        data = block_data(row, trace, register)
        issue, candidates = pick_issue(rid, matches.get(rid, []))
        entry = {"id": rid, "title": title, "issue": issue.key if issue else "", "url": issue.url if issue else ""}
        if issue is None and candidates:
            entry.update(action="ambiguous", detail="several issues hold the ID: " +
                         ", ".join(c.key for c in candidates))
            report.append(entry)
            continue
        body = client.body.merge(issue.body if issue else None, data)
        if issue is None:
            action = "create"
        else:
            same_block = client.body.block_text(issue.body) == client.body.block_text(body)
            missing_labels = [l for l in labels if l not in issue.labels]
            action = "unchanged" if same_block and issue.title == title and not missing_labels else "update"
        entry["action"] = action
        if args.apply and action in ("create", "update"):
            try:
                done = client.create(title, body, labels) if action == "create" else client.update(issue, title, body, labels)
                entry.update(issue=done.key, url=done.url, action=action + "d")
            except TrackerError as exc:
                errors += 1
                entry.update(action="error", detail=str(exc))
        report.append(entry)
    _report(args, report, ["ID", "Action", "Issue", "Title"],
            lambda e: (e["id"], e["action"], e.get("issue") or "-", e.get("detail") or e["title"]),
            dry_hint="dry run: nothing was sent; add --apply to create and update the issues")
    return 1 if errors else 0


def cmd_pull(args: argparse.Namespace, client: Optional[TrackerClient] = None) -> int:
    ws, schema = _workspace(args)
    all_rows = _load_rows(ws, schema)
    rows = [r for r in _select(all_rows, args, None) if r.get_str("Status").lower() not in RETIRED]
    if not rows:
        print("no requirements selected")
        return 0
    client = client or make_client(args.tracker, args)
    try:
        matches = client.find_many([r.get_str("ID") for r in rows])
    except TrackerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    register_path = ws / "requirements.csv"
    report = []
    changes: Dict[str, str] = {}
    for row in rows:
        rid = row.get_str("ID")
        current = row.get_str("Status").lower()
        issue, candidates = pick_issue(rid, matches.get(rid, []))
        entry = {"id": rid, "issue": issue.key if issue else "", "tracker_status": issue.status if issue else "",
                 "mapped": "", "current": current}
        if issue is None:
            entry["action"] = "ambiguous" if candidates else "no issue"
            if candidates:
                entry["detail"] = "several issues hold the ID: " + ", ".join(c.key for c in candidates)
            report.append(entry)
            continue
        mapped, why = map_status(args.tracker, issue, schema)
        if mapped is None:
            entry.update(action="skipped", detail=why)
        else:
            entry["mapped"] = mapped
            if mapped.lower() == current:
                entry["action"] = "unchanged"
            elif not args.ignore_lifecycle and not transition_allowed(current, mapped.lower(), schema):
                entry.update(action="skipped", detail=f"lifecycle does not allow {current} -> {mapped} "
                                                      "(--ignore-lifecycle overrides)")
            elif Path(row.file).resolve() != register_path.resolve():
                entry.update(action="skipped", detail=f"row lives in {Path(row.file).name}, not requirements.csv")
            else:
                entry["action"] = "update" if not args.apply else "updated"
                changes[rid] = mapped
        report.append(entry)
    if args.apply and changes:
        table = reqio.read_table(register_path)
        updated = []
        for row in table.rows:
            if row.get_str("ID") in changes:
                row["Status"] = changes[row.get_str("ID")]
            updated.append(row)
        reqio.write_csv(register_path, updated, table.columns)
    _report(args, report, ["ID", "Issue", "Tracker status", "Mapped", "Current", "Action"],
            lambda e: (e["id"], e["issue"] or "-", e["tracker_status"] or "-", e["mapped"] or "-", e["current"],
                       e["action"] + (f" ({e['detail']})" if e.get("detail") else "")),
            dry_hint="dry run: requirements.csv was not changed; add --apply to write the Status changes")
    if args.apply:
        print(f"{len(changes)} Status value(s) written to {register_path}" if changes else "requirements.csv unchanged")
    return 0


def _report(args: argparse.Namespace, report: List[Dict], headers: Sequence[str],
            row_fn: Callable[[Dict], Sequence[str]], dry_hint: str) -> None:
    if args.format == "json":
        print(json.dumps({"tracker": args.tracker, "apply": bool(args.apply), "items": report},
                         indent=2, ensure_ascii=False))
        return
    _print_table(headers, [row_fn(e) for e in report])
    counts: Dict[str, int] = {}
    for e in report:
        counts[e["action"]] = counts.get(e["action"], 0) + 1
    print("\n" + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    if not args.apply:
        print(dry_hint)


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        description="Sync requirements with GitHub Issues (gh CLI), Jira Cloud or Azure DevOps: plan offline, "
                    "push issues (title '<ID>: <Title>', managed body block) and pull Status back.",
        epilog="Dry run unless --apply. Jira: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT. "
               "Azure DevOps: ADO_ORG_URL, ADO_PROJECT, ADO_PAT. Exit codes: 0 ok, 1 tracker call failed, "
               "2 usage or configuration error.",
    )
    sub = parser.add_subparsers(dest="action", metavar="{plan,push,pull}")
    sub.required = True
    for name, help_text in (("plan", "show what push would send (no network)"),
                            ("push", "create or update one issue per requirement"),
                            ("pull", "refresh Status in requirements.csv from the tracker")):
        p = sub.add_parser(name, help=help_text, description=help_text)
        p.add_argument("--tracker", choices=TRACKERS, required=True)
        p.add_argument("--ids", metavar="ID", nargs="+", action="extend", help="only these requirement IDs")
        p.add_argument("--status", metavar="S", nargs="+", action="extend",
                       help="requirements with these statuses (default: agreed for plan/push; all but "
                            "withdrawn and rejected for pull)")
        p.add_argument("--format", choices=("text", "json"), default="text")
        p.add_argument("--repo", metavar="OWNER/REPO", help="GitHub repository (default: the current one)")
        p.add_argument("--issue-type", metavar="TYPE",
                       help="Jira issue type (default Story) or Azure DevOps work item type (default User Story)")
        p.add_argument("--workspace", metavar="DIR", help="workspace folder (default: <repo root>/requirements)")
        p.add_argument("--schema", metavar="FILE", help="schema.json to use (default: <workspace>/schema.json)")
        if name in ("plan", "push"):
            p.add_argument("--label", metavar="L", nargs="+", action="extend",
                           help="labels (GitHub labels must exist), Jira labels or Azure DevOps tags to add")
        if name == "plan":
            p.add_argument("--out", metavar="FILE", help="also write the plan as JSON to FILE")
        else:
            p.add_argument("--apply", action="store_true", help="make the changes (default: dry run)")
        if name == "pull":
            p.add_argument("--ignore-lifecycle", action="store_true",
                           help="apply mapped statuses even when the lifecycle does not allow the transition")
    return parser


def run(args: argparse.Namespace, client: Optional[TrackerClient] = None) -> int:
    handlers = {"plan": cmd_plan, "push": cmd_push, "pull": cmd_pull}
    try:
        return handlers[args.action](args, client)
    except (UsageError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
