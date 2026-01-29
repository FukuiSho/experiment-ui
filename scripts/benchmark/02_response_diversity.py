import json
import os
import sys
import numpy as np
import ollama
from typing import List

# Fix path to import clone_agentAI
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/cloneai'))
from clone_agentAI import AIPersonaAgent, create_yamada_taro_persona, check_ollama_available

# Configuration
INPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\01_syntax_filtered.jsonl'
OUTPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\02_diversity_filtered.jsonl'
MODEL_NAME = "gemma2:2b" # Use a lighter model for speed if possible, or same as agent
# Using gemma2:2b for fast diversity check might be better than 27b if available
# But let's stick to what's available. The agent uses 'gemma3:27b' by default.
# I'll check available models later. For now default to what agent uses.

NUM_GENERATIONS = 3
DIVERSITY_THRESHOLD = 0.1 # Cosine distance threshold. If avg distance < 0.1, drop it.
LIMIT_ITEMS = 50 # For testing/demo purposes, process only 50 items. remove later.

def get_embedding(text: str, model: str = "gemma2:2b") -> List[float]:
    try:
        # Check if model exists, if not use a fallback or fail
        # For speed, using a small embedding model is better.
        # But ollama.embeddings requires a model that supports it.
        # mxbai-embed-large is good if installed.
        res = ollama.embeddings(model=model, prompt=text)
        return res['embedding']
    except Exception as e:
        # fallback to gemma3:27b if strict
        try:
            res = ollama.embeddings(model="gemma3:27b", prompt=text)
            return res['embedding']
        except:
            print(f"Embedding error: {e}")
            return []

def cosine_distance(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    similarity = np.dot(v1, v2) / (norm1 * norm2)
    return 1.0 - similarity

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found")
        return

    # Initialize Agent
    persona = create_yamada_taro_persona()
    # Check what models are available. For now assuming default.
    # We use simulation mode if Ollama not available, but real mode is needed for meaningful benchmark
    agent = AIPersonaAgent(persona, model_name="gemma3:27b", simulation_mode=False) 
    
    # Override client model for speed if needed? No, use the main one.
    
    results = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Limit for execution speed in this turn
    process_lines = lines[:LIMIT_ITEMS]
    print(f"Processing {len(process_lines)} items (Total available: {len(lines)})")
    
    passed_count = 0
    
    embed_model = "mxbai-embed-large" # Try this first
    # Check if we can list models to pick embedding model?
    # subprocess.run(['ollama', 'list'])? 
    # Just try-except in get_embedding.
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        for i, line in enumerate(process_lines):
            try:
                data = json.loads(line)
                query = data['query']
                
                print(f"[{i+1}/{len(process_lines)}] Processing: {query[:30]}...")
                
                responses = []
                for _ in range(NUM_GENERATIONS):
                    # Reset conversation for each generation to ensure independence?
                    # Or keep history? Usually benchmark generation is "Single Turn" or "Single Turn with same context".
                    # Here we treat it as single turn query.
                    agent.reset_conversation() 
                    resp = agent.process_input(query)
                    responses.append(resp)
                
                # Calculate Diversity
                embeddings = [get_embedding(r, model="gemma3:27b") for r in responses]
                embeddings = [e for e in embeddings if e] # valid only
                
                if len(embeddings) < 2:
                    avg_dist = 0.0
                else:
                    distances = []
                    for k in range(len(embeddings)):
                        for l in range(k+1, len(embeddings)):
                            dist = cosine_distance(embeddings[k], embeddings[l])
                            distances.append(dist)
                    avg_dist = sum(distances) / len(distances)
                
                print(f"  > Avg Dist: {avg_dist:.4f}")
                
                if avg_dist >= DIVERSITY_THRESHOLD:
                    data['diversity_score'] = avg_dist
                    fout.write(json.dumps(data, ensure_ascii=False) + '\n')
                    passed_count += 1
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error processing item {i}: {e}")

    print(f"=== Phase 1.2: Diversity Filter Results ===")
    print(f"Input: {len(process_lines)}")
    print(f"Passed: {passed_count}")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
