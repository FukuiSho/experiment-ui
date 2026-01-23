import json
import os

INPUT_FILE = 'benchmark_human_eval.jsonl'
OUTPUT_FILE = 'benchmark_persona_match_yes.jsonl'
OUTPUT_TEXT_FILE = 'benchmark_persona_match_yes.txt'

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    count = 0
    matches = []
    
    print(f"Reading from {INPUT_FILE}...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get('is_persona_match') is True:
                    matches.append(data)
                    count += 1
            except json.JSONDecodeError:
                continue

    # Save as JSONL
    print(f"Found {count} matches. Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for item in matches:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    # Save as readable Text
    print(f"Saving readable list to {OUTPUT_TEXT_FILE}...")
    with open(OUTPUT_TEXT_FILE, 'w', encoding='utf-8') as f:
        for item in matches:
            f.write(f"Query: {item.get('query', '')}\n")
            f.write(f"Response: {item.get('generated_response', '').strip()}\n")
            f.write("-" * 40 + "\n")

    print("Done.")

if __name__ == "__main__":
    main()
