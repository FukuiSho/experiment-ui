import tkinter as tk
from tkinter import ttk, messagebox, filedialog  # filedialogを追加
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AIParameterTuner:
    def __init__(self, root):
        self.root = root
        self.root.title("AIパラメーターチューナー")
        self.root.geometry("800x600")
        
        # 質問と選択肢を定義
        self.questions = [
            # 基本的な特性に関する質問
            "1. あなたは新しいアイデアや意外性のある発想を好みますか？",
            "2. あなたは会話や文章において、どの程度の多様な表現を好みますか？",
            "3. あなたは同じ内容の繰り返しにどの程度敏感ですか？",
            
            # Temperature調整のための質問
            "4. あなたは会話において、どの程度の予測不可能性や冒険的な回答を望みますか？",
            "5. あなたは創造的な文章よりも事実に基づいた正確な情報を重視しますか？",
            
            # 創造性と予測可能性に関する質問（temperature調整用）
            "6. あなたは新しいアイデアや発想を好みますか？",
            "7. 会話の中で予測できない展開や意外性を楽しいと感じますか？",
            "8. あなたは決まった回答よりも多様な回答を好みますか？",
            
            # 文脈理解の深さに関する質問（num_ctx調整用）
            "9. あなたは会話の中で前後の文脈を重視しますか？",
            "10. 長い会話や複雑な話題についてどの程度詳細に記憶しておいてほしいですか？",
            
            # 繰り返しと一貫性に関する質問（repeat関連パラメーター調整用）
            "11. 会話の中で同じ表現や内容が繰り返されることをどう感じますか？",
            "12. あなたは話の一貫性をどの程度重視しますか？",
            
            # 制御性と多様性のバランスに関する質問（mirostat関連調整用）
            "13. 会話の流れがどの程度制御されていると感じると快適ですか？",
            "14. あなたは一貫した回答と多様な回答のどちらを重視しますか？",
            
            # Top_p調整のための質問
            "15. あなたは会話や文章において、どの程度の語彙の多様性を好みますか？",
            "16. あなたは質問に対して、どの程度幅広い視点からの回答を期待しますか？",
            
            # Presence/Frequency Penalty調整のための質問
            "17. あなたは会話の中で話題の広がりをどの程度重視しますか？",
            "18. あなたは文章表現において、どの程度の変化や多様性を好みますか？",
            
            # Logit_bias調整のための質問
            "19. あなたは専門用語をどの程度使いますか？",
            "20. あなたはフォーマルな表現とカジュアルな表現、どちらを好みますか？",
            "21. あなたは抽象的な概念と具体的な例え話、どちらの説明方法を好みますか？",
            
            # ユーザーの特性を把握するための追加質問
            "22. あなたは詳細な説明と簡潔な説明のどちらを好みますか？",
            "23. 新しい情報を処理する際、どの程度の速さが快適ですか？",
            "24. あなたは論理的な会話と感情的な会話のどちらを好みますか？",
            "25. 専門的な用語をどの程度使用した会話が好ましいですか？",
            "26. あなたは会話の中でどの程度の確実性を求めますか？",
            "27. 会話の中で冗談やユーモアをどの程度取り入れることを好みますか？",
            
            # ユースケースに関する質問
            "28. あなたはAIとの会話をどのような目的で主に使用しますか？",
            "29. あなたは長文と短文、どちらの回答を好みますか？",
            "30. あなたはAIの回答にどの程度の感情表現を望みますか？"
        ]
        
        self.options = [
            # 質問1の選択肢
            ["1. 全く好まない（確実で予測可能な情報を好む）", 
             "2. あまり好まない", 
             "3. どちらでもない", 
             "4. やや好む", 
             "5. 非常に好む（意外性やユニークな発想を重視する）"],
            
            # 質問2の選択肢
            ["1. 非常に一貫した表現を好む", 
             "2. どちらかといえば一貫した表現を好む", 
             "3. バランスが取れているのが良い", 
             "4. どちらかといえば多様な表現を好む", 
             "5. 非常に多様で変化に富んだ表現を好む"],
            
            # 質問3の選択肢
            ["1. 全く気にならない", 
             "2. あまり気にならない", 
             "3. どちらでもない", 
             "4. やや気になる", 
             "5. 非常に気になる（繰り返しは極力避けてほしい）"],
            # 質問4の選択肢
            ["1. 全く望まない（常に安定した予測可能な回答がよい）", 
             "2. あまり望まない", 
             "3. どちらでもない", 
             "4. やや望む", 
             "5. 非常に望む（予想外の回答や冒険的な発想を歓迎する）"],
            
            # 質問5の選択肢
            ["1. 常に事実重視（創造性より正確さを優先）", 
             "2. どちらかといえば事実重視", 
             "3. バランスが取れているのが良い", 
             "4. どちらかといえば創造性重視", 
             "5. 常に創造性重視（正確さより面白さや独創性を優先）"],
            
            # 質問6の選択肢
            ["1. 非常に限定的な語彙（最も一般的な言葉のみ）", 
             "2. やや限定的な語彙", 
             "3. 標準的な語彙", 
             "4. やや豊富な語彙", 
             "5. 非常に豊富な語彙（珍しい言葉や表現も含む）"],
            # 質問7の選択望む（予想外の回答や冒険的な発想を歓迎する）"],
            

            ["1. 非常に焦点を絞った回答", 
             "2. やや焦点を絞った回答", 
             "3. バランスの取れた回答", 
             "4. やや幅広い視点からの回答", 
             "5. 非常に幅広い視点からの回答（様々な角度からの考察）"],
            
            # 質問8の選択肢
            ["1. 決まった回答が良い", 
             "2. どちらかといえば決まった回答が良い", 
             "3. どちらでもない", 
             "4. どちらかといえば多様な回答が良い", 
             "5. 多様な回答が良い"],
            
            # 質問9の選択肢（文脈理解の深さ）
            ["1. あまり重視しない", 
             "2. やや重視する", 
             "3. 普通", 
             "4. かなり重視する", 
             "5. 非常に重視する"],
            
            # 質問10の選択肢
            ["1. 要点だけで良い", 
             "2. 基本的な内容のみ", 
             "3. バランスよく", 
             "4. やや詳細に", 
             "5. できるだけ詳細に"],
            
            # 質問11の選択肢
            ["1. 常にフォーマル（堅い表現）", 
             "2. どちらかといえばフォーマル", 
             "3. バランスが取れているのが良い", 
             "4. どちらかといえばカジュアル", 
             "5. 常にカジュアル（砕けた表現）"],
            
            # 質問12の選択肢
            ["1. 常に抽象的な概念説明", 
             "2. どちらかといえば抽象的", 
             "3. バランスが取れているのが良い", 
             "4. どちらかといえば具体的", 
             "5. 常に具体的な例え話"],
            
            # 質問13の選択肢（制御性と多様性）
            ["1. 自由な流れが良い", 
             "2. どちらかといえば自由な流れが良い", 
             "3. バランスが良い", 
             "4. どちらかといえば制御された流れが良い", 
             "5. 制御された流れが良い"],
            
            # 質問14の選択肢
            ["1. 非常に簡潔な回答（1〜2文）", 
             "2. やや簡潔な回答", 
             "3. 標準的な長さの回答", 
             "4. やや詳細な回答", 
             "5. 非常に詳細な回答（包括的な説明）"],
            
            # 質問15の選択肢
            ["1. 全く望まない（完全に中立的な回答）", 
             "2. あまり望まない", 
             "3. どちらでもない", 
             "4. やや望む", 
             "5. 非常に望む（感情豊かな表現を好む）"],
             # 質問16の選択肢（幅広い視点）
            ["1. 単一の視点からの回答が良い", 
            "2. どちらかといえば焦点を絞った回答が良い", 
            "3. バランスの取れた視点が良い", 
            "4. どちらかといえば幅広い視点が良い", 
            "5. 非常に幅広い多角的な視点からの回答が良い"],

            # 質問17の選択肢（話題の広がり）
            ["1. 話題を絞って進めるのが良い", 
            "2. どちらかといえば話題を絞るのが良い", 
            "3. バランス良く話題を展開するのが良い", 
            "4. どちらかといえば話題を広げるのが良い", 
            "5. 積極的に話題を広げて展開するのが良い"],

            # 質問18の選択肢（文章表現の多様性）
            ["1. 一貫した同じ表現スタイルが良い", 
            "2. どちらかといえば一貫した表現が良い", 
            "3. バランスの取れた表現が良い", 
            "4. どちらかといえば多様な表現が良い", 
            "5. 非常に変化に富んだ表現スタイルが良い"],

            # 質問19の選択肢（専門用語の使用）
            ["1. 専門用語はほとんど使わない", 
            "2. 専門用語はあまり使わない", 
            "3. 時々使う程度が良い", 
            "4. 適度に専門用語を使う", 
            "5. 積極的に専門用語を使う"],

            # 質問20の選択肢（フォーマル vs カジュアル）
            ["1. 常にフォーマルな表現が良い", 
            "2. どちらかといえばフォーマルな表現が良い", 
            "3. 状況に応じたバランスが良い", 
            "4. どちらかといえばカジュアルな表現が良い", 
            "5. 常にカジュアルな表現が良い"],

            # 質問21の選択肢（抽象的 vs 具体的）
            ["1. 抽象的な概念による説明が良い", 
            "2. どちらかといえば抽象的な説明が良い", 
            "3. バランスの取れた説明が良い", 
            "4. どちらかといえば具体例を用いた説明が良い", 
            "5. 具体的な例え話による説明が良い"],

            # 質問22の選択肢（詳細 vs 簡潔）
            ["1. とても簡潔な説明が良い", 
            "2. どちらかといえば簡潔な説明が良い", 
            "3. バランスの取れた説明が良い", 
            "4. どちらかといえば詳細な説明が良い", 
            "5. 非常に詳細で包括的な説明が良い"],

            # 質問23の選択肢（情報処理速度）
            ["1. ゆっくりと確実に理解したい", 
            "2. やや慎重なペースが良い", 
            "3. 一般的な速さで良い", 
            "4. やや速いペースが好ましい", 
            "5. できるだけ速く情報を得たい"],

            # 質問24の選択肢（論理的 vs 感情的）
            ["1. 完全に論理的な会話が良い", 
            "2. どちらかといえば論理的な会話が良い", 
            "3. 論理と感情のバランスが良い", 
            "4. どちらかといえば感情的な会話が良い", 
            "5. 感情表現を重視した会話が良い"],

            # 質問25の選択肢（専門用語の使用頻度）
            ["1. 専門用語を全く使わない会話が良い", 
            "2. 専門用語をほとんど使わない会話が良い", 
            "3. 一般的な専門用語を時々使う程度が良い", 
            "4. 適度に専門用語を取り入れた会話が良い", 
            "5. 積極的に専門用語を使用した会話が良い"],

            # 質問26の選択肢（確実性）
            ["1. 推測や可能性も含めた回答が良い", 
            "2. やや不確かな情報も含めて良い", 
            "3. バランスの取れた確実性が良い", 
            "4. どちらかといえば確実な情報を求める", 
            "5. 完全に確実な情報のみを求める"],

            # 質問27の選択肢（ユーモア）
            ["1. 冗談やユーモアは全く必要ない", 
            "2. 冗談やユーモアはあまり必要ない", 
            "3. 時々冗談を交えるくらいが良い", 
            "4. 適度に冗談やユーモアを取り入れるのが良い", 
            "5. 頻繁に冗談やユーモアを取り入れるのが良い"],

            # 質問28の選択肢（AI会話の目的）
            ["1. 事実確認や情報収集が主目的", 
            "2. どちらかといえば情報収集が目的", 
            "3. 情報収集と対話を同程度に行いたい", 
            "4. どちらかといえば対話やエンターテイメントが目的", 
            "5. 対話やエンターテイメントが主目的"],

            # 質問29の選択肢（回答の長さ）
            ["1. 非常に短い簡潔な回答が良い", 
            "2. どちらかといえば短めの回答が良い", 
            "3. 状況に応じた長さが良い", 
            "4. どちらかといえば長めの回答が良い", 
            "5. 非常に詳細で長文の回答が良い"],

            # 質問30の選択肢（感情表現）
            ["1. 感情表現のない淡々とした回答が良い", 
            "2. あまり感情表現を含まない回答が良い", 
            "3. 適度な感情表現を含む回答が良い", 
            "4. やや感情豊かな表現を含む回答が良い", 
            "5. 非常に感情豊かで表現力のある回答が良い"]
        ]
        
        # 質問のカテゴリー
        self.categories = [
            "基本的な特性に関する質問",
            "基本的な特性に関する質問",
            "基本的な特性に関する質問",
            "Temperature調整のための質問",
            "Temperature調整のための質問",
            "創造性と予測可能性に関する質問",
            "創造性と予測可能性に関する質問",
            "創造性と予測可能性に関する質問",
            "文脈理解の深さに関する質問",
            "文脈理解の深さに関する質問",
            "繰り返しと一貫性に関する質問",
            "繰り返しと一貫性に関する質問",
            "制御性と多様性のバランスに関する質問",
            "制御性と多様性のバランスに関する質問",
            "Top_p調整のための質問",
            "Top_p調整のための質問",
            "Presence/Frequency Penalty調整のための質問",
            "Presence/Frequency Penalty調整のための質問",
            "Logit_bias調整のための質問",
            "Logit_bias調整のための質問",
            "Logit_bias調整のための質問",
            "ユーザーの特性を把握するための質問",
            "ユーザーの特性を把握するための質問",
            "ユーザーの特性を把握するための質問",
            "ユーザーの特性を把握するための質問",
            "ユーザーの特性を把握するための質問",
            "ユーザーの特性を把握するための質問",
            "ユースケースに関する質問",
            "ユースケースに関する質問",
            "ユースケースに関する質問"
        ]
        
        # ユーザーの回答を保存する辞書
        self.answers = {}
        
        # 現在の質問のインデックス
        self.current_question = 0
        
        # UIコンポーネントの初期化
        self.setup_ui()
    
    def setup_ui(self):
        # カテゴリーラベル
        self.category_label = ttk.Label(self.root, text=self.categories[self.current_question], font=("Helvetica", 14, "bold"))
        self.category_label.pack(pady=20)
        
        # 質問ラベル
        self.question_label = ttk.Label(self.root, text=self.questions[self.current_question], font=("Helvetica", 12))
        self.question_label.pack(pady=10)
        
        # 選択肢のフレーム
        self.options_frame = ttk.Frame(self.root)
        self.options_frame.pack(pady=20, fill="x", padx=50)
        
        # ラジオボタンの変数
        self.selected_option = tk.IntVar()
        self.selected_option.set(0)  # デフォルトは未選択
        
        # 選択肢のラジオボタン
        self.radio_buttons = []
        for i, option in enumerate(self.options[self.current_question]):
            rb = ttk.Radiobutton(
                self.options_frame,
                text=option,
                variable=self.selected_option,
                value=i+1
            )
            rb.pack(anchor="w", pady=5)
            self.radio_buttons.append(rb)
        
        # ナビゲーションボタンのフレーム
        self.nav_frame = ttk.Frame(self.root)
        self.nav_frame.pack(side=tk.BOTTOM, pady=20, fill="x", padx=50)
        
        # 進むボタン
        self.next_button = ttk.Button(self.nav_frame, text="次へ", command=self.next_question)
        self.next_button.pack(side=tk.RIGHT)
        
        # プログレスバー
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=700, mode='determinate')
        self.progress.pack(side=tk.BOTTOM, pady=20)
        self.progress['maximum'] = len(self.questions)
        self.progress['value'] = 0
    
    def next_question(self):
        # 現在の質問の回答を保存
        if self.selected_option.get() == 0:
            messagebox.showwarning("選択必須", "選択肢を選んでください")
            return
        
        self.answers[self.current_question] = self.selected_option.get()
        
        # 次の質問へ移動または結果表示
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.update_question()
        else:
            self.show_results()
    
    def update_question(self):
        # プログレスバーの更新
        self.progress['value'] = self.current_question
        
        # カテゴリーラベルの更新
        self.category_label.config(text=self.categories[self.current_question])
        
        # 質問の更新
        self.question_label.config(text=self.questions[self.current_question])
        
        # 選択肢の更新
        for rb in self.radio_buttons:
            rb.destroy()
        
        self.radio_buttons = []
        self.selected_option.set(0)  # リセット
        for i, option in enumerate(self.options[self.current_question]):
            rb = ttk.Radiobutton(
                self.options_frame,
                text=option,
                variable=self.selected_option,
                value=i+1
            )
            rb.pack(anchor="w", pady=5)
            self.radio_buttons.append(rb)
        
        # 最後の質問の場合、ボタンテキストを変更
        if self.current_question == len(self.questions) - 1:
            self.next_button.config(text="結果を表示")
    
    def calculate_parameters(self):
        # 各パラメーターの計算ロジック
        
        # Temperature (0.0-2.0)
        # 質問1, 4, 5, 6, 7, 8, 28, 30から算出
        temperature_questions = [0, 3, 4, 5, 6, 7, 27, 29]
        temperature_weights = [0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.05, 0.05]  # 重み付け
        
        # 質問5は逆転項目（値が高いほどtemperatureは低くなる）
        temp_values = [self.answers[q] if q != 4 else 6 - self.answers[q] for q in temperature_questions]
        temperature = sum([val * weight for val, weight in zip(temp_values, temperature_weights)]) / 5 * 2
        
        # Top_p (0.0-1.0)
        # 質問2, 15, 16から算出
        top_p_questions = [1, 14, 15]
        top_p_weights = [0.3, 0.35, 0.35]  # 重み付け
        top_p = sum([self.answers[q] * weight for q, weight in zip(top_p_questions, top_p_weights)]) / 5
        
        # Presence_penalty
        # 質問3, 11, 17から算出
        presence_penalty_questions = [2, 10, 16]
        presence_penalty_weights = [0.4, 0.4, 0.2]  # 重み付け
        presence_penalty = sum([self.answers[q] * weight for q, weight in zip(presence_penalty_questions, presence_penalty_weights)]) / 5 * 2 - 1
        
        # Frequency_penalty
        # 質問3, 11, 18から算出
        frequency_penalty_questions = [2, 10, 17]
        frequency_penalty_weights = [0.3, 0.4, 0.3]  # 重み付け
        frequency_penalty = sum([self.answers[q] * weight for q, weight in zip(frequency_penalty_questions, frequency_penalty_weights)]) / 5 * 2 - 1
        
        # 新規：Num_ctx (コンテキスト長)
        # 質問9, 10から算出
        num_ctx_questions = [8, 9]
        num_ctx_weights = [0.5, 0.5]
        num_ctx_normalized = sum([self.answers[q] * weight for q, weight in zip(num_ctx_questions, num_ctx_weights)]) / 5
        # 1024から4096の範囲に変換
        num_ctx = int(1024 + num_ctx_normalized * 3072)
        
        # 新規：Repeat_penalty
        # 質問11, 12から算出
        repeat_penalty_questions = [10, 11]
        repeat_penalty_weights = [0.6, 0.4]
        repeat_penalty = 1.0 + sum([self.answers[q] * weight for q, weight in zip(repeat_penalty_questions, repeat_penalty_weights)]) / 5
        
        # 新規：Mirostat関連
        # 質問13, 14から算出
        mirostat_questions = [12, 13]
        mirostat_weights = [0.5, 0.5]
        mirostat_normalized = sum([self.answers[q] * weight for q, weight in zip(mirostat_questions, mirostat_weights)]) / 5
        mirostat_mode = 0  # デフォルト
        if mirostat_normalized > 0.7:
            mirostat_mode = 2
        elif mirostat_normalized > 0.3:
            mirostat_mode = 1
        
        # Logit_bias関連の指標（実際の実装では特定の単語に対する重みを調整）
        logit_bias_questions = [18, 19, 20]
        
        # 専門用語の使用レベル (1-5)
        jargon_level = self.answers[logit_bias_questions[0]]
        
        # フォーマル度 (1-5)
        formality_level = self.answers[logit_bias_questions[1]]
        
        # 抽象度 vs 具体例 (1-5)
        abstraction_level = self.answers[logit_bias_questions[2]]
        
        # ユーザー特性に基づく追加調整
        # 詳細/簡潔な説明の好み（質問22）が最大トークン数に影響
        max_tokens_base = 1000
        if self.answers.get(21, 3) <= 2:  # 簡潔な説明を好む
            max_tokens_base = 500
        elif self.answers.get(21, 3) >= 4:  # 詳細な説明を好む
            max_tokens_base = 2000
        
        # 論理/感情のバランス（質問24）がtemperatureに影響
        if self.answers.get(23, 3) <= 2:  # 論理的
            temperature *= 0.85
        elif self.answers.get(23, 3) >= 4:  # 感情的
            temperature *= 1.15
        
        # ユーモアの好み（質問27）がtemperatureとtop_pに影響
        if self.answers.get(26, 3) >= 4:  # ユーモアを好む
            temperature *= 1.1
            top_p *= 1.05
        
        # 値の範囲調整
        temperature = max(0.0, min(2.0, temperature))
        top_p = max(0.0, min(1.0, top_p))
        presence_penalty = max(-2.0, min(2.0, presence_penalty))
        frequency_penalty = max(-2.0, min(2.0, frequency_penalty))
        
        return {
            "temperature": round(temperature, 2),
            "top_p": round(top_p, 2),
            "presence_penalty": round(presence_penalty, 2),
            "frequency_penalty": round(frequency_penalty, 2),
            "num_ctx": num_ctx,
            "repeat_penalty": round(repeat_penalty, 2),
            "mirostat_mode": mirostat_mode,
            "max_tokens": max_tokens_base,
            "jargon_level": jargon_level,
            "formality_level": formality_level,
            "abstraction_level": abstraction_level
        }
    
    def show_results(self):
        # 既存のUIコンポーネントをクリア
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # パラメーターを計算
        params = self.calculate_parameters()
        
        # 結果ウィンドウの設定
        self.root.title("AIパラメーター調整結果")
        
        # 結果ヘッダー
        result_header = ttk.Label(self.root, text="あなたに最適なAIパラメーター", font=("Helvetica", 16, "bold"))
        result_header.pack(pady=20)
        
        # パラメーター表示フレーム
        param_frame = ttk.Frame(self.root)
        param_frame.pack(pady=20, fill="both", expand=True)
        
        # 数値パラメーター
        numeric_params = [
            ("Temperature", params["temperature"], "0.0～2.0", "予測のランダム性: 値が高いほど創造的な回答に"),
            ("Top_p", params["top_p"], "0.0～1.0", "トークン選択の多様性: 値が高いほど多様な表現に"),
            ("Presence Penalty", params["presence_penalty"], "-2.0～2.0", "繰り返し回避度: 値が高いほど同じ話題の繰り返しを避ける"),
            ("Frequency Penalty", params["frequency_penalty"], "-2.0～2.0", "単語繰り返し抑制度: 値が高いほど同じ単語の繰り返しを避ける"),
            ("Num_ctx", params["num_ctx"], "1024～4096", "コンテキスト長: 値が大きいほど長い文脈を理解"),
            ("Repeat Penalty", params["repeat_penalty"], "1.0～2.0", "繰り返し抑制: 値が高いほど繰り返しを避ける"),
            ("Mirostat Mode", params["mirostat_mode"], "0～2", "文章の複雑さ制御: 値が高いほど制御が強い"),
            ("Max Tokens", params["max_tokens"], "500～2000", "最大トークン数: 回答の長さ上限")
        ]
        
        # 図の作成
        fig = plt.Figure(figsize=(8, 5), dpi=100)  # サイズを大きく
        ax = fig.add_subplot(111)
        
        # 表示するパラメーターを選択
        param_names = [p[0] for p in numeric_params]
        param_values = [p[1] for p in numeric_params]
        
        # 正規化値に変換
        norm_values = [
            params["temperature"] / 2.0,
            params["top_p"] / 1.0,
            (params["presence_penalty"] + 2.0) / 4.0,
            (params["frequency_penalty"] + 2.0) / 4.0,
            (params["num_ctx"] - 1024) / 3072,
            (params["repeat_penalty"] - 1.0) / 1.0,
            params["mirostat_mode"] / 2.0,
            (params["max_tokens"] - 500) / 1500
        ]
        
        # 横棒グラフ
        bars = ax.barh(param_names, norm_values, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#d35400'])
        ax.set_xlim(0, 1)
        ax.set_title('パラメーター設定値 (正規化)')
        
        # 実際の値をグラフに表示
        for i, bar in enumerate(bars):
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, 
                    f"{param_values[i]}", va='center')
        
        # グラフをGUIに埋め込み
        canvas = FigureCanvasTkAgg(fig, master=param_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # パラメーター詳細表示
        details_frame = ttk.Frame(self.root)
        details_frame.pack(pady=10, fill="both", expand=True, padx=20)
        
        # パラメーター詳細表
        columns = ("パラメーター", "設定値", "範囲", "説明")
        tree = ttk.Treeview(details_frame, columns=columns, show="headings")
        
        # ヘッダー設定
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # データ追加
        for item in numeric_params:
            tree.insert("", tk.END, values=item)
        
        # Logit_bias関連の指標
        logit_bias_params = [
            ("専門用語レベル", params["jargon_level"], "1～5", "値が高いほど専門的な用語を多く使用"),
            ("フォーマル度", params["formality_level"], "1～5", "値が高いほどカジュアルな表現に"),
            ("抽象/具体例", params["abstraction_level"], "1～5", "値が高いほど具体例を多用")
        ]
        
        for item in logit_bias_params:
            tree.insert("", tk.END, values=item)
        
        tree.pack(fill="both", expand=True)
        
        # JSONエクスポートボタン
        export_button = ttk.Button(self.root, text="設定をエクスポート", command=self.export_parameters)
        export_button.pack(pady=10)
        
        # パラメーターインスタンスを保存
        self.final_params = params
    
    def export_parameters(self):
        params = self.final_params
        
        try:
            file_path = tk.filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="パラメーター設定を保存"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(params, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("エクスポート成功", f"パラメーター設定を {file_path} に保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイル保存中にエラーが発生しました: {e}")

def main():
    root = tk.Tk()
    app = AIParameterTuner(root)
    root.mainloop()

if __name__ == "__main__":
    main()