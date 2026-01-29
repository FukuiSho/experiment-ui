import json
import os
import sys
import numpy as np
import ollama
import re

# Fix path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/cloneai'))
from clone_agentAI import AIPersonaAgent, create_yamada_taro_persona, PersonaTemplate

# Configuration
INPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\01_syntax_filtered.jsonl'
OUTPUT_FILE = r'C:\Users\ok220109\experiment-ui\scripts\benchmark\03_scored_candidates.jsonl'
TOP_N = 300

# Scoring Weights
W_DIVERSITY = 1.0
W_INFO = 1.0
W_PERSONA = 2.0

LIMIT_ITEMS = 10 # Process only 10 for demo

def get_embedding(text):
    try:
        return ollama.embeddings(model="gemma2:2b", prompt=text)['embedding']
    except:
        return []

def cosine_distance(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    return 1 - np.dot(v1, v2)/(n1*n2) if n1*n2 > 0 else 0

def calculate_info_score(response):
    # 1. Length Score (Sigmoid-ish: favor 50-200 chars)
    length = len(response)
    score_len = min(length / 100.0, 1.0)
    
    # 2. First Person Score
    fp_score = 0
    if re.search(r'(俺|僕|私|自分)', response):
        fp_score = 0.5
        
    # 3. Emotion/Opinion Score
    # Simple keyword match for opinionated words
    emo_score = 0
    keywords = ['思う', '感じる', '好き', '嫌い', '実は', 'やっぱり']
    if any(k in response for k in keywords):
        emo_score = 0.5
        
    return score_len + fp_score + emo_score

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"{INPUT_FILE} not found.")
        return

    # Setup Agents
    # 1. Persona Agent
    persona = create_yamada_taro_persona()
    agent_persona = AIPersonaAgent(persona, model_name="gemma3:27b", simulation_mode=False)

    # 2. Base Agent (Empty Persona)
    # Creating a dummy empty persona
    empty_persona = PersonaTemplate(name="Assistant", description="A helpful assistant.", personality="", background="", values=[])
    agent_base = AIPersonaAgent(empty_persona, model_name="gemma3:27b", simulation_mode=False)

    candidates = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    print(f"Scoring {len(lines)} candidates (Limited to {LIMIT_ITEMS})...")
    
    for i, line in enumerate(lines[:LIMIT_ITEMS]):
        try:
            data = json.loads(line)
            query = data['query']
            diversity_score = data.get('diversity_score', 0)
            
            print(f"[{i+1}/{len(lines)}] Scoring: {query[:20]}...")
            
            # Generate Responses
            # We need strictly single turn
            agent_persona.reset_conversation()
            resp_persona = agent_persona.process_input(query)
            
            agent_base.reset_conversation()
            resp_base = agent_base.process_input(query)
            
            # 1. Info Score (based on Persona Response)
            info_score = calculate_info_score(resp_persona)
            
            # 2. Persona Dependency Score (Distance between Persona and Base)
            emb_p = get_embedding(resp_persona)
            emb_b = get_embedding(resp_base)
            if emb_p and emb_b:
                persona_dep_score = cosine_distance(emb_p, emb_b)
            else:
                persona_dep_score = 0
            
            # Total Score
            total_score = (diversity_score * W_DIVERSITY) + \
                          (info_score * W_INFO) + \
                          (persona_dep_score * W_PERSONA)
            
            data['scores'] = {
                'diversity': diversity_score,
                'info': info_score,
                'persona_dep': persona_dep_score,
                'total': total_score
            }
            data['generated_response_sample'] = resp_persona # Save for human review
            
            candidates.append(data)
            
        except Exception as e:
            print(f"Error {i}: {e}")
            continue

    # Sort by Total Score
    candidates.sort(key=lambda x: x['scores']['total'], reverse=True)
    
    # Save Top N
    top_candidates = candidates[:TOP_N]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        for c in top_candidates:
            fout.write(json.dumps(c, ensure_ascii=False) + '\n')
            
    print(f"=== Phase 2 Results ===")
    print(f"Scored: {len(candidates)}")
    print(f"Selected Top: {len(top_candidates)}")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
