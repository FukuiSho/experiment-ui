import json
import os
import re

INPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\01_syntax_filtered.jsonl'
OUTPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\03_scored_fast.jsonl'

def calculate_score(query, response):
    score = 0
    
    # 1. Length Score (Ideally 20-100 chars)
    # Too short is bad, too long is less relevant for chat
    length = len(response)
    if 20 <= length <= 150:
        score += 2.0
    elif 10 <= length < 20:
        score += 1.0
    elif length > 150:
        score += 0.5
        
    # 2. First Person (Strong indicator of persona)
    if re.search(r'(俺|僕|自分|ウチ|私)', response):
        score += 3.0
        
    # 3. Emotion/Vibe Keywords
    # Creating a list of words that indicate "personality" or "casual talk"
    keywords = [
        '笑', 'ｗ', 'w', # Laughter (very common in chat)
        '思う', '感じる', '好き', '嫌い', '頼む', 'お願い',
        'マジ', 'ガチ', 'やば', 'すごい',
        'かも', 'かな', 'だね', 'でしょ',
        '！', '？'
    ]
    hit_count = sum(1 for k in keywords if k in response)
    score += min(hit_count * 0.5, 3.0)  # Cap at 3.0
    
    # 4. Query Quality
    # If query is a question, answer is more likely to be interesting
    if '？' in query or '?' in query:
        score += 1.0
        
    return score

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found")
        return

    scored_items = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                query = data.get('query', '')
                expected = data.get('expected_response', '')
                
                # Fast score
                score = calculate_score(query, expected)
                
                data['scores'] = {'total': score, 'method': 'fast_heuristic'}
                
                # Filter meaningless scores (Optional)
                scored_items.append(data)
                
            except:
                continue
                
    # Sort by score desc
    scored_items.sort(key=lambda x: x['scores']['total'], reverse=True)
    
    # Save top 1000 candidates for pool
    output_count = 1000
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for item in scored_items[:output_count]:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
    print(f"Fast Scoring Complete.")
    print(f"Total processed: {len(scored_items)}")
    print(f"Saved Top {output_count} to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
