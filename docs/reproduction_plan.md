# FairEval Reproduction Plan

## Target

The first reproducible target is Wang et al., *Large Language Models are not Fair Evaluators*. This is a good starting point because the official repository provides:

- 80 FairEval questions.
- Candidate answers from ChatGPT and Vicuna-13B.
- Human preference labels for ChatGPT vs Vicuna-13B.
- The original MEC/BPC implementation.

The phenomenon to reproduce is position bias: a judge's model-level result changes when the same two answers are shown in the opposite order.

## Baselines

1. **Naive pairwise judge**
   - Run only `AB`: ChatGPT answer as Assistant 1, Vicuna-13B answer as Assistant 2.
   - Convert the two scores into `CHATGPT`, `VICUNA13B`, or `TIE`.

2. **Balanced Position Calibration (BPC)**
   - Run `AB` and `BA` for the same question.
   - Map both judgments back to the real candidate model names.
   - Accept the result only if both orders identify the same real winner.
   - Otherwise mark the sample as `UNCERTAIN`.

3. **MEC + BPC**
   - The original FairEval code samples multiple evaluation evidences with `n=k`.
   - It averages scores from all evidence samples and both answer orders.

## Metrics

- **AB first-position win rate**: how often the answer shown first wins among non-ties.
- **Position flip rate**: how often `AB` and `BA` imply different real winners.
- **BPC uncertain rate**: how often BPC refuses to force a winner.
- **Accuracy vs human**: agreement with the released human labels, excluding `UNCERTAIN` for BPC.
- **Permutation-test p-value**: whether the calibrated ChatGPT-vs-Vicuna win imbalance is significant after paired sign flipping.

## Commands

Validate local official data:

```bash
uv run scripts/reproduce_faireval.py --dry-run
```

Run a small paid/API reproduction:

```bash
OPENAI_API_KEY=... uv run scripts/reproduce_faireval.py --model gpt-4o-mini --limit 10
```

Run with DeepSeek and Qwen after filling `configs/judges.local.json`:

```bash
uv run scripts/run_judges.py --config configs/judges.local.json --limit 10
```

Run the full 80-example reproduction:

```bash
uv run scripts/run_judges.py --config configs/judges.local.json
```

The row-level output is written to `results/faireval_bpc.csv`.

## Notes For The Paper

This setup reproduces the existing phenomenon and the strongest easy baseline from FairEval. For our own method, we can keep the same `AB/BA` calls but change the aggregation layer:

- Structured JSON prompt instead of free-form score lines.
- Criterion-level scoring before winner selection.
- `UNCERTAIN` label for contradictory order judgments.
- Paired permutation test before claiming one model wins.
