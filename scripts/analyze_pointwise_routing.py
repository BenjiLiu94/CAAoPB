#!/usr/bin/env python3
"""Analyze pointwise scoring and pointwise+AB/BA routing."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def by_qid(rows: list[dict]) -> dict[str, dict]:
    return {row["question_id"]: row for row in rows}


def acc(rows: list[dict], key: str, exclude_uncertain: bool = False) -> tuple[float, float, int]:
    xs = [row for row in rows if not (exclude_uncertain and row[key] == "UNCERTAIN")]
    if not xs:
        return float("nan"), 0.0, 0
    return sum(row[key] == row["human"] for row in xs) / len(xs), len(xs) / len(rows), len(xs)


def route(pointwise_row: dict, pairwise_row: dict, threshold: float) -> str:
    gap = abs(float(pointwise_row["score_gap"]))
    if gap >= threshold:
        return pointwise_row["pointwise_winner"]
    return pairwise_row["bpc_winner"]


def generate(pointwise_path: Path, pairwise_path: Path, output: Path, thresholds: list[float]) -> None:
    pointwise = by_qid(read_csv(pointwise_path))
    pairwise = by_qid(read_csv(pairwise_path))
    qids = sorted(set(pointwise) & set(pairwise), key=lambda x: int(x))
    rows = []
    for qid in qids:
        p = pointwise[qid]
        b = pairwise[qid]
        row = {
            "question_id": qid,
            "human": p["human"],
            "pointwise_winner": p["pointwise_winner"],
            "pairwise_conflict": b["bpc_winner"],
            "score_gap_abs": abs(float(p["score_gap"])),
        }
        for threshold in thresholds:
            row[f"route_{threshold}"] = route(p, b, threshold)
        rows.append(row)

    pointwise_acc, _, _ = acc(rows, "pointwise_winner")
    pairwise_acc, pairwise_cov, pairwise_n = acc(rows, "pairwise_conflict", exclude_uncertain=True)

    lines = [
        "# Pointwise Routing Analysis",
        "",
        f"- Pointwise: `{pointwise_path}`",
        f"- Pairwise conflict-aware: `{pairwise_path}`",
        f"- Overlap: {len(rows)} samples",
        "",
        "## Baselines On Overlap",
        "",
        "| Method | Accuracy | Coverage | Accepted n | Counts |",
        "| --- | ---: | ---: | ---: | --- |",
        f"| Pointwise only | {pointwise_acc:.3f} | 1.000 | {len(rows)} | `{dict(Counter(row['pointwise_winner'] for row in rows))}` |",
        f"| Conflict-aware AB/BA | {pairwise_acc:.3f} | {pairwise_cov:.3f} | {pairwise_n} | `{dict(Counter(row['pairwise_conflict'] for row in rows))}` |",
        "",
        "## Pointwise + AB/BA Tie-Break Routing",
        "",
        "If the absolute pointwise score gap is at least the threshold, accept the pointwise winner. Otherwise, use conflict-aware AB/BA.",
        "",
        "| Gap threshold | Accuracy excl. uncertain | Coverage | Accepted n | Counts |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]

    for threshold in thresholds:
        key = f"route_{threshold}"
        route_acc, route_cov, route_n = acc(rows, key, exclude_uncertain=True)
        lines.append(
            f"| {threshold:.2f} | {route_acc:.3f} | {route_cov:.3f} | {route_n} | `{dict(Counter(row[key] for row in rows))}` |"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Pointwise routing report written to {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pointwise", type=Path, required=True)
    parser.add_argument("--pairwise", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/pointwise_routing.md"))
    parser.add_argument("--thresholds", nargs="+", type=float, default=[0.5, 1.0, 1.5, 2.0])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(args.pointwise, args.pairwise, args.output, args.thresholds)
