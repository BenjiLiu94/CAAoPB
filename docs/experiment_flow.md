# Experiment Flow

## Research Question

Can open-source LLM judges reproduce position bias on FairEval, and can a symmetric judging protocol reduce unstable model preferences compared with naive pairwise judging and BPC?

## Data

- Dataset: official FairEval.
- Questions: 80.
- Candidate answers: ChatGPT vs Vicuna-13B.
- Human labels: ChatGPT / Vicuna-13B / Tie.

## Judges

- DeepSeek API: TODO fill in `configs/judges.local.json`.
- Qwen API: TODO fill in `configs/judges.local.json`.

Use fixed judge parameters for all methods:

- `temperature = 1.0` for comparability with FairEval-style stochastic judging.
- Same prompt for AB and BA inside one method.
- Same question subset across DeepSeek and Qwen.

## Stage 1: Reproduce Position Bias

For each judge and each FairEval sample:

1. Run `AB`: ChatGPT as Assistant 1, Vicuna-13B as Assistant 2.
2. Run `BA`: Vicuna-13B as Assistant 1, ChatGPT as Assistant 2.
3. Map positional winner back to the real model name.

Report:

- `AB first-position win rate`.
- `BA first-position win rate`.
- `position flip rate`.
- `naive accuracy vs human`.

Expected paper claim:

> Open-source judges also show order sensitivity under pairwise judging, suggesting that position bias is not limited to proprietary judges.

## Stage 2: Reproduce Existing Baseline

Baseline: Balanced Position Calibration (BPC).

Aggregation:

- If AB and BA point to the same real model, accept that winner.
- If both are tie, accept tie.
- Otherwise output `UNCERTAIN`.

Report:

- `BPC accuracy vs human, excluding uncertain`.
- `BPC uncertain rate`.
- `position flip samples`.

Expected paper claim:

> BPC reduces forced contradictory judgments, but it discards or abstains on unstable cases and does not by itself test whether model-level win-rate differences are significant.

## Stage 3: Our Symmetric Judge Protocol

Add three components on top of AB/BA:

1. Structured JSON output.
2. Criterion-level scores before final winner.
3. Paired permutation test over calibrated win/loss outcomes.

Aggregation:

- Consistent content winner: accept winner.
- Consistent tie: tie.
- Same position wins in both AB and BA: `POSITION_BIASED_UNCERTAIN`.
- Other contradiction: `UNCERTAIN`.

Report:

- `symmetric consistency`.
- `uncertain rate`.
- `accuracy vs human, excluding uncertain`.
- `permutation-test p-value`.

Expected paper claim:

> The proposed protocol makes unstable judgments explicit and avoids claiming a significant model winner when the calibrated evidence is weak.

## Tables

Table 1: Position bias reproduction.

| Judge | First-position win rate | Position flip rate | Naive acc. vs human |
| --- | ---: | ---: | ---: |
| DeepSeek | TODO | TODO | TODO |
| Qwen | TODO | TODO | TODO |

Table 2: BPC baseline.

| Judge | BPC acc. excl. uncertain | Uncertain rate | Permutation p |
| --- | ---: | ---: | ---: |
| DeepSeek | TODO | TODO | TODO |
| Qwen | TODO | TODO | TODO |

Table 3: Our protocol.

| Judge | Symmetric consistency | Uncertain rate | Acc. excl. uncertain | Permutation p |
| --- | ---: | ---: | ---: | ---: |
| DeepSeek | TODO | TODO | TODO | TODO |
| Qwen | TODO | TODO | TODO | TODO |

