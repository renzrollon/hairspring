#!/usr/bin/env python3
# VENDORED from packages/re-lint/src/re_lint/issues.py by tools/vendor_scripts.py; do not edit.
# Change the package module, then run `python3 tools/vendor_scripts.py` to refresh this copy.
"""Plan, push and pull requirement issues in GitHub Issues, Jira or Azure DevOps.

Usage::

    re-lint issues plan --tracker github|jira|ado [--ids ...] [--status S ...] [--format text|json] [--out FILE]
    re-lint issues push --tracker github|jira|ado [--ids ...] [--status S ...] [--apply] [--label L ...]
    re-lint issues pull --tracker github|jira|ado [--ids ...] [--status S ...] [--apply]

The rules follow ``skills/integration/issue-sync/references/sync-rules.md``.

* ``plan`` never calls the tracker. Every row gets an action: ``create-or-match`` (selected, no
  tracker reference in ``Links``), ``update`` (selected, reference present), ``skip`` (not
  selected) or ``move-on-board`` (withdrawn, rejected or deferred with a reference: a person
  closes it). Selection: ``--ids``, else ``--status`` (default ``agreed``).
* ``push`` (dry run unless ``--apply``) matches issues by the title prefix ``<ID>: `` (two
  candidates: ``ambiguous``, untouched; a reference in ``Links`` with no matching issue:
  ``missing-issue``, never a duplicate). Title: ``<ID>: <Title, or the first 80 characters of
  Text>``. The body block between ``<!-- re-skills:begin -->`` and ``<!-- re-skills:end -->``
  follows the skill's ``assets/issue-body.md``; only that span is replaced, and an issue whose
  markers are missing or doubled is left alone (``markers-missing``). Jira descriptions are ADF
  (the markers are visible paragraphs); Azure DevOps descriptions are HTML. Withdrawn, rejected
  and deferred rows are never pushed. ``--apply`` records the tracker reference
  (``github:<owner>/<repo>#<n>``, ``jira:<KEY>``, ``ado:<id>``) in ``Links``.
* ``pull`` (dry run unless ``--apply``) maps each linked issue's status through
  ``schema.json`` -> ``issues.status_map.<tracker>`` (case-insensitive; GitHub issues closed as
  not planned use ``closed:not_planned``, default ``rejected``, never ``closed``) and writes
  ``Status`` only for class ``update``: an allowed move in ``schema.lifecycle.transitions``.
  ``needs-person`` (draft/proposed -> agreed needs a named person), ``needs-evidence`` (verified
  without a test, inspection or demonstration in ``Links`` or ``trace/trace.csv``),
  ``skip-coarse-map``, ``conflict``, ``conflict-lifecycle`` (withdrawn/rejected/deferred rows are
  never overwritten), ``unmapped`` and ``missing-issue`` are reported and never written.

Credentials (never printed, never on a command line):

* GitHub: the ``gh`` CLI, logged in (``gh auth login``); ``--repo OWNER/REPO`` or ``GH_REPO``.
* Jira Cloud (REST v3): ``JIRA_BASE_URL`` (used as given, gateway URLs work), ``JIRA_EMAIL``,
  ``JIRA_API_TOKEN``, ``JIRA_PROJECT``.
* Azure DevOps (REST 7.1): ``ADO_ORG_URL``, ``ADO_PROJECT``, ``ADO_PAT``.

Exit codes: 0 nothing to report, 1 a finding class or a failed tracker call, 2 usage or
configuration error.
"""
from __future__ import annotations

import argparse
import base64
import copy
import datetime
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
LIFECYCLE_DECISIONS = {"withdrawn", "rejected", "deferred"}
PROGRESSION = ["draft", "proposed", "agreed", "implemented", "verified"]
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

TYPE_LABELS = {"F": "F functional", "Q": "Q quality requirement", "C": "C constraint"}
_REF = re.compile(r"^(?:github:[^\s#]*#\d+|jira:[A-Z][A-Z0-9_]*-\d+|ado:\d+)$")


def tracker_refs(links: str) -> List[str]:
    return [t for t in re.split(r"[\s,;]+", links or "") if _REF.match(t)]


