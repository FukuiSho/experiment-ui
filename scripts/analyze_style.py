import glob
import os
import re

# Paths
LINE_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\LINE'
PCMEMO_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\pcmemo'
SMARTPHONE_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\smartphonememo'
TWITTER_DIR = r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\twitter\twitter-2026-01-08-95f677e853949e327feafbf89366958e71da549ad60c88c34b6e0b17bb799ec2'

def load_line_data():
    texts = []
    if not os.path.exists(LINE_DIR): return texts
    line_files = glob.glob(os.path.join(LINE_DIR, '*.txt'))
    target_speakers = ['聖', '福井']
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
                        if len(message) > 5 and "http" not in message: # Filter simple replies
                            texts.append(message)
        except: continue
    return texts

def load_memo_data(directory):
    texts = []
    if not os.path.exists(directory): return texts
    files = glob.glob(os.path.join(directory, '*'))
    for file_path in files:
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Split by newline, filtering empty or short
                    for line in content.split('\n'):
                        if len(line.strip()) > 10:
                            texts.append(line.strip())
            except: continue
    return texts

def analyze_style(line_texts, memo_texts):
    print("# Output Style Analysis")
    
    # 1. Feature: Sentence Endings (Gobi)
    print("\n## 1. Sentence Endings (Gobi)")
    def count_endings(texts, label):
        endings = {}
        target_endings = ['だ', 'である', 'ます', 'です', 'ね', 'よ', 'な', 'ねん', 'やん', 'た', 'る', 'ない']
        total = 0
        for t in texts:
            total += 1
            for end in target_endings:
                if t.endswith(end) or t.endswith(end + "笑") or t.endswith(end + "！") or t.endswith(end + "？"):
                     endings[end] = endings.get(end, 0) + 1
        
        print(f"### {label} (Total: {total})")
        sorted_ends = sorted(endings.items(), key=lambda x:x[1], reverse=True)
        for e, c in sorted_ends[:5]:
            ratio = (c / total) * 100
            print(f"- ...{e}: {ratio:.1f}%")

    count_endings(line_texts, "LINE (Conversational)")
    count_endings(memo_texts, "Memo (Thought/Writing)")

    # 2. Feature: Pronouns (First Person)
    print("\n## 2. First Person Pronouns")
    def count_pronouns(texts, label):
        pronouns = {'私': 0, '僕': 0, '俺': 0, 'オレ': 0, '自分': 0}
        total_hits = 0
        for t in texts:
            for p in pronouns:
                if p in t:
                    pronouns[p] += 1
                    total_hits += 1
        
        print(f"### {label}")
        if total_hits == 0:
            print("No data.")
            return

        for p, c in pronouns.items():
            if c > 0:
                print(f"- {p}: {c} times")

    count_pronouns(line_texts, "LINE")
    count_pronouns(memo_texts, "Memo")

    # 3. Tone / Nuance Indicators
    print("\n## 3. Other Style Indicators")
    # Kansai Dialect
    kansai_cues = ['やん', 'せや', 'ちゃう', 'ほんま', 'ねん']
    kansai_count_line = sum(1 for t in line_texts if any(k in t for k in kansai_cues))
    kansai_count_memo = sum(1 for t in memo_texts if any(k in t for k in kansai_cues))
    
    print(f"- Kansai Dialect Ratio (LINE): {(kansai_count_line/len(line_texts)*100 if line_texts else 0):.1f}%")
    print(f"- Kansai Dialect Ratio (Memo): {(kansai_count_memo/len(memo_texts)*100 if memo_texts else 0):.1f}%")
    
    # "Like" / "Laugh" markers
    laugh_markers = ['笑', 'w', 'ｗ']
    laugh_count = sum(1 for t in line_texts if any(k in t for k in laugh_markers))
    print(f"- Laugh Marker Usage (LINE): {(laugh_count/len(line_texts)*100 if line_texts else 0):.1f}%")

def main():
    line_texts = load_line_data()
    # Combine memo sources
    memo_texts = load_memo_data(PCMEMO_DIR) + load_memo_data(SMARTPHONE_DIR) + load_memo_data(TWITTER_DIR)
    
    analyze_style(line_texts, memo_texts)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    main()
