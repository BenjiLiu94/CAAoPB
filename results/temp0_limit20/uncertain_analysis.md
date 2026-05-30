# Uncertain Sample Analysis

This report analyzes samples marked `UNCERTAIN` by conflict-aware AB/BA aggregation.

## deepseek-v4-flash

- Total samples: 20
- Uncertain samples: 5/20 (25.0%)
- Accepted samples: 15/20 (75.0%)
- Human label distribution in uncertain: `{'CHATGPT': 3, 'TIE': 1, 'VICUNA13B': 1}`
- Human label distribution in accepted: `{'TIE': 3, 'VICUNA13B': 10, 'CHATGPT': 2}`
- Naive accuracy on uncertain samples: 0.400
- Naive accuracy on accepted samples: 0.733
- Conflict-aware accuracy on accepted samples: 0.733
- Same-position conflicts among uncertain: 4/5 (80.0%)

### Top Conflict Patterns

| Pattern | Count |
| --- | ---: |
| `AB=CHATGPT, BA=VICUNA13B` | 4 |
| `AB=TIE, BA=VICUNA13B` | 1 |

### Uncertain Question IDs

`1, 6, 13, 16, 19`
