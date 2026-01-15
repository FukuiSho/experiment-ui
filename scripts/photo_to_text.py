from __future__ import annotations

import argparse
import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Tuple

import requests
from PIL import Image

try:
    import pillow_heif  # type: ignore

    pillow_heif.register_heif_opener()
except Exception:
    # pillow-heif is optional at runtime but required for HEIC decode; tests rely on install.
    pillow_heif = None  # type: ignore


SUPPORTED_EXTS = {".heic", ".heif", ".jpg", ".jpeg", ".png"}
DEFAULT_SCHEMA_VERSION = "photo_to_text.v1"


@dataclass
class Config:
    input_dir: Path
    output_dir: Path
    cache_dir: Path
    model: str
    host: str
    prompt: str
    skip_existing: bool = True
    timeout: int = 120


def compute_sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_jpg_cache(source_path: Path, cache_dir: Path, quality: int = 92) -> Tuple[str, Path]:
    image_sha = compute_sha256(source_path)
    target = cache_dir / f"{image_sha}.jpg"
    if target.exists() and target.stat().st_size > 0:
        return image_sha, target

    target.parent.mkdir(parents=True, exist_ok=True)
    ext = source_path.suffix.lower()
    if ext in {".heic", ".heif"} and pillow_heif is None:
        raise RuntimeError("pillow-heif is required to decode HEIC/HEIF images. Please install dependencies.")
    with Image.open(source_path) as img:
        img = img.convert("RGB")
        img.save(target, format="JPEG", quality=quality)
    return image_sha, target


def call_ollama_image(image_path: Path, *, model: str, host: str, prompt: str, timeout: int = 120) -> dict:
    b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [b64],
            }
        ],
        "format": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "confidence": {"type": "number"},
            },
            "required": ["text", "confidence"],
        },
    }
    resp = requests.post(f"{host.rstrip('/')}/api/chat", json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    msg = data.get("message", {})
    content = msg.get("content", "")
    parsed = json.loads(content)
    return parsed


def is_successful_output(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text("utf-8"))
        return bool(data.get("text"))
    except Exception:
        return False


def process_image(path: Path, cfg: Config) -> str:
    image_sha, jpg_path = ensure_jpg_cache(path, cfg.cache_dir)
    out_path = cfg.output_dir / f"{image_sha}.json"
    if cfg.skip_existing and is_successful_output(out_path):
        return "skipped"

    result = call_ollama_image(jpg_path, model=cfg.model, host=cfg.host, prompt=cfg.prompt, timeout=cfg.timeout)
    record = {
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "source_path": str(path.as_posix()),
        "image_sha256": image_sha,
        "jpg_cache_path": str(jpg_path.as_posix()),
        "model": cfg.model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "text": result.get("text"),
        "confidence": result.get("confidence"),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), "utf-8")
    return "written"


def iter_images(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in SUPPORTED_EXTS:
            yield p


def check_model_capabilities(*, host: str, model: str) -> None:
    resp = requests.post(f"{host.rstrip('/')}/api/show", json={"model": model}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    caps = data.get("capabilities") or []
    if "vision" not in caps:
        raise RuntimeError(f"Model {model} does not advertise vision capability (capabilities={caps})")


def run(cfg: Config, *, max_images: int | None = None) -> None:
    check_model_capabilities(host=cfg.host, model=cfg.model)
    processed = 0
    for p in iter_images(cfg.input_dir):
        if max_images is not None and processed >= max_images:
            break
        try:
            status = process_image(p, cfg)
            processed += 1
            print(f"{status}: {p}")
        except Exception as exc:  # noqa: BLE001
            fail_log = cfg.output_dir / "_failures.jsonl"
            fail_log.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "source_path": str(p.as_posix()),
                "stage": "process",
                "error": str(exc),
            }
            with fail_log.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"failed: {p}: {exc}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Photo to text via Gemma3 (Ollama)")
    parser.add_argument("--input", dest="input_dir", default="src/lib/pesonaldata/unlabeldata/smartphonephoto")
    parser.add_argument("--output", dest="output_dir", default="src/lib/pesonaldata/derived/photo_to_text")
    parser.add_argument("--model", default="gemma3:27b", help="Ollama Vision model")
    parser.add_argument("--ollama-host", dest="host", default=os.environ.get("PHOTO_TO_TEXT_OLLAMA_HOST", "http://127.0.0.1:11434"))
    parser.add_argument("--prompt", dest="prompt", default="画像内容を日本語で要約し、text(日本語文字列)とconfidence(0..1)のみを含むJSONで返してください。JSON以外は出力しないこと。")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--no-skip-existing", action="store_false", dest="skip_existing")
    parser.add_argument("--max-images", type=int, default=None)
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    cfg = Config(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        cache_dir=Path(args.output_dir) / "jpg_cache",
        model=args.model,
        host=args.host,
        prompt=args.prompt,
        skip_existing=args.skip_existing,
        timeout=args.timeout,
    )
    run(cfg, max_images=args.max_images)
