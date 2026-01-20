
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random

# Configuration
INPUT_FILE = 'benchmark_results.jsonl'
OUTPUT_FILE = 'benchmark_human_eval.jsonl'

class LabelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("福井聖らしさ 評価ツール (Fukui Sho-ness Evaluator)")
        self.root.geometry("800x600")

        self.data_items = []
        self.current_index = 0
        self.evaluated_ids = set()

        # Load Data
        self.load_data()
        
        # Shuffle Data
        random.shuffle(self.data_items)

        # UI Setup
        self.setup_ui()
        
        # Display first item
        self.show_current_item()

    def load_data(self):
        # Load processed IDs
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        self.evaluated_ids.add(data['id'])
                    except:
                        pass
        
        # Load benchmark results
        if os.path.exists(INPUT_FILE):
            with open(INPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data['id'] not in self.evaluated_ids:
                            self.data_items.append(data)
                    except:
                        pass
        else:
            messagebox.showerror("Error", f"{INPUT_FILE} NOT FOUND")
            self.root.destroy()
            return

        print(f"Loaded {len(self.data_items)} items remaining to evaluate.")

    def setup_ui(self):
        # Styles
        style = ttk.Style()
        style.configure("TLabel", font=("Meiryo", 10))
        style.configure("TButton", font=("Meiryo", 10))

        # Progress
        self.progress_var = tk.StringVar()
        lbl_progress = ttk.Label(self.root, textvariable=self.progress_var, font=("Meiryo", 10, "bold"))
        lbl_progress.pack(pady=5)

        # Container
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Query
        ttk.Label(container, text="[Query] (質問)", foreground="blue").pack(anchor=tk.W)
        self.txt_query = tk.Text(container, height=3, font=("Meiryo", 11), wrap=tk.WORD)
        self.txt_query.pack(fill=tk.X, pady=(0, 10))

        # Expected
        ttk.Label(container, text="[Expected] (正解データ)", foreground="green").pack(anchor=tk.W)
        self.txt_expected = tk.Text(container, height=3, font=("Meiryo", 11), wrap=tk.WORD)
        self.txt_expected.pack(fill=tk.X, pady=(0, 10))

        # Generated
        ttk.Label(container, text="[Generated] (生成結果 - 判定対象)", foreground="red").pack(anchor=tk.W)
        self.txt_generated = tk.Text(container, height=6, font=("Meiryo", 12, "bold"), wrap=tk.WORD, bg="#fff0f0")
        self.txt_generated.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Buttons
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)

        btn_yes = ttk.Button(btn_frame, text="Yes (y) - らしい", command=lambda: self.save_result(True))
        btn_yes.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        btn_no = ttk.Button(btn_frame, text="No (n) - らしくない", command=lambda: self.save_result(False))
        btn_no.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

        # Key Bindings
        self.root.bind('<y>', lambda e: self.save_result(True))
        self.root.bind('<n>', lambda e: self.save_result(False))
        self.root.bind('<Y>', lambda e: self.save_result(True))
        self.root.bind('<N>', lambda e: self.save_result(False))

    def show_current_item(self):
        if self.current_index < len(self.data_items):
            item = self.data_items[self.current_index]
            
            self.progress_var.set(f"Progress: {self.current_index + 1} / {len(self.data_items)} (Total Evaluated: {len(self.evaluated_ids)})")
            
            self.txt_query.delete("1.0", tk.END)
            self.txt_query.insert("1.0", item.get('query', ''))

            self.txt_expected.delete("1.0", tk.END)
            self.txt_expected.insert("1.0", item.get('expected_response', ''))

            self.txt_generated.delete("1.0", tk.END)
            self.txt_generated.insert("1.0", item.get('generated_response', ''))
        else:
            messagebox.showinfo("Done", "Complete! All items evaluated.")
            self.root.destroy()

    def save_result(self, is_match):
        if self.current_index < len(self.data_items):
            item = self.data_items[self.current_index]
            
            result_entry = {
                "id": item['id'],
                "query": item['query'],
                "generated_response": item['generated_response'],
                "is_persona_match": is_match,
                "timestamp": item.get('timestamp')
            }

            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result_entry, ensure_ascii=False) + '\n')
            
            self.evaluated_ids.add(item['id'])
            self.current_index += 1
            self.show_current_item()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingApp(root)
    root.mainloop()
