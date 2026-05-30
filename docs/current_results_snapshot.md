# Current Results Snapshot

This snapshot freezes the main results before adding exploratory methods.

## Main Judge Pair

- DeepSeek: `deepseek-v4-flash`
- Qwen: `Qwen3.6-35B-A3B`
- Dataset: FairEval, ChatGPT vs Vicuna-13B, 80 samples

## Main Result Files

- `results/faireval_deepseek-v4-flash_bpc.csv`
- `results/faireval_Qwen3.6-35B-A3B_bpc.csv`
- `results/cross_judge_summary_deepseek_qwen36.md`
- `results/judge_agreement_deepseek_qwen36.md`
- `results/uncertain_analysis_deepseek_qwen36.md`

## Position Sensitivity

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| DeepSeek | 0.667 | 0.225 | 0.163 |
| Qwen3.6 | 0.773 | 0.287 | 0.188 |

## Human Agreement

| Judge | Naive acc. | FairEval-style BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| DeepSeek | 0.637 | 0.613 | 0.661 | 0.775 |
| Qwen3.6 | 0.550 | 0.562 | 0.632 | 0.713 |

## Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | Naive | 52 | 26 | 2 | 0 | 0.0047 |
| DeepSeek | BPC | 44 | 31 | 5 | 0 | 0.1656 |
| DeepSeek | Conflict-aware | 36 | 26 | 0 | 18 | 0.2624 |
| Qwen3.6 | Naive | 58 | 17 | 5 | 0 | 0.0001 |
| Qwen3.6 | BPC | 48 | 22 | 10 | 0 | 0.0030 |
| Qwen3.6 | Conflict-aware | 42 | 14 | 1 | 23 | 0.0003 |

## Two-Judge Routing

Accept a winner only when both judges produce the same non-uncertain winner.

| Route | Accuracy on accepted | Coverage | Accepted n |
| --- | ---: | ---: | ---: |
| Naive two-judge agreement | 0.695 | 0.738 | 59 |
| Conflict-aware two-judge agreement | 0.762 | 0.525 | 42 |

## Stable Interpretation

The current results do not show that position bias is eliminated. They support a more conservative claim:

> AB/BA disagreement and cross-judge disagreement are useful uncertainty signals. Treating unstable cases as uncertain improves reliability on accepted judgments, but reduces coverage.

