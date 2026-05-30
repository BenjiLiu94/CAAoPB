#!/usr/bin/env python3
"""Build whole-answer repetition prompts for FairEval.

Unlike chunk interleaving, this keeps each answer intact and repeats the full
candidate answers in alternating order, e.g. X/Y/X/Y or Y/X/Y/X.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reproduce_faireval import ROOT, load_examples


def candidate_text(example, candidate: str) -> str:
    if candidate == "chatgpt":
        return example.answer_1
    if candidate == "vicuna13b":
        return example.answer_2
    raise ValueError(f"unknown candidate: {candidate}")


def build_prompt(question: str, x_answer: str, y_answer: str, sequence: list[str]) -> str:
    blocks = []
    for idx, source in enumerate(sequence, start=1):
        answer = x_answer if source == "X" else y_answer
        blocks.append(f"[Presentation {idx} | Candidate {source}]\n{answer}")
    block_text = "\n\n".join(blocks)
    return f"""You are an impartial evaluator.

The same two candidate answers are shown multiple times in alternating order.
Repeated presentations are exact duplicates and should not be counted as extra evidence.

Important rules:
1. Evaluate Candidate X by its answer content, ignoring repeated copies.
2. Evaluate Candidate Y by its answer content, ignoring repeated copies.
3. The presentation order must not affect your judgment.
4. Choose Tie if both candidates are similar in quality.

User question:
{question}

Repeated presentations:
{block_text}

Output exactly:
Evaluation evidence: <brief explanation>
Score of Candidate X: <score from 1 to 10>
Score of Candidate Y: <score from 1 to 10>
Winner: <X or Y or Tie>"""


def build_conditions(example) -> list[dict]:
    specs = [
        {"condition": "c1_chatgpt_x_xyxy", "X": "chatgpt", "Y": "vicuna13b", "sequence": ["X", "Y", "X", "Y"]},
        {"condition": "c2_chatgpt_x_yxyx", "X": "chatgpt", "Y": "vicuna13b", "sequence": ["Y", "X", "Y", "X"]},
        {"condition": "c3_vicuna_x_xyxy", "X": "vicuna13b", "Y": "chatgpt", "sequence": ["X", "Y", "X", "Y"]},
        {"condition": "c4_vicuna_x_yxyx", "X": "vicuna13b", "Y": "chatgpt", "sequence": ["Y", "X", "Y", "X"]},
    ]
    out = []
    for spec in specs:
        x_answer = candidate_text(example, spec["X"])
        y_answer = candidate_text(example, spec["Y"])
        out.append(
            {
                "condition": spec["condition"],
                "question_id": example.question_id,
                "human": example.human,
                "x_candidate": spec["X"],
                "y_candidate": spec["Y"],
                "x_language": "en",
                "y_language": "en",
                "start": spec["sequence"][0],
                "sequence": "".join(spec["sequence"]),
                "prompt": build_prompt(example.question, x_answer, y_answer, spec["sequence"]),
            }
        )
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--pattern", choices=["abab", "abba"], default="abab")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "repeat_whole_prompts_limit5.jsonl")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = load_examples()
    if args.limit:
        examples = examples[: args.limit]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.output.open("w", encoding="utf-8") as handle:
        for example in examples:
            conditions = build_conditions(example)
            if args.pattern == "abba":
                for condition in conditions:
                    sequence = ["X", "Y", "Y", "X"] if condition["sequence"] == "XYXY" else ["Y", "X", "X", "Y"]
                    condition["condition"] = condition["condition"].replace("xyxy", "xyyx").replace("yxyx", "yxxy")
                    condition["sequence"] = "".join(sequence)
                    condition["start"] = sequence[0]
                    condition["prompt"] = build_prompt(
                        example.question,
                        candidate_text(example, condition["x_candidate"]),
                        candidate_text(example, condition["y_candidate"]),
                        sequence,
                    )
            for condition in conditions:
                handle.write(json.dumps(condition, ensure_ascii=False) + "\n")
                count += 1
    print(f"Wrote {count} whole-answer repetition prompts to {args.output}")


if __name__ == "__main__":
    main()
