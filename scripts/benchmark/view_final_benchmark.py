import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

INPUT_FILE = r'C:\Users\ok220109\experiment-ui\benchmark_final_100.jsonl'

class BenchmarkViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Final Benchmark Viewer (100 items)")
        self.root.geometry("800x600")
        
        self.items = []
        self.current_idx = 0
        
        self.load_data()
        self.setup_ui()
        self.show_item()
        
    def load_data(self):
        if not os.path.exists(INPUT_FILE):
            messagebox.showerror("Error", f"{INPUT_FILE} not found")
            return
            
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    self.items.append(json.loads(line))
                except:
                    pass
        print(f"Loaded {len(self.items)} items.")

    def setup_ui(self):
        # Header
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)
        self.lbl_status = ttk.Label(header_frame, text="Item 1 / 100", font=("Meiryo", 12, "bold"))
        self.lbl_status.pack()
        
        # Content
        content_frame = ttk.Frame(self.root, padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Meta Info
        self.lbl_meta = ttk.Label(content_frame, text="", foreground="gray")
        self.lbl_meta.pack(anchor=tk.W, pady=2)
        
        # Query
        ttk.Label(content_frame, text="[Query]", font=("Meiryo", 10, "bold"), foreground="blue").pack(anchor=tk.W, pady=(5,0))
        self.txt_query = tk.Text(content_frame, height=4, font=("Meiryo", 11), wrap=tk.WORD, bg="#f5f5f5")
        self.txt_query.pack(fill=tk.X, pady=5)
        
        # Expected Response
        ttk.Label(content_frame, text="[Expected Response]", font=("Meiryo", 10, "bold"), foreground="green").pack(anchor=tk.W, pady=(10,0))
        self.txt_expected = tk.Text(content_frame, map=None, height=8, font=("Meiryo", 11), wrap=tk.WORD, bg="#f0fff0")
        self.txt_expected.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="<< Prev", command=self.prev_item).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Next >>", command=self.next_item).pack(side=tk.RIGHT, padx=10)
        
        # Bind keys
        self.root.bind('<Left>', lambda e: self.prev_item())
        self.root.bind('<Right>', lambda e: self.next_item())

    def show_item(self):
        if not self.items:
            return
            
        item = self.items[self.current_idx]
        
        # Update Status
        self.lbl_status.config(text=f"Item {self.current_idx + 1} / {len(self.items)}")
        
        # Update Meta
        cat = item.get('category', 'Unknown')
        meta = item.get('meta', {})
        score = meta.get('score', 0)
        source = meta.get('source', 'unknown')
        self.lbl_meta.config(text=f"ID: {item.get('id')} | Category: {cat} | Score: {score:.1f} | Source: {source}")
        
        # Update Text
        self.txt_query.delete("1.0", tk.END)
        self.txt_query.insert("1.0", item.get('query', ''))
        
        self.txt_expected.delete("1.0", tk.END)
        self.txt_expected.insert("1.0", item.get('expected_response', ''))

    def next_item(self):
        if self.current_idx < len(self.items) - 1:
            self.current_idx += 1
            self.show_item()
            
    def prev_item(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.show_item()

if __name__ == "__main__":
    root = tk.Tk()
    app = BenchmarkViewer(root)
    root.mainloop()
