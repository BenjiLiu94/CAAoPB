#!/usr/bin/env python3
"""Diagnose an OpenAI-compatible chat API with progressively harder prompts."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def resolve_api_key(value: str) -> str:
    return os.environ.get(value) or value


def load_judge(config_path: Path, judge_name: str) -> dict:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    judges = data.get("judges", [])
    for judge in judges:
        if judge["name"] == judge_name:
            return judge
    raise SystemExit(f"Judge {judge_name!r} not found in {config_path}")


def fair_eval_prompt() -> list[dict]:
    from reproduce_faireval import build_prompt, load_examples

    example = load_examples()[0]
    return build_prompt(example.question, example.answer_1, example.answer_2)


def call_chat(
    client,
    model: str,
    messages: list[dict],
    max_tokens: int,
    temperature: float,
    extra_body: dict | None,
) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=extra_body,
    )
    return response.choices[0].message.content or ""


def run_case(
    label: str,
    client,
    model: str,
    messages: list[dict],
    max_tokens: int,
    temperature: float,
    extra_body: dict | None,
) -> bool:
    print(f"\n== {label} ==", flush=True)
    start = time.monotonic()
    try:
        text = call_chat(client, model, messages, max_tokens, temperature, extra_body)
    except Exception as exc:
        elapsed = time.monotonic() - start
        print(f"FAILED after {elapsed:.2f}s", flush=True)
        print(f"{type(exc).__name__}: {exc}", flush=True)
        return False

    elapsed = time.monotonic() - start
    preview = text.replace("\n", "\\n")[:500]
    print(f"OK after {elapsed:.2f}s", flush=True)
    print(f"response preview: {preview}", flush=True)
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "judges.local.json")
    parser.add_argument("--judge", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--api-key-env", default="")
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.judge:
        judge = load_judge(args.config, args.judge)
        model = judge["model"]
        base_url = judge["base_url"]
        api_key_env = judge["api_key_env"]
        extra_body = judge.get("extra_body")
    else:
        model = args.model
        base_url = args.base_url
        api_key_env = args.api_key_env
        extra_body = None

    if not model or not base_url or not api_key_env:
        raise SystemExit("Provide --judge or all of --model, --base-url, and --api-key-env")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install the OpenAI SDK first: uv sync") from exc

    api_key = resolve_api_key(api_key_env)
    if extra_body is None and "Qwen3.6" in model:
        extra_body = {"enable_thinking": False}
    print("API diagnostic", flush=True)
    print(f"model: {model}", flush=True)
    print(f"base_url: {base_url}", flush=True)
    print(f"timeout: {args.timeout}s", flush=True)
    print(f"api_key: {'env:' + api_key_env if os.environ.get(api_key_env) else api_key[:6] + '...' + api_key[-4:]}", flush=True)
    print(f"extra_body: {extra_body}", flush=True)

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=args.timeout, max_retries=0)

    minimal = [{"role": "user", "content": 'Say exactly: ok'}]
    score_format = [
        {"role": "system", "content": "You are a precise evaluator."},
        {
            "role": "user",
            "content": (
                "Compare two answers.\n"
                "Question: What is 2+2?\n"
                "Assistant 1: 4\n"
                "Assistant 2: 5\n"
                "Output exactly:\n"
                "Evaluation evidence: <brief>\n"
                "Score of the Assistant 1: <score>\n"
                "Score of the Assistant 2: <score>"
            ),
        },
    ]

    ok1 = run_case("minimal", client, model, minimal, max_tokens=8, temperature=0, extra_body=extra_body)
    ok2 = run_case("score-format", client, model, score_format, max_tokens=128, temperature=0, extra_body=extra_body)
    ok3 = run_case(
        "faireval-first-prompt",
        client,
        model,
        fair_eval_prompt(),
        max_tokens=256,
        temperature=0,
        extra_body=extra_body,
    )

    print("\nSummary", flush=True)
    print(f"minimal: {'OK' if ok1 else 'FAIL'}", flush=True)
    print(f"score-format: {'OK' if ok2 else 'FAIL'}", flush=True)
    print(f"faireval-first-prompt: {'OK' if ok3 else 'FAIL'}", flush=True)


if __name__ == "__main__":
    main()
