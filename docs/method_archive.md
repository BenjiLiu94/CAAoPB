# Method Archive

This file records existing methods and candidate ideas discussed so far. It is a working archive, not a final method choice.

## Existing Methods

### Prompt Debiasing

Add instructions such as "do not prefer an answer because it appears first or second".

- Pros: cheapest and easy to combine with other methods.
- Cons: weak guarantee; models may still exhibit order sensitivity.

### Randomized Position

Randomly assign candidate answers to A/B positions.

- Pros: prevents one model from always occupying the favored position.
- Cons: does not detect whether an individual pair is order-sensitive.

### AB/BA Swap

Evaluate the same pair twice with reversed answer order.

- Pros: direct intervention on position.
- Cons: doubles judging cost and still needs an aggregation rule.

### Balanced Position Calibration (BPC)

FairEval-style calibration: run AB and BA, map swapped scores back to the original candidates, and aggregate.

- Pros: strong and simple baseline for position bias.
- Cons: averaging can hide contradictory judgments.

### Multiple Evidence Calibration (MEC)

Sample multiple evaluation evidences/scores for the same comparison and average them.

- Pros: reduces stochastic instability.
- Cons: not specifically targeted at position bias; increases cost.

### MEC + BPC

Run multiple samples under both AB and BA, map scores back, and average all results.

- Pros: strong FairEval baseline.
- Cons: expensive and still not very explicit about sample-level uncertainty.

### Human-in-the-Loop Calibration

Route unstable or hard examples to human annotators.

- Pros: reliable for ambiguous cases.
- Cons: expensive and not fully automatic.

### Rubric / Criteria-Based Evaluation

Ask the judge to score correctness, completeness, clarity, helpfulness, and other criteria before producing an overall score or winner.

- Pros: gives the model more explicit evaluation evidence.
- Cons: criteria scores can still be position-sensitive or scale-sensitive.

### Reference-Guided Evaluation

Evaluate candidates against a gold/reference answer when available.

- Pros: reduces subjective pairwise comparison.
- Cons: many open-ended tasks lack a reliable reference.

### Independent Pointwise Scoring

Score each answer separately instead of presenting both in one prompt.

- Pros: avoids direct A/B position structure.
- Cons: absolute score scales can drift across calls.

### Multi-Judge Ensemble

Use multiple judge models and treat disagreement as uncertainty.

- Pros: reduces dependence on one judge's bias.
- Cons: cost increases; judges may share correlated biases.

### Pairwise Ranking Aggregation

Use pairwise tournament results and aggregate with Elo, Bradley-Terry, Borda, or related ranking methods.

- Pros: useful for ranking many candidate models.
- Cons: does not remove bias in the underlying pairwise judgments.

### Split-and-Merge / PORTIA-Style Methods

Split answers into parts, align comparable parts, and merge local comparison evidence.

- Pros: directly related to reducing pairwise position bias.
- Cons: more complex; split/alignment quality becomes a new source of error.

## Candidate Ideas

### Same-Language Translation Perturbation

Translate both candidate answers into the same target language and compare stability across languages.

- Intended use: diagnostic robustness test.
- Main risk: translation quality and language bias.

### Reconstruction / Normalization Layer

Corrupt, normalize, translate, or reconstruct answers before judging.

- Intended use: test whether surface-form sensitivity drives bias.
- Main risk: reconstruction may change answer content.

### Multi-Presentation Robustness

Evaluate the same pair under multiple prompt labels, formats, and layouts.

- Intended use: measure presentation sensitivity beyond AB/BA.
- Main risk: additional cost and more aggregation choices.

### Independent Scoring + Pairwise Tie-Break

Score each answer independently first. If the score gap is large, accept the pointwise winner. If the score gap is small, run AB/BA pairwise comparison.

- Intended use: reduce unnecessary pairwise comparisons and isolate near-tie cases.
- Main risk: pointwise scores may be poorly calibrated.
- Pilot result: negative on the first 20 FairEval samples. DeepSeek and Qwen3.6 pointwise-only accuracy were both 0.350. Routing by pointwise score gap did not beat conflict-aware AB/BA on DeepSeek and remained weak on Qwen3.6. This suggests absolute pointwise scoring suffers from scale saturation and poor calibration in this setup.

