
import pandas as pd
import json
import os
import glob

RESULTS_DIR = "results/evaluation"
OUTPUT_FILE = "evaluation_report.md"

def main():
    report = "# Automated Evaluation Report\n\n"
    
    # 1. 100-Item Benchmark Results
    csv_path = os.path.join(RESULTS_DIR, "final_summary.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        report += "## 100-Item Benchmark Results\n\n"
        report += "This benchmark evaluates the similarity between the generated response and the expected response (ground truth) for 100 test cases.\n\n"
        
        # Manual Markdown Table
        headers = df.columns.tolist()
        report += "| " + " | ".join(headers) + " |\n"
        report += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        for _, row in df.iterrows():
            report += "| " + " | ".join(str(val) for val in row.values) + " |\n"
            
        report += "\n\n"
        
        # Best/Worst analysis
        best_text = df.loc[df['Text Similarity'].idxmax()]
        best_sem = df.loc[df['Semantic Similarity'].idxmax()]
        
        report += "### Highlights\n"
        report += f"- **Highest Text Similarity**: {best_text['Experiment']} ({best_text['Text Similarity']:.4f})\n"
        report += f"- **Highest Semantic Similarity**: {best_sem['Experiment']} ({best_sem['Semantic Similarity']:.4f})\n\n"
    else:
        report += "No 100-item benchmark results found.\n\n"

    # 2. Big Five Personality Test Results
    report += "## Big Five Personality Test Results\n\n"
    report += "The Big Five test consists of 117 questions. We analyze the consistency of responses across the Likert scale.\n\n"
    
    json_files = glob.glob(os.path.join(RESULTS_DIR, "*_big_five.json"))
    if json_files:
        for json_file in json_files:
            exp_name = os.path.basename(json_file).replace("_big_five.json", "")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check format
                if isinstance(data, list):
                    responses = [item.get('response', '') for item in data]
                    # Count distribution
                    dist = pd.Series(responses).value_counts().reindex(
                        ['そう思う', '少しそう思う', 'どちらともいえない', 'あまりそう思わない', 'そう思わない'], 
                        fill_value=0
                    )
                    
                    report += f"### {exp_name}\n"
                    report += f"Total Responses: {len(data)}\n\n"
                    report += "| Response | Count | Percentage |\n"
                    report += "| :--- | :--- | :--- |\n"
                    for label, count in dist.items():
                        report += f"| {label} | {count} | {count/len(data)*100:.1f}% |\n"
                    report += "\n"
                else:
                    report += f"### {exp_name}\nInvalid data format.\n\n"
            except Exception as e:
                report += f"### {exp_name}\nError loading data: {e}\n\n"
    else:
        report += "No Big Five test results found.\n"

    # Save
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
