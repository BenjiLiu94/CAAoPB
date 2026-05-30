#!/usr/bin/env python3
"""Run the FairEval reproduction for all judges in a config file."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_config(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    judges = data.get("judges", [])
    if not judges:
        raise SystemExit(f"No judges found in {path}")
    return judges


def resolve_api_key_env(judge: dict) -> tuple[str, dict[str, str]]:
    configured = judge["api_key_env"]
    if os.environ.get(configured):
        return configured, {}
    if re.match(r"^[A-Za-z0-9_-]{20,}$", configured):
        env_name = f"JUDGE_API_KEY_{judge['name'].upper().replace('-', '_')}"
        return env_name, {env_name: configured}
    return configured, {}


def run_judge(judge: dict, args: argparse.Namespace) -> None:
    name = judge["name"]
    output = args.output_dir / f"faireval_{name}_bpc.csv"
    api_key_env, extra_env = resolve_api_key_env(judge)
    model = judge["model"]
    # Compatibility mapping for DeepSeek models
    if model == "deepseek-v4-flash":
        model = "deepseek-chat"
    extra_body = judge.get("extra_body")
    if extra_body is None and "Qwen3.6" in model:
        extra_body = {"enable_thinking": False}
    command = [
        "uv",
        "run",
        "scripts/reproduce_faireval.py",
        "--api-key-env",
        api_key_env,
        "--base-url",
        judge["base_url"],
        "--model",
        model,
        "--output",
        str(output),
        "--temperature",
        str(args.temperature),
        "--sleep",
        str(args.sleep),
        "--request-timeout",
        str(args.request_timeout),
        "--max-tokens",
        str(args.max_tokens),
    ]
    if extra_body:
        command.extend(["--extra-body-json", json.dumps(extra_body)])
    if args.limit:
        command.extend(["--limit", str(args.limit)])
    if args.dry_run:
        command.append("--dry-run")

    print(f"\n=== {name} ({judge['model']}) ===")
    if not args.dry_run:
        key = os.environ.get(api_key_env)
        if not key and not extra_env:
            raise SystemExit(f"{api_key_env} is not set for judge {name}")
    env = os.environ.copy()
    env.update(extra_env)
    env["PYTHONUNBUFFERED"] = "1"
    subprocess.run(command, cwd=ROOT, check=True, env=env)

    if args.dry_run:
        return

    # Auto-generate report after successful run
    report_cmd = [
        "uv",
        "run",
        "scripts/generate_report.py",
        str(output),
    ]
    if args.output_dir != ROOT / "results":
        report_cmd.extend(["--output-dir", str(args.output_dir)])
    print("\n--- Generating report ---")
    subprocess.run(report_cmd, cwd=ROOT, check=True, env=env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "judges.local.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--request-timeout", type=float, default=60.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--judge", type=str, default="", help="Only run the judge with this name")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for judge in load_config(args.config):
        if args.judge and judge["name"] != args.judge:
            continue
        if judge.get("model", "").startswith("TODO"):
            print(f"Skipping {judge['name']}: model is TODO")
            continue
        run_judge(judge, args)


if __name__ == "__main__":
    main()
