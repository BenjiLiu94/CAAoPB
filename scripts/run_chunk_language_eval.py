#!/usr/bin/env python3
"""Run judge evaluation on chunk-language prompts."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from pathlib import Path

from reproduce_faireval import ROOT
from run_judges import load_config, resolve_api_key_env


def parse_output(text: str) -> tuple[float, float, str]:
    score_x = re.search(r"Score of Candidate X\s*:\s*([0-9]+(?:\.[0-9]+)?)", text, flags=re.IGNORECASE)
    score_y = re.search(r"Score of Candidate Y\s*:\s*([0-9]+(?:\.[0-9]+)?)", text, flags=re.IGNORECASE)
    winner = re.search(r"Winner\s*:\s*(X|Y|Tie)", text, flags=re.IGNORECASE)
    if not (score_x and score_y and winner):
        raise ValueError(f"could not parse chunk-language output: {text!r}")
    return float(score_x.group(1)), float(score_y.group(1)), winner.group(1).upper().replace("TIE", "Tie")


def real_winner(display_winner: str, x_candidate: str, y_candidate: str) -> str:
    if display_winner == "Tie":
        return "TIE"
    candidate = x_candidate if display_winner == "X" else y_candidate
    if candidate == "chatgpt":
        return "CHATGPT"
    if candidate == "vicuna13b":
        return "VICUNA13B"
    raise ValueError(f"unknown candidate: {candidate}")


def run(args: argparse.Namespace) -> None:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install dependencies with uv sync") from exc

    judge = next(j for j in load_config(args.config) if j["name"] == args.judge)
    model = judge["model"]
    if model == "deepseek-v4-flash":
        model = "deepseek-chat"
    extra_body = judge.get("extra_body")
    if extra_body is None and "Qwen3.6" in model:
        extra_body = {"enable_thinking": False}
    api_key_env, extra_env = resolve_api_key_env(judge)
    os.environ.update(extra_env)
    client = OpenAI(
        api_key=os.environ.get(api_key_env) or api_key_env,
        base_url=judge["base_url"],
        timeout=args.request_timeout,
        max_retries=0,
    )

    rows = [json.loads(line) for line in args.prompts.open(encoding="utf-8") if line.strip()]
    if args.limit_conditions:
        rows = rows[: args.limit_conditions]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_rows = []
    for idx, row in enumerate(rows, start=1):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a careful and impartial evaluator."},
                {"role": "user", "content": row["prompt"]},
            ],
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            extra_body=extra_body,
        )
        raw = response.choices[0].message.content or ""
        score_x, score_y, display_winner = parse_output(raw)
        winner = real_winner(display_winner, row["x_candidate"], row["y_candidate"])
        result = {
            "question_id": row["question_id"],
            "condition": row["condition"],
            "human": row["human"],
            "x_candidate": row["x_candidate"],
            "y_candidate": row["y_candidate"],
            "x_language": row["x_language"],
            "y_language": row["y_language"],
            "start": row["start"],
            "score_x": score_x,
            "score_y": score_y,
            "display_winner": display_winner,
            "real_winner": winner,
            "raw": raw,
        }
        out_rows.append(result)
        print(f"[{idx}/{len(rows)}] qid={row['question_id']} {row['condition']} winner={winner}", flush=True)
        time.sleep(args.sleep)

    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Wrote {args.output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "judges.local.json")
    parser.add_argument("--judge", required=True)
    parser.add_argument("--prompts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--request-timeout", type=float, default=60.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--limit-conditions", type=int, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