def block_data(row: reqio.Row, ctx: Dict) -> Dict:
    """The managed block's content (``assets/issue-body.md`` of the issue-sync skill)."""
    rid = row.get_str("ID")
    attrs = [("Source", _one_line(row.get_str("Source"))), ("Rationale", _one_line(row.get_str("Rationale"))),
             ("Verification", _one_line(row.get_str("Verification")) or "TBD")]
    if "Owner" in row:
        attrs.append(("Owner", _one_line(row.get_str("Owner"))))
    sources = []
    for kind in ("source", "stakeholder", "interview"):
        try:
            pattern = reqio.id_prefix_regex(kind, ctx["schema"])
        except KeyError:
            continue
        prefix = str(((ctx["schema"].get("ids") or {}).get(kind) or {}).get("prefix", ""))
        for match in pattern.finditer(row.get_str("Source")):
            sid = prefix + match.group(1)
            title = ctx["source_titles"].get(sid)
            entry = f"{sid} ({title})" if title else sid
            if entry not in sources:
                sources.append(entry)
    links = [t for t in re.split(r"[\s,;]+", row.get_str("Links")) if t and not _REF.match(t)]
    traced = ctx["trace"].get(rid, {})
    tests_code = [f"`{v}` (test)" for v in traced.get("test", [])[:10]] + \
                 [f"`{v}` (code)" for v in traced.get("code", [])[:10]]
    return {
        "id": rid,
        "header": f"{TYPE_LABELS.get(row.get_str('Type').upper(), row.get_str('Type') or 'requirement')} · priority "
                  f"{row.get_str('Priority') or 'TBD'} · register status at last push: {row.get_str('Status')}",
        "text": _one_line(row.get_str("Text")),
        "attributes": attrs,
        "acs": ctx["acs"].get(rid, []),
        "trace": [("Register", f"`{ctx['register']}` ({rid})"),
                  ("Sources", ", ".join(sources) or "none"),
                  ("Decisions and links", " ".join(links) or "none"),
                  ("Tests and code", ", ".join(tests_code) or "not traced yet")],
        "footer": f"Managed by re-skills issue-sync. Change the requirement in `{ctx['register']}` and push again: "
                  "edits inside this block are overwritten. Discuss outside the block or in comments.",
    }


