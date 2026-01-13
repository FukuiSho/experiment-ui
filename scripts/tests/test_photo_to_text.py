from __future__ import annotations

import json
import sys
import base64
from pathlib import Path

import pytest
from PIL import Image

# Make project root importable so we can import scripts.photo_to_text
sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.photo_to_text import (  # noqa: E402
    compute_sha256,
    ensure_jpg_cache,
    call_ollama_image,
    process_image,
    run,
    Config,
    check_model_capabilities,
)


@pytest.fixture()
def tmp_png(tmp_path: Path) -> Path:
    path = tmp_path / "sample.png"
    img = Image.new("RGB", (2, 2), color=(123, 45, 67))
    img.save(path, format="PNG")
    return path


def test_compute_sha256(tmp_path: Path) -> None:
    target = tmp_path / "data.bin"
    target.write_bytes(b"abc")
    assert compute_sha256(target) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_ensure_jpg_cache_converts_png(tmp_png: Path, tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    image_sha, jpg_path = ensure_jpg_cache(tmp_png, cache_dir)

    assert image_sha == compute_sha256(tmp_png)
    assert jpg_path.exists()
    assert jpg_path.suffix.lower() == ".jpg"
    assert jpg_path.read_bytes()  # not empty


def test_call_ollama_image_posts_base64_and_parses_response(tmp_png: Path, requests_mock) -> None:
    host = "http://127.0.0.1:11434"
    model = "gemma3:27b"
    prompt = "Return JSON"
    expected_text = "test caption"
    expected_conf = 0.42

    def _match(request, context):
        body = request.json()
        assert body["model"] == model
        assert body["stream"] is False
        messages = body["messages"]
        assert len(messages) == 1
        m0 = messages[0]
        assert m0["role"] == "user"
        assert m0["content"] == prompt
        images = m0.get("images")
        assert isinstance(images, list) and len(images) == 1
        # Ensure the base64 decodes to image bytes
        base64.b64decode(images[0])

        context.status_code = 200
        return {
            "model": model,
            "message": {
                "role": "assistant",
                "content": json.dumps({"text": expected_text, "confidence": expected_conf}),
            },
            "done": True,
        }

    requests_mock.post(f"{host}/api/chat", json=_match)

    result = call_ollama_image(tmp_png, model=model, host=host, prompt=prompt)
    assert result["text"] == expected_text
    assert result["confidence"] == expected_conf


def test_process_image_writes_schema_and_created_at(tmp_png: Path, tmp_path: Path, monkeypatch) -> None:
    out_dir = tmp_path / "out"
    cfg = Config(
        input_dir=tmp_path,
        output_dir=out_dir,
        cache_dir=out_dir / "jpg_cache",
        model="gemma3:27b",
        host="http://localhost:11434",
        prompt="p",
    )

    def fake_call(*args, **kwargs):
        return {"text": "ok", "confidence": 0.5}

    monkeypatch.setattr("scripts.photo_to_text.call_ollama_image", fake_call)

    status = process_image(tmp_png, cfg)
    assert status == "written"
    json_path = out_dir / f"{compute_sha256(tmp_png)}.json"
    data = json.loads(json_path.read_text("utf-8"))
    assert data["schema_version"] == "photo_to_text.v1"
    assert data["text"] == "ok"
    assert data["confidence"] == 0.5
    assert data["created_at"]  # non-empty ISO string


def test_run_respects_max_images(tmp_path: Path, monkeypatch) -> None:
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    for i in range(3):
        img = Image.new("RGB", (1, 1), color=(i, i, i))
        img.save(in_dir / f"img{i}.jpg", format="JPEG")

    called: list[Path] = []

    def fake_process(p: Path, cfg):
        called.append(p)
        return "written"

    monkeypatch.setattr("scripts.photo_to_text.process_image", fake_process)
    monkeypatch.setattr("scripts.photo_to_text.check_model_capabilities", lambda **kwargs: None)

    cfg = Config(
        input_dir=in_dir,
        output_dir=tmp_path / "out",
        cache_dir=tmp_path / "out" / "jpg_cache",
        model="m",
        host="h",
        prompt="p",
    )
    run(cfg, max_images=2)
    assert len(called) == 2


def test_check_model_capabilities_requires_vision(requests_mock) -> None:
    host = "http://127.0.0.1:11434"
    model = "gemma3:27b"
    requests_mock.post(f"{host}/api/show", json={"capabilities": ["vision", "completion"]})
    check_model_capabilities(host=host, model=model)

    requests_mock.post(f"{host}/api/show", json={"capabilities": ["completion"]})
    with pytest.raises(RuntimeError):
        check_model_capabilities(host=host, model=model)
