"""``re-lint`` command-line entry point.

Each subcommand is a self-contained module exposing ``build_parser()``, ``run(args)`` and
``main(argv)``. Modules are imported lazily so one missing or broken optional command never breaks
the others, and ``re-lint --help`` works even when a command module is absent.
"""
from __future__ import annotations

import argparse
import difflib
import importlib
import importlib.util
import os
import sys
from typing import List, Optional, TextIO

from . import __version__

PACKAGE = __package__ or "re_lint"

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

EXIT_CODES = "Exit codes: 0 clean, 1 findings at or above --fail-on, 2 usage, schema or parse error."


def _available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(f"{PACKAGE}.{module_name}") is not None
    except (ImportError, ValueError):  # pragma: no cover - broken package metadata
        return False


def _load(module_name: str):
    return importlib.import_module(f"{PACKAGE}.{module_name}")


def _top_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="re-lint",
        usage="re-lint [-h] [--version] COMMAND [ARGS ...]",
        description="Deterministic requirement checks and tools for the re-skills catalogue.",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="store_true", help="show this help message and exit")
    parser.add_argument("-V", "--version", action="store_true", help="print the version and exit")
    return parser


def print_help(stream: TextIO) -> None:
    stream.write(_top_parser().format_help())
    stream.write("\ncommands:\n")
    for name, (module, help_text) in COMMANDS.items():
        note = "" if _available(module) else "  (not available in this installation)"
        stream.write(f"  {name:<11} {help_text}{note}\n")
    stream.write("\nRun 're-lint COMMAND --help' for the options of one command.\n")
    stream.write(EXIT_CODES + "\n")


def _error(message: str) -> int:
    sys.stderr.write(f"re-lint: error: {message}\n")
    return 2


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print_help(sys.stderr)
        return 2
    first = argv[0]
    if first in ("-h", "--help"):
        print_help(sys.stdout)
        return 0
    if first == "help":
        if len(argv) > 1 and argv[1] in COMMANDS:
            return main([argv[1], "--help"])
        print_help(sys.stdout)
        return 0
    if first in ("-V", "--version"):
        sys.stdout.write(f"re-lint {__version__}\n")
        return 0
    if first.startswith("-"):
        return _error(f"unknown option {first!r}; put options after the command "
                      "(re-lint COMMAND --help)")
    if first not in COMMANDS:
        close = difflib.get_close_matches(first, list(COMMANDS), n=1)
        hint = f"; did you mean {close[0]!r}?" if close else ""
        return _error(f"unknown command {first!r}{hint} Commands: {', '.join(COMMANDS)}")

    command, rest = first, argv[1:]
    module_name = COMMANDS[command][0]
    try:
        module = _load(module_name)
    except ModuleNotFoundError as exc:
        if exc.name in (f"{PACKAGE}.{module_name}", module_name):
            return _error(f"the '{command}' command is not available in this installation of "
                          f"re-lint {__version__} (module {PACKAGE}.{module_name} is missing); "
                          "upgrade or reinstall re-lint")
        return _error(f"the '{command}' command needs the module {exc.name!r}, which is not installed")
    except Exception as exc:  # a broken command module must not take the others down
        if os.environ.get("RE_LINT_DEBUG"):
            raise
        return _error(f"could not load the '{command}' command: {type(exc).__name__}: {exc} "
                      "(set RE_LINT_DEBUG=1 for a traceback)")

    # argparse derives prog (and the prog of any subparsers) from sys.argv[0] at build time.
    saved_argv0 = sys.argv[0] if sys.argv else ""
    if sys.argv:
        sys.argv[0] = f"re-lint {command}"
    try:
        parser = module.build_parser()
    finally:
        if sys.argv:
            sys.argv[0] = saved_argv0
    parser.prog = f"re-lint {command}"
    try:
        args = parser.parse_args(rest)
    except SystemExit as exc:  # argparse: --help (0) or usage error (2)
        return int(exc.code or 0) if not isinstance(exc.code, str) else 2
    try:
        return int(module.run(args) or 0)
    except KeyboardInterrupt:  # pragma: no cover - interactive only
        return 130
    except BrokenPipeError:  # output piped into head and closed early
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:  # pragma: no cover
            pass
        return 0
    except (OSError, ValueError) as exc:
        if os.environ.get("RE_LINT_DEBUG"):
            raise
        return _error(f"{command}: {exc}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
