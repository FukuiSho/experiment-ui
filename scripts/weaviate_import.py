from __future__ import annotations

"""Import normalized chunks/entities/relations into Weaviate.

This is a scaffold: it assumes normalized JSONL files produced by
`scripts/normalize_personaldata.py` under `src/lib/pesonaldata/DBmakedused`.
Chunk vectors must be supplied by the caller (e.g., via Ollama embeddings)
before upsert; the placeholder here raises NotImplementedError.
"""

import argparse
import json
from pathlib import Path
from typing import Iterable, Iterator

import weaviate
from weaviate.classes.config import Configure, Property, ReferenceProperty

DEFAULT_DB_ROOT = Path("src/lib/pesonaldata/DBmakedused")
DEFAULT_WEAVIATE_URL = "http://127.0.0.1:8080"
DEFAULT_CHUNK_CLASS = "Chunk"
DEFAULT_ENTITY_CLASS = "Entity"
DEFAULT_RELATION_CLASS = "Relation"


def iter_jsonl(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def ensure_schema(client: weaviate.WeaviateClient, *, chunk_class: str, entity_class: str, relation_class: str) -> None:
    existing = {c.name for c in client.collections.list_all()}
    if chunk_class not in existing:
        client.collections.create(
            name=chunk_class,
            description="Text chunks for RAG (external embeddings)",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="source_type", data_type=weaviate.classes.data_type.DataType.TEXT),
                Property(name="source_path", data_type=weaviate.classes.data_type.DataType.TEXT),
                Property(name="doc_id", data_type=weaviate.classes.data_type.DataType.TEXT),
                Property(name="chunk_index", data_type=weaviate.classes.data_type.DataType.INT),
                Property(name="content", data_type=weaviate.classes.data_type.DataType.TEXT),
                Property(name="timestamp_start", data_type=weaviate.classes.data_type.DataType.DATE, optional=True),
                Property(name="timestamp_end", data_type=weaviate.classes.data_type.DataType.DATE, optional=True),
                Property(name="author", data_type=weaviate.classes.data_type.DataType.TEXT, optional=True),
                Property(name="language", data_type=weaviate.classes.data_type.DataType.TEXT, optional=True),
            ],
        )
    if entity_class not in existing:
        client.collections.create(
            name=entity_class,
            description="Graph entity nodes",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="name", data_type=weaviate.classes.data_type.DataType.TEXT),
                Property(name="type", data_type=weaviate.classes.data_type.DataType.TEXT),
                Property(name="confidence", data_type=weaviate.classes.data_type.DataType.NUMBER, optional=True),
                Property(name="aliases", data_type=weaviate.classes.data_type.DataType.TEXT_ARRAY, optional=True),
            ],
            references=[
                ReferenceProperty(name="mentionedIn", target_collection=chunk_class, optional=True),
            ],
        )
    if relation_class not in existing:
        client.collections.create(
            name=relation_class,
            description="Graph edges with provenance",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="relation_type", data_type=weaviate.classes.data_type.DataType.TEXT),
                Property(name="confidence", data_type=weaviate.classes.data_type.DataType.NUMBER, optional=True),
                Property(name="evidence", data_type=weaviate.classes.data_type.DataType.TEXT, optional=True),
            ],
            references=[
                ReferenceProperty(name="from", target_collection=entity_class),
                ReferenceProperty(name="to", target_collection=entity_class),
                ReferenceProperty(name="sourceChunk", target_collection=chunk_class, optional=True),
            ],
        )


def embed_chunk(_content: str) -> list[float]:
    # TODO: call Ollama embeddings or another embedding provider.
    raise NotImplementedError("embed_chunk is not implemented. Provide vector externally.")


def upsert_chunks(client: weaviate.WeaviateClient, *, chunk_class: str, records: Iterable[dict], batch_size: int) -> None:
    coll = client.collections.get(chunk_class)
    batch: list[dict] = []
    for rec in records:
        batch.append(rec)
        if len(batch) >= batch_size:
            _flush_chunks(coll, batch)
            batch.clear()
    if batch:
        _flush_chunks(coll, batch)


