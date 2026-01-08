from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


@dataclass
class Result:
    model: str
    count: int
    avg_similarity: float
    avg_length: float
    hijiri_pronoun_rate: float


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate multiple Ollama models on Hijiri benchmark JSONL")
    parser.add_argument("--benchmark", required=True, help="Path to benchmark jsonl")
    parser.add_argument("--models", required=True, help="Comma-separated Ollama model names")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--max", type=int, default=50, help="Max examples to evaluate")

    args = parser.parse_args()

    # Lazy import so this script can be run even when ollama isn't installed.
    try:
        import ollama  # type: ignore
    except Exception:
        print("ERROR: python package 'ollama' is not available. Activate venv and pip install ollama")
        return 1

    bench_path = Path(args.benchmark)
    examples: List[Dict] = []
    with bench_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            examples.append(json.loads(line))
            if len(examples) >= args.max:
                break

    models = [m.strip() for m in str(args.models).split(",") if m.strip()]
    if not models:
        print("No models provided")
        return 1

    results: List[Result] = []

    for model in models:
        sims: List[float] = []
        lengths: List[int] = []
        pronoun_hits = 0

        for ex in examples:
            prompt = ex.get("prompt", "")
            ctx = ex.get("context", "")
            ref = ex.get("reference", "")

            user_content = prompt
            system_content = (
                "あなたは福井聖です。日本語で短めに会話口調で答えてください。"
                "一人称は『俺』を基本とします。"
            )
            if ctx:
                system_content += "\n\n以下は直近の会話文脈です。参考にしてください。\n" + ctx

            resp = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content},
                ],
            )
            out = resp.message.content if resp.message else ""

            sims.append(similarity(out, ref))
            lengths.append(len(out))
            if "俺" in out:
                pronoun_hits += 1

        count = len(examples)
        results.append(
            Result(
                model=model,
                count=count,
                avg_similarity=sum(sims) / max(1, len(sims)),
                avg_length=sum(lengths) / max(1, len(lengths)),
                hijiri_pronoun_rate=pronoun_hits / max(1, count),
            )
        )

        print(
            f"{model}: avg_similarity={results[-1].avg_similarity:.3f} "
            f"avg_length={results[-1].avg_length:.1f} pronoun_rate={results[-1].hijiri_pronoun_rate:.2f}"
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump([r.__dict__ for r in results], f, ensure_ascii=False, indent=2)

    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
