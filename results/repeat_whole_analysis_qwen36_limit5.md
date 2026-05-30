# Chunk-Language Analysis

- Input: `results/repeat_whole_qwen36_limit5.csv`
- Samples: 5
- Accuracy on accepted: 0.250
- Coverage: 0.800

## Per-Sample Aggregation

| QID | Human | Final | Consistency | Winner counts |
| ---: | --- | --- | ---: | --- |
| 1 | CHATGPT | TIE | 1.000 | `{'TIE': 4}` |
| 2 | TIE | VICUNA13B | 0.750 | `{'TIE': 1, 'VICUNA13B': 3}` |
| 3 | VICUNA13B | CHATGPT | 1.000 | `{'CHATGPT': 4}` |
| 4 | VICUNA13B | VICUNA13B | 1.000 | `{'VICUNA13B': 4}` |
| 5 | VICUNA13B | UNCERTAIN | 0.500 | `{'TIE': 2, 'CHATGPT': 1, 'VICUNA13B': 1}` |