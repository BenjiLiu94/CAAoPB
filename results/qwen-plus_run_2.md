# FairEval Debias Report — qwen-plus

> Plan: `debias_execution_plan`  
> Run: #2  
> Samples: 80  
> Generated: 2026-05-28T22:51:37.519033

## Table 1: Position Bias

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| qwen-plus | 0.684 | 0.188 | 0.175 |

## Table 2: Human Agreement

| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| qwen-plus | 0.588 | 0.588 | 0.646 | 0.812 |

## Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| qwen-plus | Naive | 54 | 25 | 1 | 0 | 0.0014 |
| qwen-plus | BPC | 54 | 24 | 2 | 0 | 0.0010 |
| qwen-plus | Conflict-aware | 45 | 20 | 0 | 15 | 0.0025 |

## Key Findings

- Moderate position sensitivity detected (flip rate = 18.8%).
- BPC (score-averaging) accuracy = 0.588 vs naive accuracy = 0.588.
- Conflict-aware BPC marks 15/80 (18.8%) samples as uncertain, avoiding overconfident claims.
- Excluding uncertain samples improves accuracy over the naive baseline.

## Raw Data

Row-level results: `/home/benji94/BRflow/results/faireval_qwen-plus_bpc.csv`
