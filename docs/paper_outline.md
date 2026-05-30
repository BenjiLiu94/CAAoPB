# Paper Outline

## Working Title

**Order Sensitivity as Uncertainty: A Conflict-Aware Analysis of Position Bias in LLM-as-a-Judge**

## 1. Introduction

- LLM-as-a-Judge is widely used for open-ended response evaluation.
- Pairwise judging is simple and scalable, but it can be sensitive to answer order.
- Existing AB/BA balancing and BPC reduce direct order imbalance, but score averaging can hide contradictory sample-level judgments.
- This work asks whether AB/BA disagreement should be treated not merely as noise to average away, but as an uncertainty signal.

Core claim:

> Position bias is not fully removed by balancing. However, order conflicts reveal unreliable judgments and should be surfaced in evaluation protocols.

## 2. Background and Related Work

- LLM-as-a-Judge and pairwise evaluation.
- MT-Bench / Chatbot Arena: strong judge models and known biases.
- FairEval: position bias, MEC, BPC, human-in-the-loop calibration.
- Position bias studies: repetition stability, position consistency, preference fairness.
- Uncertainty and abstention in model evaluation.

## 3. Problem Setup

Given a question `q` and two candidate answers:

```text
Answer X: response from ChatGPT
Answer Y: response from Vicuna-13B
```

Pairwise judge is run under two orders:

```text
AB: X first, Y second
BA: Y first, X second
```

An ideal content-based judge should map both orders to the same real winner.

## 4. Methods

### 4.1 Naive Pairwise Judge

- Run fixed AB only.
- Convert score difference into winner.

### 4.2 FairEval-Style BPC

- Run AB and BA.
- Map BA scores back to true candidate identities.
- Average candidate scores and select winner.

### 4.3 Conflict-Aware BPC

Aggregation rule:

| AB real winner | BA real winner | Output |
| --- | --- | --- |
| Same non-tie candidate | Same candidate | Candidate wins |
| Tie | Tie | Tie |
| Different outputs | Any conflict | Uncertain |

Rationale:

- A conflict after order swap indicates that the judgment is presentation-sensitive.
- Such a pair should not contribute equally to model-level win claims.

### 4.4 Two-Judge Agreement Routing

- Run the conflict-aware protocol with two judges.
- Accept a final winner only when both judges produce the same non-uncertain winner.
- Otherwise mark the pair as uncertain.

## 5. Experimental Setup

- Dataset: FairEval, 80 ChatGPT vs Vicuna-13B comparisons.
- Human labels: ChatGPT / Vicuna-13B / Tie.
- Judges:
  - DeepSeek v4 flash
  - Qwen3.6-35B-A3B
- Metrics:
  - First-position win rate
  - Position flip rate
  - Human agreement
  - Coverage
  - Model-level win counts
  - Paired permutation-test p-value

## 6. Results

### 6.1 Position Bias Appears Across Judges

Main table: first-position win rate and position flip rate.

Expected interpretation:

- Both judges substantially favor the first answer.
- AB/BA flip rates show sample-level instability.

### 6.2 BPC Does Not Guarantee Better Sample-Level Accuracy

Main table: naive accuracy vs FairEval-style BPC accuracy.

Expected interpretation:

- Score averaging is not a stable sample-level accuracy improvement.
- It can hide order conflicts.

### 6.3 Conflict-Aware Aggregation Improves Accepted-Set Reliability

Main table: conflict-aware accuracy and coverage.

Expected interpretation:

- Accuracy on accepted samples improves for both judges.
- This is a precision-coverage tradeoff, not a free accuracy gain.

### 6.4 Cross-Judge Agreement Further Increases Reliability

Main table: two-judge agreement routing.

Expected interpretation:

- Requiring both judges to agree gives higher accepted-set accuracy.
- Coverage drops substantially.

## 7. Discussion

- AB/BA should be viewed as an uncertainty detector, not only as a calibration trick.
- Fixed-order evaluation can overstate model-level significance.
- A reliable evaluation protocol should report both accuracy and coverage.
- Judge choice itself is an uncertainty source.

## 8. Limitations

- Only one model pair: ChatGPT vs Vicuna-13B.
- Dataset size is small: 80 FairEval samples.
- Conflict-aware accuracy is computed on accepted samples only.
- Does not prove elimination of internal judge bias.
- API judges are black boxes; no white-box causal mechanism is analyzed.

## 9. Conclusion

The study shows that position bias persists across open judge APIs. Existing score-averaging calibration is insufficient as a sample-level reliability mechanism. Treating AB/BA disagreements and cross-judge disagreements as uncertainty provides a more conservative and reliable evaluation protocol, at the cost of lower coverage.

