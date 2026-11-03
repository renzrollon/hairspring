#!/usr/bin/env python3
"""Check a Mermaid stateDiagram-v2 for unreachable states, dead ends and state x event gaps.

Single-skill helper of the re-skills ``state-model`` skill. Stdlib only, Python 3.9+.

It reads one ``stateDiagram-v2`` block from a Markdown file (or a raw ``.mmd`` file), and the
state x event matrix table in the same Markdown file (a pipe table whose first header cell
contains both "state" and "event", for example ``State / event``). Every cell of that matrix
must be a transition (``-> Target``), ``ignored`` or ``impossible``.

Exit codes: 0 no findings, 1 findings, 2 usage or parse error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

PSEUDO = "[*]"

_ID = r"(?:\[\*\]|[A-Za-z_][A-Za-z0-9_]*)"
_STYLE = r"(?::::[A-Za-z0-9_-]+)?"
TRANSITION_RE = re.compile(
    rf"^(?P<src>{_ID}){_STYLE}\s*-->\s*(?P<dst>{_ID}){_STYLE}\s*(?::(?P<label>.*))?$"
)
LABEL_RE = re.compile(r"^(?P<event>[^\[/]*?)\s*(?:\[(?P<guard>[^\]]*)\])?\s*(?:/(?P<action>.*))?$")
STATE_AS_RE = re.compile(r'^state\s+"(?P<label>[^"]*)"\s+as\s+(?P<id>[A-Za-z_]\w*)\s*(?P<rest>.*)$')
STATE_DECL_RE = re.compile(r"^state\s+(?P<id>[A-Za-z_]\w*)\s*(?P<rest>.*)$")
STATE_DESC_RE = re.compile(r"^(?P<id>[A-Za-z_]\w*)" + _STYLE + r"\s*:\s*(?P<desc>.*)$")
NOTE_ONE_RE = re.compile(r"^note\s+(left|right)\s+of\s+\S+\s*:")
NOTE_START_RE = re.compile(r"^note\s+(left|right)\s+of\s+\S+\s*$")
ARROW_TARGET_RE = re.compile(r"(?:→|->)\s*(\[\*\]|[A-Za-z_][A-Za-z0-9_]*)")
SKIP_PREFIXES = (
    "%%", "direction ", "classDef ", "class ", "style ", "accTitle", "accDescr", "click ",
)
UNSUPPORTED_HINT = (
    "composite states, concurrency (--), and <<choice>>/<<fork>>/<<join>> pseudo-states are not "
    "supported; flatten the machine, use guards in transition labels, or model the sub-machine "
    "in its own block"
)

GAP, IGNORED, IMPOSSIBLE, TRANSITION, UNCLEAR = "gap", "ignored", "impossible", "transition", "unclear"


class ParseError(Exception):
    """The input cannot be checked (exit code 2)."""


class Transition:
    def __init__(self, src: str, dst: str, event: str, guard: str, action: str, line: int):
        self.src, self.dst, self.event, self.guard, self.action, self.line = (
            src, dst, event, guard, action, line,
        )

    def as_dict(self) -> Dict[str, object]:
        return {
            "from": self.src, "to": self.dst, "event": self.event,
            "guard": self.guard, "action": self.action, "line": self.line,
        }


class Machine:
    def __init__(self) -> None:
        self.states: List[str] = []
        self.labels: Dict[str, str] = {}
        self.first_line: Dict[str, int] = {}
        self.transitions: List[Transition] = []

    def add_state(self, state: str, line: int) -> None:
        if state == PSEUDO:
            return
        if state not in self.first_line:
            self.states.append(state)
            self.first_line[state] = line


# --------------------------------------------------------------------------- reading


def _fenced_blocks(lines: Sequence[str]) -> List[Tuple[str, List[Tuple[int, str]]]]:
    """Every fenced code block as (info string, [(line number, text), ...])."""
    blocks: List[Tuple[str, List[Tuple[int, str]]]] = []
    fence: Optional[str] = None
    info = ""
    body: List[Tuple[int, str]] = []
    for number, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if fence is None:
            match = re.match(r"^(`{3,}|~{3,})\s*(\S*)", stripped)
            if match:
                fence, info, body = match.group(1), match.group(2).lower(), []
            continue
        if stripped.startswith(fence) and stripped.strip(fence[0]) == "":
            blocks.append((info, body))
            fence = None
            continue
        body.append((number, raw))
    return blocks


def _significant(body: Sequence[Tuple[int, str]]) -> List[Tuple[int, str]]:
    """Drop front matter, blank lines and comments."""
    out: List[Tuple[int, str]] = []
    in_front = False
    for index, (number, raw) in enumerate(body):
        text = raw.strip()
        if index == 0 and text == "---":
            in_front = True
            continue
        if in_front:
            if text == "---":
                in_front = False
            continue
        if not text or text.startswith("%%"):
            continue
        out.append((number, text))
    return out


def find_state_blocks(text: str) -> List[List[Tuple[int, str]]]:
    lines = text.splitlines()
    blocks = []
    for info, body in _fenced_blocks(lines):
        if info != "mermaid":
            continue
        sig = _significant(body)
        if sig and sig[0][1].startswith("stateDiagram"):
            blocks.append(sig)
    if not blocks:
        sig = _significant(list(enumerate(lines, start=1)))
        if sig and sig[0][1].startswith("stateDiagram"):
            blocks.append(sig)
    return blocks


def parse_machine(block: Sequence[Tuple[int, str]]) -> Machine:
    machine = Machine()
    in_note = False
    for number, text in block[1:]:
        if in_note:
            if text.lower() == "end note":
                in_note = False
            continue
        if NOTE_ONE_RE.match(text):
            continue
        if NOTE_START_RE.match(text):
            in_note = True
            continue
        if text.startswith(SKIP_PREFIXES) or text == "direction":
            continue
        if text == "--" or text.endswith("{") or text == "}" or re.search(r"<<\w+>>", text):
            raise ParseError(f"line {number}: unsupported construct {text!r}: {UNSUPPORTED_HINT}")
        if "-->" in text:
            match = TRANSITION_RE.match(text)
            if not match:
                raise ParseError(
                    f"line {number}: cannot parse transition {text!r}; expected "
                    "'From --> To : event [guard] / action' with identifier state names"
                )
            label = (match.group("label") or "").strip()
            parts = LABEL_RE.match(label)
            event = guard = action = ""
            if parts:
                event = (parts.group("event") or "").strip()
                guard = (parts.group("guard") or "").strip()
                action = (parts.group("action") or "").strip()
            src, dst = match.group("src"), match.group("dst")
            machine.add_state(src, number)
            machine.add_state(dst, number)
            machine.transitions.append(Transition(src, dst, event, guard, action, number))
            continue
        match = STATE_AS_RE.match(text)
        if match:
            if match.group("rest").strip():
                raise ParseError(f"line {number}: unsupported construct {text!r}: {UNSUPPORTED_HINT}")
            machine.add_state(match.group("id"), number)
            machine.labels[match.group("id")] = match.group("label")
            continue
        match = STATE_DECL_RE.match(text)
        if match:
            if match.group("rest").strip():
                raise ParseError(f"line {number}: unsupported construct {text!r}: {UNSUPPORTED_HINT}")
            machine.add_state(match.group("id"), number)
            continue
        match = STATE_DESC_RE.match(text)
        if match:
            machine.add_state(match.group("id"), number)
            continue
        raise ParseError(f"line {number}: cannot parse {text!r}")
    return machine


# --------------------------------------------------------------------------- matrix table


def _split_row(line: str) -> List[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    cells, buf, in_code, i = [], [], False, 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text) and text[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def _clean(cell: str) -> str:
    return re.sub(r"[`*_]", "", cell).strip()


def _key(name: str) -> str:
    return re.sub(r"\s+", " ", _clean(name)).lower()


class Matrix:
    def __init__(self) -> None:
        self.events: List[str] = []
        self.rows: Dict[str, Dict[str, str]] = {}
        self.row_names: Dict[str, str] = {}
        self.row_line: Dict[str, int] = {}
        self.line = 0


def find_matrix(text: str) -> Optional[Matrix]:
    lines = text.splitlines()
    in_fence = False
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence or not stripped.startswith("|") or i + 1 >= len(lines):
            i += 1
            continue
        header = _split_row(lines[i])
        separator = _split_row(lines[i + 1])
        is_table = all(re.match(r"^:?-+:?$", c.replace(" ", "")) for c in separator if c) and any(separator)
        first = _key(header[0]) if header else ""
        if is_table and "state" in first and "event" in first:
            matrix = Matrix()
            matrix.line = i + 1
            matrix.events = [_clean(h) for h in header[1:]]
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = _split_row(lines[j])
                name = _clean(cells[0]) if cells else ""
                if name:
                    k = _key(name)
                    matrix.row_names[k] = name
                    matrix.row_line[k] = j + 1
                    matrix.rows[k] = {
                        _key(ev): (cells[n + 1] if n + 1 < len(cells) else "")
                        for n, ev in enumerate(matrix.events)
                    }
                j += 1
            return matrix
        i += 1
    return None


def classify_cell(cell: Optional[str]) -> str:
    value = _clean(cell or "").lower()
    if value in ("", "?", "-", "—", "–", "n/a") or value.startswith("tbd"):
        return GAP
    if value == "ignore" or value.startswith("ignored") or value.startswith("ignore "):
        return IGNORED
    if value.startswith("impossible"):
        return IMPOSSIBLE
    if value.startswith("→") or value.startswith("->"):
        return TRANSITION
    return UNCLEAR


# --------------------------------------------------------------------------- analysis


def _finding(kind: str, message: str, line: int, state: str = "", event: str = "") -> Dict[str, object]:
    return {"kind": kind, "state": state, "event": event, "line": line, "message": message}


def _cell_text(transitions: Sequence[Transition]) -> str:
    parts = []
    for t in transitions:
        if t.guard.lower() == "else":
            parts.append(f"else → {t.dst}")
        elif t.guard:
            parts.append(f"→ {t.dst} [{t.guard}]")
        else:
            parts.append(f"→ {t.dst}")
    plain = [p for p in parts if not p.startswith("else")]
    other = [p for p in parts if p.startswith("else")]
    return "; ".join(plain + other)


def events_of(machine: Machine, matrix: Optional[Matrix]) -> List[str]:
    events: List[str] = []
    seen = set()
    for t in machine.transitions:
        if t.src != PSEUDO and t.event and _key(t.event) not in seen:
            seen.add(_key(t.event))
            events.append(t.event)
    for ev in (matrix.events if matrix else []):
        if ev and _key(ev) not in seen:
            seen.add(_key(ev))
            events.append(ev)
    return events


def analyze(machine: Machine, matrix: Optional[Matrix]) -> Tuple[List[Dict[str, object]], List[str]]:
    findings: List[Dict[str, object]] = []
    states = machine.states
    outgoing: Dict[str, List[Transition]] = {s: [] for s in states}
    for t in machine.transitions:
        if t.src != PSEUDO:
            outgoing[t.src].append(t)

    initial = [t.dst for t in machine.transitions if t.src == PSEUDO and t.dst != PSEUDO]
    final = {t.src for t in machine.transitions if t.dst == PSEUDO and t.src != PSEUDO}
    if not initial:
        findings.append(_finding("no-initial-state", "no '[*] --> State' transition", 0))

    reachable = set()
    queue = list(initial)
    while queue:
        state = queue.pop()
        if state in reachable or state == PSEUDO:
            continue
        reachable.add(state)
        queue.extend(t.dst for t in outgoing.get(state, []))
    if initial:
        for s in states:
            if s not in reachable:
                findings.append(_finding(
                    "unreachable-state", f"{s} cannot be reached from the initial state",
                    machine.first_line[s], state=s))

    for s in states:
        exits = [t for t in outgoing[s] if t.dst != s]
        if s not in final and not exits:
            findings.append(_finding(
                "dead-end",
                f"{s} is not final (no '{s} --> [*]') and has no transition to another state",
                machine.first_line[s], state=s))
        loops = [t for t in outgoing[s] if t.dst == s]
        if len(loops) > 1:
            findings.append(_finding(
                "multiple-self-transitions",
                f"{s} has {len(loops)} self-transitions; Mermaid draws only one, so readers miss the "
                "others. A second reaction without a state change usually means a separate state",
                loops[1].line, state=s))

    events = events_of(machine, matrix)
    for s in states:
        for ev in events:
            ts = [t for t in outgoing[s] if _key(t.event) == _key(ev)]
            if len(ts) > 1:
                guards = [t.guard.lower() for t in ts]
                if any(not g for g in guards) or len(set(guards)) != len(guards):
                    findings.append(_finding(
                        "ambiguous-transition",
                        f"{s} x {ev}: {len(ts)} transitions and the guards do not tell them apart",
                        ts[0].line, state=s, event=ev))

    if matrix is None and events:
        findings.append(_finding(
            "no-matrix",
            "no state x event matrix table found (first header cell must contain 'state' and "
            "'event'); run with --print-matrix to generate one",
            0))
    elif matrix is not None:
        known = {_key(s) for s in states} | {_key(v) for v in machine.labels.values()}
        for k, name in matrix.row_names.items():
            if k not in known:
                findings.append(_finding(
                    "matrix-unknown-state", f"matrix row {name!r} is not a state in the diagram",
                    matrix.row_line[k], state=name))

    for s in states:
        row = None
        row_line = matrix.line if matrix else machine.first_line[s]
        if matrix is not None:
            for k in (_key(s), _key(machine.labels.get(s, ""))):
                if k and k in matrix.rows:
                    row, row_line = matrix.rows[k], matrix.row_line[k]
                    break
        for ev in events:
            ts = [t for t in outgoing[s] if _key(t.event) == _key(ev)]
            cell = row.get(_key(ev)) if row is not None else None
            kind = classify_cell(cell)
            shown = f" (cell: {cell!r})" if cell else ""
            where = f"{s} x {ev}"
            if not ts:
                if kind == GAP:
                    findings.append(_finding(
                        "matrix-gap",
                        f"{where}: no transition and not marked 'ignored' or 'impossible'{shown}",
                        row_line, state=s, event=ev))
                elif kind == TRANSITION:
                    findings.append(_finding(
                        "matrix-mismatch",
                        f"{where}: matrix names a transition but the diagram has none{shown}",
                        row_line, state=s, event=ev))
                elif kind == UNCLEAR:
                    findings.append(_finding(
                        "matrix-unclear-cell",
                        f"{where}: start the cell with '→ Target', 'ignored' or 'impossible'{shown}",
                        row_line, state=s, event=ev))
                continue
            expected = _cell_text(ts)
            if matrix is None:
                continue
            if kind != TRANSITION:
                findings.append(_finding(
                    "matrix-mismatch",
                    f"{where}: diagram has {expected!r} but the matrix cell does not{shown}",
                    row_line, state=s, event=ev))
                continue
            named = set(ARROW_TARGET_RE.findall(_clean(cell or "")))
            if named != {t.dst for t in ts}:
                findings.append(_finding(
                    "matrix-mismatch",
                    f"{where}: diagram has {expected!r} but the matrix cell names "
                    f"{', '.join(sorted(named)) or 'no target'}{shown}",
                    row_line, state=s, event=ev))
                continue
            all_guarded = all(t.guard for t in ts)
            has_else = any(t.guard.lower() == "else" for t in ts)
            if all_guarded and not has_else and "else" not in _clean(cell or "").lower():
                findings.append(_finding(
                    "guard-without-else",
                    f"{where}: every transition is guarded; add an [else] transition or say "
                    f"'; else ignored' / '; else impossible' in the cell{shown}",
                    row_line, state=s, event=ev))
    return findings, events


# --------------------------------------------------------------------------- output


def render_matrix(machine: Machine, matrix: Optional[Matrix], events: Sequence[str]) -> str:
    header = ["State / event", *events]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    for s in machine.states:
        row = matrix.rows.get(_key(s)) if matrix else None
        cells = [s]
        for ev in events:
            ts = [t for t in machine.transitions if t.src == s and _key(t.event) == _key(ev)]
            if ts:
                text = _cell_text(ts)
                if all(t.guard for t in ts) and not any(t.guard.lower() == "else" for t in ts):
                    text += "; else TBD"
                cells.append(text)
                continue
            old = row.get(_key(ev), "") if row else ""
            cells.append(old if classify_cell(old) in (IGNORED, IMPOSSIBLE) else "TBD")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _count(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_states.py",
        description=(
            "Check a Mermaid stateDiagram-v2 block for unreachable states, dead ends (non-final "
            "states with no way out), ambiguous transitions and gaps in the state x event matrix. "
            "Transitions are read as 'From --> To : event [guard] / action'; '[*]' marks the "
            "initial and final pseudo-states. Composite states, concurrency and "
            "choice/fork/join pseudo-states are not supported (exit 2)."
        ),
        epilog="Exit codes: 0 no findings, 1 findings, 2 usage or parse error.",
    )
    parser.add_argument("file", help="Markdown file with a ```mermaid stateDiagram-v2 block, or a raw .mmd file")
    parser.add_argument("--block", type=int, default=1, metavar="N",
                        help="which stateDiagram block in the file to check, counting from 1 (default: 1)")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="text (default, one finding per line) or json (machine-readable)")
    parser.add_argument("--print-matrix", action="store_true",
                        help="print a Markdown state x event matrix built from the diagram (cells "
                             "already marked ignored/impossible are kept, others are TBD) and exit 0")
    return parser


def run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"check_states.py: cannot read {path}: {exc}\n")
        return 2
    blocks = find_state_blocks(text)
    if not blocks:
        sys.stderr.write(f"check_states.py: {path}: no mermaid stateDiagram block found\n")
        return 2
    if args.block < 1 or args.block > len(blocks):
        sys.stderr.write(f"check_states.py: {path}: --block {args.block} out of range (1..{len(blocks)})\n")
        return 2
    try:
        machine = parse_machine(blocks[args.block - 1])
    except ParseError as exc:
        sys.stderr.write(f"check_states.py: {path}: {exc}\n")
        return 2
    matrix = find_matrix(text) if path.suffix.lower() in (".md", ".markdown") else None
    findings, events = analyze(machine, matrix)
    if args.print_matrix:
        print(render_matrix(machine, matrix, events))
        return 0
    if args.format == "json":
        print(json.dumps({
            "file": str(path),
            "states": machine.states,
            "events": events,
            "initial": [t.dst for t in machine.transitions if t.src == PSEUDO],
            "final": sorted({t.src for t in machine.transitions if t.dst == PSEUDO}),
            "transitions": [t.as_dict() for t in machine.transitions],
            "findings": findings,
        }, indent=2))
    else:
        print(f"{path}: {_count(len(machine.states), 'state')}, {_count(len(events), 'event')}, "
              f"{_count(len(machine.transitions), 'transition')}")
        for f in findings:
            where = f"{path}:{f['line']}" if f["line"] else str(path)
            print(f"{where}: {f['kind']}: {f['message']}")
        print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:  # arrows in the output must not crash a non-UTF-8 console
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
