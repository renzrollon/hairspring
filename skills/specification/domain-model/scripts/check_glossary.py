#!/usr/bin/env python3
"""Cross-check the classes of a Mermaid domain model against the terms of a glossary.

Single-skill helper of the re-skills ``domain-model`` skill. Stdlib only, Python 3.9+.

Reads the first ``classDiagram`` or ``erDiagram`` block of a Markdown file and the term table of
a glossary (a Markdown pipe table or CSV with a ``Term`` column; optional columns whose header
contains "synonym" or "abbreviation", and a ``Status`` column in which ``deprecated`` terms count
as names to avoid). Notes in parentheses and a trailing ": avoid" in synonym cells are dropped.
Names are compared case-, space- and punctuation-insensitively, so ``PointsTransaction``,
``POINTS_TRANSACTION`` and "Points transaction" match.

Findings:
  class-without-term         a class matches no glossary term, synonym or abbreviation
  class-named-after-synonym  a class is named after a synonym, not the preferred term
  duplicate-concept          two or more classes map to the same glossary term
  term-without-class         a glossary term matches no class, class label or attribute

Exit codes: 0 no findings, 1 findings, 2 usage or parse error.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

CLASS_DECL_RE = re.compile(
    r'^class\s+(?P<name>[A-Za-z_]\w*)(?:~[^~]*~)?(?:\["(?P<label>[^"]*)"\])?\s*(?::::\w+)?\s*(?P<brace>\{)?\s*(?P<inline>.*)$'
)
ANNOTATION_RE = re.compile(r"^<<(?P<ann>[^>]+)>>\s*(?P<name>[A-Za-z_]\w*)?\s*$")
CLASS_REL_RE = re.compile(
    r'^(?P<a>[A-Za-z_]\w*)\s*(?:"[^"]*"\s*)?'
    r"(?P<arrow>(?:<\||\*|o|<)?(?:--|\.\.)(?:\|>|\*|o|>)?)"
    r'\s*(?:"[^"]*"\s*)?(?P<b>[A-Za-z_]\w*)\s*(?::.*)?$'
)
MEMBER_LINE_RE = re.compile(r"^(?P<name>[A-Za-z_]\w*)\s*:\s*(?P<member>.+)$")
ER_ENTITY_RE = re.compile(r'^(?P<name>"[^"]+"|[A-Za-z_][\w-]*)(?:\["(?P<label>[^"]*)"\])?\s*\{\s*$')
ER_REL_RE = re.compile(
    r'^(?P<a>"[^"]+"|[A-Za-z_][\w-]*)\s*(?P<card>[|}][o|](?:--|\.\.)[o|][|{])\s*'
    r'(?P<b>"[^"]+"|[A-Za-z_][\w-]*)\s*:\s*.*$'
)
SKIP_PREFIXES = (
    "%%", "direction ", "note", "classDef ", "cssClass ", "style ", "click ", "link ",
    "callback ", "accTitle", "accDescr", "title ",
)


class ParseError(Exception):
    """The input cannot be checked (exit code 2)."""


def norm(name: str) -> str:
    """Compare key: no markup, no trailing qualifier in parentheses, lowercase alphanumerics."""
    text = re.sub(r"[`*_\"]", " ", name or "")
    text = re.sub(r"\s*\([^)]*\)\s*$", "", text.strip())
    return re.sub(r"[^0-9a-z]", "", text.lower())


def keys(name: str) -> Set[str]:
    """The compare key plus a naive singular form, so 'Vouchers' matches 'Voucher'."""
    key = norm(name)
    out = {key} if key else set()
    if len(key) > 3 and key.endswith("s"):
        out.add(key[:-1])
    return out


# --------------------------------------------------------------------------- diagram


class Model:
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self.classes: List[str] = []
        self.labels: Dict[str, str] = {}
        self.lines: Dict[str, int] = {}
        self.attributes: Dict[str, List[str]] = {}
        self.enumerations: Set[str] = set()

    def add(self, name: str, line: int) -> None:
        name = name.strip('"')
        if name not in self.lines:
            self.classes.append(name)
            self.lines[name] = line
            self.attributes[name] = []


def _blocks(text: str) -> List[List[Tuple[int, str]]]:
    blocks: List[List[Tuple[int, str]]] = []
    fence: Optional[str] = None
    is_mermaid = False
    body: List[Tuple[int, str]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if fence is None:
            match = re.match(r"^(`{3,}|~{3,})\s*(\S*)", stripped)
            if match:
                fence, is_mermaid, body = match.group(1), match.group(2).lower() == "mermaid", []
            continue
        if stripped.startswith(fence) and stripped.strip(fence[0]) == "":
            if is_mermaid:
                sig = [(n, t.strip()) for n, t in body if t.strip() and not t.strip().startswith("%%")]
                if sig and sig[0][1].split()[0] in ("classDiagram", "classDiagram-v2", "erDiagram"):
                    blocks.append(sig)
            fence = None
            continue
        body.append((number, raw))
    return blocks


def _attribute_name(member: str) -> Optional[str]:
    """'points: Points' -> points; '+Points points' -> points; methods (with '(') -> None."""
    text = member.strip().lstrip("+-#~").strip()
    if not text or "(" in text or text.startswith("<<"):
        return None
    if ":" in text:
        return text.split(":", 1)[0].strip() or None
    parts = text.split()
    return parts[-1] if parts else None


def parse_class_diagram(block: Sequence[Tuple[int, str]]) -> Model:
    model = Model("classDiagram")
    current: Optional[str] = None
    depth_namespace = 0
    for number, text in block[1:]:
        if current is not None:
            if text.startswith("}"):
                current = None
                continue
            ann = ANNOTATION_RE.match(text)
            if ann and ann.group("ann").strip().lower() == "enumeration":
                model.enumerations.add(current)
                continue
            attr = _attribute_name(text)
            if attr:
                model.attributes[current].append(attr)
            continue
        if text.startswith(SKIP_PREFIXES) or text == "direction":
            continue
        if text.startswith("namespace "):
            depth_namespace += 1
            continue
        if text == "}" and depth_namespace:
            depth_namespace -= 1
            continue
        match = CLASS_DECL_RE.match(text)
        if match:
            name = match.group("name")
            model.add(name, number)
            if match.group("label"):
                model.labels[name] = match.group("label")
            inline = (match.group("inline") or "").strip()
            if match.group("brace"):
                if inline.endswith("}"):
                    continue
                current = name
            continue
        ann = ANNOTATION_RE.match(text)
        if ann and ann.group("name"):
            model.add(ann.group("name"), number)
            if ann.group("ann").strip().lower() == "enumeration":
                model.enumerations.add(ann.group("name"))
            continue
        match = CLASS_REL_RE.match(text)
        if match:
            model.add(match.group("a"), number)
            model.add(match.group("b"), number)
            continue
        match = MEMBER_LINE_RE.match(text)
        if match:
            model.add(match.group("name"), number)
            member = match.group("member").strip()
            if member.lower() == "<<enumeration>>":
                model.enumerations.add(match.group("name"))
            else:
                attr = _attribute_name(member)
                if attr:
                    model.attributes[match.group("name")].append(attr)
            continue
        raise ParseError(f"line {number}: cannot parse {text!r}")
    return model


def parse_er_diagram(block: Sequence[Tuple[int, str]]) -> Model:
    model = Model("erDiagram")
    current: Optional[str] = None
    for number, text in block[1:]:
        if current is not None:
            if text.startswith("}"):
                current = None
                continue
            parts = text.split()
            if len(parts) >= 2:
                model.attributes[current].append(parts[1])
            continue
        if text.startswith(SKIP_PREFIXES) or text == "direction":
            continue
        match = ER_ENTITY_RE.match(text)
        if match:
            name = match.group("name").strip('"')
            model.add(name, number)
            if match.group("label"):
                model.labels[name] = match.group("label")
            current = name
            continue
        match = ER_REL_RE.match(text)
        if match:
            model.add(match.group("a"), number)
            model.add(match.group("b"), number)
            continue
        if re.match(r'^("[^"]+"|[A-Za-z_][\w-]*)$', text):
            model.add(text, number)
            continue
        raise ParseError(f"line {number}: cannot parse {text!r}")
    return model


def parse_model(text: str, block: int = 1) -> Model:
    blocks = _blocks(text)
    if not blocks:
        raise ParseError("no mermaid classDiagram or erDiagram block found")
    if block < 1 or block > len(blocks):
        raise ParseError(f"--block {block} out of range (1..{len(blocks)})")
    chosen = blocks[block - 1]
    if chosen[0][1].startswith("erDiagram"):
        return parse_er_diagram(chosen)
    return parse_class_diagram(chosen)


# --------------------------------------------------------------------------- glossary


class Term:
    def __init__(self, name: str, line: int, synonyms: Sequence[str], deprecated: bool = False) -> None:
        self.name = name
        self.line = line
        self.synonyms = [s for s in synonyms if norm(s)]
        self.deprecated = deprecated


def _split_md_row(line: str) -> List[str]:
    text = line.strip().strip("|")
    return [c.strip() for c in re.split(r"(?<!\\)\|", text)]


def _split_list(cell: str) -> List[str]:
    """'customer (code: `Customer`; LOY-204), account holder (LOY-202): avoid' -> two names."""
    cell = re.sub(r"\([^)]*\)", " ", cell or "")
    cell = re.sub(r"[`*]", "", cell)
    if norm(cell) in ("", "none", "na", "tbd"):
        return []
    names = []
    for part in re.split(r"[,;/]", cell):
        name = part.split(":", 1)[0].strip()
        if name and name not in ("-", "—", "–"):
            names.append(name)
    return names


def _terms_from_rows(header: Sequence[str], rows: Sequence[Tuple[int, Sequence[str]]]) -> List[Term]:
    lowered = [re.sub(r"[`*_]", "", h).strip().lower() for h in header]
    if "term" not in lowered:
        return []
    t_col = lowered.index("term")
    alt_cols = [i for i, h in enumerate(lowered) if "synonym" in h or "abbreviation" in h]
    status_col = lowered.index("status") if "status" in lowered else None
    terms = []
    for line, cells in rows:
        cells = list(cells) + [""] * (len(header) - len(cells))
        name = re.sub(r"[`*]", "", cells[t_col]).strip()
        if not norm(name):
            continue
        alts: List[str] = []
        for i in alt_cols:
            alts.extend(_split_list(cells[i]))
        deprecated = status_col is not None and norm(cells[status_col]) == "deprecated"
        terms.append(Term(name, line, alts, deprecated))
    return terms


def parse_glossary(path: Path) -> List[Term]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".csv":
        reader = list(csv.reader(io.StringIO(text.lstrip("﻿"))))
        if not reader:
            return []
        return _terms_from_rows(reader[0], [(n + 2, r) for n, r in enumerate(reader[1:]) if any(r)])
    lines = text.splitlines()
    in_fence = False
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        elif not in_fence and stripped.startswith("|") and i + 1 < len(lines):
            separator = _split_md_row(lines[i + 1])
            if separator and all(re.match(r"^:?-+:?$", c.replace(" ", "")) for c in separator if c):
                header = _split_md_row(lines[i])
                rows = []
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    rows.append((j + 1, _split_md_row(lines[j])))
                    j += 1
                terms = _terms_from_rows(header, rows)
                if terms:
                    return terms
                i = j
                continue
        i += 1
    return []


# --------------------------------------------------------------------------- check


def check(model: Model, terms: Sequence[Term], ignore: Sequence[str]) -> Tuple[List[Dict[str, object]], List[str]]:
    ignored: Set[str] = set()
    for item in ignore:
        ignored |= keys(item)
    findings: List[Dict[str, object]] = []
    as_attribute: List[str] = []

    preferred: Dict[str, Term] = {}
    alternative: Dict[str, Term] = {}
    for term in terms:
        for k in keys(term.name):
            (alternative if term.deprecated else preferred).setdefault(k, term)
        for syn in term.synonyms:
            for k in keys(syn):
                alternative.setdefault(k, term)

    by_term: Dict[str, List[str]] = {}
    for cls in model.classes:
        if cls in model.enumerations:
            continue
        names = keys(cls) | keys(model.labels.get(cls, ""))
        if names & ignored:
            continue
        hit = next((preferred[k] for k in names if k in preferred), None)
        if hit is not None:
            by_term.setdefault(hit.name, []).append(cls)
            continue
        alt = next((alternative[k] for k in names if k in alternative), None)
        if alt is not None:
            by_term.setdefault(alt.name, []).append(cls)
            if alt.deprecated and keys(alt.name) & names:
                message = (f"class {cls} is named after deprecated glossary term '{alt.name}'; "
                           "use the replacement the glossary names")
            else:
                message = (f"class {cls} is named after a synonym of glossary term '{alt.name}'; "
                           "rename the class or change the preferred term in the glossary")
            findings.append({
                "kind": "class-named-after-synonym", "name": cls, "line": model.lines[cls],
                "message": message,
            })
            continue
        findings.append({
            "kind": "class-without-term", "name": cls, "line": model.lines[cls],
            "message": f"class {cls} has no glossary entry; raise it to the glossary",
        })

    for term_name, classes in by_term.items():
        if len(classes) > 1:
            findings.append({
                "kind": "duplicate-concept", "name": term_name,
                "line": min(model.lines[c] for c in classes),
                "message": f"classes {', '.join(classes)} all map to glossary term '{term_name}'; "
                           "merge them or split the term in the glossary",
            })

    class_keys: Set[str] = set()
    for cls in model.classes:
        class_keys |= keys(cls) | keys(model.labels.get(cls, ""))
    attribute_keys: Dict[str, str] = {}
    for cls, attrs in model.attributes.items():
        for attr in attrs:
            for k in keys(attr):
                attribute_keys.setdefault(k, f"{cls}.{attr}")

    for term in terms:
        if term.deprecated:
            continue
        names = keys(term.name)
        alts: Set[str] = set()
        for syn in term.synonyms:
            alts |= keys(syn)
        if names & ignored or (names | alts) & class_keys:
            continue
        attr_hit = next((attribute_keys[k] for k in names if k in attribute_keys), None)
        if attr_hit:
            as_attribute.append(f"{term.name} -> {attr_hit}")
            continue
        findings.append({
            "kind": "term-without-class", "name": term.name, "line": term.line,
            "message": f"glossary term '{term.name}' matches no class or attribute; model it, or "
                       "record why it is not a business object (actor, rule, process) and --ignore it",
        })
    return findings, as_attribute


def _default_glossary(model_path: Path) -> Optional[Path]:
    for candidate in (
        model_path.parent.parent / "glossary.md",
        model_path.parent / "glossary.md",
        Path("requirements") / "glossary.md",
    ):
        if candidate.is_file():
            return candidate
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_glossary.py",
        description=(
            "Cross-check the class (or entity) names of the first Mermaid classDiagram/erDiagram "
            "block in a Markdown file against the terms of a glossary. Reports classes with no "
            "glossary entry, classes named after a synonym, several classes for one term, and "
            "glossary terms with no class. Terms that match an attribute name count as modeled."
        ),
        epilog="Exit codes: 0 no findings, 1 findings, 2 usage or parse error.",
    )
    parser.add_argument("model", help="Markdown file with the domain model diagram, e.g. requirements/models/domain-model.md")
    parser.add_argument("--glossary", metavar="FILE",
                        help="glossary file (.md with a pipe table, or .csv) holding a 'Term' column; "
                             "default: ../glossary.md next to the model's folder, then requirements/glossary.md")
    parser.add_argument("--ignore", action="append", default=[], metavar="NAME[,NAME]",
                        help="terms or classes to skip because their decision is already recorded "
                             "(e.g. actors or business rules that are not business objects); repeatable")
    parser.add_argument("--block", type=int, default=1, metavar="N",
                        help="which classDiagram/erDiagram block to check, counting from 1 (default: 1)")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="text (default, one finding per line) or json (machine-readable)")
    return parser


def run(args: argparse.Namespace) -> int:
    model_path = Path(args.model)
    try:
        model = parse_model(model_path.read_text(encoding="utf-8"), args.block)
    except OSError as exc:
        sys.stderr.write(f"check_glossary.py: cannot read {model_path}: {exc}\n")
        return 2
    except ParseError as exc:
        sys.stderr.write(f"check_glossary.py: {model_path}: {exc}\n")
        return 2
    glossary_path = Path(args.glossary) if args.glossary else _default_glossary(model_path)
    if glossary_path is None or not glossary_path.is_file():
        sys.stderr.write("check_glossary.py: glossary not found; pass --glossary FILE\n")
        return 2
    terms = parse_glossary(glossary_path)
    if not terms:
        sys.stderr.write(f"check_glossary.py: {glossary_path}: no table with a 'Term' column found\n")
        return 2
    ignore = [part.strip() for value in args.ignore for part in value.split(",") if part.strip()]
    findings, as_attribute = check(model, terms, ignore)
    if args.format == "json":
        print(json.dumps({
            "model": str(model_path), "glossary": str(glossary_path), "diagram": model.kind,
            "classes": [c for c in model.classes if c not in model.enumerations],
            "enumerations": sorted(model.enumerations),
            "terms": [t.name for t in terms], "terms_as_attributes": as_attribute,
            "findings": findings,
        }, indent=2))
    else:
        print(f"{model_path}: {len(model.classes) - len(model.enumerations)} classes ({model.kind}); "
              f"{glossary_path}: {len(terms)} terms")
        for item in as_attribute:
            print(f"info: term modeled as attribute: {item}")
        for f in findings:
            source = glossary_path if f["kind"] == "term-without-class" else model_path
            print(f"{source}:{f['line']}: {f['kind']}: {f['message']}")
        print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
