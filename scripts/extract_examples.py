import glob
import os
import random

LINE_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\LINE'

def get_line_examples():
    if not os.path.exists(LINE_DIR):
        return []
    
    line_files = glob.glob(os.path.join(LINE_DIR, '*.txt'))
    target_speakers = ['聖', '福井']
    messages = []

    for file_path in line_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    speaker = parts[1]
                    message = parts[2]
                    
                    # Filter for user
                    if any(target in speaker for target in target_speakers):
                        # Filter out system messages or very short ones
                        if message not in ['[スタンプ]', '[写真]', '[動画]'] and len(message) > 5:
                            # Remove quotes if they exist (CSV style)
                            clean_msg = message.strip('"')
                            messages.append(clean_msg)
        except:
            continue
            
    # Heuristic for "characteristic": longer sentences, use of "オレ" or characteristic particles
    # But random sampling from user's filtered messages is the most unbiased "characteristic" check 
    # if we assume the whole corpus represents them.
    # However, to be "concrete examples" (具体例), they should ideally be substantive.
    
    # Filter to avoid URLs and very short lines
    candidates = []
    
    # Characteristic keywords (based on previous analysis: オレ, 笑, Kansai dialect cues)
    keywords = ['オレ', '笑', 'やん', 'せや', 'ちゃう', 'マジ', '確か', 'なるほど']
    
    for m in messages:
        if "http" in m:
            continue
        if len(m) < 8:
            continue
            
        # Score message by keyword presence
        score = sum(1 for k in keywords if k in m)
        # Also favor slightly longer messages for context
        if len(m) > 20:
            score += 1
            
        candidates.append((score, m))
    
    # Sort by score desc, then length desc
    candidates.sort(key=lambda x: (x[0], len(x[1])), reverse=True)
    
    # Pick top 20 to shuffle from, or just top 10 unique
    unique_top = []
    seen = set()
    for _, msg in candidates:
        if msg not in seen:
            unique_top.append(msg)
            seen.add(msg)
        if len(unique_top) >= 10:
            break
            
    return unique_top

if __name__ == "__main__":
    # Set stdout to utf-8 explicitly for Windows console if needed
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    examples = get_line_examples()
    for i, ex in enumerate(examples, 1):
        print(f"{i}. {ex}")
