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

## qwen-plus

- Total samples: 80
- Uncertain samples: 15/80 (18.8%)
- Accepted samples: 65/80 (81.2%)
- Human label distribution in uncertain: `{'CHATGPT': 5, 'VICUNA13B': 6, 'TIE': 4}`
- Human label distribution in accepted: `{'TIE': 10, 'VICUNA13B': 19, 'CHATGPT': 36}`
- Naive accuracy on uncertain samples: 0.333
- Naive accuracy on accepted samples: 0.646
- Conflict-aware accuracy on accepted samples: 0.646
- Same-position conflicts among uncertain: 14/15 (93.3%)

### Top Conflict Patterns

| Pattern | Count |
| --- | ---: |
| `AB=CHATGPT, BA=VICUNA13B` | 9 |
| `AB=VICUNA13B, BA=CHATGPT` | 5 |
| `AB=TIE, BA=CHATGPT` | 1 |

### Uncertain Question IDs

`1, 5, 9, 10, 13, 21, 26, 36, 39, 52, 53, 54, 58, 59, 72`
