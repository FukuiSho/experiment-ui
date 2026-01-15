import os
import glob
import re
from janome.tokenizer import Tokenizer
from collections import Counter

# Paths to data directories
PCMEMO_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\pcmemo'
SMARTPHONE_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\smartphonememo'
TWITTER_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\twitter\twitter-2026-01-08-95f677e853949e327feafbf89366958e71da549ad60c88c34b6e0b17bb799ec2'

OUTPUT_DOC = r'c:\Users\ok220109\experiment-ui\personal_philosophy_analysis.md'

def load_text_files(directory, is_twitter=False):
    texts = []
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return texts
    
    # Twitter data might be JS/JSON or MD files, but user said 'data' in that specific folder
    # Assuming text files or markdown for now based on 'dir' output showing files exist
    # If Twitter is JS file (window.YTD.tweet.part0 = ...), we need to parse it.
    
    files = glob.glob(os.path.join(directory, '*'))
    for file_path in files:
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    if is_twitter and file_path.endswith('.js'):
                        # Very basic extraction of "full_text" from Twitter JS export
                        # tweet.js usually contains: window.YTD.tweet.part0 = [ ... ]
                        matches = re.findall(r'"full_text" : "(.*?)"', content, re.DOTALL)
                        for m in matches:
                            # Unescape unicode
                            try:
                                decoded = m.encode('utf-8').decode('unicode_escape')
                                texts.append(decoded)
                            except:
                                texts.append(m)
                    else:
                        texts.append(content)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    return texts

def analyze_philosophy(all_texts):
    # Keywords indicating philosophy/values
    # Note: This is a heuristic.
    value_keywords = [
        "べき", "重要", "大切", "価値", "意味", "目的", "理由", "思う", "考える", "必要", 
        "したい", "なりたい", "嫌だ", "許せない", "好き", "楽しい", "幸せ", "人生", "社会", 
        "仕事", "人間", "自分", "世界", "未来"
    ]
    
    extracted_sentences = []
    
    for text in all_texts:
        # Split into sentences roughly
        sentences = re.split(r'[。\n]', text)
        for s in sentences:
            s = s.strip()
            if len(s) < 10: continue
            
            # Check for keywords
            score = sum(1 for k in value_keywords if k in s)
            if score >= 1:
                extracted_sentences.append((score, s))
                
    # Sort by "value density" (heuristic)
    extracted_sentences.sort(key=lambda x: x[0], reverse=True)
    
    return [s[1] for s in extracted_sentences[:100]] # Return top 100 relevant sentences

def main():
    print("Loading data...")
    pc_texts = load_text_files(PCMEMO_DIR)
    phone_texts = load_text_files(SMARTPHONE_DIR)
    twitter_texts = load_text_files(TWITTER_DIR, is_twitter=True)
    
    all_texts = pc_texts + phone_texts + twitter_texts
    print(f"Total raw text sources: {len(all_texts)}")
    
    print("Analyzing for philosophy and values...")
    sentences = analyze_philosophy(all_texts)
    
    # Generate Markdown Report
    with open(OUTPUT_DOC, 'w', encoding='utf-8') as f:
        f.write("# 個人の思想・価値観・判断軸の分析レポート\n\n")
        f.write("以下の分析は、PCメモ、スマートフォンメモ、Twitterデータから抽出された発言に基づいています。\n\n")
        
        f.write("## 抽出された主要な価値観・思想を示す文\n")
        for s in sentences:
             # Basic Markdown list
             f.write(f"- {s}\n")
             
    print(f"Analysis saved to: {OUTPUT_DOC}")
    # Also print to console for immediate context
    for s in sentences[:20]:
        print(s)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    main()
