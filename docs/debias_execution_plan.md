# LLM-as-a-Judge Debias Execution Plan

## Goal

Build a short-cycle experiment to evaluate and reduce position bias in pairwise LLM-as-a-Judge.

The project should not claim to remove the judge model's internal bias. The safer goal is:

> Detect presentation-sensitive judgments, reduce their impact on final model comparison, and report uncertainty instead of forcing unstable wins.

## Research Questions

1. Do DeepSeek and Qwen judges show position sensitivity on FairEval?
2. How much does AB/BA balancing improve stability compared with naive AB judging?
3. Does treating AB/BA conflicts as uncertainty produce more reliable conclusions than simple score averaging?
4. Can light presentation perturbations identify unstable samples beyond standard AB/BA?

## Scope

Use only black-box OpenAI-compatible APIs:

- DeepSeek judge
- Qwen judge

Use the official FairEval data already downloaded in `external/FairEval`:

- Questions: `external/FairEval/question.jsonl`
- Answers: ChatGPT vs Vicuna-13B
- Human labels: `external/FairEval/review/review_gpt35_vicuna-13b_human.txt`

Avoid heavy methods in the first pass:

- No fine-tuning
- No white-box model analysis
- No translation method in the main experiment
- No unlabeled chunk reconstruction in the main experiment

## Methods To Run

### Method 1: Naive Pairwise Judge

Run one order only:

```text
AB: ChatGPT answer first, Vicuna-13B answer second
```

Output:

- scores for both candidates
- winner
- raw judge explanation

Purpose:

- Establish naive baseline.

### Method 2: AB/BA Swap

Run both:

```text
AB: ChatGPT first, Vicuna second
BA: Vicuna first, ChatGPT second
```

Map winners back to real candidates.

Report:

- AB winner
- BA winner
- whether the content-level winner is consistent
- whether the same position wins in both orders

Purpose:

- Directly measure position sensitivity.

### Method 3: FairEval-Style BPC

Use the FairEval-style score aggregation:

```text
score_candidate = average(score_in_AB, score_in_BA_after_mapping)
```

Winner is selected by averaged score.

Purpose:

- Reproduce the main existing solution.

### Method 4: Conflict-Aware BPC

Use AB/BA winner agreement instead of only averaged scores:

```text
AB and BA support same real candidate -> accept winner
AB and BA both tie -> tie
otherwise -> uncertain
```

Purpose:

- Avoid hiding contradictory judgments through averaging.

### Method 5: Light Presentation Robustness

Run a small number of logically equivalent prompt variants:

- `Assistant 1/2`
- `Answer A/B`
- `Candidate X/Y`

For each variant, run AB/BA.

Aggregate:

```text
stable winner across variants -> accept
conflicting winner across variants -> uncertain
```

Purpose:

- Test whether instability is broader than simple answer order.

Do this only after Methods 1-4 are working.

## Metrics

### Position Metrics

- First-position win rate:

```text
# first-position wins / # non-tie judgments
```

- Position flip rate:

```text
# pairs where AB and BA imply different real winners / # total pairs
```

- Same-position selection rate:

```text
# pairs where judge selects first in both AB and BA, or second in both AB and BA / # total pairs
```

### Accuracy Metrics

Compare against FairEval human labels:

- naive accuracy
- BPC accuracy
- conflict-aware BPC accuracy excluding uncertain
- coverage for conflict-aware BPC

Coverage:

```text
# accepted non-uncertain judgments / # total pairs
```

### Robustness Metrics

- Presentation consistency:

```text
# pairs with same real winner across prompt variants / # total pairs
```

- Uncertain rate:

```text
# uncertain pairs / # total pairs
```

### Statistical Metrics

Use a paired sign/permutation test over accepted win/loss outcomes:

```text
H0: ChatGPT and Vicuna have equal win probability.
```

Report p-value separately for:

- naive AB
- FairEval-style BPC
- conflict-aware BPC

## Experimental Procedure

