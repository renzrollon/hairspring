#!/usr/bin/env python3
"""Fill the result columns of a re-skills questionnaire analysis sheet from a forms export.

Stdlib only, Python 3.9+. Single-skill helper of `questionnaire-builder`.

Reads the questionnaire folder's form-import.csv (item definitions) and analysis.csv (the plan:
Item, Hypothesis, Metric, Threshold, MinN agreed before fielding), matches each item to a column
of the response export (Google Forms or Microsoft Forms, saved as CSV), and writes N, Missing,
Distribution, Value, Result and Notes back into analysis.csv.

Exit codes: 0 every planned item computed, 1 findings (an item, column or metric could not be
used), 2 usage or parse error.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

FORM_COLUMNS = ["ID", "Type", "Title", "HelpText", "Required", "Options",
                "ScaleMin", "ScaleMax", "MinLabel", "MaxLabel"]
ANALYSIS_COLUMNS = ["Item", "Hypothesis", "Metric", "Threshold", "MinN",
                    "N", "Missing", "Distribution", "Value", "Result", "Notes"]
TYPES = {"section", "scale", "single", "multi", "dropdown", "short", "paragraph"}
SHARE_METRICS = ("top2", "bottom2")
THRESHOLD = re.compile(r"^\s*(>=|<=|>|<|=)\s*(-?\d+(?:\.\d+)?)\s*(%)?\s*$")
UNSET = ("", "TBD")


class UsageError(Exception):
    """Input files are missing or malformed (exit 2)."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyze_responses.py",
        description=(
            "Compute the planned metric for every item in analysis.csv from a forms response "
            "export and write N, Missing, Distribution, Value, Result and Notes."
        ),
        epilog=(
            "Metrics: top2 and bottom2 (share of answers in the two highest or lowest scale "
            "points), median and mean (scale items), share:<option> (any closed item), themes "
            "(open items; counted only, coded by hand). Threshold: an operator and a number, "
            "for example '>=60%' for shares or '>=4' for a median; TBD leaves the result "
            "inconclusive. Exit codes: 0 all items computed, 1 findings, 2 usage or parse error."
        ),
    )
    parser.add_argument("folder", nargs="?", default=".",
                        help="questionnaire folder holding form-import.csv and analysis.csv (default: .)")
    parser.add_argument("--responses", required=True,
                        help="response export as CSV: one row per respondent, one column per question")
    parser.add_argument("--items", default=None, help="item definitions (default: <folder>/form-import.csv)")
    parser.add_argument("--analysis", default=None, help="analysis plan (default: <folder>/analysis.csv)")
    parser.add_argument("--out", default=None, help="where to write the filled sheet (default: overwrite --analysis)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="summary printed to stdout: text (default) or json")
    return parser


def _read_csv(path: Path, required: Sequence[str]) -> Tuple[List[str], List[Dict[str, str]]]:
    if not path.is_file():
        raise UsageError(f"{path} not found")
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    try:
        header = [h.strip() for h in next(reader)]
    except StopIteration:
        raise UsageError(f"{path}: empty file")
    missing = [c for c in required if c not in header]
    if missing:
        raise UsageError(f"{path}: missing columns {', '.join(missing)}")
    rows = []
    for record in reader:
        if not any(c.strip() for c in record):
            continue
        record += [""] * (len(header) - len(record))
        rows.append({h: record[i] for i, h in enumerate(header)})
    return header, rows


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _options(item: Dict[str, str]) -> List[str]:
    return [o.strip() for o in item.get("Options", "").split("|") if o.strip()]


def _find_column(item: Dict[str, str], header: List[str]) -> Optional[int]:
    title = _norm(item["Title"])
    for i, h in enumerate(header):
        if _norm(h) == title:
            return i
    prefix = re.compile(rf"^{re.escape(item['ID'].strip())}(?:[\s.:)\-]|$)", re.I)
    for i, h in enumerate(header):
        if prefix.match(h.strip()):
            return i
    return None


def parse_threshold(text: str, share: bool) -> Optional[Tuple[str, float]]:
    """``(operator, value)``; ``None`` when not agreed (empty or TBD). Shares become fractions."""
    if text.strip().upper() in UNSET:
        return None
    m = THRESHOLD.match(text)
    if not m:
        raise ValueError(f"threshold {text!r} is not like '>=60%' or '>=4'")
    value = float(m.group(2))
    if m.group(3):
        value /= 100
    elif share and value > 1:
        raise ValueError(f"threshold {text!r} for a share must be a percentage, e.g. '>=60%'")
    return m.group(1), value


def _compare(value: float, op: str, target: float) -> bool:
    value, target = round(value, 6), round(target, 6)
    return {">=": value >= target, "<=": value <= target, ">": value > target,
            "<": value < target, "=": value == target}[op]


def _fmt_share(x: float) -> str:
    return f"{x * 100:.1f}%"


def _fmt_num(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _contains(answer: str, option: str) -> bool:
    pattern = rf"(?:^|[;,]\s*){re.escape(option)}\s*(?:$|[;,])"
    return re.search(pattern, answer.strip()) is not None


def compute(item: Dict[str, str], metric: str, answers: List[str]):
    """Return ``(n, missing, distribution, value, is_share, notes)`` or raise ValueError."""
    kind = item["Type"].strip()
    notes: List[str] = []
    given = [a.strip() for a in answers if a.strip()]
    missing = len(answers) - len(given)
    if kind in ("short", "paragraph"):
        if metric != "themes":
            raise ValueError(f"metric {metric!r} needs a closed item; use 'themes' for {kind}")
        return len(given), missing, "", None, False, ["code themes by hand"]
    if metric == "themes":
        raise ValueError("metric 'themes' is for open items (short, paragraph)")
    if kind == "scale":
        try:
            lo, hi = int(item["ScaleMin"]), int(item["ScaleMax"])
        except ValueError:
            raise ValueError("scale item needs integer ScaleMin and ScaleMax")
        values: List[int] = []
        bad = 0
        for a in given:
            try:
                v = int(float(a))
            except ValueError:
                bad += 1
                continue
            if lo <= v <= hi:
                values.append(v)
            else:
                bad += 1
        if bad:
            notes.append(f"{bad} answer(s) not on the {lo}-{hi} scale ignored")
        n = len(values)
        dist = "; ".join(f"{p}={values.count(p)}" for p in range(lo, hi + 1))
        if n == 0:
            return 0, missing, dist, None, metric.startswith(("top", "bottom", "share")), notes
        if metric == "top2":
            return n, missing, dist, sum(v >= hi - 1 for v in values) / n, True, notes
        if metric == "bottom2":
            return n, missing, dist, sum(v <= lo + 1 for v in values) / n, True, notes
        if metric == "median":
            return n, missing, dist, float(statistics.median(values)), False, notes
        if metric == "mean":
            return n, missing, dist, float(statistics.mean(values)), False, notes
        if metric.startswith("share:"):
            target = metric.split(":", 1)[1].strip()
            try:
                t = int(target)
            except ValueError:
                raise ValueError(f"share:{target} is not a point of the {lo}-{hi} scale")
            return n, missing, dist, values.count(t) / n, True, notes
        raise ValueError(f"unknown metric {metric!r} for a scale item")
    if kind in ("single", "dropdown", "multi"):
        options = _options(item)
        if not options:
            raise ValueError(f"{kind} item has no Options")
        if metric in SHARE_METRICS or metric in ("median", "mean"):
            raise ValueError(f"metric {metric!r} needs a scale item; use share:<option>")
        if not metric.startswith("share:"):
            raise ValueError(f"unknown metric {metric!r}")
        target = metric.split(":", 1)[1].strip()
        if target not in options:
            raise ValueError(f"share:{target} is not one of the item's Options")
        if kind == "multi":
            counts = {o: sum(_contains(a, o) for a in given) for o in options}
        else:
            counts = {o: sum(a == o for a in given) for o in options}
            other = len(given) - sum(counts.values())
            if other:
                notes.append(f"{other} answer(s) outside the options")
        n = len(given)
        dist = "; ".join(f"{o}={c}" for o, c in counts.items())
        value = counts[target] / n if n else None
        return n, missing, dist, value, True, notes
    raise ValueError(f"item type {kind!r} cannot be analyzed")


def analyze(items_path: Path, analysis_path: Path, responses_path: Path):
    _, items = _read_csv(items_path, FORM_COLUMNS)
    a_header, plan = _read_csv(analysis_path, ["Item", "Hypothesis", "Metric", "Threshold", "MinN"])
    if not responses_path.is_file():
        raise UsageError(f"{responses_path} not found")
    text = responses_path.read_text(encoding="utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    try:
        r_header = next(reader)
    except StopIteration:
        raise UsageError(f"{responses_path}: empty file")
    responses = [r + [""] * (len(r_header) - len(r)) for r in reader if any(c.strip() for c in r)]

    by_id = {i["ID"].strip(): i for i in items if i["ID"].strip()}
    findings: List[str] = []
    for i in items:
        if i["Type"].strip() not in TYPES:
            findings.append(f"{i['ID']}: unknown Type {i['Type']!r}")
    titles = [_norm(i["Title"]) for i in items if i["Type"].strip() != "section"]
    for t in sorted({t for t in titles if titles.count(t) > 1}):
        findings.append(f"duplicate question title {t!r}: titles must be unique to match the export")

    out_rows: List[Dict[str, str]] = []
    for row in plan:
        row = {c: row.get(c, "") for c in ANALYSIS_COLUMNS}
        for c in ("N", "Missing", "Distribution", "Value", "Result", "Notes"):
            row[c] = ""
        item_id = row["Item"].strip()
        item = by_id.get(item_id)
        metric = row["Metric"].strip()
        if item is None:
            row["Notes"] = "item not in form-import.csv"
            findings.append(f"{item_id}: not in {items_path.name}")
            out_rows.append(row)
            continue
        col = _find_column(item, r_header)
        if col is None:
            row["Notes"] = "response column not found"
            findings.append(f"{item_id}: no column titled {item['Title']!r} in {responses_path.name}")
            out_rows.append(row)
            continue
        answers = [r[col] for r in responses]
        try:
            n, missing, dist, value, is_share, notes = compute(item, metric, answers)
            threshold = None if metric == "themes" else parse_threshold(row["Threshold"], is_share)
        except ValueError as exc:
            row["Notes"] = str(exc)
            findings.append(f"{item_id}: {exc}")
            out_rows.append(row)
            continue
        row["N"], row["Missing"], row["Distribution"] = str(n), str(missing), dist
        if value is not None:
            row["Value"] = _fmt_share(value) if is_share else _fmt_num(value)
        min_n = row["MinN"].strip()
        if metric == "themes":
            row["Result"] = "manual"
        elif threshold is None:
            row["Result"] = "inconclusive"
            notes.append("threshold not agreed")
        elif min_n.upper() in UNSET:
            row["Result"] = "inconclusive"
            notes.append("MinN not agreed")
        elif not min_n.isdigit():
            row["Notes"] = f"MinN {min_n!r} is not a whole number"
            findings.append(f"{item_id}: MinN {min_n!r} is not a whole number")
            out_rows.append(row)
            continue
        elif n < int(min_n) or value is None:
            row["Result"] = "inconclusive"
            notes.append(f"N below MinN ({n} < {min_n})")
        else:
            row["Result"] = "supported" if _compare(value, *threshold) else "not supported"
        row["Notes"] = "; ".join(notes)
        out_rows.append(row)
    columns = a_header if a_header[: len(ANALYSIS_COLUMNS)] == ANALYSIS_COLUMNS else ANALYSIS_COLUMNS
    return columns, out_rows, findings, len(responses)


def _write(path: Path, columns: Sequence[str], rows: List[Dict[str, str]]) -> None:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(list(columns))
    for row in rows:
        writer.writerow([row.get(c, "") for c in columns])
    path.write_text(buf.getvalue(), encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    folder = Path(args.folder)
    items = Path(args.items) if args.items else folder / "form-import.csv"
    analysis = Path(args.analysis) if args.analysis else folder / "analysis.csv"
    out = Path(args.out) if args.out else analysis
    try:
        columns, rows, findings, respondents = analyze(items, analysis, Path(args.responses))
    except (UsageError, csv.Error, UnicodeDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    _write(out, columns, rows)
    if args.format == "json":
        print(json.dumps({"respondents": respondents, "out": str(out), "findings": findings,
                          "items": [{c: r[c] for c in ("Item", "Hypothesis", "Value", "Threshold", "Result")}
                                    for r in rows]}, indent=2))
    else:
        print(f"{respondents} respondent(s); wrote {out}")
        for r in rows:
            print(f"  {r['Item']:<6} {r['Hypothesis']:<5} value={r['Value'] or '-':<8} "
                  f"threshold={r['Threshold'] or '-':<8} {r['Result'] or 'not computed'}")
        for f in findings:
            print(f"finding: {f}")
    return 1 if findings else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
