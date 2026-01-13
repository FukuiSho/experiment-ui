from __future__ import annotations

"""Inspect DBmakedused JSONL shards for quick health checks."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_DB_ROOT = Path("src/lib/pesonaldata/DBmakedused")


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def inspect_chunks(chunks_dir: Path) -> dict:
    summary: dict[str, object] = {
        "total": 0,
        "by_source": Counter(),
        "empty_content": 0,
        "empty_metadata": 0,
    }
    for path in sorted(chunks_dir.glob("*.jsonl")):
        for rec in iter_jsonl(path):
            summary["total"] = summary.get("total", 0) + 1  # type: ignore[arg-type]
            src = rec.get("source_type", "unknown")
            summary["by_source"][src] += 1  # type: ignore[index]
            content = rec.get("content") or ""
            meta = rec.get("metadata")
            if not str(content).strip():
                summary["empty_content"] = summary.get("empty_content", 0) + 1  # type: ignore[arg-type]
            if meta in (None, "", {}):
                summary["empty_metadata"] = summary.get("empty_metadata", 0) + 1  # type: ignore[arg-type]
    return summary


def inspect_entities(entities_dir: Path) -> dict:
    summary: dict[str, object] = {
        "total": 0,
        "by_type": Counter(),
    }
    for path in sorted(entities_dir.glob("*.jsonl")):
        for rec in iter_jsonl(path):
            summary["total"] = summary.get("total", 0) + 1  # type: ignore[arg-type]
            etype = rec.get("type", "unknown")
            summary["by_type"][etype] += 1  # type: ignore[index]
    return summary


def inspect_relations(relations_dir: Path) -> dict:
    summary: dict[str, object] = {
        "total": 0,
        "by_predicate": Counter(),
    }
    for path in sorted(relations_dir.glob("*.jsonl")):
        for rec in iter_jsonl(path):
            summary["total"] = summary.get("total", 0) + 1  # type: ignore[arg-type]
            pred = rec.get("relation_type", "unknown")
            summary["by_predicate"][pred] += 1  # type: ignore[index]
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-root", type=Path, default=DEFAULT_DB_ROOT)
    args = parser.parse_args()

    root = args.db_root
    chunks_dir = root / "chunks"
    entities_dir = root / "entities"
    relations_dir = root / "relations"

    print(f"Inspecting DBmakedused at {root}")
    if not chunks_dir.exists():
        print("No chunks directory found")
        return

    chunk_summary = inspect_chunks(chunks_dir)
    print("\n[Chunks]")
    print(json.dumps(chunk_summary, ensure_ascii=False, indent=2, default=lambda o: dict(o)))

    if entities_dir.exists():
        entity_summary = inspect_entities(entities_dir)
        print("\n[Entities]")
        print(json.dumps(entity_summary, ensure_ascii=False, indent=2, default=lambda o: dict(o)))
    else:
        print("\n[Entities] none")

    if relations_dir.exists():
        relation_summary = inspect_relations(relations_dir)
        print("\n[Relations]")
        print(json.dumps(relation_summary, ensure_ascii=False, indent=2, default=lambda o: dict(o)))
    else:
        print("\n[Relations] none")


if __name__ == "__main__":
    main()