def _flush_chunks(coll, batch: list[dict]) -> None:
    with coll.batch.dynamic() as writer:
        for rec in batch:
            vector = rec.get("vector") or embed_chunk(rec["content"])
            properties = {k: v for k, v in rec.items() if k not in {"vector", "chunk_id"}}
            writer.add_object(properties=properties, uuid=rec.get("chunk_id"), vector=vector)


def upsert_entities(client: weaviate.WeaviateClient, *, entity_class: str, chunk_class: str, records: Iterable[dict], batch_size: int) -> None:
    coll = client.collections.get(entity_class)
    batch: list[dict] = []
    for rec in records:
        batch.append(rec)
        if len(batch) >= batch_size:
            _flush_entities(coll, chunk_class, batch)
            batch.clear()
    if batch:
        _flush_entities(coll, chunk_class, batch)


def _flush_entities(coll, chunk_class: str, batch: list[dict]) -> None:
    with coll.batch.dynamic() as writer:
        for rec in batch:
            props = {k: v for k, v in rec.items() if k not in {"entity_id", "chunk_id"}}
            uuid = rec.get("entity_id")
            chunk_ref = rec.get("chunk_id")
            refs = None
            if chunk_ref:
                refs = {"mentionedIn": [{"beacon": f"weaviate://localhost/{chunk_class}/{chunk_ref}"}]}
            writer.add_object(properties=props, uuid=uuid, references=refs)


def upsert_relations(client: weaviate.WeaviateClient, *, relation_class: str, entity_class: str, chunk_class: str, records: Iterable[dict], batch_size: int) -> None:
    coll = client.collections.get(relation_class)
    batch: list[dict] = []
    for rec in records:
        batch.append(rec)
        if len(batch) >= batch_size:
            _flush_relations(coll, relation_class, entity_class, chunk_class, batch)
            batch.clear()
    if batch:
        _flush_relations(coll, relation_class, entity_class, chunk_class, batch)


def _flush_relations(coll, relation_class: str, entity_class: str, chunk_class: str, batch: list[dict]) -> None:
    with coll.batch.dynamic() as writer:
        for rec in batch:
            props = {k: v for k, v in rec.items() if k not in {"relation_id", "from_entity_id", "to_entity_id", "chunk_id"}}
            uuid = rec.get("relation_id")
            refs = {
                "from": [{"beacon": f"weaviate://localhost/{entity_class}/{rec.get('from_entity_id')}"}],
                "to": [{"beacon": f"weaviate://localhost/{entity_class}/{rec.get('to_entity_id')}"}],
            }
            chunk_ref = rec.get("chunk_id")
            if chunk_ref:
                refs["sourceChunk"] = [{"beacon": f"weaviate://localhost/{chunk_class}/{chunk_ref}"}]
            writer.add_object(properties=props, uuid=uuid, references=refs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-root", type=Path, default=DEFAULT_DB_ROOT)
    parser.add_argument("--weaviate-url", default=DEFAULT_WEAVIATE_URL)
    parser.add_argument("--chunk-class", default=DEFAULT_CHUNK_CLASS)
    parser.add_argument("--entity-class", default=DEFAULT_ENTITY_CLASS)
    parser.add_argument("--relation-class", default=DEFAULT_RELATION_CLASS)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--apply-schema", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = weaviate.connect_to_local(host=args.weaviate_url)
    try:
        if args.apply_schema:
            ensure_schema(client, chunk_class=args.chunk_class, entity_class=args.entity_class, relation_class=args.relation_class)
        db_root = args.db_root.resolve()
        chunk_dir = db_root / "chunks"
        entity_dir = db_root / "entities"
        relation_dir = db_root / "relations"

        for path in sorted(chunk_dir.glob("*.jsonl")):
            upsert_chunks(client, chunk_class=args.chunk_class, records=iter_jsonl(path), batch_size=args.batch_size)
        for path in sorted(entity_dir.glob("*.jsonl")):
            upsert_entities(client, entity_class=args.entity_class, chunk_class=args.chunk_class, records=iter_jsonl(path), batch_size=args.batch_size)
        for path in sorted(relation_dir.glob("*.jsonl")):
            upsert_relations(client, relation_class=args.relation_class, entity_class=args.entity_class, chunk_class=args.chunk_class, records=iter_jsonl(path), batch_size=args.batch_size)
    finally:
        client.close()


if __name__ == "__main__":
    main()
