import os
import json
from pathlib import Path

TARGET_DIR = r"C:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata"

def analyze_folder(folder_path):
    stats = {
        "files": 0,
        "extensions": {},
        "samples": {}
    }
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            stats["files"] += 1
            ext = Path(file).suffix.lower()
            
            if ext not in stats["extensions"]:
                stats["extensions"][ext] = 0
                stats["samples"][ext] = []
            
            stats["extensions"][ext] += 1
            
            # Keep up to 3 samples per extension
            if len(stats["samples"][ext]) < 3:
                stats["samples"][ext].append(file)

    return stats

def main():
    if not os.path.exists(TARGET_DIR):
        print(f"Directory not found: {TARGET_DIR}")
        return

    output_file = "scripts/analyze_unlabeldata_detailed_output.txt"
    print(f"Analyzing structure of {TARGET_DIR}...")
    print(f"Writing results to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        subdirs = [d for d in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, d))]
        
        for subdir in subdirs:
            subdir_path = os.path.join(TARGET_DIR, subdir)
            f.write(f"### 📁 {subdir}\n")
            stats = analyze_folder(subdir_path)
            
            f.write(f"  - Total Files: {stats['files']}\n")
            if stats['files'] == 0:
                 f.write("  - (Empty Folder)\n")
            else:
                sorted_exts = sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True)
                for ext, count in sorted_exts:
                    samples = ", ".join(stats['samples'][ext])
                    f.write(f"  - {ext}: {count} files (e.g., {samples})\n")
            f.write("\n")
    
    print("Done.")

if __name__ == "__main__":
    main()