class MarkdownBody:
    """GitHub: Markdown with HTML-comment markers."""

    name = "markdown"
    _region = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)

    def render(self, data: Dict) -> str:
        out = [BEGIN, f"**{data['id']}** · {data['header']}", "", f"> {data['text']}", "",
               "| Attribute | Value |", "| --- | --- |"]
        out += [f"| {k} | {_md_cell(v)} |" for k, v in data["attributes"]]
        out += ["", "**Acceptance criteria**", ""]
        out += [f"- {ac}" for ac in data["acs"]] or ["- none recorded"]
        out += ["", "**Trace**", ""]
        out += [f"- {k}: {v}" for k, v in data["trace"]]
        out += ["", f"_{data['footer']}_", END]
        return "\n".join(out)

    def markers(self, body: Any) -> Tuple[int, int]:
        text = body or ""
        return text.count(BEGIN), text.count(END)

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
        acs = "".join(f"<li>{e(ac)}</li>" for ac in data["acs"]) or "<li>none recorded</li>"
        trace = "".join(f"<li>{e(k)}: {e(v)}</li>" for k, v in data["trace"])
        return "".join([
            BEGIN, "<div>", f"<p><strong>{e(data['id'])}</strong> · {e(data['header'])}</p>",
            f"<blockquote>{e(data['text'])}</blockquote>",
            f"<table><tr><th>Attribute</th><th>Value</th></tr>{rows}</table>",
            f"<p><strong>Acceptance criteria</strong></p><ul>{acs}</ul>",
            f"<p><strong>Trace</strong></p><ul>{trace}</ul>",
            f"<p><em>{e(data['footer'])}</em></p>", "</div>", END])

    def markers(self, body: Any) -> Tuple[int, int]:
        text = body or ""
        count = lambda word: len(re.findall(rf"(?:<!--|&lt;!--)\s*re-skills:{word}\s*(?:-->|--&gt;)", text, re.I))
        return count("begin"), count("end")

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
    """Jira Cloud: Atlassian Document Format; the markers are their own (visible) paragraphs."""

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

    def _bullets(self, items: Sequence[str]) -> Dict:
        return {"type": "bulletList", "content": [
            {"type": "listItem", "content": [self._para(self._t(item))]} for item in items]}

    def nodes(self, data: Dict) -> List[Dict]:
        return [
            self._para(self._t(BEGIN)),
            self._para(self._t(data["id"], "strong"), self._t(f" · {data['header']}")),
            {"type": "blockquote", "content": [self._para(self._t(data["text"] or " "))]},
            self._bullets([f"{k}: {v}" for k, v in data["attributes"]]),
            self._para(self._t("Acceptance criteria", "strong")),
            self._bullets(list(data["acs"]) or ["none recorded"]),
            self._para(self._t("Trace", "strong")),
            self._bullets([f"{k}: {v}" for k, v in data["trace"]]),
            self._para(self._t(data["footer"], "em")),
            self._para(self._t(END)),
        ]

    def _bounds(self, content: List[Any]) -> Optional[Tuple[int, int]]:
        begin = next((i for i, n in enumerate(content) if _one_line(self._text(n)) == BEGIN), None)
        if begin is None:
            return None
        end = next((i for i in range(begin + 1, len(content)) if _one_line(self._text(content[i])) == END), None)
        return (begin, end) if end is not None else None

    def markers(self, body: Any) -> Tuple[int, int]:
        content = list(body.get("content") or []) if isinstance(body, dict) else []
        texts = [_one_line(self._text(n)) for n in content]
        return texts.count(BEGIN), texts.count(END)

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


def body_is_empty(body: Any) -> bool:
    if body is None:
        return True
    if isinstance(body, dict):
        return not _one_line(AdfBody._text(body))
    return not re.sub(r"<[^>]+>", "", str(body)).strip()


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
    """Tests (verified-by) and code (implemented-by) per requirement from ``trace/trace.csv``."""
    path = ws / "trace" / "trace.csv"
    out: Dict[str, Dict[str, List[str]]] = {}
    if not path.is_file():
        return out
    try:
        table = reqio.read_table(path)
    except (OSError, UnicodeDecodeError, ValueError):
        return out
    for row in table.rows:
        relation = row.get_str("Relation")
        kind = {"verified-by": "test", "implemented-by": "code"}.get(relation)
        if kind is None:
            continue
        rid = row.get_str("From").split(".AC", 1)[0]
        values = out.setdefault(rid, {}).setdefault(kind, [])
        if row.get_str("To") and row.get_str("To") not in values:
            values.append(row.get_str("To"))
    return out


def _acceptance_criteria(ws: Path, schema: Dict) -> Dict[str, List[str]]:
    """``R-nnn.ACn: <criterion>`` lines per requirement from ``stories/*.md``."""
    spec = (schema.get("ids") or {}).get("requirement") or {"prefix": "R-", "digits": 3}
    ac = rf"({re.escape(str(spec.get('prefix', 'R-')))}\d{{{int(spec.get('digits', 3))},}})\.AC(\d+)"
    found: Dict[str, Dict[int, str]] = {}
    stories = ws / "stories"
    for path in sorted(stories.glob("*.md")) if stories.is_dir() else []:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            tables = reqio.read_tables(path)
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        for table in tables:
            if "ID" not in table.columns:
                continue
            text_col = next((c for c in table.columns if c.lower().startswith("acceptance")), table.columns[-1])
            for row in table.rows:
                m = re.match(rf"^{ac}$", row.get_str("ID"))
                if m:
                    found.setdefault(m.group(1), {}).setdefault(int(m.group(2)), _one_line(row.get_str(text_col)))
        for i, line in enumerate(lines):
            if line.lstrip().startswith("|"):
                continue
            label = re.match(rf"^\s*(?:[-*+]\s+)?(?:\*\*|__)\s*{ac}\s*:?\s*(.*?)\s*(?:\*\*|__)", line)
            if label:
                steps = []
                for nxt in lines[i + 1:]:
                    step = re.match(r"^\s*[-*+]\s+(?:\*\*|__)?(Given|When|Then|And|But)(?:\*\*|__)?:?\s+(.*)$", nxt, re.I)
                    if not step:
                        if nxt.strip() or steps:
                            break
                        continue
                    steps.append(f"{step.group(1).capitalize()} {step.group(2).strip()}")
                text = (label.group(3) + ": " if label.group(3) else "") + "; ".join(steps)
                found.setdefault(label.group(1), {}).setdefault(int(label.group(2)), _one_line(text))
                continue
            item = re.match(rf"^\s*[-*+]\s+{ac}\s*:\s*(.+)$", line)
            if item:
                found.setdefault(item.group(1), {}).setdefault(int(item.group(2)), _one_line(item.group(3)))
    return {rid: [f"{rid}.AC{n}: {text}" for n, text in sorted(items.items())] for rid, items in found.items()}


