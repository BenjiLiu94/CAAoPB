#!/usr/bin/env python3
"""Run rubric-first independent scoring for FairEval answers."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from pathlib import Path

from reproduce_faireval import ROOT, load_examples


DIMENSIONS = ["factuality", "relevance", "completeness", "reasoning", "clarity"]


def load_judge(config_path: Path, judge_name: str) -> dict:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    for judge in data.get("judges", []):
        if judge["name"] == judge_name:
            return judge
    raise SystemExit(f"Judge {judge_name!r} not found in {config_path}")


def resolve_api_key(value: str) -> str:
    return os.environ.get(value) or value


def build_prompt(question: str, answer: str) -> list[dict]:
    system = "You are a strict evaluator. Score only the provided answer, not any hidden alternative answer."
    user = f"""Evaluate the answer to the user question with the fixed rubric below.

Rubric dimensions:
- factuality: factual correctness and absence of hallucination.
- relevance: whether the answer directly addresses the question.
- completeness: whether important parts of the question are sufficiently covered.
- reasoning: quality, consistency, and usefulness of reasoning.
- clarity: organization and readability.

Use integer scores from 1 to 10 for each dimension. Then give an overall score from 1 to 10.
Do not compare this answer against any other answer.

Question:
{question}

Answer:
{answer}

Output only valid JSON with this exact schema:
{{
  "factuality": 1,
  "relevance": 1,
  "completeness": 1,
  "reasoning": 1,
  "clarity": 1,
  "overall": 1,
  "evidence": "brief reason"
}}"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{", text)
        if not match:
            raise ValueError(f"could not find JSON object in output: {text!r}")
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(text[match.start() :])
        return data


def parse_result(text: str) -> dict:
    data = extract_json(text)
    result = {}
    for key in [*DIMENSIONS, "overall"]:
        value = float(data[key])
        if value < 1 or value > 10:
            raise ValueError(f"{key} score out of range: {value}")
        result[key] = value
    result["evidence"] = str(data.get("evidence", ""))
    return result


def query(client, model: str, messages: list[dict], temperature: float, max_tokens: int, extra_body: dict | None) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=extra_body,
    )
    message = response.choices[0].message
    content = message.content or ""
    if content:
        return content
    reasoning = getattr(message, "reasoning_content", None)
    return reasoning or ""


def infer_extra_body(model: str, thinking: str, configured: dict | None) -> dict | None:
    if thinking == "config":
        if configured is not None:
            return configured
        if "Qwen3.6" in model:
            return {"enable_thinking": False}
        return None
    if thinking == "on":
        return {"enable_thinking": True}
    if thinking == "off":
        return {"enable_thinking": False}
    raise ValueError(f"unknown thinking mode: {thinking}")


def winner(score_chatgpt: float, score_vicuna: float, tie_margin: float) -> str:
    diff = score_chatgpt - score_vicuna
    if abs(diff) <= tie_margin:
        return "TIE"
    if diff > 0:
        return "CHATGPT"
    return "VICUNA13B"


def run(args: argparse.Namespace) -> None:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install dependencies with uv sync") from exc

    judge = load_judge(args.config, args.judge)
    model = judge["model"]
    if model == "deepseek-v4-flash":
        model = "deepseek-chat"
    extra_body = infer_extra_body(model, args.thinking, judge.get("extra_body"))

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

        chatgpt = parse_result(raw_chatgpt)
        vicuna = parse_result(raw_vicuna)
        score_gap = chatgpt["overall"] - vicuna["overall"]
        row = {
            "question_id": example.question_id,
            "human": example.human,
            "judge": args.judge,
            "model": model,
            "thinking": args.thinking,
            "score_chatgpt": chatgpt["overall"],
            "score_vicuna13b": vicuna["overall"],
            "score_gap": score_gap,
            "rubric_winner": winner(chatgpt["overall"], vicuna["overall"], args.tie_margin),
            "chatgpt_evidence": chatgpt["evidence"],
            "vicuna_evidence": vicuna["evidence"],
            "chatgpt_raw": raw_chatgpt,
            "vicuna_raw": raw_vicuna,
        }
        for dimension in DIMENSIONS:
            row[f"chatgpt_{dimension}"] = chatgpt[dimension]
            row[f"vicuna13b_{dimension}"] = vicuna[dimension]
            row[f"gap_{dimension}"] = chatgpt[dimension] - vicuna[dimension]
        rows.append(row)
        correct = row["rubric_winner"] == row["human"]
        print(
            f"[{idx}/{len(examples)}] qid={example.question_id} "
            f"ChatGPT={chatgpt['overall']:.1f} Vicuna={vicuna['overall']:.1f} "
            f"winner={row['rubric_winner']} human={example.human} correct={correct}",
            flush=True,
        )

    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    acc = sum(row["rubric_winner"] == row["human"] for row in rows) / len(rows)
    print(f"\nRubric pointwise accuracy: {acc:.3f}")
    print(f"Wrote {args.output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "judges.local.json")
    parser.add_argument("--judge", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--request-timeout", type=float, default=60.0)
    parser.add_argument("--max-tokens", type=int, default=768)
    parser.add_argument("--thinking", choices=["config", "on", "off"], default="config")
    parser.add_argument("--tie-margin", type=float, default=0.0)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
