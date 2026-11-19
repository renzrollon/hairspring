#!/usr/bin/env python3
"""Compute a weighted prioritization matrix (Wiegers or WSJF) with rank and tie flags.

Usage::

    re-lint prioritize ITEMS.csv [--method wiegers|wsjf] [--weights benefit=2,penalty=1,cost=1,risk=0.5]
                       [--tie-band 0.05] [--out FILE] [--format md|csv|json]

Input is a ``.csv`` (or a Markdown table) with one row per item. Headers are matched
case-insensitively, ignoring spaces, ``_`` and ``-`` (``Business Value`` = ``business_value`` =
``BusinessValue``):

``wiegers``  ``ID``, ``Benefit``, ``Penalty``, ``Cost``, ``Risk`` (``Title`` optional; ``Relative
             Benefit`` etc. accepted). Relative scores, usually 1-9.
``wsjf``     ``ID``, ``BusinessValue``, ``TimeCriticality``, ``RiskReduction`` (also ``RR|OE``),
             ``JobSize`` (``Title`` optional).

Wiegers (Software Requirements, "First Things First"): ``value = benefit*wb + penalty*wp``;
``value%``, ``cost%`` and ``risk%`` are each item's share of the column total; the score is
``value% / (cost%*wc + risk%*wr)``. Default weights: benefit 2, penalty 1, cost 1, risk 0.5.

WSJF: ``(business value*w1 + time criticality*w2 + risk reduction*w3) / (job size*w4)``; weights
``business_value``, ``time_criticality``, ``risk_reduction``, ``job_size`` default to 1.

A row whose ID is ``Weights`` (or ``Weight``) sets the weights from its cells; ``--weights``
overrides it per key. The row is kept at the top of the output.

Items are ranked by score (equal scores share a rank). Neighbours whose scores differ by at
most ``--tie-band`` (relative to the larger score, default 0.05 = 5%) form a tie group, chained
along the ranking, and get ``Tie = "tie, do not over-interpret"``. The output CSV is the input
columns plus ``Score``, ``Rank``, ``Tie`` (replaced if already present), sorted by rank.

Exit codes: 0 ok, 2 usage or input error (missing column, non-numeric or negative score,
zero cost or job size).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

if not __package__:  # run as a plain script: make the sibling reqio.py importable
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # inside the package
    from . import reqio
except ImportError:  # vendored next to reqio.py in a skill's scripts/
    import reqio

TIE_TEXT = "tie, do not over-interpret"
WEIGHT_ROW_IDS = {"weights", "weight"}

# canonical field -> accepted header spellings (normalized: lower case, alphanumerics only)
ALIASES: Dict[str, List[str]] = {
    "id": ["id", "itemid", "requirementid", "requirement", "key"],
    "title": ["title", "name", "item", "feature", "summary"],
    "benefit": ["benefit", "relativebenefit"],
    "penalty": ["penalty", "relativepenalty"],
    "cost": ["cost", "relativecost"],
    "risk": ["risk", "relativerisk"],
    "business_value": ["businessvalue", "userbusinessvalue", "ubv", "bv"],
    "time_criticality": ["timecriticality", "tc"],
    "risk_reduction": ["riskreduction", "rroe", "riskreductionopportunityenablement",
                       "riskreductionandopportunityenablement", "rr"],
    "job_size": ["jobsize", "size", "js"],
}
METHODS = {
    "wiegers": {
        "fields": ["benefit", "penalty", "cost", "risk"],
        "weights": {"benefit": 2.0, "penalty": 1.0, "cost": 1.0, "risk": 0.5},
        "positive": ["cost"],
        "decimals": 3,
    },
    "wsjf": {
        "fields": ["business_value", "time_criticality", "risk_reduction", "job_size"],
        "weights": {"business_value": 1.0, "time_criticality": 1.0, "risk_reduction": 1.0, "job_size": 1.0},
        "positive": ["job_size"],
        "decimals": 2,
    },
}
LABELS = {
    "id": "ID", "title": "Title", "benefit": "Benefit", "penalty": "Penalty", "cost": "Cost", "risk": "Risk",
    "business_value": "BusinessValue", "time_criticality": "TimeCriticality",
    "risk_reduction": "RiskReduction", "job_size": "JobSize",
}


class UsageError(Exception):
    """A problem the user can fix (exit 2)."""


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def map_columns(columns: Sequence[str]) -> Dict[str, str]:
    """Canonical field -> actual header, for the fields that are present."""
    by_norm: Dict[str, str] = {}
    for col in columns:
        by_norm.setdefault(_norm(col), col)
    out: Dict[str, str] = {}
    for field, aliases in ALIASES.items():
        for alias in aliases:
            if alias in by_norm and by_norm[alias] not in out.values():
                out[field] = by_norm[alias]
                break
    return out


def parse_number(raw: str) -> Optional[float]:
    text = (raw or "").strip().replace("−", "-")
    if re.match(r"^-?\d+,\d+$", text):
        text = text.replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def parse_weights(spec: Optional[str], method: str) -> Dict[str, float]:
    valid = METHODS[method]["weights"]
    out: Dict[str, float] = {}
    if not spec:
        return out
    by_norm = {_norm(k): k for k in valid}
    for part in [p for p in re.split(r"[,;]", spec) if p.strip()]:
        if "=" not in part:
            raise UsageError(f"--weights: {part.strip()!r} is not key=value (e.g. benefit=2,penalty=1,cost=1,risk=0.5)")
        key, value = part.split("=", 1)
        canon = by_norm.get(_norm(key))
        if canon is None:
            raise UsageError(f"--weights: unknown key {key.strip()!r} for {method}; use {', '.join(valid)}")
        number = parse_number(value)
        if number is None or number < 0:
            raise UsageError(f"--weights: {key.strip()} must be a number >= 0, got {value.strip()!r}")
        out[canon] = number
    return out


def _value(row: reqio.Row, field: str, header: str, label: str) -> float:
    raw = row.get_str(header)
    where = f"{label} (line {row.line})"
    if raw == "":
        raise UsageError(f"{where}: {header} is empty; score every item before running")
    number = parse_number(raw)
    if number is None:
        raise UsageError(f"{where}: {header} {raw!r} is not a number")
    if number < 0:
        raise UsageError(f"{where}: {header} {raw!r} is negative")
    return number


def score_items(rows: List[reqio.Row], columns: Sequence[str], method: str, weights_arg: Dict[str, float],
                tie_band: float) -> Tuple[List[Dict], Dict[str, float], Optional[reqio.Row], List[str]]:
    """Scored items (sorted by rank), effective weights, the weights row and warnings."""
    spec = METHODS[method]
    mapping = map_columns(columns)
    missing = [LABELS[f] for f in ["id"] + spec["fields"] if f not in mapping]
    if missing:
        accepted = "; ".join(f"{LABELS[f]}: {', '.join(ALIASES[f])}" for f in ["id"] + spec["fields"])
        raise UsageError(
            f"missing column(s) for {method}: {', '.join(missing)} (found: {', '.join(columns) or 'none'}). "
            f"Accepted header names, case and spaces ignored: {accepted}"
        )
    warnings: List[str] = []
    weights = dict(spec["weights"])
    weight_row = None
    items: List[reqio.Row] = []
    for row in rows:
        if row.get_str(mapping["id"]).lower() in WEIGHT_ROW_IDS:
            weight_row = row
            continue
        items.append(row)
    if weight_row is not None:
        for field in spec["weights"]:
            if field in mapping and weight_row.get_str(mapping[field]):
                weights[field] = _value(weight_row, field, mapping[field], "Weights row")
    weights.update(weights_arg)
    if not items:
        raise UsageError("no items to prioritize")
    seen: Dict[str, int] = {}
    parsed: List[Tuple[reqio.Row, Dict[str, float]]] = []
    for row in items:
        rid = row.get_str(mapping["id"])
        if not rid:
            raise UsageError(f"line {row.line}: {mapping['id']} is empty")
        if rid in seen:
            warnings.append(f"{rid} appears twice (lines {seen[rid]} and {row.line})")
        seen.setdefault(rid, row.line)
        values = {f: _value(row, f, mapping[f], rid) for f in spec["fields"]}
        for f in spec["positive"]:
            if values[f] <= 0:
                raise UsageError(f"{rid} (line {row.line}): {mapping[f]} must be greater than 0 (it is a divisor)")
        if method == "wiegers":
            out_of_scale = [mapping[f] for f in spec["fields"] if not 1 <= values[f] <= 9]
            if out_of_scale:
                warnings.append(f"{rid}: {', '.join(out_of_scale)} outside the usual 1-9 relative scale")
        parsed.append((row, values))
    scores: List[float] = []
    if method == "wiegers":
        totals = {f: sum(v[f] for _, v in parsed) for f in ("cost", "risk")}
        value_of = [v["benefit"] * weights["benefit"] + v["penalty"] * weights["penalty"] for _, v in parsed]
        value_total = sum(value_of)
        if value_total <= 0:
            raise UsageError("cannot compute value percentages: weighted benefit and penalty sum to 0")
        for (row, v), value in zip(parsed, value_of):
            value_pct = value / value_total * 100
            cost_pct = v["cost"] / totals["cost"] * 100
            risk_pct = v["risk"] / totals["risk"] * 100 if totals["risk"] > 0 else 0.0
            denominator = cost_pct * weights["cost"] + risk_pct * weights["risk"]
            if denominator <= 0:
                raise UsageError("cost and risk weights are both 0 (or risk is 0 everywhere and cost weight is 0); "
                                 "the score would divide by zero")
            scores.append(value_pct / denominator)
    else:
        if weights["job_size"] <= 0:
            raise UsageError("--weights: job_size must be greater than 0 (it is a divisor)")
        for _, v in parsed:
            numerator = (v["business_value"] * weights["business_value"]
                         + v["time_criticality"] * weights["time_criticality"]
                         + v["risk_reduction"] * weights["risk_reduction"])
            scores.append(numerator / (v["job_size"] * weights["job_size"]))
    order = sorted(range(len(parsed)), key=lambda i: -scores[i])
    results: List[Dict] = []
    rank = 0
    previous: Optional[float] = None
    for position, i in enumerate(order, 1):
        if previous is None or not math.isclose(scores[i], previous, rel_tol=1e-9, abs_tol=1e-12):
            rank = position
        previous = scores[i]
        row = parsed[i][0]
        results.append({"row": row, "id": row.get_str(mapping["id"]),
                        "title": row.get_str(mapping["title"]) if "title" in mapping else "",
                        "score": scores[i], "rank": rank, "tie": False, "group": 0})
    group = 0
    for a, b in zip(results, results[1:]):
        top = max(abs(a["score"]), abs(b["score"]))
        if top == 0 or abs(a["score"] - b["score"]) <= tie_band * top + 1e-12:
            if not a["tie"]:
                group += 1
                a["tie"], a["group"] = True, group
            b["tie"], b["group"] = True, a["group"]
    return results, weights, weight_row, warnings


def _output_columns(columns: Sequence[str]) -> Tuple[List[str], Dict[str, str]]:
    names: Dict[str, str] = {}
    for wanted in ("Score", "Rank", "Tie"):
        names[wanted] = next((c for c in columns if _norm(c) == _norm(wanted)), wanted)
    out = list(columns) + [names[w] for w in ("Score", "Rank", "Tie") if names[w] not in columns]
    return out, names


def render_md(results: List[Dict], method: str, weights: Dict[str, float], tie_band: float, decimals: int) -> str:
    weight_text = ", ".join(f"{k}={weights[k]:g}" for k in METHODS[method]["weights"])
    out = [f"# Prioritization ({method})", "",
           f"- Weights: {weight_text}",
           f"- Tie band: {tie_band:g} (scores within {tie_band * 100:g}% of their neighbour are ties)",
           "- Scores are relative to this set of items; adding or removing an item changes them.", "",
           "| Rank | ID | Title | Score | Tie |", "| --- | --- | --- | --- | --- |"]
    for r in results:
        title = " ".join(r["title"].split()).replace("|", "\\|")
        out.append(f"| {r['rank']} | {r['id']} | {title} | {r['score']:.{decimals}f} | {TIE_TEXT if r['tie'] else ''} |")
    groups: Dict[int, List[str]] = {}
    for r in results:
        if r["tie"]:
            groups.setdefault(r["group"], []).append(r["id"])
    if groups:
        out += ["", "Tie groups (do not over-interpret the order inside a group):", ""]
        out += [f"- {', '.join(ids)}" for _, ids in sorted(groups.items())]
    return "\n".join(out) + "\n"


def cmd_prioritize(args: argparse.Namespace) -> int:
    path = Path(args.items)
    if not path.is_file():
        raise UsageError(f"{path} not found")
    if not 0 <= args.tie_band < 1:
        raise UsageError("--tie-band must be at least 0 and below 1 (0.05 means 5%)")
    try:
        table = reqio.read_table(path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise UsageError(f"cannot read {path}: {exc}") from exc
    if not table.columns:
        raise UsageError(f"{path} is empty")
    weights_arg = parse_weights(args.weights, args.method)
    results, weights, weight_row, warnings = score_items(table.rows, table.columns, args.method, weights_arg,
                                                         args.tie_band)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    decimals = METHODS[args.method]["decimals"]
    columns, names = _output_columns(table.columns)
    records: List[Dict[str, str]] = []
    if weight_row is not None:
        rec = dict(weight_row)
        rec.update({names["Score"]: "", names["Rank"]: "", names["Tie"]: ""})
        records.append(rec)
    for r in results:
        rec = dict(r["row"])
        rec.update({names["Score"]: f"{r['score']:.{decimals}f}", names["Rank"]: str(r["rank"]),
                    names["Tie"]: TIE_TEXT if r["tie"] else ""})
        records.append(rec)
    if args.out:
        reqio.write_csv(args.out, records, columns)
        print(f"wrote {args.out} ({len(results)} items)", file=sys.stderr)
    if args.format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(columns)
        for rec in records:
            writer.writerow([rec.get(c, "") for c in columns])
        print(buf.getvalue(), end="")
    elif args.format == "json":
        payload = {"method": args.method, "weights": weights, "tie_band": args.tie_band,
                   "items": [{"id": r["id"], "title": r["title"], "score": round(r["score"], decimals),
                              "rank": r["rank"], "tie": r["tie"], "tie_group": r["group"] or None} for r in results]}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_md(results, args.method, weights, args.tie_band, decimals), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank items with Wiegers' weighted benefit/penalty/cost/risk method or WSJF, and flag "
                    "near-ties so nobody over-reads small score differences.",
        epilog=(
            "Columns (case, spaces, '_' and '-' ignored):\n"
            "  wiegers: ID, Benefit, Penalty, Cost, Risk (Title optional), relative 1-9 scores\n"
            "  wsjf:    ID, BusinessValue, TimeCriticality, RiskReduction, JobSize (Title optional)\n"
            "A row with ID 'Weights' sets the weights; --weights overrides it.\n"
            "Output adds Score, Rank, Tie. Exit codes: 0 ok, 2 usage or input error."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("items", metavar="ITEMS.csv", help="items with criteria scores (.csv or a Markdown table)")
    parser.add_argument("--method", choices=sorted(METHODS), default="wiegers", help="scoring method (default wiegers)")
    parser.add_argument("--weights", metavar="K=V,...",
                        help="wiegers: benefit=2,penalty=1,cost=1,risk=0.5 (defaults); wsjf: business_value, "
                             "time_criticality, risk_reduction, job_size (default 1 each)")
    parser.add_argument("--tie-band", type=float, default=0.05, metavar="F",
                        help="relative score difference treated as a tie (default 0.05 = 5%%)")
    parser.add_argument("--out", metavar="FILE", help="write the scored CSV (input columns + Score, Rank, Tie)")
    parser.add_argument("--format", choices=("md", "csv", "json"), default="md",
                        help="what to print on stdout (default md: ranked table and tie groups)")
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        return cmd_prioritize(args)
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
