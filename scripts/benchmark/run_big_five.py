
import json
import argparse
from eval_agent import EvalAgent

# Load Questions
QUESTIONS_FILE = 'scripts/benchmark/big_five_questions.json'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--exclude', nargs='*', help='Prompt sections to exclude')
    args = parser.parse_args()

    agent = EvalAgent(excluded_sections=args.exclude)

    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    results = []
    print(f"Running Big Five Benchmark on {len(questions)} items...")

    for i, q in enumerate(questions):
        # q is the question string
        question_text = q
        
        user_message = f"""
質問: {question_text}

以下の選択肢から、最も当てはまるものを一つ選び、その回答のみを出力してください。余計な説明は不要です。
選択肢:
- そう思う
- 少しそう思う
- どちらともいえない
- あまりそう思わない
- そう思わない
"""
        response = agent.query(user_message).strip()
        
        # Clean up response (sometimes models add punctuation or "回答: ")
        cleaned_response = response
        for opt in ['そう思う', '少しそう思う', 'どちらともいえない', 'あまりそう思わない', 'そう思わない']:
            if opt in response:
                cleaned_response = opt
                break
        
        results.append({
            "id": i + 1,
            "question": question_text,
            "response": cleaned_response,
            "raw_response": response
        })
        print(f"[{i+1}/{len(questions)}] {question_text[:10]}... -> {cleaned_response}")

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"Finished Big Five. Saved to {args.output}")

if __name__ == "__main__":
    main()
