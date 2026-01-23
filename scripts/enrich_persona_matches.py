import json
import os

SOURCE_RESULTS_FILE = 'benchmark_results.jsonl'
TARGET_FILE = 'benchmark_persona_match_yes.jsonl'

def main():
    if not os.path.exists(SOURCE_RESULTS_FILE):
        print(f"Error: {SOURCE_RESULTS_FILE} not found.")
        return
    if not os.path.exists(TARGET_FILE):
        print(f"Error: {TARGET_FILE} not found.")
        return

    # Load expected responses map
    print(f"Loading expected responses from {SOURCE_RESULTS_FILE}...")
    expected_map = {}
    with open(SOURCE_RESULTS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'id' in data and 'expected_response' in data:
                    expected_map[data['id']] = data['expected_response']
            except json.JSONDecodeError:
                continue

    # Enrich target file
    print(f"Enriching {TARGET_FILE}...")
    enriched_data = []
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if data['id'] in expected_map:
                    data['expected_response'] = expected_map[data['id']]
                else:
                    print(f"Warning: No expected response found for ID {data.get('id')}")
                enriched_data.append(data)
            except json.JSONDecodeError:
                continue

    # Save back
    print(f"Saving {len(enriched_data)} items back to {TARGET_FILE}...")
    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        for item in enriched_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print("Done.")

if __name__ == "__main__":
    main()
