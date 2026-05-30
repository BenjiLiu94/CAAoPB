# FairEval Debias Report — deepseek-v4-flash

> Plan: `debias_execution_plan`  
> Run: #1  
> Samples: 10  
> Generated: 2026-05-28T22:21:27.623624

## Table 1: Position Bias

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| deepseek-v4-flash | 0.500 | 0.500 | 0.500 |

## Table 2: Human Agreement

| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| deepseek-v4-flash | 0.500 | 0.500 | 0.600 | 0.500 |

## Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| deepseek-v4-flash | Naive | 5 | 5 | 0 | 0 | 1.0000 |
| deepseek-v4-flash | BPC | 1 | 9 | 0 | 0 | 0.0231 |
| deepseek-v4-flash | Conflict-aware | 0 | 5 | 0 | 5 | 0.0612 |

## Key Findings

- **Position bias is pronounced**: flip rate = 50.0%. Judgments are highly sensitive to answer order.
- BPC (score-averaging) accuracy = 0.500 vs naive accuracy = 0.500.
- Conflict-aware BPC marks 5/10 (50.0%) samples as uncertain, avoiding overconfident claims.
- Excluding uncertain samples improves accuracy over the naive baseline.

## Raw Data

Row-level results: `results/faireval_deepseek-v4-flash_bpc.csv`
