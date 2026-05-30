#!/usr/bin/env python3
"""Build chunk-language prompts for FairEval.

This script implements the presentation construction only. It uses an
open-source tokenizer (`tiktoken`) to split answers into token-bounded chunks.

The intended experiment uses English original answers plus translated answers
from a cache file. It then constructs factorial conditions that swap:

- candidate language assignment
- candidate label
- first chunk source
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from reproduce_faireval import ROOT, load_examples


@dataclass(frozen=True)
class Chunk:
    source: str
    language: str
    index: int
    text: str


def get_tokenizer(name: str):
    try:
        import tiktoken
    except ImportError as exc:
        raise SystemExit("Missing dependency: run `uv sync` after adding tiktoken.") from exc
    return tiktoken.get_encoding(name)


def chunk_text(text: str, max_tokens: int, tokenizer_name: str) -> list[str]:
    enc = get_tokenizer(tokenizer_name)
    ids = enc.encode(text)
    chunks = []
    for start in range(0, len(ids), max_tokens):
        piece = enc.decode(ids[start : start + max_tokens]).strip()
        if piece:
            chunks.append(piece)
    return chunks or [text.strip()]


def load_translation_cache(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            data[str(row["question_id"])] = row
    return data


def get_answer_text(example, candidate: str, language: str, translations: dict[str, dict]) -> str:
    if language == "en":
        return example.answer_1 if candidate == "chatgpt" else example.answer_2
    if language == "zh":
        row = translations.get(str(example.question_id))
        if not row:
            raise KeyError(f"missing translation for question_id={example.question_id}")
        key = "chatgpt_zh" if candidate == "chatgpt" else "vicuna13b_zh"
        if not row.get(key):
            raise KeyError(f"missing {key} for question_id={example.question_id}")
        return row[key]
    raise ValueError(f"unsupported language: {language}")


def interleave_chunks(x_chunks: list[str], y_chunks: list[str], x_language: str, y_language: str, start: str) -> list[Chunk]:
    chunks = []
    max_len = max(len(x_chunks), len(y_chunks))
    for idx in range(max_len):
        pair = []
        if idx < len(x_chunks):
            pair.append(Chunk("X", x_language, idx + 1, x_chunks[idx]))
        if idx < len(y_chunks):
            pair.append(Chunk("Y", y_language, idx + 1, y_chunks[idx]))
        if start == "Y":
            pair = list(reversed(pair))
        chunks.extend(pair)
    return chunks


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    chunk_lines = []
    for order, chunk in enumerate(chunks, start=1):
        chunk_lines.append(
            f"[Chunk {order} | Candidate {chunk.source} | language={chunk.language} | source_order={chunk.index}]\n{chunk.text}"
        )
    chunk_block = "\n\n".join(chunk_lines)
    return f"""You are an impartial evaluator.

The same user question has two candidate answers, Candidate X and Candidate Y.
Each answer has been split into ordered chunks. Chunks from the two candidates are interleaved.

Important rules:
1. Evaluate Candidate X using all chunks labeled Candidate X.
2. Evaluate Candidate Y using all chunks labeled Candidate Y.
3. The interleaving order must not affect your judgment.
4. Some chunks may be in different languages; judge semantic quality, not language preference.
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


def build_conditions(example, translations: dict[str, dict], max_tokens: int, tokenizer_name: str) -> list[dict]:
    # Candidate X/Y are anonymous display labels. Conditions map them to real candidates.
    specs = [
        {"condition": "c1_chatgpt_en_vicuna_zh_x_start", "X": ("chatgpt", "en"), "Y": ("vicuna13b", "zh"), "start": "X"},
        {"condition": "c2_chatgpt_en_vicuna_zh_y_start", "X": ("chatgpt", "en"), "Y": ("vicuna13b", "zh"), "start": "Y"},
        {"condition": "c3_chatgpt_zh_vicuna_en_x_start", "X": ("chatgpt", "zh"), "Y": ("vicuna13b", "en"), "start": "X"},
        {"condition": "c4_chatgpt_zh_vicuna_en_y_start", "X": ("chatgpt", "zh"), "Y": ("vicuna13b", "en"), "start": "Y"},
        {"condition": "c5_vicuna_en_chatgpt_zh_x_start", "X": ("vicuna13b", "en"), "Y": ("chatgpt", "zh"), "start": "X"},
        {"condition": "c6_vicuna_en_chatgpt_zh_y_start", "X": ("vicuna13b", "en"), "Y": ("chatgpt", "zh"), "start": "Y"},
        {"condition": "c7_vicuna_zh_chatgpt_en_x_start", "X": ("vicuna13b", "zh"), "Y": ("chatgpt", "en"), "start": "X"},
        {"condition": "c8_vicuna_zh_chatgpt_en_y_start", "X": ("vicuna13b", "zh"), "Y": ("chatgpt", "en"), "start": "Y"},
    ]

    conditions = []
    for spec in specs:
        x_candidate, x_language = spec["X"]
        y_candidate, y_language = spec["Y"]
        x_text = get_answer_text(example, x_candidate, x_language, translations)
        y_text = get_answer_text(example, y_candidate, y_language, translations)
        x_chunks = chunk_text(x_text, max_tokens, tokenizer_name)
        y_chunks = chunk_text(y_text, max_tokens, tokenizer_name)
        chunks = interleave_chunks(x_chunks, y_chunks, x_language, y_language, spec["start"])
        conditions.append(
            {
                "condition": spec["condition"],
                "question_id": example.question_id,
                "human": example.human,
                "x_candidate": x_candidate,
                "y_candidate": y_candidate,
                "x_language": x_language,
                "y_language": y_language,
                "start": spec["start"],
                "x_chunks": len(x_chunks),
                "y_chunks": len(y_chunks),
                "prompt": build_prompt(example.question, chunks),
            }
        )
    return conditions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--translations", type=Path, default=ROOT / "data" / "translations_zh.jsonl")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--max-chunk-tokens", type=int, default=80)
    parser.add_argument("--tokenizer", default="cl100k_base")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "chunk_language_prompts.jsonl")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    translations = load_translation_cache(args.translations)
    examples = load_examples()
    if args.limit:
        examples = examples[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.output.open("w", encoding="utf-8") as handle:
        for example in examples:
            for condition in build_conditions(example, translations, args.max_chunk_tokens, args.tokenizer):
                handle.write(json.dumps(condition, ensure_ascii=False) + "\n")
                count += 1
    print(f"Wrote {count} chunk-language prompts to {args.output}")


if __name__ == "__main__":
    main()
