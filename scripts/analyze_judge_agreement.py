#!/usr/bin/env python3
"""Analyze agreement and routing between two FairEval judge result files."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def read_rows(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["question_id"]: row for row in csv.DictReader(handle)}


def judge_name(path: Path) -> str:
    return path.stem.replace("faireval_", "").replace("_bpc", "")


def route_pair(a: str, b: str) -> str:
    if a == b and a != "UNCERTAIN":
        return a
    return "UNCERTAIN"


def accuracy(rows: list[dict], pred_key: str) -> tuple[float, float, int]:
    accepted = [row for row in rows if row[pred_key] != "UNCERTAIN"]
    if not accepted:
        return float("nan"), 0.0, 0
    acc = sum(row[pred_key] == row["human"] for row in accepted) / len(accepted)
    return acc, len(accepted) / len(rows), len(accepted)


def generate(path_a: Path, path_b: Path, output: Path) -> None:
    name_a = judge_name(path_a)
    name_b = judge_name(path_b)
    rows_a = read_rows(path_a)
    rows_b = read_rows(path_b)
    qids = sorted(set(rows_a) & set(rows_b), key=lambda x: int(x))
    if not qids:
        raise SystemExit("No overlapping question_id values")

    rows = []
    for qid in qids:
        a = rows_a[qid]
        b = rows_b[qid]
        row = {
            "question_id": qid,
            "human": a["human"],
            f"{name_a}_naive": a["naive_winner"],
            f"{name_b}_naive": b["naive_winner"],
            f"{name_a}_conflict": a["bpc_winner"],
            f"{name_b}_conflict": b["bpc_winner"],
        }
        row["naive_ensemble"] = route_pair(row[f"{name_a}_naive"], row[f"{name_b}_naive"])
        row["conflict_ensemble"] = route_pair(row[f"{name_a}_conflict"], row[f"{name_b}_conflict"])
        rows.append(row)

    naive_acc, naive_cov, naive_n = accuracy(rows, "naive_ensemble")
    conflict_acc, conflict_cov, conflict_n = accuracy(rows, "conflict_ensemble")

    naive_agree = sum(row[f"{name_a}_naive"] == row[f"{name_b}_naive"] for row in rows) / len(rows)
    conflict_agree = sum(row[f"{name_a}_conflict"] == row[f"{name_b}_conflict"] for row in rows) / len(rows)

    conflict_both_uncertain = sum(
        row[f"{name_a}_conflict"] == "UNCERTAIN" and row[f"{name_b}_conflict"] == "UNCERTAIN"
        for row in rows
    )
    either_uncertain = sum(
        row[f"{name_a}_conflict"] == "UNCERTAIN" or row[f"{name_b}_conflict"] == "UNCERTAIN"
        for row in rows
    )

    lines = [
        "# Judge Agreement Routing",
        "",
        f"- Judge A: `{name_a}`",
        f"- Judge B: `{name_b}`",
        f"- Overlap: {len(rows)} samples",
        "",
        "## Agreement",
        "",
        "| Setting | Agreement rate |",
        "| --- | ---: |",
        f"| Naive winner | {naive_agree:.3f} |",
        f"| Conflict-aware winner | {conflict_agree:.3f} |",
        "",
        "## Ensemble Routing",
        "",
        "Accept a winner only when both judges produce the same non-uncertain winner.",
        "",
        "| Route | Accuracy on accepted | Coverage | Accepted n |",
        "| --- | ---: | ---: | ---: |",
        f"| Naive two-judge agreement | {naive_acc:.3f} | {naive_cov:.3f} | {naive_n} |",
        f"| Conflict-aware two-judge agreement | {conflict_acc:.3f} | {conflict_cov:.3f} | {conflict_n} |",
        "",
        "## Conflict-Aware Uncertainty Overlap",
        "",
        f"- Both judges uncertain: {conflict_both_uncertain}/{len(rows)} ({conflict_both_uncertain/len(rows):.1%})",
        f"- At least one judge uncertain: {either_uncertain}/{len(rows)} ({either_uncertain/len(rows):.1%})",
        "",
        "## Routed Prediction Counts",
        "",
        "| Route | Counts |",
        "| --- | --- |",
        f"| Naive two-judge agreement | `{dict(Counter(row['naive_ensemble'] for row in rows))}` |",
        f"| Conflict-aware two-judge agreement | `{dict(Counter(row['conflict_ensemble'] for row in rows))}` |",
        "",
    ]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Agreement report written to {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_a", type=Path)
    parser.add_argument("csv_b", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/judge_agreement.md"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate(args.csv_a, args.csv_b, args.output)


if __name__ == "__main__":
    main()
