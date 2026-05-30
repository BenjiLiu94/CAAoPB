# Judge Agreement Routing

- Judge A: `deepseek-v4-flash`
- Judge B: `Qwen3.6-35B-A3B`
- Overlap: 80 samples

## Agreement

| Setting | Agreement rate |
| --- | ---: |
| Naive winner | 0.738 |
| Conflict-aware winner | 0.625 |

## Ensemble Routing

Accept a winner only when both judges produce the same non-uncertain winner.

| Route | Accuracy on accepted | Coverage | Accepted n |
| --- | ---: | ---: | ---: |
| Naive two-judge agreement | 0.695 | 0.738 | 59 |
| Conflict-aware two-judge agreement | 0.762 | 0.525 | 42 |

## Conflict-Aware Uncertainty Overlap

- Both judges uncertain: 8/80 (10.0%)
- At least one judge uncertain: 33/80 (41.2%)

## Routed Prediction Counts

| Route | Counts |
| --- | --- |
| Naive two-judge agreement | `{'UNCERTAIN': 21, 'VICUNA13B': 13, 'CHATGPT': 46}` |
| Conflict-aware two-judge agreement | `{'UNCERTAIN': 38, 'VICUNA13B': 12, 'CHATGPT': 30}` |
