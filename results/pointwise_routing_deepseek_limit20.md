# Pointwise Routing Analysis

- Pointwise: `results/pointwise_deepseek_limit20.csv`
- Pairwise conflict-aware: `results/temp0_limit20/faireval_deepseek-v4-flash_bpc.csv`
- Overlap: 20 samples

## Baselines On Overlap

| Method | Accuracy | Coverage | Accepted n | Counts |
| --- | ---: | ---: | ---: | --- |
| Pointwise only | 0.350 | 1.000 | 20 | `{'VICUNA13B': 7, 'TIE': 9, 'CHATGPT': 4}` |
| Conflict-aware AB/BA | 0.733 | 0.750 | 15 | `{'UNCERTAIN': 5, 'VICUNA13B': 13, 'CHATGPT': 2}` |

## Pointwise + AB/BA Tie-Break Routing

If the absolute pointwise score gap is at least the threshold, accept the pointwise winner. Otherwise, use conflict-aware AB/BA.

| Gap threshold | Accuracy excl. uncertain | Coverage | Accepted n | Counts |
| ---: | ---: | ---: | ---: | --- |
| 0.50 | 0.556 | 0.900 | 18 | `{'VICUNA13B': 13, 'CHATGPT': 5, 'UNCERTAIN': 2}` |
| 1.00 | 0.556 | 0.900 | 18 | `{'VICUNA13B': 13, 'CHATGPT': 5, 'UNCERTAIN': 2}` |
| 1.50 | 0.667 | 0.750 | 15 | `{'UNCERTAIN': 5, 'VICUNA13B': 12, 'CHATGPT': 3}` |
| 2.00 | 0.667 | 0.750 | 15 | `{'UNCERTAIN': 5, 'VICUNA13B': 12, 'CHATGPT': 3}` |