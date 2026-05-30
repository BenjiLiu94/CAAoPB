# Rubric Pointwise Thinking Pilot

- Judge: `Qwen3.6-35B-A3B`
- Dataset: first FairEval GPT-3.5 vs Vicuna-13B samples
- Prompt: independent rubric-first scoring, no pairwise comparison
- Rubric dimensions: factuality, relevance, completeness, reasoning, clarity, plus overall score
- Temperature: `0`

## Results

| Setting | Samples | Accuracy | Winner counts | Avg ChatGPT score | Avg Vicuna score | Avg abs. gap |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| Thinking off | 20 | 0.250 | `{'TIE': 9, 'CHATGPT': 8, 'VICUNA13B': 3}` | 9.55 | 9.10 | 0.95 |
| Thinking off, first 10 only | 10 | 0.300 | `{'TIE': 5, 'CHATGPT': 4, 'VICUNA13B': 1}` | 9.80 | 9.10 | 0.90 |
| Thinking on | 10 | 0.200 | `{'TIE': 4, 'VICUNA13B': 2, 'CHATGPT': 4}` | 8.90 | 8.50 | 0.80 |

## Notes

The 20-sample thinking-on run timed out at sample 19 before writing a CSV. The first 18 printed results did not suggest a decisive improvement, and the successful 10-sample rerun was worse than thinking-off on the same prefix.

Opening thinking mode reduced the most extreme 10/10 score saturation in some cases, but it did not improve agreement with human labels in this pilot. The main failure mode remains poor calibration of independent absolute scores: many answers receive very high and similar scores, while wrong non-tie decisions still appear.

Current interpretation: rubric-first pointwise judging is useful as a diagnostic, but this pilot does not support it as a stronger debiasing method than conflict-aware AB/BA.
