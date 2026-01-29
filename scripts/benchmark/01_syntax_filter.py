import json
import re
import os
import sys

# Configuration
INPUT_FILE = r'C:\Users\ok220109\experiment-ui\benchmark.jsonl'
OUTPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\01_syntax_filtered.jsonl'

# Filtering Thresholds
MIN_LENGTH = 10
MAX_LENGTH = 100
NO_CONTEXT_CLUES = [
    # Low context dependency clues (Self-contained questions)
    # Actually we want to DROP Hi-Context items (that depend on previous conversation)
    # The user said: "Select items with LOW context dependency"
    # Items containing these words likely refer to previous context -> DROP
    "それ", "あれ", "これ", "そっち", "あっち", "こっち", # Demonstratives (Ko-So-A-Do)
    "その", "あの", "この", 
    "さっき", "いま", "次", "前", # Temporal relativity
    "続き", "さっきの",
]

# Meaningless / Low Quality Patterns (Remove)
BAD_PATTERNS = [
    r"^[wｗ\s]+$", # Only 'w' or whitespace
    r"^草+$",
    r"^[!！?？\s]+$", # Only punctuation
    r"^[\d\s]+$", # Only numbers
    r"よろしくお願いします", 
    r"おはよう", r"こんにちは", r"こんばんは", r"おやすみ",
    r"ありがと", r"サンキュー",
    r"了解", r"わかった", r"おけ", r"うぃ",
    r"誰？", r"何？", r"どこ？", # Too short questions
]

def is_valid_question(query):
    # 1. Length Check
    if len(query) < MIN_LENGTH:
        return False, "Too short"
    if len(query) > MAX_LENGTH:
        return False, "Too long"

    # 2. Syntax Check (Simple Regex)
    for pattern in BAD_PATTERNS:
        if re.search(pattern, query):
            return False, "Bad pattern match"

    # 3. Context Dependency Check (User Request: Select LOW context dependency)
    # If it contains "That", "It", "The previous one", it implies High Context Dependency
    for clue in NO_CONTEXT_CLUES:
        if clue in query:
             return False, f"High context dependency clue: {clue}"

    # 4. Question Check (Ideally should look like a question or a topic starter)
    # This is hard to strictly enforce without NLP, but we can favor items with ? or specific endings
    # But for now, let's trust the length and context check
    
    return True, "Valid"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found")
        return

    total = 0
    passed = 0
    reasons = {}

    with open(INPUT_FILE, 'r', encoding='utf-8') as fin, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        
        for line in fin:
            total += 1
            try:
                data = json.loads(line)
                query = data.get('query', '')
                
                is_valid, reason = is_valid_question(query)
                
                if is_valid:
                    fout.write(json.dumps(data, ensure_ascii=False) + '\n')
                    passed += 1
                else:
                    reasons[reason] = reasons.get(reason, 0) + 1
                    
            except json.JSONDecodeError:
                continue

    print(f"=== Phase 1: Syntax Filter Results ===")
    print(f"Total Input: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Removed: {total - passed}")
    print("\nRemoval Reasons:")
    for r, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {r}: {count}")
    print(f"\nOutput saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
