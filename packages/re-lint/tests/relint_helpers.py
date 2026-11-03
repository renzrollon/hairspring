"""Helpers shared by the re-lint tests (fixtures live in conftest.py).

Importing this module puts ``src/`` first on ``sys.path``, so the tests run against the source
tree whether or not the package is installed.
"""
from __future__ import annotations

import csv
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_ROOT.parent.parent
SRC = PACKAGE_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

HEADER = ["ID", "Type", "Text", "Source", "Priority", "Status", "Rationale"]
GOOD_TEXT = "WHEN the POS sends a completed purchase event, the loyalty service shall create a pending points transaction."


def make_row(rid: str = "R-001", text: str = GOOD_TEXT, **attrs: str) -> Dict[str, str]:
    row = {"ID": rid, "Type": "F", "Text": text, "Source": "S-01", "Priority": "must",
           "Status": "draft", "Rationale": "Core earning flow."}
    row.update(attrs)
    return row


def csv_text(rows: Iterable[Dict[str, str]], header: Optional[List[str]] = None) -> str:
    header = header or HEADER
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow([row.get(c, "") for c in header])
    return buf.getvalue()


class Workspace:
    """A temporary repo with a ``requirements/`` workspace."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.ws = root / "requirements"
        self.ws.mkdir(parents=True, exist_ok=True)

    def write(self, rel: str, content: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def register(self, rows: Iterable[Dict[str, str]], header: Optional[List[str]] = None,
                 name: str = "requirements/requirements.csv") -> Path:
        return self.write(name, csv_text(rows, header))

    def schema(self, data: Dict) -> Path:
        return self.write("requirements/schema.json", json.dumps(data))

    def git(self, *args: str) -> str:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
        proc = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, env=env)
        assert proc.returncode == 0, proc.stderr
        return proc.stdout


def run_cli(module, argv: List[str], capsys) -> "Result":
    code = module.main(argv)
    out, err = capsys.readouterr()
    return Result(code, out, err)


class Result:
    def __init__(self, code: int, out: str, err: str) -> None:
        self.code = code
        self.out = out
        self.err = err

    def json(self):
        return json.loads(self.out)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Result(code={self.code}, out={self.out!r}, err={self.err!r})"
