#!/usr/bin/env python3
"""Build spec-strict copies of every skill, optionally validate them, and zip them for upload.

Our SKILL.md files use three widely honored extension keys (``disable-model-invocation``,
``user-invocable``, ``argument-hint``). The agentskills.io reference validator (``skills-ref``)
and some upload paths (claude.ai, the Skills API) accept only the six spec keys. This tool writes
a portable copy of each skill with those keys removed, so we can prove spec conformance in CI and
hand out upload-ready zips.

Usage:
  python3 tools/build_dist.py                 # dist/portable/<skill>/ and dist/zips/<skill>.zip
  python3 tools/build_dist.py --validate      # also run `skills-ref validate` on each copy
  python3 tools/build_dist.py --validate --require-validator   # fail if skills-ref is missing (CI)

Install the validator with:
  pip install "git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref"
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTENSION_KEYS = ("disable-model-invocation:", "user-invocable:", "argument-hint:")
EXCLUDE = {"evals", "__pycache__", ".pytest_cache", "agents"}


def strip_extensions(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    head, body = text[: end + 1], text[end + 1 :]
    kept = [line for line in head.splitlines(keepends=True) if not line.startswith(EXTENSION_KEYS)]
    return "".join(kept) + body


def build(out: Path) -> list:
    portable = out / "portable"
    zips = out / "zips"
    for path in (portable, zips):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
    built = []
    for skill_md in sorted((ROOT / "skills").glob("*/*/SKILL.md")):
        src = skill_md.parent
        dest = portable / src.name
        shutil.copytree(src, dest, ignore=lambda _d, names: [n for n in names if n in EXCLUDE or n.endswith(".pyc")])
        (dest / "SKILL.md").write_text(strip_extensions(skill_md.read_text(encoding="utf-8")), encoding="utf-8")
        with zipfile.ZipFile(zips / f"{src.name}.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            for file in sorted(dest.rglob("*")):
                if file.is_file():
                    zf.write(file, Path(src.name) / file.relative_to(dest))
        built.append(dest)
    return built


def validate(dirs: list, require: bool) -> int:
    exe = shutil.which("skills-ref")
    if not exe:
        msg = "skills-ref not found; install it with the command in --help"
        print(("error: " if require else "skip: ") + msg, file=sys.stderr)
        return 1 if require else 0
    failures = 0
    for d in dirs:
        proc = subprocess.run([exe, "validate", str(d)], capture_output=True, text=True)
        if proc.returncode != 0:
            failures += 1
            print(f"FAIL {d.name}\n{(proc.stdout + proc.stderr).strip()}\n")
    print(f"skills-ref: {len(dirs) - failures}/{len(dirs)} skills conform to the agentskills.io spec")
    return 1 if failures else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "dist"), help="output folder (default: dist/)")
    ap.add_argument("--validate", action="store_true", help="run skills-ref validate on each portable copy")
    ap.add_argument("--require-validator", action="store_true", help="fail when skills-ref is not installed")
    args = ap.parse_args(argv)
    dirs = build(Path(args.out))
    print(f"built {len(dirs)} portable skills in {args.out}/portable and zips in {args.out}/zips")
    return validate(dirs, args.require_validator) if args.validate else 0


if __name__ == "__main__":
    sys.exit(main())
