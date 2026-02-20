import json
import os
from Levenshtein import ratio
import ollama
import numpy as np
import argparse
from eval_agent import EvalAgent


INPUT_FILE = os.path.join(os.path.dirname(__file__), '../../benchmark_final_100.jsonl')
EMBED_MODEL = "nomic-embed-text" 

def get_embedding(text):
    try:
        return ollama.embeddings(model=EMBED_MODEL, prompt=text)['embedding']
    except Exception as e:
        print(f"Embedding error: {e}")
        return []

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0.0
    v1 = np.array(v1)
    v2 = np.array(v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0: return 0.0
    return np.dot(v1, v2) / (norm1 * norm2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--exclude', nargs='*', help='Prompt sections to exclude')
    args = parser.parse_args()

    agent = EvalAgent(excluded_sections=args.exclude)
    
    results = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    print(f"Running 100-item benchmark on {len(lines)} items...")
    
    total_text_sim = 0
    total_sem_sim = 0
    
    for i, line in enumerate(lines):
        item = json.loads(line)
        query = item['query']
        expected = item['expected_response']
        
        # Generator
        generated = agent.query(query)
        
        # Metrics
        text_sim = ratio(generated, expected)
        
        emb_gen = get_embedding(generated)
        emb_exp = get_embedding(expected)
        sem_sim = cosine_similarity(emb_gen, emb_exp)
        
        total_text_sim += text_sim
        total_sem_sim += sem_sim
        
        results.append({
            "id": item['id'],
            "query": query,
            "expected": expected,
            "generated": generated,
            "text_similarity": text_sim,
            "semantic_similarity": sem_sim
        })
        
        print(f"[{i+1}/{len(lines)}] TSim: {text_sim:.2f}, SSim: {sem_sim:.2f}")

    avg_text = total_text_sim / len(lines) if lines else 0
    avg_sem = total_sem_sim / len(lines) if lines else 0
    
    final_output = {
        "config": {
            "excluded_sections": args.exclude
        },
        "metrics": {
            "average_text_similarity": avg_text,
            "average_semantic_similarity": avg_sem
        },
        "details": results
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"Finished. Avg Text Sim: {avg_text:.3f}, Avg Semantic Sim: {avg_sem:.3f}")

if __name__ == "__main__":
    main()
