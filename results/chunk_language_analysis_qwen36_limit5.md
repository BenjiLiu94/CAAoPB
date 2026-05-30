# Chunk-Language Analysis

- Input: `results/chunk_language_qwen36_limit5.csv`
- Samples: 5
- Accuracy on accepted: 0.000
- Coverage: 0.200

## Per-Sample Aggregation

| QID | Human | Final | Consistency | Winner counts |
| ---: | --- | --- | ---: | --- |
| 1 | CHATGPT | UNCERTAIN | 0.500 | `{'CHATGPT': 3, 'VICUNA13B': 4, 'TIE': 1}` |
| 2 | TIE | UNCERTAIN | 0.500 | `{'VICUNA13B': 4, 'CHATGPT': 3, 'TIE': 1}` |
| 3 | VICUNA13B | CHATGPT | 1.000 | `{'CHATGPT': 8}` |
| 4 | VICUNA13B | UNCERTAIN | 0.500 | `{'CHATGPT': 4, 'TIE': 2, 'VICUNA13B': 2}` |
| 5 | VICUNA13B | UNCERTAIN | 0.500 | `{'CHATGPT': 3, 'TIE': 1, 'VICUNA13B': 4}` |