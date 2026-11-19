"""Fixtures for the re-lint tests; helpers live in relint_helpers.py."""
from __future__ import annotations

import shutil

import pytest

from relint_helpers import Workspace


@pytest.fixture
def workspace(tmp_path, monkeypatch) -> Workspace:
    root = tmp_path / "repo"
    root.mkdir()
    monkeypatch.chdir(root)
    return Workspace(root)


@pytest.fixture
def git_available() -> bool:
    if shutil.which("git") is None:
        pytest.skip("git is not installed")
    return True
