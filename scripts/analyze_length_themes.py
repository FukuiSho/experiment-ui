import glob
import os
import re
from janome.tokenizer import Tokenizer
from collections import Counter

# Paths
LINE_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\LINE'

def analyze_length_themes():
    if not os.path.exists(LINE_DIR):
        print("LINE directory not found.")
        return

    files = glob.glob(os.path.join(LINE_DIR, '*.txt'))
    target_speakers = ['聖', '福井']
    
    short_messages = [] # < 15 chars
    long_messages = []  # > 30 chars

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    speaker = parts[1]
                    message = parts[2].strip('"')
                    if any(target in speaker for target in target_speakers):
                        if "http" in message or "[スタンプ]" in message or "[写真]" in message:
                            continue
                        
                        length = len(message)
                        if length < 15:
                            short_messages.append(message)
                        elif length > 30:
                            long_messages.append(message)
        except: continue
        
    print(f"Short Messages: {len(short_messages)}")
    print(f"Long Messages: {len(long_messages)}")

    tokenizer = Tokenizer()
    stop_words = {'する', 'いる', 'ある', 'ない', 'なる', 'れる', 'の', 'こと', 'よう', 'それ', 'これ', 'ん', '私', '俺', '僕', '今日', '明日', '昨日', '笑', 'スタンプ', '写真', '動画', '送信', '取り消し', 'メッセージ', 'て', 'に', 'を', 'は', 'が', 'た', 'ね', 'よ', 'な', 'ます', 'です', 'か', 'って', 'し', 'う', 'けど', 'から', 'ので', 'もの', 'ん', 'さん', 'ちゃん', 'くん', 'あと', 'なん', 'いい', 'そう', '思う', '自分', 'オレ', '人', '気', '時', '俺', '何'}

    def get_frequent_words(texts):
        words = []
        for text in texts:
            try:
                tokens = tokenizer.tokenize(text)
                for token in tokens:
                    # Filter: Noun only for topics
                    if token.part_of_speech.startswith('名詞'):
                        base = token.base_form
                        if base not in stop_words and len(base) > 1 and not base.isdigit():
                            words.append(base)
            except: pass
        return Counter(words).most_common(20)
    
    short_freq = get_frequent_words(short_messages)
    long_freq = get_frequent_words(long_messages)
    
    print("\n### Themes in Short Messages (<15 chars)")
    print("(Often reactive, scheduling, quick status)")
    for w, c in short_freq:
        print(f"- {w}: {c}")

    print("\n### Themes in Long Messages (>30 chars)")
    print("(Often explanatory, philosophical, complex planning)")
    for w, c in long_freq:
        print(f"- {w}: {c}")

    # Extract sample sentences for context
    print("\n### Sample Long Messages (Context)")
    import random
    if long_messages:
        for m in random.sample(long_messages, min(5, len(long_messages))):
            print(f"- {m}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    analyze_length_themes()
