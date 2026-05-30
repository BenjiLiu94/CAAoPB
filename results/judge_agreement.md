# Judge Agreement Routing

- Judge A: `deepseek-v4-flash`
- Judge B: `qwen-plus`
- Overlap: 80 samples

## Agreement

| Setting | Agreement rate |
| --- | ---: |
| Naive winner | 0.863 |
| Conflict-aware winner | 0.750 |

## Ensemble Routing

Accept a winner only when both judges produce the same non-uncertain winner.

| Route | Accuracy on accepted | Coverage | Accepted n |
| --- | ---: | ---: | ---: |
| Naive two-judge agreement | 0.638 | 0.863 | 69 |
| Conflict-aware two-judge agreement | 0.698 | 0.662 | 53 |

## Conflict-Aware Uncertainty Overlap

- Both judges uncertain: 7/80 (8.8%)
- At least one judge uncertain: 26/80 (32.5%)

## Routed Prediction Counts

| Route | Counts |
| --- | --- |
| Naive two-judge agreement | `{'VICUNA13B': 21, 'UNCERTAIN': 11, 'CHATGPT': 48}` |
| Conflict-aware two-judge agreement | `{'UNCERTAIN': 27, 'VICUNA13B': 18, 'CHATGPT': 35}` |