def _source_titles(ws: Path) -> Dict[str, str]:
    path = ws / "sources.csv"
    if not path.is_file():
        return {}
    try:
        table = reqio.read_table(path)
    except (OSError, UnicodeDecodeError, ValueError):
        return {}
    col = next((c for c in ("Title", "Source", "Name", "Description") if c in table.columns), None)
    return {r.get_str("ID"): _one_line(r.get_str(col)) for r in table.rows if col and r.get_str(col)}


def _context(ws: Path, schema: Dict) -> Dict:
    register = os.path.relpath(ws / "requirements.csv", reqio.find_repo_root(ws)).replace(os.sep, "/")
    return {"schema": schema, "register": register, "trace": _trace(ws), "acs": _acceptance_criteria(ws, schema),
            "source_titles": _source_titles(ws)}


def _selection(rows: "OrderedDict[str, reqio.Row]", args: argparse.Namespace) -> Tuple[set, bool]:
    ids = _split_list(getattr(args, "ids", None))
    if ids:
        unknown = [i for i in ids if i not in rows]
        if unknown:
            raise UsageError(f"unknown requirement ID(s): {', '.join(unknown)}")
        return set(ids), True
    statuses = {s.lower() for s in _split_list(getattr(args, "status", None))} or {"agreed"}
    return {rid for rid, r in rows.items() if r.get_str("Status").lower() in statuses}, False


def _status_map(tracker: str, schema: Dict) -> Dict[str, str]:
    status_map = ((schema.get("issues") or {}).get("status_map") or {}).get(tracker) or {}
    return {str(k).strip().lower(): str(v) for k, v in status_map.items()}


def map_status(tracker: str, issue: Issue, schema: Dict) -> Tuple[Optional[str], str]:
    """(requirement status, the key that matched or why nothing matched)."""
    lowered = _status_map(tracker, schema)
    for key in issue.status_keys():
        if key.strip().lower() in lowered:
            return lowered[key.strip().lower()], key
        if key == "closed:not_planned":  # never falls back to "closed" (which means implemented)
            return "rejected", key
    keys = issue.status_keys()
    return None, f"{keys[0]!r} is not in issues.status_map.{tracker}"


def initial_tracker_status(tracker: str, status: str, schema: Dict) -> Optional[str]:
    """The first tracker status that maps to ``status`` (what a new issue is expected to start in)."""
    status_map = ((schema.get("issues") or {}).get("status_map") or {}).get(tracker) or {}
    return next((str(k) for k, v in status_map.items() if str(v).lower() == status.lower() and ":" not in str(k)), None)


def _has_evidence(row: reqio.Row, trace: Dict[str, Dict[str, List[str]]]) -> bool:
    if trace.get(row.get_str("ID"), {}).get("test"):
        return True
    return bool(re.search(r"test|inspection|demonstration|review", row.get_str("Links"), re.I))


