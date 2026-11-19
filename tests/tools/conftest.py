"""Fixtures for the tests of tools/*.py; helpers live in tools_helpers.py."""
from __future__ import annotations

import pytest

from tools_helpers import Catalogue, load_tool


@pytest.fixture(scope="session")
def vc():
    return load_tool("validate_catalogue")


@pytest.fixture(scope="session")
def vs():
    return load_tool("vendor_scripts")


@pytest.fixture
def catalogue(tmp_path) -> Catalogue:
    return Catalogue(tmp_path / "repo")
