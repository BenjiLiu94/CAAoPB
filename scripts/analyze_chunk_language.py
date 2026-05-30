#!/usr/bin/env python3
"""Aggregate chunk-language evaluation conditions by sample."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def aggregate(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["question_id"]].append(row)

    out = []
    for qid, items in sorted(grouped.items(), key=lambda kv: int(kv[0])):
        winners = [row["real_winner"] for row in items]
        counts = Counter(winners)
        non_tie = {winner for winner in winners if winner != "TIE"}
        if len(counts) == 1:
            final = winners[0]
        elif len(non_tie) == 1 and counts.most_common(1)[0][1] >= len(items) * 0.75:
            final = counts.most_common(1)[0][0]
        else:
            final = "UNCERTAIN"
        out.append(
            {
                "question_id": qid,
                "human": items[0]["human"],
                "conditions": len(items),
                "final_winner": final,
                "winner_counts": dict(counts),
                "consistent_rate": counts.most_common(1)[0][1] / len(items),
            }
        )
    return out


def generate(input_path: Path, output: Path) -> None:
    rows = read_csv(input_path)
    agg = aggregate(rows)
    accepted = [row for row in agg if row["final_winner"] != "UNCERTAIN"]
    acc = sum(row["final_winner"] == row["human"] for row in accepted) / len(accepted) if accepted else float("nan")
    coverage = len(accepted) / len(agg) if agg else 0.0

    lines = [
        "# Chunk-Language Analysis",
        "",
        f"- Input: `{input_path}`",
        f"- Samples: {len(agg)}",
        f"- Accuracy on accepted: {acc:.3f}",
        f"- Coverage: {coverage:.3f}",
        "",
        "## Per-Sample Aggregation",
        "",
        "| QID | Human | Final | Consistency | Winner counts |",
        "| ---: | --- | --- | ---: | --- |",
    ]
    for row in agg:
        lines.append(
            f"| {row['question_id']} | {row['human']} | {row['final_winner']} | {row['consistent_rate']:.3f} | `{row['winner_counts']}` |"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Chunk-language report written to {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/chunk_language_analysis.md"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(args.input, args.output)
