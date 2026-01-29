import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Configuration
INPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\03_scored_candidates.jsonl'
OUTPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\04_final_selection.jsonl'

class ReviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Benchmark Candidate Reviewer (300 -> 100)")
        self.root.geometry("1000x800")
        
        self.data_items = []
        self.current_index = 0
        self.selected_count = 0
        
        self.load_data()
        self.setup_ui()
        self.show_current_item()
        
    def load_data(self):
        if not os.path.exists(INPUT_FILE):
            messagebox.showerror("Error", f"{INPUT_FILE} not found!")
            self.root.destroy()
            return

        if os.path.getsize(INPUT_FILE) == 0:
            print(f"Warning: {INPUT_FILE} is empty.")
            return

        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    self.data_items.append(json.loads(line))
                except:
                    pass
        print(f"Loaded {len(self.data_items)} candidates.")
        
        # Check existing
        if os.path.exists(OUTPUT_FILE):
             with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    self.selected_count += 1

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top Info
        self.lbl_info = ttk.Label(main_frame, text="", font=("Meiryo", 12))
        self.lbl_info.pack(pady=5)
        
        # Scores
        self.lbl_scores = ttk.Label(main_frame, text="", font=("Meiryo", 10), foreground="blue")
        self.lbl_scores.pack(pady=5)
        
        # Query
        ttk.Label(main_frame, text="Query (質問):", font=("Meiryo", 10, "bold")).pack(anchor=tk.W)
        self.txt_query = tk.Text(main_frame, height=3, font=("Meiryo", 12), wrap=tk.WORD)
        self.txt_query.pack(fill=tk.X, pady=5)
        
        # Sample Response
        ttk.Label(main_frame, text="Sample Response (回答例):", font=("Meiryo", 10, "bold")).pack(anchor=tk.W)
        self.txt_response = tk.Text(main_frame, height=10, font=("Meiryo", 11), wrap=tk.WORD, bg="#f0f8ff")
        self.txt_response.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="KEEP (残す)", command=lambda: self.save_result(True)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(btn_frame, text="DISCARD (捨てる)", command=lambda: self.save_result(False)).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Key bindings
        self.root.bind('y', lambda e: self.save_result(True))
        self.root.bind('n', lambda e: self.save_result(False))

    def show_current_item(self):
        if self.current_index < len(self.data_items):
            item = self.data_items[self.current_index]
            
            self.lbl_info.config(text=f"Progress: {self.current_index + 1}/{len(self.data_items)} | Selected: {self.selected_count}")
            
            scores = item.get('scores', {})
            score_text = f"Total: {scores.get('total', 0):.2f} | Diversity: {scores.get('diversity', 0):.2f} | Info: {scores.get('info', 0):.2f} | Persona: {scores.get('persona_dep', 0):.2f}"
            self.lbl_scores.config(text=score_text)
            
            self.txt_query.delete("1.0", tk.END)
            self.txt_query.insert("1.0", item.get('query', ''))
            
            self.txt_response.delete("1.0", tk.END)
            # Use 'generated_response_sample' if available, otherwise 'generated_response'
            resp = item.get('generated_response_sample') or item.get('generated_response', '')
            self.txt_response.insert("1.0", resp)
            
        else:
            messagebox.showinfo("Done", f"Review Complete! Selected {self.selected_count} items.")
            self.root.destroy()

    def save_result(self, keep):
        if self.current_index < len(self.data_items):
            if keep:
                item = self.data_items[self.current_index]
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                self.selected_count += 1
            
            self.current_index += 1
            self.show_current_item()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReviewApp(root)
    root.mainloop()
