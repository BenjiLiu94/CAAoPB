#!/usr/bin/env python3
"""Prepare Chinese translation cache for FairEval answers."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from reproduce_faireval import ROOT, load_examples
from run_judges import load_config, resolve_api_key_env


def existing_rows(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    rows = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                row = json.loads(line)
                rows[str(row["question_id"])] = row
    return rows


def translate(client, model: str, text: str, timeout_hint: str, extra_body: dict | None, max_tokens: int) -> str:
    messages = [
        {"role": "system", "content": "You are a precise translator."},
        {
            "role": "user",
            "content": (
                "Translate the following answer into Simplified Chinese. "
                "Preserve all factual content, numbers, lists, and logical structure. "
                "Do not add new information. Output only the translation.\n\n"
                f"{text}"
            ),
        },
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens,
        extra_body=extra_body,
    )
    return (response.choices[0].message.content or "").strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "judges.local.json")
    parser.add_argument("--judge", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--request-timeout", type=float, default=60.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "translations_zh.jsonl")
    return parser.parse_args()


def main() -> None:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install dependencies with uv sync") from exc

    args = parse_args()
    judge = next(j for j in load_config(args.config) if j["name"] == args.judge)
    model = judge["model"]
    if model == "deepseek-v4-flash":
        model = "deepseek-chat"
    extra_body = judge.get("extra_body")
    if extra_body is None and "Qwen3.6" in model:
        extra_body = {"enable_thinking": False}

    api_key_env, extra_env = resolve_api_key_env(judge)
    os.environ.update(extra_env)
    api_key = os.environ.get(api_key_env) or api_key_env
    client = OpenAI(api_key=api_key, base_url=judge["base_url"], timeout=args.request_timeout, max_retries=0)

    examples = load_examples()
    if args.limit:
        examples = examples[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = existing_rows(args.output)
    with args.output.open("a", encoding="utf-8") as handle:
        for idx, example in enumerate(examples, start=1):
            qid = str(example.question_id)
            if qid in rows:
                print(f"[{idx}/{len(examples)}] qid={qid} exists, skip", flush=True)
                continue
            chatgpt_zh = translate(client, model, example.answer_1, "chatgpt", extra_body, args.max_tokens)
            time.sleep(args.sleep)
            vicuna_zh = translate(client, model, example.answer_2, "vicuna", extra_body, args.max_tokens)
            time.sleep(args.sleep)
            row = {
                "question_id": example.question_id,
                "chatgpt_zh": chatgpt_zh,
                "vicuna13b_zh": vicuna_zh,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            print(f"[{idx}/{len(examples)}] qid={qid} translated", flush=True)


if __name__ == "__main__":
    main()
