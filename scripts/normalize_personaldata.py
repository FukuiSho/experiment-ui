from __future__ import annotations

"""Normalize personal data into chunk/entity/relation JSONL under DBmakedused.

This is a scaffold for a Python-first ingestion pipeline. Each source connector
should emit deterministic chunk IDs and (optionally) extracted entities/relations.
Graph extraction is intended to run during ingest by calling Ollama, but the
connector stubs are placeholders to be filled in next.
"""

import argparse
import json
import re
import ijson
import requests
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
    date_header = re.compile(r"^(\d{4})/(\d{2})/(\d{2})")
    for path in sorted(root.glob("*.txt")):
        doc_id = f"line:{path.stem}"
        current_date: str | None = None
        messages: list[str] = []
        chunk_idx = 0

        def flush() -> Iterator[ChunkRecord]:
            nonlocal messages, chunk_idx, current_date
            if current_date is None or not messages:
                return iter(())
            chunk_id = f"{doc_id}:{current_date}"
            content = "\n".join(messages)
            rec = ChunkRecord(
                chunk_id=chunk_id,
                source_type="line",
                source_path=path.as_posix(),
                doc_id=doc_id,
                chunk_index=chunk_idx,
                content=content,
                timestamp_start=f"{current_date}T00:00:00",
                timestamp_end=f"{current_date}T23:59:59",
                author=None,
                language="ja",
                metadata={"date": current_date},
            )
            chunk_idx += 1
            messages = []
            return iter((rec,))

        for raw_line in path.read_text("utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            m = date_header.match(line)
            if m:
                for rec in flush():
                    yield rec
                current_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            time_str, speaker, message = parts[0].strip(), parts[1].strip(), "\t".join(parts[2:]).strip()
            if not current_date:
                continue
            messages.append(f"{time_str} {speaker}: {message}")

        for rec in flush():
            yield rec


def iter_twitter_chunks(root: Path) -> Iterator[ChunkRecord]:
    for path in sorted(root.glob("**/*.js")):
        try:
            text = path.read_text("utf-8")
        except Exception:
            continue
        if "[" not in text:
            continue
        json_part = text[text.find("[") :].strip()
        if json_part.endswith(";"):
            json_part = json_part[:-1]
        try:
            arr = json.loads(json_part)
        except Exception:
            continue
        for obj in arr:
            tweet = obj.get("tweet") or {}
            tweet_id = tweet.get("id_str") or tweet.get("id")
            full_text = tweet.get("full_text") or tweet.get("text") or ""
            created_at = tweet.get("created_at")
            if not tweet_id or not full_text:
                continue
            doc_id = f"tweet:{tweet_id}"
            chunk_id = f"twitter:tweet:{tweet_id}"
            yield ChunkRecord(
                chunk_id=chunk_id,
                source_type="twitter",
                source_path=path.as_posix(),
                doc_id=doc_id,
                chunk_index=0,
                content=full_text,
                timestamp_start=None,
                timestamp_end=None,
                author=None,
                language=None,
                metadata={"created_at": created_at},
            )


def iter_pcmemo_chunks(root: Path, *, max_chars: int = 1200) -> Iterator[ChunkRecord]:
    for path in sorted(root.glob("*.txt")):
        doc_id = f"pcmemo:{path.stem}"
        paragraphs = [p.strip() for p in path.read_text("utf-8").split("\n\n") if p.strip()]
        chunk_idx = 0
        current: list[str] = []
        current_len = 0

        def flush() -> Iterator[ChunkRecord]:
            nonlocal current, current_len, chunk_idx
            if not current:
                return iter(())
            content = "\n\n".join(current)
            chunk_id = f"{doc_id}:{chunk_idx}"
            rec = ChunkRecord(
                chunk_id=chunk_id,
                source_type="pcmemo",
                source_path=path.as_posix(),
                doc_id=doc_id,
                chunk_index=chunk_idx,
                content=content,
                language="ja",
                metadata=None,
            )
            chunk_idx += 1
            current = []
            current_len = 0
            return iter((rec,))

        for para in paragraphs:
            if current and current_len + len(para) + 2 > max_chars:
                for rec in flush():
                    yield rec
            current.append(para)
            current_len += len(para) + 2

        for rec in flush():
            yield rec


def iter_smartphonememo_chunks(root: Path, *, max_chars: int = 1200) -> Iterator[ChunkRecord]:
    for path in sorted(root.glob("**/*.txt")):
        rel = path.relative_to(root)
        stem_safe = rel.with_suffix("").as_posix().replace("/", "_")
        doc_id = f"smartphonememo:{stem_safe}"
        paragraphs = [p.strip() for p in path.read_text("utf-8").split("\n\n") if p.strip()]
        chunk_idx = 0
        current: list[str] = []
        current_len = 0

        def flush() -> Iterator[ChunkRecord]:
            nonlocal current, current_len, chunk_idx
            if not current:
                return iter(())
            content = "\n\n".join(current)
            chunk_id = f"{doc_id}:{chunk_idx}"
            rec = ChunkRecord(
                chunk_id=chunk_id,
                source_type="smartphonememo",
                source_path=path.as_posix(),
                doc_id=doc_id,
                chunk_index=chunk_idx,
                content=content,
                language="ja",
                metadata=None,
            )
            chunk_idx += 1
            current = []
            current_len = 0
            return iter((rec,))

        for para in paragraphs:
            if current and current_len + len(para) + 2 > max_chars:
                for rec in flush():
                    yield rec
            current.append(para)
            current_len += len(para) + 2

        for rec in flush():
            yield rec


def iter_photo_chunks(root: Path) -> Iterator[ChunkRecord]:
    for path in sorted(root.glob("*.json")):
        if path.name.startswith("_failures"):
            continue
        try:
            data = json.loads(path.read_text("utf-8"))
        except Exception:
            continue

        image_sha = str(data.get("image_sha256") or "").strip()
        text = str(data.get("text") or "").strip()
        if not image_sha or not text:
            continue

        doc_id = f"photo:{image_sha}"
        chunk_id = f"{doc_id}:0"
        metadata = {
            "schema_version": data.get("schema_version"),
            "confidence": data.get("confidence"),
            "model": data.get("model"),
            "created_at": data.get("created_at"),
            "jpg_cache_path": data.get("jpg_cache_path"),
        }
        yield ChunkRecord(
            chunk_id=chunk_id,
            source_type="photo_to_text",
            source_path=path.as_posix(),
            doc_id=doc_id,
            chunk_index=0,
            content=text,
            timestamp_start=data.get("created_at"),
            timestamp_end=data.get("created_at"),
            author=None,
            language=None,
            metadata=metadata,
        )


def iter_gpt_chunks(root: Path, *, max_messages: int = 20) -> Iterator[ChunkRecord]:
    conv_path = root / "conversations.json"
    if not conv_path.exists():
        return iter(())

    with conv_path.open("rb") as f:
        parser = ijson.items(f, "item")
        for conv in parser:
            conv_id = conv.get("id") or conv.get("conversation_id") or ""
            if not conv_id:
                continue
            doc_id = f"gpt:{conv_id}"
            # Flatten mapping to ordered messages by create_time
            mapping = conv.get("mapping") or {}
            messages = []
            for node in mapping.values():
                msg = node.get("message") or {}
                author = (msg.get("author") or {}).get("role") or "unknown"
                content = msg.get("content") or {}
                parts = content.get("parts") or []
                text = "\n".join(str(p) for p in parts if p is not None)
                ts = msg.get("create_time")
                if text:
                    messages.append((ts, author, text))
            messages.sort(key=lambda x: x[0] if x[0] is not None else 0)

            # chunk by fixed message window
            chunk_idx = 0
            window: list[tuple] = []
            for msg in messages:
                window.append(msg)
                if len(window) >= max_messages:
                    content = "\n".join(f"{a}: {t}" for _, a, t in window)
                    yield ChunkRecord(
                        chunk_id=f"{doc_id}:{chunk_idx}",
                        source_type="gpt",
                        source_path=conv_path.as_posix(),
                        doc_id=doc_id,
                        chunk_index=chunk_idx,
                        content=content,
                        language="ja",
                        metadata={"title": conv.get("title")},
                    )
                    chunk_idx += 1
                    window = []
            if window:
                content = "\n".join(f"{a}: {t}" for _, a, t in window)
                yield ChunkRecord(
                    chunk_id=f"{doc_id}:{chunk_idx}",
                    source_type="gpt",
                    source_path=conv_path.as_posix(),
                    doc_id=doc_id,
                    chunk_index=chunk_idx,
                    content=content,
                    language="ja",
                    metadata={"title": conv.get("title")},
                )


def call_ollama_extract(content: str, *, host: str, model: str, timeout: int) -> dict:
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": (
                    "以下のテキストからエンティティと関係を抽出し、JSONのみを返してください。"
                    "形式: {\"entities\":[{\"name\":...,\"type\":...,\"confidence\":0.0}],"
                    "\"relations\":[{\"from\":...,\"to\":...,\"relation_type\":...,\"confidence\":0.0,\"evidence\":...}]}"
                ),
            },
            {"role": "user", "content": content},
        ],
        "format": {
            "type": "object",
            "properties": {
                "entities": {"type": "array"},
                "relations": {"type": "array"},
            },
            "required": ["entities", "relations"],
        },
    }
    resp = requests.post(f"{host.rstrip('/')}/api/chat", json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    message = data.get("message", {})
    content_str = message.get("content", "{}")
    try:
        parsed = json.loads(content_str)
    except Exception:
        parsed = {"entities": [], "relations": []}
    return parsed


def _emit_graph(*, chunks_dir: Path, entities_path: Path, relations_path: Path, ollama_host: str, model: str, timeout: int) -> None:
    entities_path.parent.mkdir(parents=True, exist_ok=True)
    relations_path.parent.mkdir(parents=True, exist_ok=True)
    with entities_path.open("w", encoding="utf-8") as f_ent, relations_path.open("w", encoding="utf-8") as f_rel:
        for chunk_file in sorted(chunks_dir.glob("*.jsonl")):
            for rec in iter_jsonl(chunk_file):
                chunk_id = rec.get("chunk_id")
                content = rec.get("content") or ""
                if not chunk_id or not str(content).strip():
                    continue
                extracted = call_ollama_extract(str(content), host=ollama_host, model=model, timeout=timeout)
                for idx, ent in enumerate(extracted.get("entities", []) or []):
                    ent_id = ent.get("entity_id") or f"{chunk_id}:ent{idx}"
                    out = {
                        "entity_id": ent_id,
                        "name": ent.get("name"),
                        "type": ent.get("type"),
                        "confidence": ent.get("confidence"),
                        "chunk_id": chunk_id,
                        "aliases": ent.get("aliases") if isinstance(ent.get("aliases"), list) else None,
                        "metadata": None,
                    }
                    f_ent.write(json.dumps(out, ensure_ascii=False) + "\n")
                for idx, rel in enumerate(extracted.get("relations", []) or []):
                    rel_id = rel.get("relation_id") or f"{chunk_id}:rel{idx}"
                    out = {
                        "relation_id": rel_id,
                        "relation_type": rel.get("relation_type") or rel.get("type"),
                        "from_entity_id": rel.get("from") or rel.get("from_entity_id"),
                        "to_entity_id": rel.get("to") or rel.get("to_entity_id"),
                        "confidence": rel.get("confidence"),
                        "chunk_id": chunk_id,
                        "evidence": rel.get("evidence"),
                        "metadata": None,
                    }
                    f_rel.write(json.dumps(out, ensure_ascii=False) + "\n")


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


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
    parser.add_argument("--extract-graph", action="store_true", help="Extract entities/relations via Ollama and write to entities/relations shards")
    parser.add_argument("--ollama-host", default="http://127.0.0.1:11434")
    parser.add_argument("--graph-model", default="gemma3:1b")
    parser.add_argument("--graph-timeout", type=int, default=60)
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

    if args.extract_graph:
        print("graph extraction: start")
        entities_file = paths.entities_dir / "entities.jsonl"
        relations_file = paths.relations_dir / "relations.jsonl"
        _emit_graph(
            chunks_dir=paths.chunks_dir,
            entities_path=entities_file,
            relations_path=relations_file,
            ollama_host=args.ollama_host,
            model=args.graph_model,
            timeout=args.graph_timeout,
        )
        print("graph extraction: done")


if __name__ == "__main__":
    main()