### Step 1: Fill API Config

Copy:

```bash
cp configs/judges.example.json configs/judges.local.json
```

Fill:

- DeepSeek model name
- DeepSeek base URL
- Qwen model name
- Qwen base URL

Export keys:

```bash
export DEEPSEEK_API_KEY="TODO"
export QWEN_API_KEY="TODO"
```

### Step 2: Dry Run

```bash
uv run scripts/run_judges.py --config configs/judges.local.json --dry-run --limit 2
```

Expected:

- both judge configs load
- FairEval examples load
- no API call is made

### Step 3: Pilot Run

Run 5-10 samples first:

```bash
uv run scripts/run_judges.py --config configs/judges.local.json --limit 10
```

Check:

- outputs are parseable
- raw judge text contains scores
- no provider-specific API incompatibility

### Step 4: Full Run

```bash
uv run scripts/run_judges.py --config configs/judges.local.json
```

Expected output:

```text
results/faireval_deepseek_bpc.csv
results/faireval_qwen_bpc.csv
```

### Step 5: Analyze Results

Generate summary tables:

Table 1: Position Bias

| Judge | First-position win rate | Position flip rate | Same-position rate |
| --- | ---: | ---: | ---: |
| DeepSeek | TODO | TODO | TODO |
| Qwen | TODO | TODO | TODO |

Table 2: Human Agreement

| Judge | Naive acc. | BPC acc. | Conflict-aware acc. | Conflict-aware coverage |
| --- | ---: | ---: | ---: | ---: |
| DeepSeek | TODO | TODO | TODO | TODO |
| Qwen | TODO | TODO | TODO | TODO |

Table 3: Model-Level Conclusion

| Judge | Method | ChatGPT wins | Vicuna wins | Tie | Uncertain | p-value |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | Naive | TODO | TODO | TODO | 0 | TODO |
| DeepSeek | BPC | TODO | TODO | TODO | 0 | TODO |
| DeepSeek | Conflict-aware | TODO | TODO | TODO | TODO | TODO |
| Qwen | Naive | TODO | TODO | TODO | 0 | TODO |
| Qwen | BPC | TODO | TODO | TODO | 0 | TODO |
| Qwen | Conflict-aware | TODO | TODO | TODO | TODO | TODO |

## Expected Outcomes

Likely positive results:

- DeepSeek/Qwen show measurable position sensitivity.
- AB/BA exposes conflicts hidden by naive AB.
- Conflict-aware aggregation reduces overconfident model-level claims.
- Some naive wins become uncertain or statistically insignificant.

Acceptable negative results:

- If BPC already solves most instability, report that simple counterbalancing is a strong baseline.
- If DeepSeek and Qwen disagree heavily, report judge dependence and use it as evidence for uncertainty-aware evaluation.
- If human agreement drops after conflict filtering, analyze whether filtering discards easy cases or preserves hard cases.

## Stop Conditions

Stop adding new methods if:

- Methods 1-4 already produce clear results.
- API cost becomes high.
- parse failures exceed 10%.
- judge outputs are too inconsistent to compare.

Only add presentation variants after the main AB/BA/BPC result is stable.

## Optional Extensions

### Pointwise Scoring + Pairwise Tie-Break

Score each candidate separately first. If score gap is small, run AB/BA. This tests whether near-tie cases are more position-sensitive.

### Labeled Chunk Interleaving

Split answers into labeled chunks and interleave them while preserving candidate identity. This should be treated as an exploratory presentation stress test, not the main method.

### Multi-Judge Agreement Routing

Accept a winner only when DeepSeek and Qwen agree after AB/BA. Otherwise mark uncertain.

## Main Risk

The project may not find a new method that clearly outperforms BPC.

Mitigation:

Frame the project as a robustness and uncertainty analysis:

> AB/BA is a strong baseline, but its output should not be collapsed into overconfident wins. Conflict-aware aggregation and statistical testing provide a more conservative model-level conclusion.

