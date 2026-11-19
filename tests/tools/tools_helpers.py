"""Helpers for the tests of tools/*.py: load the tools as modules and build temporary skills."""
from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools"


def load_tool(name: str):
    module_name = f"_tool_{name}"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


BODY = """
# {title}

One paragraph on the problem, the practice and the work product.

## When not to use

- Use `other-skill` instead when something else applies.

## Inputs

| Input | Required | Usually produced by |
| --- | --- | --- |
| `requirements/requirements.csv` | yes | `requirement-phrasing` |

## Outputs

| File | Shape | Consumed by |
| --- | --- | --- |
| `requirements/x.md` | `assets/x.md` | `requirement-linter` |

## Procedure

1. **Read the workspace.** Read the files.

## Quality checks

- [ ] Checks pass.

## Hand-offs

- **Next:** `requirement-linter`.

## References

- `references/ireb-anchor.md`.
"""

GRADER = """---
type: llm
focus: trace
weight: 1
---

The file requirements/x.md exists
"""

PROMPT = """---
tags: [re-skills, {name}]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Write]
---

Do the thing for the loyalty-points sample.
"""

CASE = """schema_version: "1.1"
name: {case}
expected_outcome: |
  A good result in two sentences.
  Second line.
"""


class Catalogue:
    """A temporary repo root with a ``skills/`` tree."""

    def __init__(self, root: Path) -> None:
        self.root = root
        (root / "skills").mkdir(parents=True, exist_ok=True)
        (root / "docs").mkdir(exist_ok=True)

    def write(self, rel: str, content: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def skill(self, name: str, stage: str = "specification", invocation: str = "model",
              frontmatter: Optional[str] = None, body: Optional[str] = None,
              outputs_to: str = "none", inputs_from: str = "none", extra_meta: str = "",
              extra_keys: str = "", evals: bool = True, folders: bool = True) -> Path:
        folder = self.root / "skills" / stage / name
        meta_stage = "primitives" if stage == "_primitives" else stage
        flags = {"user": "disable-model-invocation: true\n", "primitive": "user-invocable: false\n",
                 "model": ""}[invocation]
        if frontmatter is None:
            frontmatter = textwrap.dedent(f"""\
                name: {name}
                description: >-
                  Does one thing and leaves requirements/x.md behind. Use when a ticket needs it.
                  Not for other things (use other-skill).
                license: MIT
                """) + flags + extra_keys + textwrap.dedent(f"""\
                metadata:
                  stage: {meta_stage}
                  invocation: {invocation}
                  priority: P1
                  ireb-anchor: "CPRE FL Handbook 1.2 §3.3"
                  inputs-from: "{inputs_from}"
                  outputs-to: "{outputs_to}"
                  work-product: "requirements/x.md"
                  version: "0.1.0"
                """) + extra_meta
        self.write(f"skills/{stage}/{name}/SKILL.md",
                   f"---\n{frontmatter}---\n" + (body if body is not None else BODY.format(title=name.title())))
        if folders:
            self.write(f"skills/{stage}/{name}/references/ireb-anchor.md",
                       "# IREB anchor\n\n> re-skills is independent of IREB and not endorsed by it.\n")
            if invocation != "primitive":
                self.write(f"skills/{stage}/{name}/assets/x.md", "| ID | Text |\n")
                self.write(f"skills/{stage}/{name}/examples/input.md", "input\n")
                self.write(f"skills/{stage}/{name}/examples/expected-output.md", "output\n")
        if evals and invocation != "primitive":
            for case in ("happy-path", "messy-notes", "adversarial-vague"):
                self.case(f"skills/{stage}/{name}/evals/{case}", name)
        return folder

    def case(self, rel: str, skill_name: str, graders: int = 1) -> Path:
        case = Path(rel).name
        self.write(f"{rel}/prompt.md", PROMPT.format(name=skill_name))
        self.write(f"{rel}/case.yaml", CASE.format(case=case))
        for n in range(1, graders + 1):
            self.write(f"{rel}/graders/{n:02d}-check.md", GRADER)
        return self.root / rel


def findings_by_code(skills, name: Optional[str] = None) -> Dict[str, list]:
    out: Dict[str, list] = {}
    for skill in skills:
        if name and skill.name != name:
            continue
        for f in skill.findings:
            out.setdefault(f"{f.severity}:{f.code}", []).append(f.message)
    return out
