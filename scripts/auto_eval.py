
import os
import subprocess
import json
import time
import pandas as pd

# Paths
RESULTS_DIR = "results/evaluation"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Experiment Configurations

# 1. Data Ablation Patterns (Source Level)
DATA_ABLATION_PATTERNS = {
    "No-LINE": "*LINE*",
    "No-Limitless": "limitless*", # Prefix match mostly
    "No-PhotoText": ["*photo*", "*ocr*"], # Special handling for multiple? ingest supports 1 pattern var currently. Let's use simple CSV or handle in loop. 
    # The ingest script uses .includes(). We can pass a comma separated string maybe? Or just run it differently.
    # To keep it simple, let's stick to single string pattern support in this version, or update ingest to regex.
    # Updated ingest supports single string. 
    # Let's map strict keywords that distinguish files.
    # PhotoText seems to be files with 'photo' in name based on my `find` earlier.
    "No-GPT": "gpt_",
    "No-Twitter": "twitter"
}
# Note: For No-PhotoText, if we have multiple keywords, we might need a hack. 
# But 'photo' seemed to cover 'phototext' files if named appropriately. 
# 'ocr' was not found in filenames in previous step.

# 2. Prompt Ablation Patterns (Section Level)
# Keys must match `eval_agent.py` PROMPT_PARTS keys
PROMPT_ABLATION_PATTERNS = {
    "No-BasicRules": ["basic_rules"],
    "No-CorePhilosophy": ["core_philosophy"],
    "No-ThinkingTraits": ["thinking_traits"],
    "No-ComplexRelations": ["complex_relations"],
    "No-LanguageStyle": ["language_style"]
}


def run_command(command, env=None):
    print(f"Running: {command} (Env: {env})")
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    
    # Stream output to console
    process = subprocess.run(command, shell=True, env=full_env)
    if process.returncode != 0:
        print(f"Error: Command failed with code {process.returncode}")
    return ""

def run_experiment(exp_name, data_exclusion=None, prompt_exclusion=None):
    print(f"\n=== Starting Experiment: {exp_name} ===")
    start_time = time.time()
    
    # 1. Data Setup
    # Global state to track current database content
    global CURRENT_DATA_STATE
    
    # Determine requirements
    target_data_state = "FULL"
    exclusion_env = {"RESET_COLLECTION": "true"}
    
    if data_exclusion:
        # Handle list or string
        if isinstance(data_exclusion, list):
            pat = ",".join(data_exclusion)
        else:
            pat = data_exclusion
            
        target_data_state = pat
        exclusion_env["EXCLUDE_PATTERN"] = pat
    
    # Check if we need to re-ingest
    if "CURRENT_DATA_STATE" not in globals():
        CURRENT_DATA_STATE = None

    if CURRENT_DATA_STATE != target_data_state:
        print(f"State Change Detected: {CURRENT_DATA_STATE} -> {target_data_state}")
        print("Regenerating ChromaDB...")
        # Using relative path assuming running from repo root
        ingest_cmd = "python scripts/ingest_chroma.py"
        run_command(ingest_cmd, env=exclusion_env)
        CURRENT_DATA_STATE = target_data_state
    else:
        print("Data state matches current DB. Skipping ingestion.")
    
    # Setup prompt args
    prompt_args = ""
    if prompt_exclusion:
        prompt_args = "--exclude " + " ".join(prompt_exclusion)

    # 2. Run 100-Item Benchmark
    res_100_path = os.path.join(RESULTS_DIR, f"{exp_name}_100.json")
    if os.path.exists(res_100_path):
        print(f"Skipping 100-Item Benchmark (Found {res_100_path})...")
    else:
        print("Running 100-Item Benchmark...")
        cmd_100 = f"python scripts/benchmark/run_100_eval.py --output {res_100_path} {prompt_args}"
        run_command(cmd_100)
    
    # 3. Run Big Five
    print("Running Big Five...")
    res_bf_path = os.path.join(RESULTS_DIR, f"{exp_name}_big_five.json")
    # Always run Big Five or check if exists? User wants to run it. 
    # Let's check for robustness but user said data is missing so it will run.
    if os.path.exists(res_bf_path):
         print(f"Big Five result already exists at {res_bf_path}, overwriting as requested...")
    
    cmd_bf = f"python scripts/benchmark/run_big_five.py --output {res_bf_path} {prompt_args}"
    run_command(cmd_bf)
    
    print(f"Experiment {exp_name} finished in {time.time() - start_time:.1f}s")
    return res_100_path, res_bf_path

def main():
    summary_data = []

    # --- Phase 1: Data Ablation ---
    print("Starting Phase 1: Data Ablation")
    for name, pattern in DATA_ABLATION_PATTERNS.items():
        res100, resbf = run_experiment(name, data_exclusion=pattern)
        
        # Load results to summarize
        try:
            with open(res100, 'r', encoding='utf-8') as f:
                d100 = json.load(f)
            # Big Five summary requires parsing (maybe calculate distribution here?)
            # For now just metrics
            summary_data.append({
                "Experiment": name,
                "Type": "Data Ablation",
                "Text Similarity": d100['metrics']['average_text_similarity'],
                "Semantic Similarity": d100['metrics']['average_semantic_similarity'],
                "Details": f"Excluded Data: {pattern}"
            })
        except:
            print(f"Failed to load results for {name}")

    # --- Phase 2: Prompt Ablation ---
    print("Starting Phase 2: Prompt Ablation")
    # run_experiment will handle restoring Full Data automatically
    
    for name, sections in PROMPT_ABLATION_PATTERNS.items():
        # No data exclusion, just prompt exclusion
        res100, resbf = run_experiment(name, data_exclusion=None, prompt_exclusion=sections)
        
        try:
            with open(res100, 'r', encoding='utf-8') as f:
                d100 = json.load(f)
            summary_data.append({
                "Experiment": name,
                "Type": "Prompt Ablation",
                "Text Similarity": d100['metrics']['average_text_similarity'],
                "Semantic Similarity": d100['metrics']['average_semantic_similarity'],
                "Details": f"Excluded Prompt: {sections}"
            })
        except:
            print(f"Failed to load results for {name}")

    # Generate Summary Report
    df = pd.DataFrame(summary_data)
    csv_path = os.path.join(RESULTS_DIR, "final_summary.csv")
    df.to_csv(csv_path, index=False)
    
    print("\n=== All Evaluation Completed ===")
    print(df)
    print(f"Summary saved to {csv_path}")

if __name__ == "__main__":
    main()
