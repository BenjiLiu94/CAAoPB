# Uncertain Sample Analysis

This report analyzes samples marked `UNCERTAIN` by conflict-aware AB/BA aggregation.

## deepseek-v4-flash

- Total samples: 80
- Uncertain samples: 18/80 (22.5%)
- Accepted samples: 62/80 (77.5%)
- Human label distribution in uncertain: `{'CHATGPT': 9, 'VICUNA13B': 6, 'TIE': 3}`
- Human label distribution in accepted: `{'CHATGPT': 32, 'TIE': 11, 'VICUNA13B': 19}`
- Naive accuracy on uncertain samples: 0.556
- Naive accuracy on accepted samples: 0.661
- Conflict-aware accuracy on accepted samples: 0.661
- Same-position conflicts among uncertain: 13/18 (72.2%)

### Top Conflict Patterns

| Pattern | Count |
| --- | ---: |
| `AB=CHATGPT, BA=VICUNA13B` | 13 |
| `AB=CHATGPT, BA=TIE` | 3 |
| `AB=TIE, BA=VICUNA13B` | 2 |

### Uncertain Question IDs

`6, 7, 9, 10, 12, 13, 16, 21, 32, 35, 46, 51, 54, 58, 63, 72, 77, 78`

## Qwen3.6-35B-A3B

- Total samples: 80
- Uncertain samples: 23/80 (28.7%)
- Accepted samples: 57/80 (71.2%)
- Human label distribution in uncertain: `{'CHATGPT': 9, 'TIE': 6, 'VICUNA13B': 8}`
- Human label distribution in accepted: `{'TIE': 8, 'VICUNA13B': 17, 'CHATGPT': 32}`
- Naive accuracy on uncertain samples: 0.348
- Naive accuracy on accepted samples: 0.632
- Conflict-aware accuracy on accepted samples: 0.632
- Same-position conflicts among uncertain: 15/23 (65.2%)

### Top Conflict Patterns

| Pattern | Count |
| --- | ---: |
| `AB=CHATGPT, BA=VICUNA13B` | 14 |
| `AB=TIE, BA=VICUNA13B` | 4 |
| `AB=VICUNA13B, BA=TIE` | 2 |
| `AB=CHATGPT, BA=TIE` | 2 |
| `AB=VICUNA13B, BA=CHATGPT` | 1 |

### Uncertain Question IDs

`1, 7, 13, 14, 17, 19, 20, 21, 22, 23, 26, 32, 34, 40, 51, 52, 54, 56, 57, 58, 59, 67, 77`
