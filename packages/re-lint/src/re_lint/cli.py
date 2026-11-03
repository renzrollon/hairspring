"""``re-lint`` command-line entry point.

Each subcommand is a self-contained module exposing ``build_parser()`` and ``run(args)``.
Modules are imported lazily so one broken optional command never breaks the others.
"""
from __future__ import annotations

import argparse
import importlib
import sys
from typing import List, Optional

from . import __version__

# command name -> (module, one-line help)
COMMANDS = {
    "check": ("lint", "Lint requirement text and attributes (CI gate)."),
    "ids": ("ids", "Allocate the next free IDs, list IDs, check duplicates."),
    "trace": ("tracing", "Build the trace matrix, report gaps, follow impact."),
    "baseline": ("baseline", "Create and diff requirement baselines."),
    "views": ("views", "Generate selective, projective and aggregating views."),
    "prioritize": ("prioritize", "Compute a weighted prioritization matrix."),
    "reqif": ("reqif_io", "Export to and import from ReqIF."),
    "openspec": ("openspec", "Scaffold an OpenSpec change or spec-kit spec."),
    "issues": ("issues", "Plan, push and pull requirement issues (GitHub, Jira, Azure DevOps)."),
}


def _load(module_name: str):
    return importlib.import_module(f"{__package__}.{module_name}")


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    top = argparse.ArgumentParser(
        prog="re-lint",
        description="Deterministic requirement checks and tools for the re-skills catalogue.",
    )
    top.add_argument("--version", action="version", version=f"re-lint {__version__}")
    top.add_argument("command", nargs="?", choices=sorted(COMMANDS), help="subcommand")
    if not argv or argv[0] in ("-h", "--help", "--version"):
        top.print_help() if not argv or argv[0] != "--version" else top.parse_args(argv)
        if not argv:
            print("\ncommands:")
            for name, (_, help_text) in COMMANDS.items():
                print(f"  {name:<11} {help_text}")
            return 2
        return 0
    command, rest = argv[0], argv[1:]
    if command not in COMMANDS:
        top.error(f"unknown command {command!r}; choose from {', '.join(COMMANDS)}")
    module = _load(COMMANDS[command][0])
    parser = module.build_parser()
    parser.prog = f"re-lint {command}"
    args = parser.parse_args(rest)
    try:
        return int(module.run(args) or 0)
    except KeyboardInterrupt:  # pragma: no cover
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
