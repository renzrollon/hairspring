#!/usr/bin/env python3
"""Count candidate glossary terms across docs, code and ticket exports.

Part of the re-skills ``glossary`` skill. Stdlib only, Python 3.9+.

The script finds three kinds of candidates and counts them per file and line:

* acronyms (``POS``, ``CRM``, ``PDPA``),
* code identifiers, split into words (``PointsTransaction`` and ``points_transaction``
  both count as "points transaction"),
* prose words and phrases of up to ``--max-words`` words that contain no stopword
  (``of`` may join two words: "point of sale").

Forms that differ only in case, plural or identifier style are merged into one candidate,
and the original spellings are listed as variants. With ``--glossary`` each candidate is
marked as a known term, synonym or abbreviation of ``glossary.md``, or as new.

The output is a candidate list for a person or an agent to curate. It does not decide what
is a domain term, and it never writes the glossary.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2

DEFAULT_EXTS = frozenset(
    """
    md markdown txt rst adoc csv tsv json yaml yml toml xml html feature
    py js jsx ts tsx java kt kts scala go rb php cs swift rs sql proto graphql gql
    c h cpp hpp sh
    """.split()
)

# Files whose prose (comments, docstrings) also uses the code keyword stoplist.
CODE_EXTS = frozenset(
    "py js jsx ts tsx java kt kts scala go rb php cs swift rs sql proto graphql gql c h cpp hpp sh".split()
)

SKIP_DIRS = frozenset(
    """
    .git .hg .svn node_modules .venv venv env __pycache__ dist build target out
    .idea .vscode .tox .mypy_cache .pytest_cache .ruff_cache coverage htmlcov vendor
    """.split()
)

STOPWORDS = frozenset(
    """
    a about above after again against all also am an and any are as at be because been before
    being below between both but by can cannot could did do does doing done down during each
    either else etc even ever every few for from further get gets got had has have having he her
    here hers him his how however i if in into is it its itself just least less let like made
    make makes many may me might more most much must my need needs no nor not now of off often
    on once one only or other our ours out over own per please rather same see she shall should
    so some such than that the their theirs them then there these they this those through thus
    to too under until up upon us use used uses using very via was we well were what when where
    whether which while who whom whose why will with within without would yes yet you your yours
    able across already always another anyone anything around back new non never next still sure
    today tomorrow yesterday want wants wanted way ways really thing things lot lots
    """.split()
)

CODE_WORDS = frozenset(
    """
    def class return import from self cls const let var function func public private protected
    static void int str string bool boolean true false null none nil else elif while async await
    try except catch finally raise throw throws package interface struct enum extends implements
    lambda yield pass print len dict list tuple set map todo fixme args kwargs param params value
    values result results data obj object item items tmp temp foo bar baz main init test tests
    """.split()
)

# Leading verbs stripped from identifiers ("getPointsBalance" -> "points balance").
ACCESSOR_VERBS = frozenset(
    """
    get set is has can should create update delete find fetch load save build make to from on
    handle compute calc calculate validate check apply process add remove parse read write send
    """.split()
)
# Trailing technical parts stripped from identifiers ("member_id" -> "member").
TECH_SUFFIXES = frozenset("id ids dto impl test tests spec mock stub".split())

ACRONYM_STOP = frozenset(
    """
    WHEN WHILE WHERE IF THEN SHALL SHOULD MAY MUST AND OR NOT THE TBD TBC TODO FIXME XXX NOTE
    OK ID IDS NA TLDR EOF EOL ASAP FYI PR PRS CI CD API URL URI UTF ISO IO OS
    GET POST PUT PATCH DELETE HEAD
    """.split()
)

CONNECTORS = frozenset({"of"})

URL_RE = re.compile(r"(?:https?|ftp)://\S+|www\.\S+|\b[\w.+-]+@[\w-]+\.[\w.]+\b")
# Work-product IDs (R-001, SH-01, CAN-012, R-031.AC2) are references, not terms.
ID_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Z]{1,4}-\d+(?:\.AC\d+)?(?![A-Za-z0-9_])")
IDENT_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    r"[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+"  # snake_case, CONSTANT_CASE
    r"|[a-z][a-z0-9]*(?:[A-Z][a-z0-9]*)+"  # camelCase
    r"|[A-Z][A-Z0-9]*[a-z][a-z0-9]*(?:[A-Z][A-Za-z0-9]*)+"  # PascalCase
    r"|[A-Z]{2,}[a-z][a-z0-9]*(?:[A-Z][A-Za-z0-9]*)*"  # POSClient
    r")(?![A-Za-z0-9_])"
)
IDENT_PART_RE = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")
ACRONYM_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Z][A-Z0-9]{1,4})(s?)(?![A-Za-z0-9_])")
SEGMENT_SPLIT_RE = re.compile(r"[.,;:!?()\[\]{}\"|<>=/\\*#`~+&%$@^“”‘’]+|\s-+\s|--+")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*[A-Za-z]|[A-Za-z]")

COLUMNS = ["Term", "Kind", "Count", "Files", "Variants", "In glossary", "Locations"]
KIND_ORDER = ["acronym", "identifier", "phrase", "word"]
MAX_LOCATIONS = 3
MAX_VARIANTS = 5
MAX_LINE_CHARS = 2000


# --------------------------------------------------------------------------- normalizing


def is_acronym(token: str) -> bool:
    """POS, CRM, PDPA, QR: 2 to 5 letters, all upper case. Longer upper-case words are shouting."""
    letters = [c for c in token if c.isalpha()]
    return 2 <= len(letters) <= 5 and token.isupper()


def singular(word: str) -> str:
    """Very small English singularizer, good enough to merge 'vouchers' and 'voucher'."""
    lower = word.lower()
    if len(lower) > 4 and lower.endswith("ies"):
        return word[:-3] + "y"
    if lower.endswith(("ss", "us", "is", "ics")) or len(lower) <= 3:
        return word
    if lower.endswith(("ches", "shes", "xes", "sses")):
        return word[:-2]
    if lower.endswith("s"):
        return word[:-1]
    return word


def form_of(words: Sequence[str]) -> str:
    """Display form: lowercase except acronyms, original plural."""
    return " ".join(w if is_acronym(w) else w.lower() for w in words)


def key_of(words: Sequence[str]) -> str:
    """Merge key: the display form with the last word singularized."""
    parts = [w if is_acronym(w) else w.lower() for w in words]
    if parts and not is_acronym(parts[-1]):
        parts[-1] = singular(parts[-1]).lower()
    return " ".join(parts)


def key_of_text(text: str) -> str:
    cleaned = re.sub(r"\([^)]*\)", " ", text)
    cleaned = re.sub(r"[*_`]", "", cleaned)
    words = [t[:-2] if t.lower().endswith("'s") else t for t in TOKEN_RE.findall(cleaned)]
    if len(words) == 1 and is_acronym(words[0]):
        return words[0]
    return key_of(words)


def identifier_words(ident: str) -> List[str]:
    constant = "_" in ident and ident.upper() == ident
    parts = IDENT_PART_RE.findall(ident.replace("_", " "))
    words: List[str] = []
    for part in parts:
        if part.isdigit() or len(part) < 2:
            continue
        words.append(part.lower() if constant or not is_acronym(part) else part)
    while words and words[0].lower() in ACCESSOR_VERBS:
        words = words[1:]
    while words and words[-1].lower() in TECH_SUFFIXES:
        words = words[:-1]
    return words


# --------------------------------------------------------------------------- counting


class Candidate:
    __slots__ = ("key", "count", "files", "forms", "surfaces", "kinds", "locations")

    def __init__(self, key: str) -> None:
        self.key = key
        self.count = 0
        self.files: Set[str] = set()
        self.forms: Counter = Counter()
        self.surfaces: Counter = Counter()
        self.kinds: Set[str] = set()
        self.locations: List[str] = []

    @property
    def term(self) -> str:
        best = sorted(self.forms.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))
        return best[0][0] if best else self.key

    @property
    def kind(self) -> str:
        return "+".join(k for k in KIND_ORDER if k in self.kinds)

    def variants(self) -> List[str]:
        ranked = sorted(self.surfaces.items(), key=lambda kv: (-kv[1], kv[0]))
        return [s for s, _ in ranked[:MAX_VARIANTS]]


class Miner:
    def __init__(self, max_words: int, kinds: Set[str], stopwords: Set[str]) -> None:
        self.max_words = max_words
        self.kinds = kinds
        self.stopwords = stopwords
        self.noise = frozenset(stopwords) | CODE_WORDS
        self.candidates: Dict[str, Candidate] = {}
        self.files_scanned = 0

    def _add(self, key: str, form: str, surface: str, kind: str, where: str, file: str) -> None:
        if kind not in self.kinds or not key:
            return
        cand = self.candidates.get(key)
        if cand is None:
            cand = self.candidates[key] = Candidate(key)
        cand.count += 1
        cand.files.add(file)
        cand.forms[form] += 1
        cand.surfaces[surface] += 1
        cand.kinds.add(kind)
        if len(cand.locations) < MAX_LOCATIONS and where not in cand.locations:
            cand.locations.append(where)

    def scan_line(self, line: str, file: str, lineno: int, code: bool = False) -> None:
        if len(line) > MAX_LINE_CHARS:
            return
        where = f"{file}:{lineno}"
        text = ID_RE.sub(" | ", URL_RE.sub(" | ", line))

        def take_identifier(match: "re.Match[str]") -> str:
            ident = match.group(0)
            words = identifier_words(ident)
            if 1 <= len(words) <= 4 and not all(w.lower() in self.noise for w in words):
                if len(words) > 1 or len(words[0]) >= 3:
                    self._add(key_of(words), form_of(words), ident, "identifier", where, file)
            return " | "

        text = IDENT_RE.sub(take_identifier, text)

        for match in ACRONYM_RE.finditer(text):
            acronym = match.group(1)
            if acronym in ACRONYM_STOP or sum(c.isalpha() for c in acronym) < 2:
                continue
            self._add(acronym, acronym, match.group(0), "acronym", where, file)

        prose_stop = self.noise if code else self.stopwords
        for segment in SEGMENT_SPLIT_RE.split(text):
            run: List[str] = []
            for raw in TOKEN_RE.findall(segment) + [""]:
                token = raw[:-2] if raw.lower().endswith("'s") else raw.strip("'-")
                lower = token.lower()
                keep = bool(token) and "'" not in token and (
                    lower in CONNECTORS
                    or (lower not in prose_stop and (len(token) >= 3 or is_acronym(token)))
                )
                if keep:
                    run.append(token)
                    continue
                self._emit_run(run, where, file)
                run = []

    def _emit_run(self, run: List[str], where: str, file: str) -> None:
        for start in range(len(run)):
            for size in range(1, self.max_words + 1):
                words = run[start : start + size]
                if len(words) < size:
                    break
                if words[0].lower() in CONNECTORS or words[-1].lower() in CONNECTORS:
                    continue
                if size == 1 and is_acronym(words[0]):
                    continue  # counted by the acronym pass
                kind = "word" if size == 1 else "phrase"
                self._add(key_of(words), form_of(words), " ".join(words), kind, where, file)

    def scan_file(self, path: Path, display: str, max_bytes: int) -> bool:
        try:
            if path.stat().st_size > max_bytes:
                return False
            raw = path.read_bytes()
        except OSError:
            return False
        if b"\0" in raw[:4096]:
            return False
        text = raw.decode("utf-8", errors="replace")
        code = path.suffix.lower().lstrip(".") in CODE_EXTS
        for lineno, line in enumerate(text.splitlines(), start=1):
            self.scan_line(line, display, lineno, code)
        self.files_scanned += 1
        return True


# --------------------------------------------------------------------------- files


def iter_files(paths: Sequence[str], exts: Set[str]) -> Iterable[Tuple[Path, str]]:
    seen: Set[Path] = set()
    for given in paths:
        root = Path(given)
        if root.is_file():
            resolved = root.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield root, root.as_posix()
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(root).parts[:-1]
            if any(part in SKIP_DIRS for part in rel_parts):
                continue
            if path.suffix.lower().lstrip(".") not in exts:
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield path, path.as_posix()


# --------------------------------------------------------------------------- glossary


def _split_row(line: str) -> List[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", text)]


def load_glossary(path: Path) -> Dict[str, str]:
    """Map candidate keys to 'term', 'synonym' or 'abbreviation' from a glossary.md table."""
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines[:-1]):
        if not line.strip().startswith("|"):
            continue
        header = [re.sub(r"[*_`]", "", c).strip().lower() for c in _split_row(line)]
        if "term" not in header or not re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            continue
        col = {name: idx for idx, name in enumerate(header)}
        known: Dict[str, str] = {}
        for row_line in lines[i + 2 :]:
            if not row_line.strip().startswith("|"):
                break
            cells = _split_row(row_line) + [""] * len(header)
            for column, label in (("abbreviation", "abbreviation"), ("synonyms", "synonym")):
                if column in col:
                    cell = re.sub(r"\([^)]*\)", " ", cells[col[column]])
                    for item in re.split(r"[,;/]", cell):
                        item = re.sub(r"\b(avoid|deprecated|do not use)\b", " ", item, flags=re.I)
                        key = key_of_text(item)
                        if key and key.lower() not in ("tbd", "none", "-"):
                            known.setdefault(key, label)
            term_key = key_of_text(cells[col["term"]])
            if term_key:
                known[term_key] = "term"
        return known
    raise ValueError(f"{path}: no Markdown table with a 'Term' column")


# --------------------------------------------------------------------------- output


def rows_for(cands: Sequence[Candidate], known: Optional[Dict[str, str]]) -> List[Dict[str, str]]:
    rows = []
    for cand in cands:
        status = "-" if known is None else known.get(cand.key, "no")
        rows.append(
            {
                "Term": cand.term,
                "Kind": cand.kind,
                "Count": str(cand.count),
                "Files": str(len(cand.files)),
                "Variants": "; ".join(cand.variants()),
                "In glossary": status,
                "Locations": " ".join(cand.locations),
            }
        )
    return rows


def render(rows: List[Dict[str, str]], fmt: str, meta: Dict) -> str:
    if fmt == "json":
        return json.dumps({**meta, "candidates": rows}, indent=2) + "\n"
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow([row[c] for c in COLUMNS])
        return buf.getvalue()
    if fmt == "md":
        out = ["| " + " | ".join(COLUMNS) + " |", "|" + " --- |" * len(COLUMNS)]
        for row in rows:
            cells = [row[c].replace("|", "\\|") for c in COLUMNS]
            out.append("| " + " | ".join(cells) + " |")
        return "\n".join(out) + "\n"
    widths = {c: max([len(c)] + [len(r[c]) for r in rows]) for c in COLUMNS[:-1]}
    lines = ["  ".join(c.ljust(widths[c]) for c in COLUMNS[:-1]) + "  Locations"]
    for row in rows:
        lines.append("  ".join(row[c].ljust(widths[c]) for c in COLUMNS[:-1]) + "  " + row["Locations"])
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mine_terms.py",
        description=(
            "Count candidate glossary terms (acronyms, code identifiers, prose words and phrases) "
            "across files and directories, merging case, plural and identifier-style variants."
        ),
        epilog=(
            "Exit codes: 0 = candidates listed (and, with --glossary, all of them are known); "
            "1 = with --glossary, at least one listed candidate is not in the glossary; "
            "2 = usage error, unreadable path, no files scanned, or glossary without a Term table. "
            "Example: python3 mine_terms.py README.md docs src --glossary requirements/glossary.md "
            "--format md --top 40"
        ),
    )
    parser.add_argument("paths", nargs="+", metavar="PATH", help="files or directories to scan (directories recursively)")
    parser.add_argument("--glossary", metavar="FILE", help="glossary.md to compare against; marks each candidate term, synonym, abbreviation or no")
    parser.add_argument("--only-new", action="store_true", help="list only candidates not in the glossary (needs --glossary)")
    parser.add_argument("--min-count", type=int, default=2, metavar="N", help="drop candidates seen fewer than N times (default 2)")
    parser.add_argument("--min-files", type=int, default=1, metavar="N", help="drop candidates found in fewer than N files (default 1)")
    parser.add_argument("--top", type=int, default=50, metavar="N", help="list at most N candidates, most frequent first; 0 = all (default 50)")
    parser.add_argument("--max-words", type=int, default=3, metavar="N", help="longest prose phrase in words, 1 to 4 (default 3)")
    parser.add_argument(
        "--kinds",
        default="acronym,identifier,phrase,word",
        help="comma-separated kinds to count: acronym, identifier, phrase, word (default all)",
    )
    parser.add_argument("--ext", metavar="EXT[,EXT]", help="file extensions to read inside directories, replacing the default list (md, txt, csv, py, ts, java, go, ...)")
    parser.add_argument("--stopwords", metavar="FILE", help="extra stopwords, one per line; lines starting with # are ignored")
    parser.add_argument("--max-bytes", type=int, default=1_000_000, metavar="N", help="skip files larger than N bytes (default 1000000)")
    parser.add_argument("--format", choices=["text", "csv", "json", "md"], default="text", help="output format (default text)")
    return parser


def run(args: argparse.Namespace) -> int:
    def fail(message: str) -> int:
        sys.stderr.write(f"mine_terms.py: error: {message}\n")
        return EXIT_USAGE

    if args.only_new and not args.glossary:
        return fail("--only-new needs --glossary")
    if not 1 <= args.max_words <= 4:
        return fail("--max-words must be between 1 and 4")
    if args.min_count < 1 or args.min_files < 1 or args.top < 0:
        return fail("--min-count and --min-files must be at least 1, --top at least 0")
    kinds = {k.strip() for k in args.kinds.split(",") if k.strip()}
    unknown = kinds - set(KIND_ORDER)
    if unknown or not kinds:
        return fail(f"unknown kind(s): {', '.join(sorted(unknown)) or '(none given)'}")
    missing = [p for p in args.paths if not Path(p).exists()]
    if missing:
        return fail(f"path not found: {', '.join(missing)}")

    stopwords = set(STOPWORDS)
    if args.stopwords:
        try:
            for line in Path(args.stopwords).read_text(encoding="utf-8").splitlines():
                word = line.strip().lower()
                if word and not word.startswith("#"):
                    stopwords.add(word)
        except OSError as exc:
            return fail(f"cannot read stopwords file: {exc}")

    known: Optional[Dict[str, str]] = None
    if args.glossary:
        gpath = Path(args.glossary)
        if not gpath.is_file():
            return fail(f"glossary not found: {args.glossary}")
        try:
            known = load_glossary(gpath)
        except (OSError, ValueError) as exc:
            return fail(str(exc))

    exts = DEFAULT_EXTS
    if args.ext:
        exts = frozenset(e.strip().lower().lstrip(".") for e in args.ext.split(",") if e.strip())

    miner = Miner(args.max_words, kinds, stopwords)
    glossary_path = Path(args.glossary).resolve() if args.glossary else None
    for path, display in iter_files(args.paths, set(exts)):
        if glossary_path is not None and path.resolve() == glossary_path:
            continue  # the glossary itself is not evidence of usage
        miner.scan_file(path, display, args.max_bytes)
    if miner.files_scanned == 0:
        return fail("no readable files found under the given paths")

    cands = [
        c for c in miner.candidates.values() if c.count >= args.min_count and len(c.files) >= args.min_files
    ]
    if args.only_new and known is not None:
        cands = [c for c in cands if c.key not in known]
    cands.sort(key=lambda c: (-c.count, -len(c.files), c.term))
    if args.top:
        cands = cands[: args.top]

    rows = rows_for(cands, known)
    meta = {"files_scanned": miner.files_scanned, "glossary": args.glossary or None}
    sys.stdout.write(render(rows, args.format, meta))
    new = sum(1 for r in rows if r["In glossary"] == "no")
    summary = f"scanned {miner.files_scanned} file(s); {len(rows)} candidate(s) listed"
    if known is not None:
        summary += f"; {new} not in the glossary"
    sys.stderr.write(summary + "\n")
    return EXIT_FINDINGS if known is not None and new else EXIT_OK


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
