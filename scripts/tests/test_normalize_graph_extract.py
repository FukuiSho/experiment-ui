import json
from pathlib import Path

import scripts.normalize_personaldata as norm


class DummyResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_call_ollama_extract_parses_json(monkeypatch):
    called = {}

    def fake_post(url, json=None, timeout=None):
        called["url"] = url
        called["json"] = json
        return DummyResp({"message": {"content": json_module.dumps({
            "entities": [{"name": "Alice", "type": "PERSON", "confidence": 0.9}],
            "relations": [{"from": "Alice", "to": "Bob", "relation_type": "knows", "confidence": 0.8, "evidence": "A knows B"}],
        })}})

    json_module = json
    monkeypatch.setattr(norm.requests, "post", fake_post)

    result = norm.call_ollama_extract("hello", host="http://localhost:11434", model="gemma3:27b", timeout=5)
    assert len(result["entities"]) == 1
    assert result["entities"][0]["name"] == "Alice"
    assert len(result["relations"]) == 1
    assert result["relations"][0]["relation_type"] == "knows"
    assert called["url"].endswith("/api/chat")


def test_emit_graph_writes_entities_and_relations(tmp_path: Path, monkeypatch):
    chunks_dir = tmp_path / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    chunk_file = chunks_dir / "sample.jsonl"
    chunk_file.write_text(
        json.dumps({"chunk_id": "c1", "content": "Alice knows Bob."}) + "\n",
        encoding="utf-8",
    )

    def fake_extract(content: str, host: str, model: str, timeout: int):
        return {
            "entities": [{"name": "Alice", "type": "PERSON", "confidence": 0.9}],
            "relations": [{"from": "Alice", "to": "Bob", "relation_type": "knows", "confidence": 0.8, "evidence": "Alice knows Bob"}],
        }

    monkeypatch.setattr(norm, "call_ollama_extract", fake_extract)

    entities_path = tmp_path / "entities.jsonl"
    relations_path = tmp_path / "relations.jsonl"
    norm._emit_graph(
        chunks_dir=chunks_dir,
        entities_path=entities_path,
        relations_path=relations_path,
        ollama_host="http://localhost:11434",
        model="gemma3:27b",
        timeout=5,
    )

    ents = [json.loads(l) for l in entities_path.read_text("utf-8").splitlines() if l.strip()]
    rels = [json.loads(l) for l in relations_path.read_text("utf-8").splitlines() if l.strip()]

    assert len(ents) == 1
    assert ents[0]["name"] == "Alice"
    assert ents[0]["chunk_id"] == "c1"

    assert len(rels) == 1
    assert rels[0]["relation_type"] == "knows"
    assert rels[0]["chunk_id"] == "c1"
