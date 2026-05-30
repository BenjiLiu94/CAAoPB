#!/usr/bin/env python3
"""Run independent pointwise scoring for FairEval answers."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import time
from pathlib import Path

from reproduce_faireval import ROOT, load_examples


def load_judge(config_path: Path, judge_name: str) -> dict:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    for judge in data.get("judges", []):
        if judge["name"] == judge_name:
            return judge
    raise SystemExit(f"Judge {judge_name!r} not found in {config_path}")


def resolve_api_key(value: str) -> str:
    return os.environ.get(value) or value


def build_prompt(question: str, answer: str) -> list[dict]:
    system = "You are a careful evaluator of answer quality."
    user = f"""Evaluate the answer to the user question.

Judge only correctness, relevance, helpfulness, completeness, reasoning quality, and safety.
Do not compare against any other answer.

Question:
{question}

Answer:
{answer}

Output exactly:
Evaluation evidence: <brief explanation>
Score: <a number from 1 to 10>"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def parse_score(text: str) -> float:
    match = re.search(r"Score\s*:\s*([0-9]+(?:\.[0-9]+)?)", text, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"could not parse pointwise score from output: {text!r}")
    return float(match.group(1))


def query(client, model: str, messages: list[dict], temperature: float, max_tokens: int, extra_body: dict | None) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=extra_body,
    )
    return response.choices[0].message.content or ""


def run(args: argparse.Namespace) -> None:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install dependencies with uv sync") from exc

    judge = load_judge(args.config, args.judge)
    model = judge["model"]
    if model == "deepseek-v4-flash":
        model = "deepseek-chat"
    extra_body = judge.get("extra_body")
    if extra_body is None and "Qwen3.6" in model:
        extra_body = {"enable_thinking": False}

    client = OpenAI(
        api_key=resolve_api_key(judge["api_key_env"]),
        base_url=judge["base_url"],
        timeout=args.request_timeout,
        max_retries=0,
    )

    examples = load_examples()
    if args.limit:
        examples = examples[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, example in enumerate(examples, start=1):
        raw_chatgpt = query(
            client,
            model,
            build_prompt(example.question, example.answer_1),
            args.temperature,
            args.max_tokens,
            extra_body,
        )
        time.sleep(args.sleep)
        raw_vicuna = query(
            client,
            model,
            build_prompt(example.question, example.answer_2),
            args.temperature,
            args.max_tokens,
            extra_body,
        )
        time.sleep(args.sleep)

        score_chatgpt = parse_score(raw_chatgpt)
        score_vicuna = parse_score(raw_vicuna)
        if score_chatgpt > score_vicuna:
            winner = "CHATGPT"
        elif score_vicuna > score_chatgpt:
            winner = "VICUNA13B"
        else:
            winner = "TIE"

        rows.append(
            {
                "question_id": example.question_id,
                "human": example.human,
                "score_chatgpt": score_chatgpt,
                "score_vicuna13b": score_vicuna,
                "score_gap": score_chatgpt - score_vicuna,
                "pointwise_winner": winner,
                "chatgpt_raw": raw_chatgpt,
                "vicuna_raw": raw_vicuna,
            }
        )
        print(
            f"[{idx}/{len(examples)}] qid={example.question_id} "
            f"ChatGPT={score_chatgpt:.1f} Vicuna={score_vicuna:.1f} winner={winner}",
            flush=True,
        )

    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    acc = sum(row["pointwise_winner"] == row["human"] for row in rows) / len(rows)
    print(f"\nPointwise accuracy: {acc:.3f}")
    print(f"Wrote {args.output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "judges.local.json")
    parser.add_argument("--judge", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--request-timeout", type=float, default=30.0)
    parser.add_argument("--max-tokens", type=int, default=384)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
