#!/usr/bin/env python3
"""Simple RAG smoke evaluation against the running FastAPI service."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import requests


def load_dataset(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):  # pragma: no cover - safety
        raise ValueError("Dataset must be a list")
    return data


def score_answer(answer: str, keywords: Sequence[str]) -> float:
    if not keywords:
        return 0.0
    hits = sum(1 for kw in keywords if kw.lower() in answer.lower())
    return hits / len(keywords)


def run_eval(api_base: str, dataset_path: Path) -> None:
    questions = load_dataset(dataset_path)
    stats: list[tuple[str, float]] = []
    for item in questions:
        query = item["query"]
        response = requests.post(
            f"{api_base.rstrip('/')}/chat",
            json={"query": query},
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        score = score_answer(payload.get("answer", ""), item.get("keywords", []))
        stats.append((query, score))
        print(f"Q: {query}\n-> score: {score:.2f}, model: {payload.get('stats', {}).get('model')}\n")

    mean_score = sum(score for _, score in stats) / len(stats)
    print(f"Mean keyword hit-rate: {mean_score:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Warehouse RAG answers")
    parser.add_argument(
        "--api-base",
        default="http://localhost:8000",
        help="FastAPI base URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/eval_questions.json"),
        help="Path to evaluation dataset",
    )
    args = parser.parse_args()
    run_eval(args.api_base, args.dataset)
