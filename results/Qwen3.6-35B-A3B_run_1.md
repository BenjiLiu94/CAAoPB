# FairEval Debias Report — Qwen3.6-35B-A3B

> Plan: `debias_execution_plan`  
> Run: #1  
> Samples: 2  
> Generated: 2026-05-28T23:28:08.161847

## Table 1: Position Bias

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| Qwen3.6-35B-A3B | 0.500 | 1.000 | 0.000 |

## Table 2: Human Agreement

| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.6-35B-A3B | 0.500 | 0.500 | nan | 0.000 |

## Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3.6-35B-A3B | Naive | 1 | 1 | 0 | 0 | 1.0000 |
| Qwen3.6-35B-A3B | BPC | 1 | 1 | 0 | 0 | 1.0000 |
| Qwen3.6-35B-A3B | Conflict-aware | 0 | 0 | 0 | 2 | 1.0000 |

## Key Findings

- **Position bias is pronounced**: flip rate = 100.0%. Judgments are highly sensitive to answer order.
- BPC (score-averaging) accuracy = 0.500 vs naive accuracy = 0.500.
- Conflict-aware BPC marks 2/2 (100.0%) samples as uncertain, avoiding overconfident claims.

## Raw Data

Row-level results: `/home/benji94/BRflow/results/faireval_Qwen3.6-35B-A3B_bpc.csv`
