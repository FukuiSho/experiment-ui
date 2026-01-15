import json
import os
import glob
import re
from janome.tokenizer import Tokenizer
from collections import Counter

# Paths
LIMITLESS_FILE = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\limitless\lifelogs.json'
LINE_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\LINE'

def analyze_text(texts, label):
    if not texts:
        print(f"[{label}] No data found.")
        return

    print(f"\n--- {label} Analysis ---")
    print(f"Total messages: {len(texts)}")

    # Average Context Length
    total_length = sum(len(text) for text in texts)
    avg_length = total_length / len(texts) if texts else 0
    print(f"Average Context Length (chars): {avg_length:.2f}")

    # Frequent Words
    tokenizer = Tokenizer()
    word_counts = Counter()
    
    # Common stop words to ignore (can be expanded)
    stop_words = {'する', 'いる', 'ある', 'ない', 'なる', 'れる', 'の', 'こと', 'よう', 'それ', 'これ', 'ん', '私', '俺', '僕', '今日', '明日', '昨日', '笑', 'スタンプ', '写真', '動画', '送信', '取り消し', 'メッセージ'}

    for text in texts:
        try:
            tokens = tokenizer.tokenize(text)
            for token in tokens:
                # Filter by part of speech: Noun, Verb, Adjective
                part_of_speech = token.part_of_speech.split(',')[0]
                if part_of_speech in ['名詞', '動詞', '形容詞']:
                    base_form = token.base_form
                    if base_form not in stop_words and len(base_form) > 1: # Ignore single characters and stop words
                         word_counts[base_form] += 1
        except Exception as e:
            # print(f"Error tokenizing: {e}")
            continue

    print("Top 20 Frequent Words:")
    for word, count in word_counts.most_common(20):
        print(f"{word}: {count}")

def load_limitless_data():
    texts = []
    if not os.path.exists(LIMITLESS_FILE):
        print(f"Limitless file not found: {LIMITLESS_FILE}")
        return texts

    try:
        with open(LIMITLESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for entry in data:
            if 'contents' in entry:
                for content_block in entry['contents']:
                    if content_block.get('type') == 'blockquote':
                        text = content_block.get('content', '')
                        if text:
                            texts.append(text)
    except Exception as e:
        print(f"Error loading Limitless data: {e}")
    
    return texts

def load_line_data():
    texts = []
    if not os.path.exists(LINE_DIR):
        print(f"LINE directory not found: {LINE_DIR}")
        return texts
    
    line_files = glob.glob(os.path.join(LINE_DIR, '*.txt'))
    print(f"Found {len(line_files)} LINE files.")

    # Target speakers
    target_speakers = ['聖', '福井']

    for file_path in line_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                # Simple tab separated parsing based on sample:
                # Time [TAB] Speaker [TAB] Message
                # But sample had Date first sometimes, or different formats. 
                # Sample: "18:03	聖 (福井)	ありがとう"
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                     # Check if speaker matches one of our targets
                    speaker = parts[1]
                    message = parts[2]
                    
                    if any(target in speaker for target in target_speakers):
                         # Remove [スタンプ], [写真] etc if we want pure text, but keeping them counts as "content".
                         # Plan said analyze raw data, but maybe ignore system messages?
                         # Let's keep them but maybe the tokenizer filters them out via stop words if needed.
                         # The sample 'analyze_text' filters "スタンプ" and "写真".
                         texts.append(message)

        except Exception as e:
            print(f"Error reading LINE file {file_path}: {e}")
            
    return texts

def main():
    output = []
    output.append("Starting Chat Data Analysis...")
    
    # 1. Limitless
    limitless_texts = load_limitless_data()
    
    # Capture analysis output
    # We need to modify analyze_text to return string or append to list
    # For simplicity, let's just rewrite analyze_text in this block to append to our list
    
    def analyze_and_log(texts, label):
        entry = []
        if not texts:
            entry.append(f"[{label}] No data found.")
            return "\n".join(entry)

        entry.append(f"\n--- {label} Analysis ---")
        entry.append(f"Total messages: {len(texts)}")

        # Average Context Length
        total_length = sum(len(text) for text in texts)
        avg_length = total_length / len(texts) if texts else 0
        entry.append(f"Average Context Length (chars): {avg_length:.2f}")

        # Frequent Words
        tokenizer = Tokenizer()
        word_counts = Counter()
        
        # Common stop words
        stop_words = {'する', 'いる', 'ある', 'ない', 'なる', 'れる', 'の', 'こと', 'よう', 'それ', 'これ', 'ん', '私', '俺', '僕', '今日', '明日', '昨日', '笑', 'スタンプ', '写真', '動画', '送信', '取り消し', 'メッセージ'}

        for text in texts:
            try:
                tokens = tokenizer.tokenize(text)
                for token in tokens:
                    part_of_speech = token.part_of_speech.split(',')[0]
                    if part_of_speech in ['名詞', '動詞', '形容詞']:
                        base_form = token.base_form
                        if base_form not in stop_words and len(base_form) > 1:
                             word_counts[base_form] += 1
            except:
                continue

        entry.append("Top 20 Frequent Words:")
        for word, count in word_counts.most_common(20):
            entry.append(f"{word}: {count}")
        
        return "\n".join(entry)

    output.append(analyze_and_log(limitless_texts, "Limitless"))
    
    # 2. LINE
    line_texts = load_line_data()
    output.append(analyze_and_log(line_texts, "LINE"))
    
    final_report = "\n".join(output)
    print(final_report)
    
    # Write to file with explicit encoding
    with open('report.txt', 'w', encoding='utf-8') as f:
        f.write(final_report)

if __name__ == "__main__":
    main()
