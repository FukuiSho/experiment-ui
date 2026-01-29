import json
import os
import random

MANUAL_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\04_final_selection.jsonl'
AUTO_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\03_scored_fast.jsonl'
OUTPUT_FILE = r'C:\Users\ok220109\experiment-ui\benchmark_final_100.jsonl'

TARGET_COUNT = 100

def categorize_item(item):
    query = item.get('query', '')
    if '？' in query or '?' in query:
        if any(w in query for w in ['何', '誰', 'どこ', 'いつ']):
            return 'Fact/Question'
        return 'Opinion/Question'
    return 'Chat/Statement'

def load_jsonl(filepath):
    items = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    items.append(json.loads(line))
                except:
                    pass
    return items

def main():
    # 1. Load Manual Selection
    manual_items = load_jsonl(MANUAL_FILE)
    print(f"Loaded Manual Items: {len(manual_items)}")
    
    # 2. Load Auto Selection
    auto_items = load_jsonl(AUTO_FILE)
    print(f"Loaded Auto Items: {len(auto_items)}")
    
    # Avoid duplicates
    manual_ids = set(item['id'] for item in manual_items)
    
    final_items = manual_items.copy()
    
    # Fill remaining
    needed = TARGET_COUNT - len(final_items)
    if needed > 0:
        print(f"Need {needed} more items. Filling from Auto Selection...")
        for item in auto_items:
            if item['id'] not in manual_ids:
                final_items.append(item)
                needed -= 1
                if needed == 0:
                    break
    
    # If still not enough (unlikely if pipeline ran), we have a problem but let's just save what we have
    
    # Trim if overshoot (only if manual was > 100, which is unlikely but good safety)
    if len(final_items) > TARGET_COUNT:
         final_items = final_items[:TARGET_COUNT]
         
    # Analyze & Tag
    categories = {}
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for item in final_items:
            cat = categorize_item(item)
            categories[cat] = categories.get(cat, 0) + 1
            
            final_obj = {
                "id": item.get('id'),
                "query": item.get('query'),
                "expected_response": item.get('expected_response'),
                "category": cat,
                "meta": {
                    "score": item.get('scores', {}).get('total', 0),
                    "source": "manual" if item['id'] in manual_ids else "auto_fast"
                }
            }
            f.write(json.dumps(final_obj, ensure_ascii=False) + '\n')

    print(f"=== Final Compilation Complete ===")
    print(f"Total: {len(final_items)}")
    print("Category Stats:")
    for k, v in categories.items():
        print(f"  {k}: {v}")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
