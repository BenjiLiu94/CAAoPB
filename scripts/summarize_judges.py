#!/usr/bin/env python3
"""Generate a cross-judge summary for FairEval debias runs."""

from __future__ import annotations

import argparse
from pathlib import Path

from generate_report import compute_metrics, read_csv


def judge_name(path: Path) -> str:
    return path.stem.replace("faireval_", "").replace("_bpc", "")


def fmt(x: float) -> str:
    return f"{x:.3f}"


def generate(csv_paths: list[Path], output: Path) -> None:
    rows = []
    for path in csv_paths:
        data = read_csv(path)
        metrics = compute_metrics(data)
        rows.append((judge_name(path), metrics, path))

    lines = [
        "# Cross-Judge FairEval Debias Summary",
        "",
        "## Inputs",
        "",
    ]
    for name, m, path in rows:
        lines.append(f"- {name}: `{path}` ({m['n']} samples)")

    lines.extend(
        [
            "",
            "## Table 1: Position Sensitivity",
            "",
            "| Judge | First-position win rate | Position flip rate | Same-position rate |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for name, m, _ in rows:
        lines.append(
            f"| {name} | {fmt(m['first_position_win_rate'])} | {fmt(m['position_flip_rate'])} | {fmt(m['same_position_rate'])} |"
        )

    lines.extend(
        [
            "",
            "## Table 2: Human Agreement",
            "",
            "| Judge | Naive acc. | FairEval-style BPC acc. | Conflict-aware acc. | Conflict-aware coverage |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, m, _ in rows:
        lines.append(
            f"| {name} | {fmt(m['naive_accuracy'])} | {fmt(m['bpc_accuracy'])} | {fmt(m['conflict_accuracy'])} | {fmt(m['conflict_coverage'])} |"
        )

    lines.extend(
        [
            "",
            "## Table 3: Model-Level Conclusion",
            "",
            "| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, m, _ in rows:
        for method, counts_key, p_key in [
            ("Naive", "naive_counts", "naive_p"),
            ("BPC", "bpc_counts", "bpc_p"),
            ("Conflict-aware", "conflict_counts", "conflict_p"),
        ]:
            c = m[counts_key]
            lines.append(
                f"| {name} | {method} | {c['CHATGPT']} | {c['VICUNA13B']} | {c['TIE']} | {c['UNCERTAIN']} | {m[p_key]:.4f} |"
            )

    lines.extend(
        [
            "",
            "## Main Readout",
            "",
            "1. Both judges show a strong first-position preference. First-position win rates are well above 0.5.",
            "2. AB/BA disagreement is substantial, so fixed-order pairwise judging mixes answer quality with presentation order.",
            "3. FairEval-style BPC does not consistently improve human agreement, which suggests that score averaging is not enough at the sample level.",
            "4. Conflict-aware aggregation improves accuracy on accepted samples for both judges, but it does so by reducing coverage.",
            "5. Model-level conclusions are judge-dependent: one judge may lose statistical significance after conflict filtering while another may not.",
            "",
            "## Conservative Interpretation",
            "",
            "The most defensible conclusion is not that conflict-aware BPC makes every judgment more accurate. The stronger conclusion is that AB/BA disagreement is a useful uncertainty signal. When a judge changes its content-level winner after answer order is swapped, that pair should not be treated as equally reliable evidence for model ranking.",
            "",
            "## Limits",
            "",
            "- The experiment uses one model pair from FairEval: ChatGPT vs Vicuna-13B.",
            "- The candidate order in naive AB favors ChatGPT, so naive ChatGPT wins may be inflated by first-position preference.",
            "- Conflict-aware accuracy is measured only on accepted non-uncertain samples, so it must be read together with coverage.",
            "- Results from DeepSeek and Qwen are not identical; judge choice remains a source of uncertainty.",
            "",
        ]
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Summary written to {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/cross_judge_summary.md"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate(args.csv, args.output)


if __name__ == "__main__":
    main()
