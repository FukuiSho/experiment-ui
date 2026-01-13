import json
import sys
from pathlib import Path

# Ensure project root is on sys.path when running this file directly with `python .../test_normalize_personaldata.py`
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from scripts.normalize_personaldata import (
    ChunkRecord,
    iter_line_chunks,
    iter_pcmemo_chunks,
    iter_photo_chunks,
    iter_smartphonememo_chunks,
    iter_twitter_chunks,
    iter_gpt_chunks,
)


def write_sample_photo_json(tmpdir: Path, *, sha: str = "abc123", text: str = "テストキャプション", confidence: float = 0.7) -> Path:
    data = {
        "schema_version": "photo_to_text.v1",
        "source_path": "src/lib/pesonaldata/unlabeldata/smartphonephoto/2026/01/img001.HEIC",
        "image_sha256": sha,
        "jpg_cache_path": "src/lib/pesonaldata/derived/photo_to_text/jpg_cache/abc123.jpg",
        "model": "gemma3:27b",
        "created_at": "2026-01-09T12:34:56+09:00",
        "text": text,
        "confidence": confidence,
    }
    out = tmpdir / f"{sha}.json"
    out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return out


def test_iter_photo_chunks_emits_one_chunk_with_expected_fields(tmp_path: Path) -> None:
    root = tmp_path
    json_path = write_sample_photo_json(root)

    chunks = list(iter_photo_chunks(root))
    assert len(chunks) == 1
    chunk = chunks[0]
    assert isinstance(chunk, ChunkRecord)
    assert chunk.source_type == "photo_to_text"
    assert chunk.doc_id == "photo:abc123"
    assert chunk.chunk_id == "photo:abc123:0"
    assert chunk.chunk_index == 0
    assert chunk.content == "テストキャプション"
    assert chunk.source_path == json_path.as_posix()
    assert chunk.metadata is not None
    assert chunk.metadata.get("confidence") == pytest.approx(0.7)
    assert chunk.metadata.get("model") == "gemma3:27b"
    assert chunk.metadata.get("created_at") == "2026-01-09T12:34:56+09:00"


def test_iter_line_chunks_splits_by_date_and_is_deterministic(tmp_path: Path) -> None:
    line_root = tmp_path / "LINE"
    line_root.mkdir(parents=True, exist_ok=True)
    chat_file = line_root / "family_chat.txt"
    chat_file.write_text(
        """
2024/01/01(月)
12:00	Alice	あけおめ
13:00	Bob	よろしく
2024/01/02(火)
08:00	Alice	おはよう
""".strip(),
        encoding="utf-8",
    )

    chunks = list(iter_line_chunks(line_root))
    assert len(chunks) == 2
    # First day chunk
    first = chunks[0]
    assert first.chunk_id == "line:family_chat:2024-01-01"
    assert first.doc_id == "line:family_chat"
    assert "12:00 Alice: あけおめ" in first.content
    assert "13:00 Bob: よろしく" in first.content
    assert first.chunk_index == 0
    assert first.metadata.get("date") == "2024-01-01"
    # Second day chunk
    second = chunks[1]
    assert second.chunk_id == "line:family_chat:2024-01-02"
    assert second.chunk_index == 1
    assert "08:00 Alice: おはよう" in second.content
    assert second.metadata.get("date") == "2024-01-02"


def test_iter_pcmemo_chunks_splits_paragraphs_and_groups(tmp_path: Path) -> None:
    memo_root = tmp_path / "pcmemo"
    memo_root.mkdir(parents=True, exist_ok=True)
    note = memo_root / "ideas.txt"
    note.write_text(
        """
第一段落。アイデアA。

第二段落。アイデアB。

第三段落。アイデアC。
""".strip(),
        encoding="utf-8",
    )

    chunks = list(iter_pcmemo_chunks(memo_root, max_chars=27))
    assert len(chunks) == 2

    first = chunks[0]
    assert first.chunk_id == "pcmemo:ideas:0"
    assert "第一段落" in first.content
    assert "第二段落" in first.content

    second = chunks[1]
    assert second.chunk_id == "pcmemo:ideas:1"
    assert "第三段落" in second.content
    assert second.chunk_index == 1


def test_iter_smartphonememo_chunks_includes_subdirs(tmp_path: Path) -> None:
    root = tmp_path / "smartphonememo"
    (root / "topic1").mkdir(parents=True, exist_ok=True)
    note = root / "topic1" / "memo1.txt"
    note.write_text("A\n\nB", encoding="utf-8")

    chunks = list(iter_smartphonememo_chunks(root, max_chars=3))
    assert len(chunks) == 2
    assert chunks[0].chunk_id == "smartphonememo:topic1_memo1:0"
    assert chunks[1].chunk_id == "smartphonememo:topic1_memo1:1"
    assert "A" in chunks[0].content
    assert "B" in chunks[1].content


def test_iter_twitter_chunks_parses_js_and_emits_tweet_chunks(tmp_path: Path) -> None:
    root = tmp_path / "twitter"
    data_dir = root / "export" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    js = data_dir / "tweets.js"
    js.write_text(
        "window.YTD.tweets = [\n  {\"tweet\": {\"id_str\": \"123\", \"full_text\": \"hello world\", \"created_at\": \"Mon Jan 01 00:00:00 +0000 2024\"}}\n];",
        encoding="utf-8",
    )

    chunks = list(iter_twitter_chunks(root))
    assert len(chunks) == 1
    c = chunks[0]
    assert c.chunk_id == "twitter:tweet:123"
    assert c.doc_id == "tweet:123"
    assert c.content == "hello world"
    assert c.metadata.get("created_at") == "Mon Jan 01 00:00:00 +0000 2024"


def test_iter_gpt_chunks_streams_conversations(tmp_path: Path) -> None:
    gpt_root = tmp_path / "GPT"
    gpt_root.mkdir(parents=True, exist_ok=True)
    conv = [
        {
            "id": "conv1",
            "title": "test conv",
            "create_time": 1704067200,
            "mapping": {
                "m1": {
                    "id": "m1",
                    "message": {
                        "id": "m1",
                        "author": {"role": "user"},
                        "content": {"parts": ["hello"], "content_type": "text"},
                        "create_time": 1704067200,
                    },
                },
                "m2": {
                    "id": "m2",
                    "message": {
                        "id": "m2",
                        "author": {"role": "assistant"},
                        "content": {"parts": ["hi there"], "content_type": "text"},
                        "create_time": 1704067300,
                    },
                },
            },
        }
    ]
    conv_path = gpt_root / "conversations.json"
    conv_path.write_text(json.dumps(conv, ensure_ascii=False), encoding="utf-8")

    chunks = list(iter_gpt_chunks(gpt_root, max_messages=2))
    assert len(chunks) == 1
    c = chunks[0]
    assert c.chunk_id == "gpt:conv1:0"
    assert c.doc_id == "gpt:conv1"
    assert "user: hello" in c.content
    assert "assistant: hi there" in c.content
    assert c.chunk_index == 0