### Rubric-First Pointwise With Thinking

Score each answer independently on fixed self-built dimensions, then use the overall score to choose the winner. Test whether enabling thinking improves calibration.

- Intended use: force the judge to decompose answer quality before producing a final score.
- Implementation: Qwen3.6-35B-A3B, temperature 0, dimensions factuality/relevance/completeness/reasoning/clarity, JSON output.
- Pilot result: negative on the FairEval prefix. Thinking-off accuracy was 0.250 on 20 samples; on the same first 10 samples, thinking-off was 0.300 and thinking-on was 0.200. Thinking-on also increased latency and caused a 20-sample run to time out at sample 19.
- Main interpretation: thinking may reduce some 10/10 score saturation, but it did not improve agreement with human labels. The central problem remains poor calibration of independent absolute scores.

### Chunk-Level Interleaving

Split both answers into chunks, shuffle or interleave chunks, then ask the judge to evaluate the two underlying candidates.

- Intended use: weaken whole-answer position effects and test whether evaluation is robust to chunk presentation order.
- Main risk: chunk attribution, chunk ordering, and coherence may become new confounds.

### Chunk-Language Interleaving

Translate one candidate answer to another language, split both answers with an open-source tokenizer, preserve within-answer chunk order, and interleave chunks under factorial swaps of candidate label, language assignment, and first chunk source.

- Intended use: jointly break whole-answer position structure and expose language/label/start-order presentation sensitivity.
- Implementation: `tiktoken` chunking, English original + Simplified Chinese translation, 8 presentation conditions per sample.
- Pilot result: negative on the first 5 FairEval samples with Qwen3.6. Four of five samples were marked `UNCERTAIN` by cross-condition aggregation, and the only accepted sample was wrong. Accuracy on accepted = 0.000, coverage = 0.200. The method strongly exposes presentation sensitivity but does not currently reduce bias into reliable judgments.
- Main interpretation: this is useful as a diagnostic stress test, not as a debiasing method in its current form.

### Same-Language ABAB Chunk Interleaving

Split both original English answers with `tiktoken`, preserve within-answer chunk order, and present them as interleaved chunks under four symmetric conditions: X/Y label assignment and X-start/Y-start local order.

- Intended use: test whether chunk interleaving can dilute whole-answer position bias without introducing translation/language bias.
- Pilot result: negative on the first 5 FairEval samples with Qwen3.6. Accuracy on accepted = 0.000, coverage = 0.200, matching the poor behavior of chunk-language interleaving.
- Main interpretation: the failure is not primarily caused by translation. The chunk/interleaving presentation itself appears to disrupt stable evaluation and introduce new local presentation effects.

### Whole-Answer Repetition Interleaving

Repeat the full answers without chunking, using alternating presentation sequences such as `X/Y/X/Y` and `Y/X/Y/X`, plus X/Y candidate label swaps.

- Intended use: dilute whole-answer first/second position bias without breaking answer coherence.
- Pilot result: mixed-to-negative on the first 5 FairEval samples with Qwen3.6. It is much more stable than chunk interleaving (coverage = 0.800), but accepted accuracy is only 0.250. The method often shifted outputs toward `TIE` or ChatGPT.
- Main interpretation: preserving whole-answer coherence helps stability, but repeated presentations may introduce new repetition/recency/label effects and does not currently improve reliability.

### Whole-Answer ABBA/BAAB Repetition

Repeat full answers in first/last-balanced orders such as `X/Y/Y/X` and `Y/X/X/Y`, plus X/Y candidate label swaps.

- Intended use: reduce local first-mover effects in the `X/Y/X/Y` repetition pattern.
- Pilot result: identical aggregate behavior to the ABAB version on the first 5 FairEval samples with Qwen3.6: accuracy on accepted = 0.250, coverage = 0.800.
- Main interpretation: balancing first/last presentation did not fix the repetition-induced errors. The issue appears to be repeated whole-answer presentation itself, not merely the ABAB local order.
