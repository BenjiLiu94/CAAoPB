#!/usr/bin/env python3
"""Build same-language ABAB chunk interleaving prompts for FairEval."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from reproduce_faireval import ROOT, load_examples
from chunk_language import chunk_text


@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    text: str


def interleave(x_chunks: list[str], y_chunks: list[str], start: str) -> list[Chunk]:
    chunks = []
    max_len = max(len(x_chunks), len(y_chunks))
    for idx in range(max_len):
        pair = []
        if idx < len(x_chunks):
            pair.append(Chunk("X", idx + 1, x_chunks[idx]))
        if idx < len(y_chunks):
            pair.append(Chunk("Y", idx + 1, y_chunks[idx]))
        if start == "Y":
            pair = list(reversed(pair))
        chunks.extend(pair)
    return chunks


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    chunk_block = "\n\n".join(
        f"[Chunk {order} | Candidate {chunk.source} | source_order={chunk.index}]\n{chunk.text}"
        for order, chunk in enumerate(chunks, start=1)
    )
    return f"""You are an impartial evaluator.

The same user question has two candidate answers, Candidate X and Candidate Y.
Each answer has been split into ordered chunks. Chunks from the two candidates are interleaved.

Important rules:
1. Evaluate Candidate X using all chunks labeled Candidate X.
2. Evaluate Candidate Y using all chunks labeled Candidate Y.
3. Preserve each candidate's source_order when mentally reading its chunks.
4. The interleaving order must not affect your judgment.
5. Choose Tie if both candidates are similar in quality.

User question:
{question}

Interleaved chunks:
{chunk_block}

Output exactly:
Evaluation evidence: <brief explanation>
Score of Candidate X: <score from 1 to 10>
Score of Candidate Y: <score from 1 to 10>
Winner: <X or Y or Tie>"""


def candidate_text(example, candidate: str) -> str:
    if candidate == "chatgpt":
        return example.answer_1
    if candidate == "vicuna13b":
        return example.answer_2
    raise ValueError(f"unknown candidate: {candidate}")


def build_conditions(example, max_tokens: int, tokenizer_name: str) -> list[dict]:
    specs = [
        {"condition": "c1_chatgpt_x_x_start", "X": "chatgpt", "Y": "vicuna13b", "start": "X"},
        {"condition": "c2_chatgpt_x_y_start", "X": "chatgpt", "Y": "vicuna13b", "start": "Y"},
        {"condition": "c3_vicuna_x_x_start", "X": "vicuna13b", "Y": "chatgpt", "start": "X"},
        {"condition": "c4_vicuna_x_y_start", "X": "vicuna13b", "Y": "chatgpt", "start": "Y"},
    ]
    out = []
    for spec in specs:
        x_chunks = chunk_text(candidate_text(example, spec["X"]), max_tokens, tokenizer_name)
        y_chunks = chunk_text(candidate_text(example, spec["Y"]), max_tokens, tokenizer_name)
        chunks = interleave(x_chunks, y_chunks, spec["start"])
        out.append(
            {
                "condition": spec["condition"],
                "question_id": example.question_id,
                "human": example.human,
                "x_candidate": spec["X"],
                "y_candidate": spec["Y"],
                "x_language": "en",
                "y_language": "en",
                "start": spec["start"],
                "x_chunks": len(x_chunks),
                "y_chunks": len(y_chunks),
                "prompt": build_prompt(example.question, chunks),
            }
        )
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--max-chunk-tokens", type=int, default=120)
    parser.add_argument("--tokenizer", default="cl100k_base")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "chunk_interleave_prompts_limit5.jsonl")
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
            for condition in build_conditions(example, args.max_chunk_tokens, args.tokenizer):
                handle.write(json.dumps(condition, ensure_ascii=False) + "\n")
                count += 1
    print(f"Wrote {count} same-language chunk prompts to {args.output}")


if __name__ == "__main__":
    main()
