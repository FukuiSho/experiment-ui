import json
import os

INPUT_FILE = 'benchmark_persona_match_yes.jsonl'
OUTPUT_FILE = 'scripts/create_evaluation_form.gs'

TEMPLATE_START = """
// データ（グローバル変数）
const BENCHMARK_DATA = """

TEMPLATE_MIDDLE = """;

function createEvaluationForm() {
  // 1. フォームの新規作成
  const form = FormApp.create('福井聖の応答評価テスト');
  form.setDescription('以下の発言（Query）に対して、どちらが「福井聖」らしい応答かを選択してください。');
  // テスト（クイズ）モードにする
  form.setIsQuiz(true);

  // フォームIDを保存（集計時に使用）
  PropertiesService.getScriptProperties().setProperty('TARGET_FORM_ID', form.getId());

  BENCHMARK_DATA.forEach((item, index) => {
    // 質問セクションの作成
    const itemTitle = `Q${index + 1}. 問い: 「${item.query}」`;
    const mcItem = form.addMultipleChoiceItem();
    
    // ランダムに配置するために選択肢をシャッフル
    const choices = [
      { type: 'generated', value: item.generated_response },
      { type: 'expected', value: item.expected_response } // will be marked as correct
    ];
    // Fisher-Yates shuffle
    for (let i = choices.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [choices[i], choices[j]] = [choices[j], choices[i]];
    }

    // 選択肢の作成（正解を設定）
    const choiceObjects = choices.map(c => {
      // typeが 'expected' (正解応答) なら正解とする
      return mcItem.createChoice(c.value, c.type === 'expected');
    });

    mcItem.setTitle(itemTitle)
          //.setHelpText(`データID: ${item.id}`) // IDは削除
          .setChoices(choiceObjects)
          .setRequired(true);
  });

  console.log('フォーム作成が完了しました。');
  console.log('編集用URL: ' + form.getEditUrl());
  console.log('公開用URL: ' + form.getPublishedUrl());
  console.log('★重要: ID: ' + form.getId() + ' が保存されました。集計時に使用します。');
}

function analyzeResults() {
  // 保存されたフォームIDを取得
  const formId = PropertiesService.getScriptProperties().getProperty('TARGET_FORM_ID');
  if (!formId) {
    console.error('フォームIDが見つかりません。先に createEvaluationForm を実行してください。');
    return;
  }
  
  const form = FormApp.openById(formId);
  const formResponses = form.getResponses();
  
  let totalVotes = 0;
  let aiVotes = 0; // generated_response
  let humanVotes = 0; // expected_response
  
  console.log(`回答数: ${formResponses.length} 件の集計を開始します...`);

  // 各回答をループ
  for (let i = 0; i < formResponses.length; i++) {
    const formResponse = formResponses[i];
    const itemResponses = formResponse.getItemResponses();
    
    for (let j = 0; j < itemResponses.length; j++) {
      const itemResponse = itemResponses[j];
      const answer = itemResponse.getResponse(); // 選ばれた回答の文字列
      const questionTitle = itemResponse.getItem().getTitle(); // "Q1. 問い: ..."
      
      // 質問タイトルからインデックス(番号)を抽出
      const match = questionTitle.match(/^Q(\\d+)\\./);
      if (match) {
        const index = parseInt(match[1], 10) - 1;
        const dataItem = BENCHMARK_DATA[index];
        
        if (dataItem) {
          totalVotes++;
          if (answer === dataItem.generated_response) {
            aiVotes++;
          } else if (answer === dataItem.expected_response) {
            humanVotes++;
          }
        }
      }
    }
  }
  
  const aiRate = totalVotes > 0 ? (aiVotes / totalVotes * 100).toFixed(2) : 0;
  
  console.log('--------------------------------------------------');
  console.log(`【集計結果】`);
  console.log(`総投票数: ${totalVotes}`);
  console.log(`AI応答 (Generated) が選ばれた数: ${aiVotes}`);
  console.log(`正解応答 (Expected) が選ばれた数: ${humanVotes}`);
  console.log('--------------------------------------------------');
  console.log(`★ AI応答選択率（福井聖らしさ適合率）: ${aiRate}%`);
  console.log('--------------------------------------------------');
}
"""

TEMPLATE_END = ""

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    data_list = []
    print(f"Reading from {INPUT_FILE}...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line)
                # Keep only necessary fields to keep script size manageable
                clean_item = {
                    "id": item.get("id"),
                    "query": item.get("query"),
                    "generated_response": item.get("generated_response"),
                    "expected_response": item.get("expected_response")
                }
                data_list.append(clean_item)
            except json.JSONDecodeError:
                continue

    # Serialize to JSON string with indentation for readability
    json_data = json.dumps(data_list, ensure_ascii=False, indent=4)

    # Write the full GAS script
    print(f"Generating {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(TEMPLATE_START)
        f.write(json_data)
        f.write(TEMPLATE_END)

    print("Done.")

if __name__ == "__main__":
    main()
