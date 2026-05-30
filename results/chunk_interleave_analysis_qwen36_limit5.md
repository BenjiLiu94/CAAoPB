# Chunk-Language Analysis

- Input: `results/chunk_interleave_qwen36_limit5.csv`
- Samples: 5
- Accuracy on accepted: 0.000
- Coverage: 0.200

## Per-Sample Aggregation

| QID | Human | Final | Consistency | Winner counts |
| ---: | --- | --- | ---: | --- |
| 1 | CHATGPT | UNCERTAIN | 0.500 | `{'CHATGPT': 2, 'TIE': 1, 'VICUNA13B': 1}` |
| 2 | TIE | UNCERTAIN | 0.500 | `{'CHATGPT': 1, 'VICUNA13B': 2, 'TIE': 1}` |
| 3 | VICUNA13B | CHATGPT | 1.000 | `{'CHATGPT': 4}` |
| 4 | VICUNA13B | UNCERTAIN | 0.750 | `{'CHATGPT': 1, 'VICUNA13B': 3}` |
| 5 | VICUNA13B | UNCERTAIN | 0.500 | `{'CHATGPT': 2, 'TIE': 2}` |