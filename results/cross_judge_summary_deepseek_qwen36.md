# Cross-Judge FairEval Debias Summary

## Inputs

- deepseek-v4-flash: `results/faireval_deepseek-v4-flash_bpc.csv` (80 samples)
- Qwen3.6-35B-A3B: `results/faireval_Qwen3.6-35B-A3B_bpc.csv` (80 samples)

## Table 1: Position Sensitivity

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| deepseek-v4-flash | 0.667 | 0.225 | 0.163 |
| Qwen3.6-35B-A3B | 0.773 | 0.287 | 0.188 |

## Table 2: Human Agreement

| Judge | Naive acc. | FairEval-style BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| deepseek-v4-flash | 0.637 | 0.613 | 0.661 | 0.775 |
| Qwen3.6-35B-A3B | 0.550 | 0.562 | 0.632 | 0.713 |

## Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| deepseek-v4-flash | Naive | 52 | 26 | 2 | 0 | 0.0047 |
| deepseek-v4-flash | BPC | 44 | 31 | 5 | 0 | 0.1656 |
| deepseek-v4-flash | Conflict-aware | 36 | 26 | 0 | 18 | 0.2624 |
| Qwen3.6-35B-A3B | Naive | 58 | 17 | 5 | 0 | 0.0001 |
| Qwen3.6-35B-A3B | BPC | 48 | 22 | 10 | 0 | 0.0030 |
| Qwen3.6-35B-A3B | Conflict-aware | 42 | 14 | 1 | 23 | 0.0003 |

## Main Readout

1. Both judges show a strong first-position preference. First-position win rates are well above 0.5.
2. AB/BA disagreement is substantial, so fixed-order pairwise judging mixes answer quality with presentation order.
3. FairEval-style BPC does not consistently improve human agreement, which suggests that score averaging is not enough at the sample level.
4. Conflict-aware aggregation improves accuracy on accepted samples for both judges, but it does so by reducing coverage.
5. Model-level conclusions are judge-dependent: one judge may lose statistical significance after conflict filtering while another may not.

## Conservative Interpretation

The most defensible conclusion is not that conflict-aware BPC makes every judgment more accurate. The stronger conclusion is that AB/BA disagreement is a useful uncertainty signal. When a judge changes its content-level winner after answer order is swapped, that pair should not be treated as equally reliable evidence for model ranking.

## Limits

- The experiment uses one model pair from FairEval: ChatGPT vs Vicuna-13B.
- The candidate order in naive AB favors ChatGPT, so naive ChatGPT wins may be inflated by first-position preference.
- Conflict-aware accuracy is measured only on accepted non-uncertain samples, so it must be read together with coverage.
- Results from DeepSeek and Qwen are not identical; judge choice remains a source of uncertainty.
