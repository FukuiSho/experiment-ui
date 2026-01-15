import pytest
import json
from pathlib import Path
from scripts.generate_qa_benchmark import parse_line_file, parse_limitless_file, generate_benchmark

def test_parse_line_file(tmp_path):
    f = tmp_path / "test_talk.txt"
    f.write_text(
        "2023/01/01\n"
        "10:00\tUserA\tHello\n"
        "10:01\tUserB\tHi there\n"
        "10:02\tUserA\t[スタンプ]\n"
        "10:03\tUserA\tHow are you?\n",
        encoding="utf-8"
    )
    
    msgs = list(parse_line_file(f))
    assert len(msgs) == 3 # Sticker skipped
    assert msgs[0].content == "Hello"
    assert msgs[0].speaker == "UserA"
    assert msgs[1].content == "Hi there"
    assert msgs[2].content == "How are you?"

def test_parse_limitless_file(tmp_path):
    f = tmp_path / "lifelogs.json"
    data = [
        {
            "id": "log1",
            "contents": [
                {"type": "heading1", "content": "Title"},
                {"type": "blockquote", "content": "Line 1"},
                {"type": "blockquote", "content": "Line 2"}
            ]
        }
    ]
    f.write_text(json.dumps(data), encoding="utf-8")
    
    msgs = list(parse_limitless_file(f))
    assert len(msgs) == 2
    assert msgs[0].content == "Line 1"
    assert msgs[0].source_id == "limitless:log1:1"
    assert msgs[1].content == "Line 2"

def test_generate_benchmark(tmp_path):
    # Setup LINE
    line_dir = tmp_path / "LINE"
    line_dir.mkdir()
    (line_dir / "talk.txt").write_text(
        "2023/01/01\n"
        "10:00\tOther\tQ1\n"
        "10:01\tTarget\tA1\n",
        encoding="utf-8"
    )
    
    # Setup Limitless
    limit_file = tmp_path / "lifelogs.json"
    limit_file.write_text(json.dumps([
        {
            "id": "log1", 
            "contents": [
                {"type": "blockquote", "content": "C1"},
                {"type": "blockquote", "content": "C2"}
            ]
        }
    ]), encoding="utf-8")
    
    output = tmp_path / "bench.jsonl"
    
    # Run generator
    # We explicitly call the internal generator function to test logic
    gen = generate_benchmark(line_dir, limit_file, "Target", context_size=1)
    items = list(gen)
    
    # Expected: 
    # 1. LINE: Q1 -> A1
    # 2. Limitless: C1 -> C2
    
    assert len(items) == 2
    
    line_item = next(i for i in items if i["source_type"] == "line")
    assert line_item["query"] == "Q1"
    assert line_item["expected_response"] == "A1"
    
    limit_item = next(i for i in items if i["source_type"] == "limitless")
    assert limit_item["query"] == "C1"
    assert limit_item["expected_response"] == "C2"
