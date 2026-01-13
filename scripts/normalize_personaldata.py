from __future__ import annotations

"""Normalize personal data into chunk/entity/relation JSONL under DBmakedused.

This is a scaffold for a Python-first ingestion pipeline. Each source connector
should emit deterministic chunk IDs and (optionally) extracted entities/relations.
Graph extraction is intended to run during ingest by calling Ollama, but the
connector stubs are placeholders to be filled in next.
"""

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Literal, Sequence

DB_SCHEMA_VERSION = "dbmakedused.v1"
DEFAULT_SOURCES: Sequence[str] = (
    "line",
    "twitter",
    "pcmemo",
    "smartphonememo",
    "photo_to_text",
    "gpt",
)

ChunkSource = Literal[
    "line",
    "twitter",
    "pcmemo",
    "smartphonememo",
    "photo_to_text",
    "gpt",
]


@dataclass
class ChunkRecord:
    chunk_id: str
    source_type: ChunkSource
    source_path: str
    doc_id: str
    chunk_index: int
    content: str
    timestamp_start: str | None = None
    timestamp_end: str | None = None
    author: str | None = None
    language: str | None = None
    metadata: dict | None = None


@dataclass
class EntityRecord:
    entity_id: str
    name: str
    type: str
    confidence: float | None
    chunk_id: str
    aliases: list[str] | None = None
    metadata: dict | None = None


@dataclass
class RelationRecord:
    relation_id: str
    relation_type: str
    from_entity_id: str
    to_entity_id: str
    confidence: float | None
    chunk_id: str | None = None
    evidence: str | None = None
    metadata: dict | None = None


@dataclass
class Paths:
    unlabel_root: Path
    derived_photo_root: Path
    output_root: Path

    @property
    def manifest(self) -> Path:
        return self.output_root / "manifest.json"

    @property
    def state(self) -> Path:
        return self.output_root / "state.json"

    @property
    def chunks_dir(self) -> Path:
        return self.output_root / "chunks"

    @property
    def entities_dir(self) -> Path:
        return self.output_root / "entities"

    @property
    def relations_dir(self) -> Path:
        return self.output_root / "relations"


# ---- file helpers ---------------------------------------------------------

def _write_jsonl(dir_path: Path, filename: str, records: Iterable[dict]) -> int:
    dir_path.mkdir(parents=True, exist_ok=True)
    out_path = dir_path / filename
    count = 0
    with out_path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False))
            f.write("\n")
            count += 1
    return count


def _ensure_output_layout(paths: Paths) -> None:
    paths.output_root.mkdir(parents=True, exist_ok=True)
    paths.chunks_dir.mkdir(parents=True, exist_ok=True)
    paths.entities_dir.mkdir(parents=True, exist_ok=True)
    paths.relations_dir.mkdir(parents=True, exist_ok=True)


# ---- connector stubs (to be implemented) ---------------------------------

def iter_line_chunks(root: Path) -> Iterator[ChunkRecord]:
    # TODO: implement LINE text parsing and deterministic chunking
    return iter(())


def iter_twitter_chunks(root: Path) -> Iterator[ChunkRecord]:
    # TODO: implement twitter archive .js parsing
    return iter(())


def iter_pcmemo_chunks(root: Path) -> Iterator[ChunkRecord]:
    # TODO: implement paragraph-based splitting for pcmemo notes
    return iter(())


def iter_smartphonememo_chunks(root: Path) -> Iterator[ChunkRecord]:
    # TODO: implement paragraph-based splitting for smartphonememo
    return iter(())


def iter_photo_chunks(root: Path) -> Iterator[ChunkRecord]:
    # TODO: implement derived photo_to_text JSON ingestion
    return iter(())


def iter_gpt_chunks(root: Path) -> Iterator[ChunkRecord]:
    # TODO: implement streaming parse of conversations.json (GPT export)
    return iter(())


def _select_sources(requested: Sequence[str]) -> set[ChunkSource]:
    allowed = set(DEFAULT_SOURCES)
    selected: set[ChunkSource] = set()
    for name in requested:
        if name not in allowed:
            raise SystemExit(f"Unknown source '{name}'. Allowed: {sorted(allowed)}")
        selected.add(name)  # type: ignore[arg-type]
    return selected


def _emit_chunks(paths: Paths, sources: set[ChunkSource]) -> int:
    total = 0
    if "line" in sources:
        chunks = iter_line_chunks(paths.unlabel_root / "LINE")
        total += _write_jsonl(paths.chunks_dir, "line.jsonl", (c.__dict__ for c in chunks))
    if "twitter" in sources:
        chunks = iter_twitter_chunks(paths.unlabel_root / "twitter")
        total += _write_jsonl(paths.chunks_dir, "twitter.jsonl", (c.__dict__ for c in chunks))
    if "pcmemo" in sources:
        chunks = iter_pcmemo_chunks(paths.unlabel_root / "pcmemo")
        total += _write_jsonl(paths.chunks_dir, "pcmemo.jsonl", (c.__dict__ for c in chunks))
    if "smartphonememo" in sources:
        chunks = iter_smartphonememo_chunks(paths.unlabel_root / "smartphonememo")
        total += _write_jsonl(paths.chunks_dir, "smartphonememo.jsonl", (c.__dict__ for c in chunks))
    if "photo_to_text" in sources:
        chunks = iter_photo_chunks(paths.derived_photo_root)
        total += _write_jsonl(paths.chunks_dir, "photo_to_text.jsonl", (c.__dict__ for c in chunks))
    if "gpt" in sources:
        chunks = iter_gpt_chunks(paths.unlabel_root / "GPT")
        total += _write_jsonl(paths.chunks_dir, "gpt.jsonl", (c.__dict__ for c in chunks))
    return total


def _write_manifest(paths: Paths, sources: set[ChunkSource]) -> None:
    manifest = {
        "schema_version": DB_SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sources": sorted(sources),
    }
    paths.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unlabel-root", type=Path, default=Path("src/lib/pesonaldata/unlabeldata"))
    parser.add_argument("--derived-photo-root", type=Path, default=Path("src/lib/pesonaldata/derived/photo_to_text"))
    parser.add_argument("--output", type=Path, default=Path("src/lib/pesonaldata/DBmakedused"))
    parser.add_argument("--sources", default=",".join(DEFAULT_SOURCES), help=f"Comma-separated sources. Default: {','.join(DEFAULT_SOURCES)}")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = _select_sources([s.strip() for s in args.sources.split(",") if s.strip()])
    paths = Paths(
        unlabel_root=args.unlabel_root.resolve(),
        derived_photo_root=args.derived_photo_root.resolve(),
        output_root=args.output.resolve(),
    )
    _ensure_output_layout(paths)
    _write_manifest(paths, sources)
    total = _emit_chunks(paths, sources)
    print(f"normalize_personaldata: wrote chunks for sources={sorted(sources)}; total_chunks={total}")


if __name__ == "__main__":
    main()
