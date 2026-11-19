#!/usr/bin/env python3
"""Install the re-skills catalogue into Claude Code, Codex, GitHub Copilot or Cursor.

Skills are kept in stage folders in this repository (skills/<stage>/<skill>/). Agents expect
one flat folder per skill, so this installer copies (or links) each skill folder into the
agent's skills directory, records what it installed in a manifest, and can upgrade or remove
exactly those folders later.

Run it from a clone, or straight from GitHub without cloning:

  python3 install.py --agent claude                      # project scope: ./.claude/skills
  python3 install.py --agent all --scope user            # every agent, in your home directory
  python3 install.py --agent copilot --priority P0       # only the 12 MVP skills
  python3 install.py --agent cursor --skills glossary,requirement-linter
  python3 install.py --agent codex --uninstall
  curl -fsSL https://raw.githubusercontent.com/renzrollon/hairspring/main/install.py \\
    | python3 - --agent claude --ref main

Stdlib only, Python 3.9+, works on Linux, macOS and Windows.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

REPO = "renzrollon/hairspring"
MANIFEST = ".re-skills-manifest.json"

# agent -> (project-level dir relative to the project root, user-level dir relative to $HOME)
AGENT_DIRS: Dict[str, Dict[str, str]] = {
    "claude": {"project": ".claude/skills", "user": ".claude/skills"},
    "codex": {"project": ".agents/skills", "user": ".agents/skills"},
    "copilot": {"project": ".github/skills", "user": ".copilot/skills"},
    "cursor": {"project": ".cursor/skills", "user": ".cursor/skills"},
}
AGENT_ALIASES = {
    "claude-code": "claude",
    "openai-codex": "codex",
    "github-copilot": "copilot",
    "vscode": "copilot",
}
EXCLUDE_DIRS = {"evals", "__pycache__", ".pytest_cache"}

_FM_KEY = re.compile(r"^\s*(name|stage|invocation|priority|version):\s*['\"]?([^'\"#\n]+?)['\"]?\s*$")


# --------------------------------------------------------------------------- catalogue


def read_frontmatter(skill_md: Path) -> Dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    meta: Dict[str, str] = {}
    for line in text[3:end if end > 0 else None].splitlines():
        m = _FM_KEY.match(line)
        if m and m.group(1) not in meta:
            meta[m.group(1)] = m.group(2).strip()
    return meta


def discover(source: Path) -> List[Dict[str, str]]:
    found = []
    for skill_md in sorted((source / "skills").glob("*/*/SKILL.md")):
        meta = read_frontmatter(skill_md)
        meta.setdefault("name", skill_md.parent.name)
        meta["dir"] = str(skill_md.parent)
        found.append(meta)
    if not found:
        raise SystemExit(f"error: no skills found under {source / 'skills'}")
    return found


def select(skills: List[Dict[str, str]], args: argparse.Namespace) -> List[Dict[str, str]]:
    chosen = skills
    if args.skills:
        wanted = {s.strip() for s in args.skills.split(",") if s.strip()}
        unknown = wanted - {s["name"] for s in skills}
        if unknown:
            raise SystemExit(f"error: unknown skill(s): {', '.join(sorted(unknown))}")
        chosen = [s for s in chosen if s["name"] in wanted]
    if args.priority:
        allowed = {"P0": {"P0"}, "P1": {"P0", "P1"}, "P2": {"P0", "P1", "P2"}}[args.priority]
        chosen = [s for s in chosen if s.get("priority") in allowed or s.get("invocation") == "primitive"]
    if args.stage:
        stages = {s.strip() for s in args.stage.split(",")}
        chosen = [s for s in chosen if s.get("stage") in stages or s.get("invocation") == "primitive"]
    if args.skills and not args.no_primitives:
        # Primitives are tiny and every emitting skill leans on them.
        names = {s["name"] for s in chosen}
        chosen += [s for s in skills if s.get("invocation") == "primitive" and s["name"] not in names]
    if args.no_primitives:
        chosen = [s for s in chosen if s.get("invocation") != "primitive"]
    return chosen


# --------------------------------------------------------------------------- source


def fetch_source(ref: str, tmp: Path) -> Path:
    url = f"https://codeload.github.com/{REPO}/tar.gz/{ref}"
    print(f"Downloading {url}")
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 - fixed https URL
        data = resp.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            target = (tmp / member.name).resolve()
            if not str(target).startswith(str(tmp.resolve())):
                raise SystemExit(f"error: unsafe path in archive: {member.name}")
        if hasattr(tarfile, "data_filter"):
            tar.extractall(tmp, filter="data")
        else:  # Python < 3.12 without the backported filter; members validated above
            tar.extractall(tmp)  # noqa: S202
    roots = [p for p in tmp.iterdir() if p.is_dir()]
    if len(roots) != 1:
        raise SystemExit("error: unexpected archive layout")
    return roots[0]


def local_source() -> Optional[Path]:
    here = Path(__file__).resolve().parent if "__file__" in globals() else None
    if here and (here / "skills").is_dir():
        return here
    return None


# --------------------------------------------------------------------------- install


def target_dir(agent: str, scope: str, project: Path, override: Optional[str]) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    rel = AGENT_DIRS[agent][scope]
    base = Path.home() if scope == "user" else project
    return (base / rel).resolve()


def load_manifest(target: Path) -> Dict:
    path = target / MANIFEST
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"installed": {}}


def save_manifest(target: Path, manifest: Dict) -> None:
    (target / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ignore(_dir: str, names: List[str]) -> List[str]:
    return [n for n in names if n in EXCLUDE_DIRS or n.endswith(".pyc")]


def install_one(skill: Dict[str, str], target: Path, args: argparse.Namespace, manifest: Dict) -> str:
    name = skill["name"]
    dest = target / name
    owned = name in manifest["installed"]
    if dest.exists() or dest.is_symlink():
        if not owned and not args.force:
            return f"skip    {name} (exists and was not installed by re-skills; use --force)"
        if not args.dry_run:
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            else:
                shutil.rmtree(dest)
    action = "link" if args.link else "copy"
    if not args.dry_run:
        if args.link:
            os.symlink(skill["dir"], dest, target_is_directory=True)
        else:
            ignore = None if args.with_evals else _ignore
            shutil.copytree(skill["dir"], dest, ignore=ignore)
        manifest["installed"][name] = {"version": skill.get("version", ""), "mode": action}
    return f"{'update' if owned else action:<7} {name}"


def uninstall(target: Path, args: argparse.Namespace) -> int:
    manifest = load_manifest(target)
    names = list(manifest["installed"])
    if not names:
        print(f"Nothing installed by re-skills in {target}")
        return 0
    for name in names:
        dest = target / name
        print(f"remove  {name}")
        if not args.dry_run and (dest.exists() or dest.is_symlink()):
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            else:
                shutil.rmtree(dest)
        manifest["installed"].pop(name, None)
    if not args.dry_run:
        (target / MANIFEST).unlink(missing_ok=True)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="install.py",
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--agent", required=True, help="claude, codex, copilot, cursor, or all (comma-separated list ok)")
    p.add_argument("--scope", choices=["project", "user"], default="project", help="project (default) or user")
    p.add_argument("--project", default=".", help="project root for --scope project (default: current directory)")
    p.add_argument("--target", help="install into this exact directory instead of the agent default")
    p.add_argument("--skills", help="comma-separated skill names (primitives are added automatically)")
    p.add_argument("--priority", choices=["P0", "P1", "P2"], help="install skills up to this priority (P0 = MVP)")
    p.add_argument("--stage", help="comma-separated stages, e.g. validation,management")
    p.add_argument("--no-primitives", action="store_true", help="do not add re-interview, re-ids, re-templates")
    p.add_argument("--with-evals", action="store_true", help="also copy each skill's evals/ folder")
    p.add_argument("--link", action="store_true", help="symlink instead of copy (for contributors; needs a clone)")
    p.add_argument("--force", action="store_true", help="replace same-named folders not installed by re-skills")
    p.add_argument("--uninstall", action="store_true", help="remove the skills this installer put there")
    p.add_argument("--ref", help="download this git ref from GitHub instead of using the local clone")
    p.add_argument("--list", action="store_true", help="list the skills that would be installed, then exit")
    p.add_argument("--dry-run", action="store_true", help="print what would happen, change nothing")
    args = p.parse_args(argv)

    agents_raw = [AGENT_ALIASES.get(a.strip(), a.strip()) for a in args.agent.split(",")]
    agents = list(AGENT_DIRS) if "all" in agents_raw else agents_raw
    bad = [a for a in agents if a not in AGENT_DIRS]
    if bad:
        p.error(f"unknown agent(s): {', '.join(bad)}; choose from {', '.join(AGENT_DIRS)} or all")
    if args.target and len(agents) > 1:
        p.error("--target works with a single --agent")
    if args.link and args.ref:
        p.error("--link needs a local clone; drop --ref")

    project = Path(args.project).expanduser().resolve()

    if args.uninstall:
        for agent in agents:
            print(f"[{agent}] {target_dir(agent, args.scope, project, args.target)}")
            uninstall(target_dir(agent, args.scope, project, args.target), args)
        return 0

    with tempfile.TemporaryDirectory(prefix="re-skills-") as tmp:
        source = fetch_source(args.ref, Path(tmp)) if args.ref else local_source()
        if source is None:
            p.error("not running from a clone; pass --ref main to download the catalogue")
        chosen = select(discover(source), args)
        if args.list:
            for s in chosen:
                print(f"{s['name']:<24} {s.get('stage',''):<14} {s.get('invocation',''):<10} {s.get('priority','')}")
            return 0
        for agent in agents:
            target = target_dir(agent, args.scope, project, args.target)
            print(f"[{agent}] {target}{'  (dry run)' if args.dry_run else ''}")
            if not args.dry_run:
                target.mkdir(parents=True, exist_ok=True)
            manifest = load_manifest(target)
            manifest["source"] = f"{REPO}@{args.ref}" if args.ref else str(source)
            for skill in chosen:
                print("  " + install_one(skill, target, args, manifest))
            if not args.dry_run:
                save_manifest(target, manifest)
        print(f"\nInstalled {len(chosen)} skills. Next: run the re-setup skill once in your repo")
        print("  Claude Code / Copilot / Cursor: /re-setup    Codex: $re-setup")
    return 0


if __name__ == "__main__":
    sys.exit(main())
