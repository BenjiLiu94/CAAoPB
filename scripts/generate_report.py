#!/usr/bin/env python3
"""Generate a Markdown report from a FairEval BPC CSV result file.

Example:
    python3 scripts/generate_report.py results/faireval_deepseek-v4-flash_bpc.csv
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import statistics
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def to_float(val: str) -> float:
    return float(val)


def true_winner_from_order(order: str, winner_position: str) -> str:
    if winner_position == "tie":
        return "TIE"
    if order == "AB":
        return "CHATGPT" if winner_position == "first" else "VICUNA13B"
    return "VICUNA13B" if winner_position == "first" else "CHATGPT"


def win_value(label: str) -> int:
    if label == "CHATGPT":
        return 1
    if label == "VICUNA13B":
        return -1
    return 0


def permutation_test(wins: list[int], rounds: int = 10000, seed: int = 13) -> float:
    observed = abs(sum(wins))
    rng = random.Random(seed)
    extreme = 0
    for _ in range(rounds):
        total = 0
        for value in wins:
            if value == 0:
                continue
            total += value if rng.random() < 0.5 else -value
        if abs(total) >= observed:
            extreme += 1
    return (extreme + 1) / (rounds + 1)


def compute_faireval_bpc(rows: list[dict]) -> list[str]:
    """FairEval-style BPC: average scores across AB and BA."""
    winners = []
    for row in rows:
        chatgpt_avg = (to_float(row["ab_score_chatgpt"]) + to_float(row["ba_score_chatgpt"])) / 2
        vicuna_avg = (to_float(row["ab_score_vicuna13b"]) + to_float(row["ba_score_vicuna13b"])) / 2
        if chatgpt_avg > vicuna_avg:
            winners.append("CHATGPT")
        elif vicuna_avg > chatgpt_avg:
            winners.append("VICUNA13B")
        else:
            winners.append("TIE")
    return winners


def compute_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    labels = [row["human"] for row in rows]

    # --- Position metrics ---
    non_tie_ab = [row["ab_position_winner"] for row in rows if row["ab_position_winner"] in {"first", "second"}]
    first_position_win_rate = (
        sum(pos == "first" for pos in non_tie_ab) / len(non_tie_ab) if non_tie_ab else float("nan")
    )

    flips = sum(row["naive_winner"] != row["swapped_winner"] for row in rows)
    position_flip_rate = flips / n

    same_position_count = sum(
        row["ab_position_winner"] == row["ba_position_winner"] and row["ab_position_winner"] in {"first", "second"}
        for row in rows
    )
    same_position_rate = same_position_count / n

    # --- Accuracy metrics ---
    naive_preds = [row["naive_winner"] for row in rows]
    conflict_preds = [row["bpc_winner"] for row in rows]
    faireval_preds = compute_faireval_bpc(rows)

    def acc(preds: list[str]) -> float:
        comparable = [(p, y) for p, y in zip(preds, labels) if p != "UNCERTAIN"]
        return sum(p == y for p, y in comparable) / len(comparable) if comparable else float("nan")

    def coverage(preds: list[str]) -> float:
        accepted = sum(p != "UNCERTAIN" for p in preds)
        return accepted / n

    naive_accuracy = acc(naive_preds)
    bpc_accuracy = acc(faireval_preds)
    conflict_accuracy = acc(conflict_preds)
    conflict_coverage = coverage(conflict_preds)

    # --- Model-level counts ---
    def counts(preds: list[str]) -> dict[str, int]:
        c = {"CHATGPT": 0, "VICUNA13B": 0, "TIE": 0, "UNCERTAIN": 0}
        for p in preds:
            c[p] = c.get(p, 0) + 1
        return c

    naive_counts = counts(naive_preds)
    bpc_counts = counts(faireval_preds)
    conflict_counts = counts(conflict_preds)

    # --- Statistical tests ---
    naive_p = permutation_test([win_value(p) for p in naive_preds])
    bpc_p = permutation_test([win_value(p) for p in faireval_preds])
    conflict_p = permutation_test([win_value(p) for p in conflict_preds])

    return {
        "n": n,
        "first_position_win_rate": first_position_win_rate,
        "position_flip_rate": position_flip_rate,
        "same_position_rate": same_position_rate,
        "naive_accuracy": naive_accuracy,
        "bpc_accuracy": bpc_accuracy,
        "conflict_accuracy": conflict_accuracy,
        "conflict_coverage": conflict_coverage,
        "naive_counts": naive_counts,
        "bpc_counts": bpc_counts,
        "conflict_counts": conflict_counts,
        "naive_p": naive_p,
        "bpc_p": bpc_p,
        "conflict_p": conflict_p,
    }


def next_run_index(output_dir: Path, judge_name: str) -> int:
    """Find the next run index for this judge, e.g. run_1, run_2."""
    pattern = re.compile(re.escape(judge_name) + r"_run_(\d+)\.md$")
    existing = [int(m.group(1)) for f in output_dir.iterdir() if f.is_file() and (m := pattern.match(f.name))]
    return max(existing, default=0) + 1


def generate_report(csv_path: Path, output_dir: Path | None = None) -> Path:
    rows = read_csv(csv_path)
    if not rows:
        raise SystemExit(f"No rows found in {csv_path}")

    m = compute_metrics(rows)
    judge_name = csv_path.stem.replace("faireval_", "").replace("_bpc", "")
    out_dir = output_dir or csv_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    run_idx = next_run_index(out_dir, judge_name)
    report_path = out_dir / f"{judge_name}_run_{run_idx}.md"

    plan_name = "debias_execution_plan"

    lines = [
        f"# FairEval Debias Report — {judge_name}",
        "",
        f"> Plan: `{plan_name}`  ",
        f"> Run: #{run_idx}  ",
        f"> Samples: {m['n']}  ",
        f"> Generated: {__import__('datetime').datetime.now().isoformat()}",
        "",
        "## Table 1: Position Bias",
        "",
        "| Judge | First-position win rate | Position flip rate | Same-position rate |",
        "| --- | ---: | ---: | ---: |",
        f"| {judge_name} | {m['first_position_win_rate']:.3f} | {m['position_flip_rate']:.3f} | {m['same_position_rate']:.3f} |",
        "",
        "## Table 2: Human Agreement",
        "",
        "| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| {judge_name} | {m['naive_accuracy']:.3f} | {m['bpc_accuracy']:.3f} | {m['conflict_accuracy']:.3f} | {m['conflict_coverage']:.3f} |",
        "",
        "## Table 3: Model-Level Conclusion",
        "",
        "| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        f"| {judge_name} | Naive | {m['naive_counts']['CHATGPT']} | {m['naive_counts']['VICUNA13B']} | {m['naive_counts']['TIE']} | {m['naive_counts']['UNCERTAIN']} | {m['naive_p']:.4f} |",
        f"| {judge_name} | BPC | {m['bpc_counts']['CHATGPT']} | {m['bpc_counts']['VICUNA13B']} | {m['bpc_counts']['TIE']} | {m['bpc_counts']['UNCERTAIN']} | {m['bpc_p']:.4f} |",
        f"| {judge_name} | Conflict-aware | {m['conflict_counts']['CHATGPT']} | {m['conflict_counts']['VICUNA13B']} | {m['conflict_counts']['TIE']} | {m['conflict_counts']['UNCERTAIN']} | {m['conflict_p']:.4f} |",
        "",
        "## Key Findings",
        "",
    ]

    # Dynamic findings
    if m["position_flip_rate"] > 0.2:
        lines.append(f"- **Position bias is pronounced**: flip rate = {m['position_flip_rate']:.1%}. Judgments are highly sensitive to answer order.")
    elif m["position_flip_rate"] > 0.05:
        lines.append(f"- Moderate position sensitivity detected (flip rate = {m['position_flip_rate']:.1%}).")
    else:
        lines.append(f"- Position flip rate is low ({m['position_flip_rate']:.1%}), suggesting stable judgments across orders.")

    lines.append(f"- BPC (score-averaging) accuracy = {m['bpc_accuracy']:.3f} vs naive accuracy = {m['naive_accuracy']:.3f}.")

    if m["conflict_coverage"] < 1.0:
        lines.append(f"- Conflict-aware BPC marks {m['conflict_counts']['UNCERTAIN']}/{m['n']} ({m['conflict_counts']['UNCERTAIN']/m['n']:.1%}) samples as uncertain, avoiding overconfident claims.")

    if m["conflict_accuracy"] > m["naive_accuracy"]:
        lines.append("- Excluding uncertain samples improves accuracy over the naive baseline.")
    elif m["conflict_accuracy"] < m["naive_accuracy"]:
        lines.append("- Accuracy on the accepted subset is lower than naive; the uncertain cases may include easier examples.")

    lines.extend([
        "",
        "## Raw Data",
        "",
        f"Row-level results: `{csv_path}`",
        "",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {report_path}")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path, help="Path to the faireval_*_bpc.csv result file")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for the report (default: same as CSV)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_report(args.csv, args.output_dir)


if __name__ == "__main__":
    main()
