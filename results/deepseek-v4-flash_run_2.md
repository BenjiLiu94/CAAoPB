# FairEval Debias Report — deepseek-v4-flash

> Plan: `debias_execution_plan`  
> Run: #2  
> Samples: 80  
> Generated: 2026-05-28T22:22:01.687452

## Table 1: Position Bias

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| deepseek-v4-flash | 0.667 | 0.225 | 0.163 |

## Table 2: Human Agreement

| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| deepseek-v4-flash | 0.637 | 0.613 | 0.661 | 0.775 |

## Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| deepseek-v4-flash | Naive | 52 | 26 | 2 | 0 | 0.0047 |
| deepseek-v4-flash | BPC | 44 | 31 | 5 | 0 | 0.1656 |
| deepseek-v4-flash | Conflict-aware | 36 | 26 | 0 | 18 | 0.2624 |

## Key Findings

- **Position bias is pronounced**: flip rate = 22.5%. Judgments are highly sensitive to answer order.
- BPC (score-averaging) accuracy = 0.613 vs naive accuracy = 0.637.
- Conflict-aware BPC marks 18/80 (22.5%) samples as uncertain, avoiding overconfident claims.
- Excluding uncertain samples improves accuracy over the naive baseline.

## Raw Data

Row-level results: `results/faireval_deepseek-v4-flash_bpc.csv`
