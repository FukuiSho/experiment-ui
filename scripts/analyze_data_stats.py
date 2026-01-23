import os
import json
from pathlib import Path

TARGET_DIR = r"C:\Users\ok220109\experiment-ui\src\lib\pesonaldata"

def analyze_directory(directory):
    stats = {
        "files": 0,
        "size": 0,
        "lines": 0,
        "file_types": {}
    }
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            stats["files"] += 1
            try:
                size = os.path.getsize(file_path)
                stats["size"] += size
                
                ext = file_path.suffix.lower()
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                
                # Count lines for text files
                if ext in ['.txt', '.json', '.jsonl', '.csv', '.md', '.js', '.ts']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            stats["lines"] += sum(1 for _ in f)
                    except Exception:
                        pass
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return stats

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:3.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def main():
    if not os.path.exists(TARGET_DIR):
        print(f"Directory not found: {TARGET_DIR}")
        return

    print(f"Analyzing {TARGET_DIR}...\n")
    
    # Analyze top level subdirectories
    subdirs = [d for d in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, d))]
    
    total_stats = {"files": 0, "size": 0, "lines": 0}
    
    for subdir in subdirs:
        subdir_path = os.path.join(TARGET_DIR, subdir)
        print(f"--- FOLDER: {subdir} ---")
        stats = analyze_directory(subdir_path)
        
        print(f"  Files: {stats['files']}")
        print(f"  Size: {format_size(stats['size'])}")
        print(f"  Lines (approx): {stats['lines']:,}")
        print(f"  File Types: {json.dumps(stats['file_types'], ensure_ascii=False)}")
        print("")
        
        total_stats["files"] += stats["files"]
        total_stats["size"] += stats["size"]
        total_stats["lines"] += stats["lines"]

    print("--- TOTAL SUMMARY ---")
    print(f"  Total Files: {total_stats['files']}")
    print(f"  Total Size: {format_size(total_stats['size'])}")
    print(f"  Total Lines: {total_stats['lines']:,}")

if __name__ == "__main__":
    main()
