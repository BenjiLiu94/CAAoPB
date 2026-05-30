# FairEval Debias Report — qwen-plus

> Plan: `debias_execution_plan`  
> Run: #1  
> Samples: 2  
> Generated: 2026-05-28T22:38:22.481161

## Table 1: Position Bias

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| qwen-plus | 0.000 | 0.500 | 0.000 |

## Table 2: Human Agreement

| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| qwen-plus | 0.000 | 0.500 | 0.000 | 0.500 |

## Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| qwen-plus | Naive | 0 | 1 | 1 | 0 | 1.0000 |
| qwen-plus | BPC | 1 | 1 | 0 | 0 | 1.0000 |
| qwen-plus | Conflict-aware | 0 | 1 | 0 | 1 | 1.0000 |

## Key Findings

- **Position bias is pronounced**: flip rate = 50.0%. Judgments are highly sensitive to answer order.
- BPC (score-averaging) accuracy = 0.500 vs naive accuracy = 0.000.
- Conflict-aware BPC marks 1/2 (50.0%) samples as uncertain, avoiding overconfident claims.

## Raw Data

Row-level results: `/home/benji94/BRflow/results/faireval_qwen-plus_bpc.csv`
