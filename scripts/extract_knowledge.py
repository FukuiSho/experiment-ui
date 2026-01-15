import glob
import os

LINE_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\LINE'

def extract_knowledge_candidates():
    if not os.path.exists(LINE_DIR):
        print("LINE directory not found.")
        return
    
    line_files = glob.glob(os.path.join(LINE_DIR, '*.txt'))
    target_speakers = ['聖', '福井']
    
    knowledge_categories = {
        "Preferences (Likes/Wants)": ["好き", "嫌い", "ほしい", "欲しい", "たい", "派"],
        "Actions/Experiences": ["行った", "やった", "見た", "食べた", "買った", "決めた"],
        "Attributes/Facts": ["オレは", "俺は", "自分は", "実は", "苦手", "得意", "つもり", "予定"],
        "Opinions/Thoughts": ["思う", "考える", "感じる", "気がする", "かも"]
    }

    candidates = {k: [] for k in knowledge_categories}
    
    existing_sentences = set()

    for file_path in line_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    speaker = parts[1]
                    message = parts[2].strip('"')
                    
                    if any(target in speaker for target in target_speakers):
                        if len(message) < 5: continue # Skip too short
                        if "http" in message: continue
                        if message in existing_sentences: continue
                        
                        existing_sentences.add(message)
                        
                        # Categorize
                        matched = False
                        for category, keywords in knowledge_categories.items():
                            if any(k in message for k in keywords):
                                candidates[category].append(message)
                                matched = True
                                # Don't break, a sentence can belong to multiple, but for simple listing maybe better to just pick one or show in multiple?
                                # Let's show in all matching to see context.
                        
                        # if not matched and len(message) > 20:
                        #    candidates["Other Long Messages"].append(message)

        except Exception as e:
            # print(f"Error reading {file_path}: {e}")
            continue

    # Print results
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    for category, messages in candidates.items():
        print(f"\n### {category}")
        # Show top 15 most interesting (longest?) or just random?
        # Let's show longest ones as they likely contain more info
        messages.sort(key=len, reverse=True)
        for i, msg in enumerate(messages[:20]):
            print(f"- {msg}")

if __name__ == "__main__":
    extract_knowledge_candidates()
