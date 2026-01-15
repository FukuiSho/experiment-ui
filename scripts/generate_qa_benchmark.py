import argparse
import json
import re
import random
from pathlib import Path
from datetime import datetime
from typing import Iterator, Dict, Any, List

# --- Data Structures ---

class Message:
    def __init__(self, timestamp: str, speaker: str, content: str, source_id: str):
        self.timestamp = timestamp
        self.speaker = speaker
        self.content = content
        self.source_id = source_id # e.g. "line:file.txt:10"

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "speaker": self.speaker,
            "text": self.content
        }

# --- Parsers ---

def parse_line_file(path: Path) -> Iterator[Message]:
    """Parses a single LINE text file."""
    date_header_re = re.compile(r"^(\d{4})/(\d{2})/(\d{2})")
    current_date = "2000-01-01" # Default if missing
    
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Date header
        m = date_header_re.match(line)
        if m:
            current_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
            continue
            
        # Message line: Time <tab> Speaker <tab> Content
        parts = line.split("\t")
        if len(parts) >= 3:
            time_str = parts[0]
            speaker = parts[1]
            content = "\t".join(parts[2:]) # Rejoin if content has tabs
            
            # Filter system messages
            if not time_str or not speaker: 
                continue
                
            # Filter meta content
            if content in ["[スタンプ]", "[写真]", "[動画]", "[通話]"]:
                continue
            if content.startswith("[") and content.endswith("]") and "アルバム" in content:
                continue
            if "メッセージの送信を取り消しました" in content:
                continue
                
            # Construct timestamp
            # Use dummy seconds 00 because LINE export (text) often only has HH:MM
            # If time_str is like "18:24", -> "YYYY-MM-DDT18:24:00"
            if re.match(r"^\d{1,2}:\d{2}$", time_str):
                ts = f"{current_date}T{time_str}:00"
            else:
                ts = f"{current_date}T00:00:00" # Fallback

            yield Message(ts, speaker, content, f"line:{path.name}:{i+1}")

def parse_limitless_file(path: Path) -> Iterator[Message]:
    """Parses the Limitless lifelogs.json file."""
    try:
        data = json.load(path.open("r", encoding="utf-8"))
    except Exception as e:
        print(f"Error loading Limitless file: {e}")
        return

    for item in data:
        log_id = item.get("id")
        # Start time of the log
        base_time = item.get("startTime", "2000-01-01T00:00:00Z")
        
        contents = item.get("contents", [])
        for i, c in enumerate(contents):
            # We only care about blockquotes as they seem to be the transcript
            if c.get("type") == "blockquote":
                text = c.get("content", "").strip()
                if not text:
                    continue
                
                # We treat everything as "Unknown" speaker, or maybe "LimitlessUser"
                # Since we don't know who is speaking, we just use "limitless_speaker"
                yield Message(base_time, "limitless_speaker", text, f"limitless:{log_id}:{i}")

# --- Generator ---

def generate_benchmark(
    line_dir: Path, 
    limitless_file: Path, 
    target_speaker: str, 
    context_size: int = 5
) -> Iterator[Dict[str, Any]]:
    
    # 1. Process LINE Data
    if line_dir.exists():
        for file_path in sorted(line_dir.glob("*.txt")):
            messages = list(parse_line_file(file_path))
            for i in range(len(messages)):
                target_msg = messages[i]
                
                # We want to predict Target Speaker's response
                if target_msg.speaker == target_speaker:
                    # Gather context
                    start_idx = max(0, i - context_size)
                    context_msgs = messages[start_idx:i]
                    
                    if not context_msgs:
                        continue
                        
                    # Filter: Ensure at least one message in context is NOT from target speaker?
                    # Actually, standard conversation can be User-User (monologue) but usually it's Others-User.
                    # Let's keep it simple.
                    
                    yield {
                        "id": target_msg.source_id,
                        "timestamp": target_msg.timestamp,
                        "source_type": "line",
                        "context_messages": [m.to_dict() for m in context_msgs],
                        "query": context_msgs[-1].content, # The immediate trigger
                        "expected_response": target_msg.content
                    }

    # 2. Process Limitless Data
    if limitless_file.exists():
        limitless_msgs = list(parse_limitless_file(limitless_file))
        # Since these are chronological blocks from possibly the same conversation (or adjacent snippets)
        # We just generate pairs: (Preceding Blocks) -> (Next Block)
        # Assuming typical conversation flow. 
        # CAUTION: Limitless logs might be fragmented. 'log_id' groups them.
        
        # Group by log_id to avoid crossing conversation boundaries
        grouped = {}
        for m in limitless_msgs:
            log_id = m.source_id.split(":")[1]
            if log_id not in grouped:
                grouped[log_id] = []
            grouped[log_id].append(m)
            
        for log_id, msgs in grouped.items():
            for i in range(1, len(msgs)):
                target_msg = msgs[i]
                start_idx = max(0, i - context_size)
                context_msgs = msgs[start_idx:i]
                
                if not context_msgs:
                    continue

                yield {
                    "id": target_msg.source_id,
                    "timestamp": target_msg.timestamp,
                    "source_type": "limitless",
                    "context_messages": [m.to_dict() for m in context_msgs],
                    "query": context_msgs[-1].content,
                    "expected_response": target_msg.content
                }

def main():
    parser = argparse.ArgumentParser(description="Generate QA Benchmark from LINE and Limitless data")
    parser.add_argument("--line-dir", type=Path, default=Path("src/lib/pesonaldata/unlabeldata/LINE"))
    parser.add_argument("--limitless-file", type=Path, default=Path("src/lib/pesonaldata/unlabeldata/limitless/lifelogs.json"))
    parser.add_argument("--target-speaker", type=str, required=True, help="Exact name of the target user in LINE")
    parser.add_argument("--output", type=Path, required=True, help="Output JSONL file")
    parser.add_argument("--limit", type=int, default=0, help="Max items to output (0 for all)")
    parser.add_argument("--context-size", type=int, default=5, help="Number of previous messages as context")
    
    args = parser.parse_args()
    
    print(f"Generating benchmark to {args.output}...")
    print(f"Target Speaker: {args.target_speaker}")
    
    count = 0
    with args.output.open("w", encoding="utf-8") as f:
        generator = generate_benchmark(
            args.line_dir, 
            args.limitless_file, 
            args.target_speaker, 
            args.context_size
        )
        
        for item in generator:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            count += 1
            if args.limit > 0 and count >= args.limit:
                break
                
    print(f"Done. Generated {count} items.")

if __name__ == "__main__":
    main()