def classify_pull(row: reqio.Row, mapped: Optional[str], schema: Dict, trace: Dict) -> Tuple[str, str]:
    """Pull guard class (``sync-rules.md``) and a one-line reason. Only ``update`` is written."""
    current = row.get_str("Status").lower()
    if mapped is None:
        return "unmapped", ""
    target = mapped.lower()
    if current in LIFECYCLE_DECISIONS:
        if target == current:
            return "unchanged", ""
        return "conflict-lifecycle", f"{current} in the register but the issue maps to {target}; a person decides"
    if target == current:
        return "unchanged", ""
    if target == "agreed" and current in ("draft", "proposed"):
        return "needs-person", "agreed needs a named person in Source, Owner or a decision record"
    if target == "verified" and not _has_evidence(row, trace):
        return "needs-evidence", "verified needs a test, inspection or demonstration in Links or trace.csv"
    transitions = ((schema.get("lifecycle") or {}).get("transitions") or {})
    if target in [str(t).lower() for t in transitions.get(current) or []]:
        return "update", ""
    if current in PROGRESSION and target in PROGRESSION and PROGRESSION.index(target) < PROGRESSION.index(current):
        return "skip-coarse-map", f"{current} -> {target} is not a lifecycle transition (the tracker map is coarser)"
    return "conflict", f"{current} -> {target} is not a lifecycle transition; work went ahead without it"


def _reference(tracker: str, issue: Issue, repo: Optional[str]) -> str:
    if tracker == "github":
        m = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", issue.url or "")
        if m:
            return f"github:{m.group(1)}#{m.group(2)}"
        return f"github:{repo or ''}#{issue.key}"
    return f"{tracker}:{issue.key}"


def _record_references(ws: Path, refs: Dict[str, str]) -> List[str]:
    """Append tracker references to ``Links`` in requirements.csv; returns the IDs changed."""
    path = ws / "requirements.csv"
    if not refs or not path.is_file():
        return []
    table = reqio.read_table(path)
    columns = list(table.columns)
    if "Links" not in columns:
        columns.append("Links")
    changed = []
    rows = []
    for row in table.rows:
        ref = refs.get(row.get_str("ID"))
        if ref and ref not in row.get_str("Links").split():
            row["Links"] = (row.get_str("Links") + " " + ref).strip()
            changed.append(row.get_str("ID"))
        rows.append(row)
    if changed:
        reqio.write_csv(path, rows, columns)
    return changed


def _target(tracker: str, args: argparse.Namespace, env: Optional[Dict[str, str]] = None) -> str:
    env = dict(os.environ if env is None else env)
    if tracker == "github":
        return getattr(args, "repo", None) or env.get("GH_REPO") or "current repository"
    if tracker == "jira":
        return env.get("JIRA_PROJECT") or "?"
    org = env.get("ADO_ORG_URL", "").rstrip("/").rsplit("/", 1)[-1]
    return f"{org}/{env.get('ADO_PROJECT', '')}".strip("/") or "?"


# --------------------------------------------------------------------------- commands


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _emit(args: argparse.Namespace, command: str, network: str, actions: List[Dict], summary_note: str,
          footer: str) -> None:
    summary: "OrderedDict[str, int]" = OrderedDict()
    for a in actions:
        summary[a["action"]] = summary.get(a["action"], 0) + 1
    target = _target(args.tracker, args)
    if args.format == "json":
        print(json.dumps({"command": command, "tracker": args.tracker, "target": target,
                          "network": network != "no", "generated": _now(), "apply": bool(getattr(args, "apply", False)),
                          "actions": actions, "summary": summary}, indent=2, ensure_ascii=False))
        return
    label = {"github": "github", "jira": "jira project", "ado": "ado"}[args.tracker]
    print(f"Tracker: {label} {target} · Command: {command} · Network: {network} · Generated: {_now()}")
    print()
    print("| ID | Action | Issue | Title | Status | Notes |")
    print("| --- | --- | --- | --- | --- | --- |")
    for a in actions:
        print(f"| {a['id']} | {a['action']} | {a.get('issue') or '-'} | {_md_cell(a['title'])} | "
              f"{_md_cell(a.get('status_text', a.get('status', '')))} | {_md_cell(a.get('reason', ''))} |")
    print()
    print("Summary: " + (", ".join(f"{v} {k}" for k, v in summary.items()) or "nothing to do") + summary_note)
    print()
    print(footer)


