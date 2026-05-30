# FairEval Debias Report — Qwen3.6-35B-A3B

> Plan: `debias_execution_plan`  
> Run: #2  
> Samples: 80  
> Generated: 2026-05-28T23:44:35.718940

## Table 1: Position Bias

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| Qwen3.6-35B-A3B | 0.773 | 0.287 | 0.188 |

## Table 2: Human Agreement

| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.6-35B-A3B | 0.550 | 0.562 | 0.632 | 0.713 |

## Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3.6-35B-A3B | Naive | 58 | 17 | 5 | 0 | 0.0001 |
| Qwen3.6-35B-A3B | BPC | 48 | 22 | 10 | 0 | 0.0030 |
| Qwen3.6-35B-A3B | Conflict-aware | 42 | 14 | 1 | 23 | 0.0003 |

## Key Findings

- **Position bias is pronounced**: flip rate = 28.7%. Judgments are highly sensitive to answer order.
- BPC (score-averaging) accuracy = 0.562 vs naive accuracy = 0.550.
- Conflict-aware BPC marks 23/80 (28.7%) samples as uncertain, avoiding overconfident claims.
- Excluding uncertain samples improves accuracy over the naive baseline.

## Raw Data

Row-level results: `/home/benji94/BRflow/results/faireval_Qwen3.6-35B-A3B_bpc.csv`
