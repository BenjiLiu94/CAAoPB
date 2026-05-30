#!/usr/bin/env python3
"""Analyze AB/BA uncertain samples in one or more FairEval result files."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def judge_name(path: Path) -> str:
    return path.stem.replace("faireval_", "").replace("_bpc", "")


def summarize_one(path: Path) -> list[str]:
    rows = read_csv(path)
    name = judge_name(path)
    uncertain = [row for row in rows if row["bpc_winner"] == "UNCERTAIN"]
    accepted = [row for row in rows if row["bpc_winner"] != "UNCERTAIN"]

    def human_counts(xs: list[dict]) -> dict:
        return dict(Counter(row["human"] for row in xs))

    def acc(xs: list[dict], pred: str) -> float:
        return sum(row[pred] == row["human"] for row in xs) / len(xs) if xs else float("nan")

    conflict_patterns = Counter()
    for row in uncertain:
        key = f"AB={row['naive_winner']}, BA={row['swapped_winner']}"
        conflict_patterns[key] += 1

    same_position = sum(
        row["ab_position_winner"] == row["ba_position_winner"]
        and row["ab_position_winner"] in {"first", "second"}
        for row in uncertain
    )

    lines = [
        f"## {name}",
        "",
        f"- Total samples: {len(rows)}",
        f"- Uncertain samples: {len(uncertain)}/{len(rows)} ({len(uncertain)/len(rows):.1%})",
        f"- Accepted samples: {len(accepted)}/{len(rows)} ({len(accepted)/len(rows):.1%})",
        f"- Human label distribution in uncertain: `{human_counts(uncertain)}`",
        f"- Human label distribution in accepted: `{human_counts(accepted)}`",
        f"- Naive accuracy on uncertain samples: {acc(uncertain, 'naive_winner'):.3f}",
        f"- Naive accuracy on accepted samples: {acc(accepted, 'naive_winner'):.3f}",
        f"- Conflict-aware accuracy on accepted samples: {acc(accepted, 'bpc_winner'):.3f}",
        f"- Same-position conflicts among uncertain: {same_position}/{len(uncertain)} ({same_position/len(uncertain) if uncertain else 0:.1%})",
        "",
        "### Top Conflict Patterns",
        "",
        "| Pattern | Count |",
        "| --- | ---: |",
    ]
    for pattern, count in conflict_patterns.most_common():
        lines.append(f"| `{pattern}` | {count} |")

    lines.extend(["", "### Uncertain Question IDs", "", "`" + ", ".join(row["question_id"] for row in uncertain) + "`", ""])
    return lines


def generate(paths: list[Path], output: Path) -> None:
    lines = [
        "# Uncertain Sample Analysis",
        "",
        "This report analyzes samples marked `UNCERTAIN` by conflict-aware AB/BA aggregation.",
        "",
    ]
    for path in paths:
        lines.extend(summarize_one(path))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Uncertain report written to {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/uncertain_analysis.md"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate(args.csv, args.output)


if __name__ == "__main__":
    main()