def _decisions(row: reqio.Row) -> str:
    ids = [t for t in re.split(r"[\s,;]+", row.get_str("Links")) if re.match(r"^(?:RDR|CR|D)-\d+$", t)]
    return f" ({', '.join(ids)})" if ids else ""


def cmd_plan(args: argparse.Namespace, client: Optional[TrackerClient] = None) -> int:
    ws, schema = _workspace(args)
    rows = _load_rows(ws, schema)
    selected, named = _selection(rows, args)
    ctx = _context(ws, schema)
    actions: List[Dict] = []
    for rid, row in rows.items():
        status = row.get_str("Status").lower()
        refs = tracker_refs(row.get_str("Links"))
        ref = next((r for r in refs if r.startswith(args.tracker + ":")), None)
        entry = {"id": rid, "issue": ref, "title": issue_title(row), "status": status, "tracker_status": None}
        if status in LIFECYCLE_DECISIONS:
            if ref:
                entry.update(action="move-on-board", status_text=f"{status} -> (manual)",
                             reason=f"{status} in the register; push does not touch it; close {ref.split(':', 1)[1]} "
                                    f"by hand with the reason{_decisions(row)}")
                actions.append(entry)
            continue
        if rid not in selected:
            entry.update(action="skip", status_text=status,
                         reason=f"Status={status}; name it in --ids to push it")
            actions.append(entry)
            continue
        if ref:
            entry.update(action="update", status_text=f"{status} -> (tracker owns status)",
                         reason="refresh title and managed block; tracker owns status")
        else:
            initial = initial_tracker_status(args.tracker, status, schema)
            entry.update(action="create-or-match", tracker_status=initial,
                         status_text=f"{status} -> {initial or '(initial state)'}",
                         reason=f"no tracker reference in Links; push matches a title starting with '{rid}: ' "
                                "before creating")
        entry["body"] = MarkdownBody().render(block_data(row, ctx))
        actions.append(entry)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {"command": "plan", "tracker": args.tracker, "target": _target(args.tracker, args),
                   "network": False, "generated": _now(), "actions": actions}
        with open(out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    push_ids = ",".join(a["id"] for a in actions if a["action"] in ("create-or-match", "update"))
    _emit(args, "plan", "no", [{k: v for k, v in a.items() if k != "body"} for a in actions] if args.format != "json"
          else actions, " (push)",
          f"Nothing has been written. To apply: `push --tracker {args.tracker} --ids {push_ids} --apply`."
          if push_ids else "Nothing has been written.")
    return 0


PUSH_FINDINGS = {"ambiguous", "markers-missing", "missing-issue", "move-on-board", "error"}
PULL_FINDINGS = {"ambiguous", "needs-person", "needs-evidence", "skip-coarse-map", "conflict", "conflict-lifecycle",
                 "unmapped", "missing-issue"}


def cmd_push(args: argparse.Namespace, client: Optional[TrackerClient] = None) -> int:
    ws, schema = _workspace(args)
    rows = _load_rows(ws, schema)
    selected, named = _selection(rows, args)
    if not selected:
        print("no requirements selected")
        return 0
    client = client or make_client(args.tracker, args)
    ctx = _context(ws, schema)
    labels = _split_list(args.label)
    ids = [rid for rid in rows if rid in selected]
    try:
        matches = client.find_many(ids)
    except TrackerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    actions: List[Dict] = []
    new_refs: Dict[str, str] = {}
    for rid in ids:
        row = rows[rid]
        status = row.get_str("Status").lower()
        title = issue_title(row)
        refs = [r for r in tracker_refs(row.get_str("Links")) if r.startswith(args.tracker + ":")]
        issue, candidates = pick_issue(rid, matches.get(rid, []))
        entry: Dict[str, Any] = {"id": rid, "title": title, "status": status, "status_text": status,
                                 "issue": refs[0] if refs else None, "reason": ""}
        if issue is None and candidates:
            entry.update(action="ambiguous", reason="several issues hold the ID: " + ", ".join(c.key for c in candidates))
            actions.append(entry)
            continue
        if status in LIFECYCLE_DECISIONS:
            if issue is not None or refs:
                ref = _reference(args.tracker, issue, args.repo) if issue else refs[0]
                entry.update(action="move-on-board", issue=ref,
                             reason=f"{status} in the register; not pushed; close it by hand with the "
                                    f"reason{_decisions(row)}")
            else:
                entry.update(action="skip", reason=f"Status={status}: never pushed")
            actions.append(entry)
            continue
        if issue is None and refs:
            entry.update(action="missing-issue", reason=f"{refs[0]} is in Links but no issue title starts with "
                                                        f"'{rid}: '; fix the reference or the title")
            actions.append(entry)
            continue
        if issue is not None:
            entry["issue"] = _reference(args.tracker, issue, args.repo)
            begins, ends = client.body.markers(issue.body)
            if (begins, ends) != (1, 1) and not body_is_empty(issue.body):
                entry.update(action="markers-missing",
                             reason="managed block markers missing or doubled; body left alone (restore the block "
                                    "from `plan` and push again)")
                actions.append(entry)
                continue
        body = client.body.merge(issue.body if issue else None, block_data(row, ctx))
        if issue is None:
            action, reason = "create", "no issue holds the ID yet"
        else:
            same = client.body.block_text(issue.body) == client.body.block_text(body)
            missing_labels = [l for l in labels if l not in issue.labels]
            if same and issue.title == title and not missing_labels:
                action, reason = "unchanged", ""
            else:
                action, reason = "update", "title and managed block refreshed"
        entry.update(action=action, reason=reason)
        if args.apply and action in ("create", "update"):
            try:
                done = client.create(title, body, labels) if action == "create" else client.update(issue, title, body, labels)
                entry.update(action=action + "d", issue=_reference(args.tracker, done, args.repo))
            except TrackerError as exc:
                entry.update(action="error", reason=str(exc))
        if args.apply and entry["action"] in ("created", "updated", "unchanged") and entry["issue"] \
                and entry["issue"] not in row.get_str("Links").split():
            new_refs[rid] = entry["issue"]
        actions.append(entry)
    recorded = _record_references(ws, new_refs) if args.apply else []
    footer = ("Nothing has been written. To apply: `push --tracker {} --ids {} --apply`.".format(
        args.tracker, ",".join(a["id"] for a in actions if a["action"] in ("create", "update"))) if not args.apply
              else "Nothing was deleted. " + (f"`requirements.csv`: Links now holds {', '.join(new_refs[r] for r in recorded)}."
                                              if recorded else "`requirements.csv` unchanged."))
    _emit(args, "push" if args.apply else "push dry run", "read-write" if args.apply else "read-only", actions,
          " (push)", footer)
    return 1 if any(a["action"] in PUSH_FINDINGS for a in actions) else 0


def cmd_pull(args: argparse.Namespace, client: Optional[TrackerClient] = None) -> int:
    ws, schema = _workspace(args)
    rows = _load_rows(ws, schema)
    ids = _split_list(args.ids)
    unknown = [i for i in ids if i not in rows]
    if unknown:
        raise UsageError(f"unknown requirement ID(s): {', '.join(unknown)}")
    wanted = [rid for rid in rows if not ids or rid in ids]
    statuses = {s.lower() for s in _split_list(args.status)}
    if statuses:
        wanted = [rid for rid in wanted if rows[rid].get_str("Status").lower() in statuses]
    if not wanted:
        print("no requirements selected")
        return 0
    client = client or make_client(args.tracker, args)
    trace = _trace(ws)
    try:
        matches = client.find_many(wanted)
    except TrackerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    register_path = (ws / "requirements.csv").resolve()
    actions: List[Dict] = []
    changes: Dict[str, str] = {}
    for rid in wanted:
        row = rows[rid]
        current = row.get_str("Status").lower()
        refs = [r for r in tracker_refs(row.get_str("Links")) if r.startswith(args.tracker + ":")]
        issue, candidates = pick_issue(rid, matches.get(rid, []))
        entry: Dict[str, Any] = {"id": rid, "title": issue_title(row), "status": current, "tracker_status": None,
                                 "issue": refs[0] if refs else None, "mapped": None, "reason": ""}
        if issue is None:
            if candidates:
                entry.update(action="ambiguous", status_text=current,
                             reason="several issues hold the ID: " + ", ".join(c.key for c in candidates))
            elif refs:
                entry.update(action="missing-issue", status_text=current,
                             reason=f"{refs[0]} is in Links but no issue title starts with '{rid}: '")
            else:
                continue  # not linked: nothing to pull
            actions.append(entry)
            continue
        entry["issue"] = _reference(args.tracker, issue, getattr(args, "repo", None))
        entry["tracker_status"] = issue.status
        mapped, why = map_status(args.tracker, issue, schema)
        entry["mapped"] = mapped
        action, reason = classify_pull(row, mapped, schema, trace)
        if action == "unmapped":
            reason = f"{why}; add it with attribute-schema"
        if action == "update" and Path(row.file).resolve() != register_path:
            action, reason = "skip", f"row lives in {Path(row.file).name}, not requirements.csv"
        entry["status_text"] = f"{current} -> {issue.status}" + (f" ({mapped})" if mapped else "")
        if action == "update":
            reason = "written with --apply" if not args.apply else "written"
            changes[rid] = mapped
        entry.update(action=action, reason=reason)
        actions.append(entry)
    if args.apply and changes:
        table = reqio.read_table(register_path)
        updated = []
        for row in table.rows:
            if row.get_str("ID") in changes:
                row["Status"] = changes[row.get_str("ID")]
            updated.append(row)
        reqio.write_csv(register_path, updated, table.columns)
    written = sum(1 for a in actions if a["action"] == "update")
    kept = sum(1 for a in actions if a["action"] not in ("update", "unchanged"))
    if args.apply:
        footer = (f"`requirements.csv`: Status changed for {', '.join(changes)}; no other cell changed."
                  if changes else "`requirements.csv` unchanged.")
    else:
        footer = f"Nothing has been written. To apply: `pull --tracker {args.tracker} --apply`."
    _emit(args, "pull" if args.apply else "pull dry run", "read-only", actions,
          f" | {written} update, {sum(1 for a in actions if a['action'] == 'unchanged')} unchanged, "
          f"{kept} not written (pull)", footer)
    return 1 if any(a["action"] in PULL_FINDINGS for a in actions) else 0


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        description="Sync requirements with GitHub Issues (gh CLI), Jira Cloud or Azure DevOps: plan offline, "
                    "push issues (title '<ID>: <Title>', managed body block) and pull Status back.",
        epilog="Dry run unless --apply. Jira: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT. "
               "Azure DevOps: ADO_ORG_URL, ADO_PROJECT, ADO_PAT. GitHub: gh (GH_REPO or --repo selects the "
               "repository). Exit codes: 0 nothing to report, 1 a finding (ambiguous, markers-missing, "
               "needs-person, conflict, ...) or a failed call, 2 usage or configuration error.",
    )
    sub = parser.add_subparsers(dest="action", metavar="{plan,push,pull}")
    sub.required = True
    for name, help_text in (("plan", "show what push would do (no network)"),
                            ("push", "create or update one issue per requirement"),
                            ("pull", "refresh Status in requirements.csv from the tracker, guarded by the lifecycle")):
        p = sub.add_parser(name, help=help_text, description=help_text)
        p.add_argument("--tracker", choices=TRACKERS, required=True)
        p.add_argument("--ids", metavar="ID", nargs="+", action="extend", help="only these requirement IDs")
        p.add_argument("--status", metavar="S", nargs="+", action="extend",
                       help="requirements with these statuses (default: agreed for plan/push; every linked row "
                            "for pull)")
        p.add_argument("--format", choices=("text", "json"), default="text")
        p.add_argument("--repo", metavar="OWNER/REPO", help="GitHub repository (default: GH_REPO or the current one)")
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
