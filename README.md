# Order Sensitivity as Uncertainty

> A Conflict-Aware Analysis of Position Bias in LLM-as-a-Judge

[![GitHub](https://img.shields.io/badge/GitHub-BenjiLiu94/CAAoPB-blue?logo=github)](https://github.com/BenjiLiu94/CAAoPB)

This repository contains the code and experiments for analyzing **position bias** in LLM-based pairwise evaluators. Rather than simply averaging scores across AB/BA orderings, we treat order disagreement as an **uncertainty signal** and study how conflict-aware aggregation affects the reliability of judged outcomes.

## Core Idea

When a judge model prefers candidate X in order (X, Y) but flips to candidate Y in order (Y, X), the sample is not merely noisy—it is presentation-sensitive. We ask:

- Should AB/BA flips be treated as abstention signals?
- Does conflict-aware filtering improve human alignment on retained samples?
- How does multi-judge agreement routing trade off coverage versus accuracy?

## Project Structure

```
├── scripts/          # Core evaluation & analysis scripts
│   ├── reproduce_faireval.py
│   ├── chunk_language.py
│   ├── chunk_interleave.py
│   ├── analyze_judge_agreement.py
│   ├── analyze_uncertain.py
│   └── ...
├── data/             # Translation dataset (Chinese)
├── configs/          # Judge configuration templates
├── docs/             # Experiment plans, method archive, paper outline
├── results/          # Evaluation outputs & analysis reports
├── external/         # FairEval baseline
├── paper.md          # Paper draft (Markdown)
├── paper.tex         # Paper draft (LaTeX, English)
└── paper_zh.tex      # Paper draft (LaTeX, Chinese)
```

## Quick Start

This project uses [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
uv sync
```

Run FairEval reproduction with a configured judge:

```bash
uv run python scripts/reproduce_faireval.py --config configs/judges.example.json
```

## Key Findings

- Both DeepSeek v4 flash and Qwen3.6-35B-A3B exhibit significant first-position preference and AB/BA flip rates.
- FairEval-style score averaging (BPC) does not consistently improve human agreement.
- Conflict-aware aggregation improves retained-sample accuracy (0.695 → 0.762 with dual-judge agreement) at the cost of reduced coverage.
- AB/BA comparison can serve as a practical detector of unreliable judgments, not merely a calibration mechanism.

## Citation

If you use this code or findings, please cite:

```bibtex
@article{liu2025order,
  title={Order Sensitivity as Uncertainty: A Conflict-Aware Analysis of Position Bias in LLM-as-a-Judge},
  author={Liu, Zhibin and Ye, Yunbo},
  year={2025}
}
```

## Authors

- **Zhibin Liu** — benji94.liu@gmail.com
- **Yunbo Ye** — 488059718@qq.com
