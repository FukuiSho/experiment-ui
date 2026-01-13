import json
from pathlib import Path

import pytest

import scripts.weaviate_import as wi


class DummyResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:  # pragma: no cover - simple stub
        return None

    def json(self) -> dict:
        return self._payload


def test_embed_chunk_calls_ollama_with_prompt(monkeypatch):
    called = {}

    def fake_post(url, json=None, timeout=None):
        called["url"] = url
        called["json"] = json
        return DummyResp({"embedding": [0.1, 0.2, 0.3]})

    monkeypatch.setattr(wi.requests, "post", fake_post)

    emb = wi.embed_chunk("hello", host="http://localhost:11434", model="nomic-embed-text", timeout=5)

    assert emb == [0.1, 0.2, 0.3]
    assert called["url"].endswith("/api/embeddings")
    assert called["json"] == {"model": "nomic-embed-text", "prompt": "hello"}
    assert called["json"]["prompt"] == "hello"
