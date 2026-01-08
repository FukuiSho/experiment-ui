from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


SPEAKER_LINE_RE = re.compile(r"^\*\*(?P<speaker>[^*]+)\*\*:\s*(?P<content>.+)\s*$")


@dataclass
class Utterance:
    speaker: str
    content: str


def iter_utterances_from_md(md_text: str) -> Iterable[Utterance]:
    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = SPEAKER_LINE_RE.match(line)
        if not m:
            continue
        speaker = m.group("speaker").strip()
        content = m.group("content").strip()
        if speaker and content:
            yield Utterance(speaker=speaker, content=content)


def normalize_speaker(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip())


def build_examples(
    utterances: List[Utterance],
    hijiri_names: List[str],
    context_turns: int,
) -> List[dict]:
    hijiri_set = {normalize_speaker(x) for x in hijiri_names if x.strip()}

    examples: List[dict] = []
    for i in range(1, len(utterances)):
        prev_u = utterances[i - 1]
        cur_u = utterances[i]

        prev_speaker = normalize_speaker(prev_u.speaker)
        cur_speaker = normalize_speaker(cur_u.speaker)

        # We want: (other speaker) -> (Hijiri response)
        if cur_speaker not in hijiri_set:
            continue
        if prev_speaker in hijiri_set:
            continue

        # Build context window up to prev turn
        start = max(0, (i - 1) - context_turns * 2)
        window = utterances[start : i]

        context_lines = [f"{normalize_speaker(u.speaker)}: {u.content}" for u in window]

        examples.append(
            {
                "id": f"ex_{len(examples)+1:05d}",
                "prompt": prev_u.content,
                "reference": cur_u.content,
                "context": "\n".join(context_lines),
                "meta": {
                    "prompt_speaker": prev_speaker,
                    "reference_speaker": cur_speaker,
                },
            }
        )

    return examples


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Hijiri benchmark from Limitless markdown")
    parser.add_argument("--input", required=True, help="Path to limitless-knowledge.md")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    parser.add_argument(
        "--hijiri-names",
        default="聖,Hijiri,福井聖",
        help="Comma-separated speaker names that correspond to Hijiri",
    )
    parser.add_argument("--context-turns", type=int, default=3, help="Number of turns for context window")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of examples (0=all)")

    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    md_text = in_path.read_text(encoding="utf-8")
    utterances = list(iter_utterances_from_md(md_text))

    hijiri_names = [x.strip() for x in str(args.hijiri_names).split(",")]

    examples = build_examples(utterances, hijiri_names=hijiri_names, context_turns=args.context_turns)
    if args.limit and args.limit > 0:
        examples = examples[: args.limit]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Utterances parsed: {len(utterances)}")
    print(f"Benchmark examples: {len(examples)}")
    print(f"Wrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
