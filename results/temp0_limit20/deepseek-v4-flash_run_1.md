# FairEval Debias Report — deepseek-v4-flash

> Plan: `debias_execution_plan`  
> Run: #1  
> Samples: 20  
> Generated: 2026-05-28T23:19:28.618701

## Table 1: Position Bias

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| deepseek-v4-flash | 0.316 | 0.250 | 0.200 |

## Table 2: Human Agreement

| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| deepseek-v4-flash | 0.650 | 0.550 | 0.733 | 0.750 |

## Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| deepseek-v4-flash | Naive | 6 | 13 | 1 | 0 | 0.1675 |
| deepseek-v4-flash | BPC | 3 | 15 | 2 | 0 | 0.0086 |
| deepseek-v4-flash | Conflict-aware | 2 | 13 | 0 | 5 | 0.0091 |

## Key Findings

- **Position bias is pronounced**: flip rate = 25.0%. Judgments are highly sensitive to answer order.
- BPC (score-averaging) accuracy = 0.550 vs naive accuracy = 0.650.
- Conflict-aware BPC marks 5/20 (25.0%) samples as uncertain, avoiding overconfident claims.
- Excluding uncertain samples improves accuracy over the naive baseline.

## Raw Data

Row-level results: `results/temp0_limit20/faireval_deepseek-v4-flash_bpc.csv`
