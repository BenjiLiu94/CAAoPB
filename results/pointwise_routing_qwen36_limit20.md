# Pointwise Routing Analysis

- Pointwise: `results/pointwise_qwen36_limit20.csv`
- Pairwise conflict-aware: `results/faireval_Qwen3.6-35B-A3B_bpc.csv`
- Overlap: 20 samples

## Baselines On Overlap

| Method | Accuracy | Coverage | Accepted n | Counts |
| --- | ---: | ---: | ---: | --- |
| Pointwise only | 0.350 | 1.000 | 20 | `{'TIE': 8, 'CHATGPT': 9, 'VICUNA13B': 3}` |
| Conflict-aware AB/BA | 0.308 | 0.650 | 13 | `{'UNCERTAIN': 7, 'VICUNA13B': 6, 'CHATGPT': 7}` |

## Pointwise + AB/BA Tie-Break Routing

If the absolute pointwise score gap is at least the threshold, accept the pointwise winner. Otherwise, use conflict-aware AB/BA.

| Gap threshold | Accuracy excl. uncertain | Coverage | Accepted n | Counts |
| ---: | ---: | ---: | ---: | --- |
| 0.50 | 0.400 | 0.750 | 15 | `{'UNCERTAIN': 5, 'VICUNA13B': 5, 'CHATGPT': 10}` |
| 1.00 | 0.400 | 0.750 | 15 | `{'UNCERTAIN': 5, 'VICUNA13B': 5, 'CHATGPT': 10}` |
| 1.50 | 0.385 | 0.650 | 13 | `{'UNCERTAIN': 7, 'VICUNA13B': 5, 'CHATGPT': 8}` |
| 2.00 | 0.385 | 0.650 | 13 | `{'UNCERTAIN': 7, 'VICUNA13B': 5, 'CHATGPT': 8}` |