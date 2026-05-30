#!/usr/bin/env python3
"""Reproduce FairEval-style position bias checks and BPC calibration.

The script has two useful modes:

1. `--dry-run` validates the official FairEval files and reports human labels.
2. Without `--dry-run`, it calls an OpenAI-compatible chat API to judge both
   AB and BA orders, then aggregates with Balanced Position Calibration (BPC).

Example:
    python3 scripts/reproduce_faireval.py --dry-run
    OPENAI_API_KEY=... python3 scripts/reproduce_faireval.py --limit 10
    OTHER_API_KEY=... python3 scripts/reproduce_faireval.py --api-key-env OTHER_API_KEY --base-url https://api.example.com/v1 --model some-model
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
FAIREVAL = ROOT / "external" / "FairEval"


@dataclass(frozen=True)
class Example:
    question_id: int
    question: str
    answer_1: str
    answer_2: str
    human: str | None


@dataclass(frozen=True)
class Judgment:
    order: str
    score_1: float
    score_2: float
    raw: str

    @property
    def winner_position(self) -> str:
        if self.score_1 > self.score_2:
            return "first"
        if self.score_2 > self.score_1:
            return "second"
        return "tie"


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_human_labels(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"CHATGPT|VICUNA13B|TIE", text)


def load_examples() -> list[Example]:
    questions = read_jsonl(FAIREVAL / "question.jsonl")
    answer_1 = read_jsonl(FAIREVAL / "answer" / "answer_gpt35.jsonl")
    answer_2 = read_jsonl(FAIREVAL / "answer" / "answer_vicuna-13b.jsonl")
    human = read_human_labels(FAIREVAL / "review" / "review_gpt35_vicuna-13b_human.txt")

    count = min(len(questions), len(answer_1), len(answer_2), len(human))
    examples = []
    for idx in range(count):
        q = questions[idx]
        a1 = answer_1[idx]
        a2 = answer_2[idx]
        if not (q["question_id"] == a1["question_id"] == a2["question_id"]):
            raise ValueError(f"question_id mismatch at index {idx}")
        examples.append(
            Example(
                question_id=q["question_id"],
                question=q["text"],
                answer_1=a1["text"],
                answer_2=a2["text"],
                human=human[idx],
            )
        )
    return examples


def build_prompt(question: str, first_answer: str, second_answer: str) -> list[dict]:
    system = "You are a helpful and precise assistant for checking answer quality."
    user = f"""[Question]
{question}

[The Start of Assistant 1's Answer]
{first_answer}
[The End of Assistant 1's Answer]

[The Start of Assistant 2's Answer]
{second_answer}
[The End of Assistant 2's Answer]

[System]
We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above.
Please rate the helpfulness, relevance, accuracy, and level of detail of their responses.

Each assistant receives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance.
Please first provide concise evaluation evidence, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment.
Then output exactly two score lines.

Output with the following format:
Evaluation evidence: <your evaluation explanation here>
Score of the Assistant 1: <score>
Score of the Assistant 2: <score>"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def parse_scores(text: str) -> tuple[float, float]:
    patterns = [
        r"Score of the Assistant 1\s*:\s*([0-9]+(?:\.[0-9]+)?)",
        r"Score of the Assistant 2\s*:\s*([0-9]+(?:\.[0-9]+)?)",
    ]
    matches = [re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns]
    if not all(matches):
        raise ValueError(f"could not parse scores from judge output: {text!r}")
    return float(matches[0].group(1)), float(matches[1].group(1))


def query_openai_compatible(
    model: str,
    messages: list[dict],
    temperature: float,
    api_key_env: str,
    base_url: str | None,
    request_timeout: float,
    extra_body: dict | None,
    max_tokens: int,
) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install the OpenAI SDK first: pip install openai") from exc

    api_key = os.environ.get(api_key_env) or api_key_env
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=request_timeout)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=extra_body,
    )
    return response.choices[0].message.content or ""


def judge_once(
    example: Example,
    order: str,
    model: str,
    temperature: float,
    api_key_env: str,
    base_url: str | None,
    request_timeout: float,
    extra_body: dict | None,
    max_tokens: int,
) -> Judgment:
    if order == "AB":
        messages = build_prompt(example.question, example.answer_1, example.answer_2)
    elif order == "BA":
        messages = build_prompt(example.question, example.answer_2, example.answer_1)
    else:
        raise ValueError(f"unknown order: {order}")

    raw = query_openai_compatible(
        model,
        messages,
        temperature,
        api_key_env,
        base_url,
        request_timeout,
        extra_body,
        max_tokens,
    )
    score_1, score_2 = parse_scores(raw)
    return Judgment(order=order, score_1=score_1, score_2=score_2, raw=raw)


def true_winner_from_order(judgment: Judgment) -> str:
    if judgment.winner_position == "tie":
        return "TIE"
    if judgment.order == "AB":
        return "CHATGPT" if judgment.winner_position == "first" else "VICUNA13B"
    return "VICUNA13B" if judgment.winner_position == "first" else "CHATGPT"


def bpc_winner(ab: Judgment, ba: Judgment) -> str:
    ab_winner = true_winner_from_order(ab)
    ba_winner = true_winner_from_order(ba)
    if ab_winner == ba_winner:
        return ab_winner
    return "UNCERTAIN"


def human_summary(examples: Iterable[Example]) -> dict[str, int]:
    counts = {"CHATGPT": 0, "VICUNA13B": 0, "TIE": 0}
    for example in examples:
        if example.human in counts:
            counts[example.human] += 1
    return counts


def accuracy(predictions: list[str], labels: list[str]) -> float:
    comparable = [(p, y) for p, y in zip(predictions, labels) if p != "UNCERTAIN"]
    if not comparable:
        return float("nan")
    return sum(p == y for p, y in comparable) / len(comparable)


def permutation_test(wins: list[int], rounds: int, seed: int) -> float:
    """Two-sided sign-flip test for paired win/loss indicators.

    wins uses +1 for model 1 win, -1 for model 2 win, and 0 for ties/uncertain.
    """
    observed = abs(sum(wins))
    rng = random.Random(seed)
    extreme = 0
    for _ in range(rounds):
        total = 0
        for value in wins:
            if value == 0:
                continue
            total += value if rng.random() < 0.5 else -value
        if abs(total) >= observed:
            extreme += 1
    return (extreme + 1) / (rounds + 1)


def win_value(label: str) -> int:
    if label == "CHATGPT":
        return 1
    if label == "VICUNA13B":
        return -1
    return 0


def run(args: argparse.Namespace) -> None:
    examples = load_examples()
    if args.limit:
        examples = examples[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loaded {len(examples)} FairEval examples.")
    print(f"Human labels: {human_summary(examples)}")

    if args.dry_run:
        print(f"Dry run only: set {args.api_key_env} and remove --dry-run to call a judge model.")
        return

    rows = []
    for idx, example in enumerate(examples, start=1):
        ab = judge_once(
            example,
            "AB",
            args.model,
            args.temperature,
            args.api_key_env,
            args.base_url,
            args.request_timeout,
            args.extra_body,
            args.max_tokens,
        )
        time.sleep(args.sleep)
        ba = judge_once(
            example,
            "BA",
            args.model,
            args.temperature,
            args.api_key_env,
            args.base_url,
            args.request_timeout,
            args.extra_body,
            args.max_tokens,
        )
        time.sleep(args.sleep)

        naive = true_winner_from_order(ab)
        swapped = true_winner_from_order(ba)
        calibrated = bpc_winner(ab, ba)
        rows.append(
            {
                "question_id": example.question_id,
                "human": example.human,
                "ab_score_chatgpt": ab.score_1,
                "ab_score_vicuna13b": ab.score_2,
                "ba_score_chatgpt": ba.score_2,
                "ba_score_vicuna13b": ba.score_1,
                "ab_position_winner": ab.winner_position,
                "ba_position_winner": ba.winner_position,
                "naive_winner": naive,
                "swapped_winner": swapped,
                "bpc_winner": calibrated,
                "position_flip": naive != swapped,
                "ab_raw": ab.raw,
                "ba_raw": ba.raw,
            }
        )
        print(f"[{idx}/{len(examples)}] qid={example.question_id} AB={naive} BA={swapped} BPC={calibrated}")

    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    naive_predictions = [row["naive_winner"] for row in rows]
    bpc_predictions = [row["bpc_winner"] for row in rows]
    labels = [row["human"] for row in rows]
    non_tie_positions = [
        row["ab_position_winner"]
        for row in rows
        if row["ab_position_winner"] in {"first", "second"}
    ]
    first_rate = (
        sum(pos == "first" for pos in non_tie_positions) / len(non_tie_positions)
        if non_tie_positions
        else float("nan")
    )
    flip_rate = statistics.mean(row["position_flip"] for row in rows)
    uncertain_rate = statistics.mean(row["bpc_winner"] == "UNCERTAIN" for row in rows)
    p_value = permutation_test([win_value(row["bpc_winner"]) for row in rows], args.permutations, args.seed)

    print("\nSummary")
    print(f"Naive accuracy vs human: {accuracy(naive_predictions, labels):.3f}")
    print(f"BPC accuracy vs human, excluding uncertain: {accuracy(bpc_predictions, labels):.3f}")
    print(f"AB first-position win rate: {first_rate:.3f}")
    print(f"Position flip rate: {flip_rate:.3f}")
    print(f"BPC uncertain rate: {uncertain_rate:.3f}")
    print(f"Permutation-test p-value for BPC ChatGPT-vs-Vicuna win imbalance: {p_value:.4f}")
    print(f"Wrote row-level results to {args.output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible API base URL, e.g. https://api.example.com/v1")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY", help="Environment variable containing the API key")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--request-timeout", type=float, default=60.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--extra-body-json", default="", help="JSON object passed as OpenAI extra_body")
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--permutations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "faireval_bpc.csv")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.extra_body = json.loads(args.extra_body_json) if args.extra_body_json else None
    if not args.dry_run:
        raw = os.environ.get(args.api_key_env)
        if not raw and not args.api_key_env.startswith("sk-"):
            raise SystemExit(f"{args.api_key_env} is not set. Use --dry-run to validate local data only.")
    run(args)
