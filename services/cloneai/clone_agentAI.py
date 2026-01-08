import requests
import time
import json
import random
from typing import Dict, List, Any, Optional, Tuple, Union
# pip install ollama
try:
    import ollama  # type: ignore
except Exception:  # pragma: no cover
    ollama = None

class ThoughtFlow:
    """思考フローを記録するクラス"""
    def __init__(self):
        self.thoughts = []
        
    def add_thought(self, thought: str, category: str = "general"):
        """思考を追加する
        
        Args:
            thought: 思考内容
            category: 思考のカテゴリ
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.thoughts.append({
            "timestamp": timestamp,
            "category": category,
            "content": thought
        })
        # 思考プロセスを表示
        print(f"[{timestamp}] [{category}] {thought}")
        
    def get_thoughts(self) -> List[Dict[str, str]]:
        """記録された全思考を取得する"""
        return self.thoughts
    
    def get_thought_summary(self) -> str:
        """思考の要約を取得する"""
        summary = "思考プロセス要約:\n"
        for i, thought in enumerate(self.thoughts):
            summary += f"{i+1}. [{thought['category']}] {thought['content']}\n"
        return summary


class LLMClient:
    """LLMモデルと通信するための抽象基底クラス"""
    def generate(self, prompt: str) -> str:
        """プロンプトに基づいてテキストを生成する"""
        raise NotImplementedError("Subclasses must implement this method")


class OllamaClient(LLMClient):
    """Ollamaと通信するためのクライアント"""
    def __init__(self, model_name: str = "gemma3:1b", base_url: str = "http://localhost:11434/api"):
        self.model_name = model_name
        self.base_url = base_url
        self.simulation_mode = False  # シミュレーションモードのフラグ
        
    def generate(self, prompt: str) -> str:
        """モデルを使用してテキストを生成する
        
        Args:
            prompt: 生成のためのプロンプト
            
        Returns:
            生成されたテキスト
        """
        if self.simulation_mode:
            return self._simulate_generation(prompt)
        else:
            return self._real_generate(prompt)
    
    def _simulate_generation(self, prompt: str) -> str:
        """実際のモデル呼び出しをシミュレーション
        
        Args:
            prompt: 生成のためのプロンプト
            
        Returns:
            シミュレートされた応答
        """
        print(f"モデル {self.model_name} に問い合わせ中（シミュレーションモード）...")
        
        # プロンプトに基づいた応答をシミュレート
        responses = {
            "自己紹介": "こんにちは！山田太郎です。30代のバックエンドエンジニアとして働いています。まあ、そうだね...Pythonが大好きで、最近はRustにも興味を持っているんだ。技術の世界は日々進化していて面白いよね。趣味は登山とゲームで、休日にはよく山に出かけるんだ。技術書を読むのも好きで、常に新しい知識を吸収しようとしているよ。何か手伝えることがあれば、気軽に聞いてね！",
            "プログラミング": "まあ、そうだね...最近はWebAssemblyとRustの組み合わせに興味があるんだ。特にエッジコンピューティングでの活用が面白いと思っているよ。あとは、Pythonの非同期処理とFastAPIを使ったマイクロサービス開発にハマってて、パフォーマンスと拡張性のバランスが絶妙なんだよね。機械学習フレームワークの軽量化にも注目しているかな。TensorFlow LiteやPyTorchのモバイル対応は進化が速くて追いかけるのが大変だけど、端末上での推論は今後もっと重要になると思うんだ。君は何か興味ある技術はある？",
            "週末": "この週末の予定か、まあ、そうだね...土曜日は朝から奥多摩の山に登りに行く予定だよ。天気が良ければ景色が最高なんだ。日曜日は新しく買ったRustの本を読みながら、小さなプロジェクトを始めようと思っている。あとはスタートアップの仲間とオンライミーティングで次のスプリントの計画を立てる約束もしているかな。プログラマーらしく、リラックスしながらもコードを書く時間は確保するつもりさ。君の週末の予定はどうなの？",
            "Rust": "まあ、そうだね...Rustと他の言語を比較すると、メモリ安全性と並行処理の扱いやすさが際立つよね。特にC++と比べると、所有権システムが明示的でありながらGCがないのがRustの素晴らしいところだと思う。Pythonと比較すると実行速度は桁違いに速いけど、開発スピードではPythonのほうが上だね。Goと比べるとエラー処理の考え方が違って、Rustはより厳格なアプローチを取っている。まあ、言語ごとに適材適所があるから、プロジェクトの要件によって使い分けるのが賢明だと思うよ。僕の場合、パフォーマンスクリティカルな部分はRust、高速に開発したい部分はPythonという組み合わせが好きかな。"
        }
        
        # プロンプトのキーワードに基づいて応答を選択
        if "自己紹介" in prompt:
            response = responses["自己紹介"]
        elif any(word in prompt.lower() for word in ["プログラミング", "技術", "興味", "言語"]):
            response = responses["プログラミング"]
        elif any(word in prompt.lower() for word in ["週末", "予定", "休み"]):
            response = responses["週末"]
        elif "Rust" in prompt:
            response = responses["Rust"]
        else:
            response = "まあ、そうだね...それは興味深い話題だね。技術者としての視点から考えると、いくつかの側面があるように思うよ。もう少し具体的に話してみない？"
        
        # 応答生成に時間がかかるのをシミュレート
        time.sleep(0.5)
        
        return response
    
    def _real_generate(self, prompt: str) -> str:
        """実際のOllama APIを呼び出す
        
        Args:
            prompt: 生成のためのプロンプト
            
        Returns:
            モデルからの応答
        
        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            if ollama is None:
                return "エラー: ollama パッケージが見つかりません。仮想環境を有効化して 'pip install ollama' を実行してください"
            print(f"モデル {self.model_name} に問い合わせ中...")
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            # response.raise_for_status()
            summary = response.message.content if response.message else "応答がありません。"
            return summary
            # response = requests.post(
            #     f"{self.base_url}/generate",
            #     json={
            #         "model": self.model_name,
            #         "prompt": prompt,
            #         "stream": False
            #     },
            #     timeout=30  # タイムアウト設定
            # )
            # response.raise_for_status()
            # return response.json().get("response", "応答がありませんでした")
        except requests.exceptions.Timeout:
            return "エラー: APIリクエストがタイムアウトしました"
        except requests.exceptions.ConnectionError:
            return "エラー: APIサーバーに接続できませんでした。Ollamaが実行されていることを確認してください"
        except requests.exceptions.HTTPError as e:
            return f"エラー: HTTPエラー {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"エラー: {str(e)}"
    
    def set_simulation_mode(self, enabled: bool = True) -> None:
        """シミュレーションモードを切り替える
        
        Args:
            enabled: シミュレーションモードを有効にするかどうか
        """
        self.simulation_mode = enabled


class PersonaTemplate:
    """特定の個人の特徴を定義するテンプレートクラス"""
    def __init__(self, 
                 name: str, 
                 description: str, 
                 traits: Dict[str, Any] = None,
                 background: str = None,
                 personality: str = None,
                 speech_style: str = None,
                 knowledge_areas: List[str] = None,
                 values: List[str] = None):
        self.name = name
        self.description = description
        self.traits = traits or {}
        self.background = background
        self.personality = personality
        self.speech_style = speech_style
        self.knowledge_areas = knowledge_areas or []
        self.values = values or []
        
    def to_prompt(self) -> str:
        """ペルソナをプロンプトに変換"""
        prompt = [
            f"# ペルソナ設定: {self.name}",
            f"## 基本情報\n{self.description}\n"
        ]
        
        if self.background:
            prompt.append(f"## 経歴\n{self.background}\n")
            
        if self.personality:
            prompt.append(f"## 性格\n{self.personality}\n")
            
        if self.speech_style:
            prompt.append(f"## 話し方の特徴\n{self.speech_style}\n")
        
        if self.traits:
            prompt.append("## 個人的特徴")
            for trait, value in self.traits.items():
                prompt.append(f"- {trait}: {value}")
            prompt.append("")
        
        if self.knowledge_areas:
            prompt.append("## 知識分野")
            for area in self.knowledge_areas:
                prompt.append(f"- {area}")
            prompt.append("")
            
        if self.values:
            prompt.append("## 価値観・信条")
            for value in self.values:
                prompt.append(f"- {value}")
            prompt.append("")
            
        prompt.append("## 指示")
        prompt.append("あなたは上記の人物になりきって応答してください。")
        prompt.append("一人称は「俺」を使い、上記の性格や話し方、知識に基づいて応答してください。")
        prompt.append("応答は簡潔すぎず、かといって冗長になりすぎないよう心がけてください。")
        prompt.append("ユーザーとの対話ではできるだけ自然な会話の流れを維持してください。")
        
        return "\n".join(prompt)


class MemoryManager:
    """会話の履歴や重要な情報を管理するクラス"""
    def __init__(self, max_history: int = 10):
        self.conversation_history: List[Dict[str, str]] = []
        self.key_facts: Dict[str, Any] = {}
        self.max_history = max_history
        
    def add_interaction(self, user_input: str, agent_response: str) -> None:
        """対話を履歴に追加する
        
        Args:
            user_input: ユーザーの入力
            agent_response: エージェントの応答
        """
        self.conversation_history.append({
            "user": user_input,
            "agent": agent_response,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 履歴の長さを制限
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
            
    def add_fact(self, key: str, value: Any) -> None:
        """重要な事実を記録する
        
        Args:
            key: 事実の識別子
            value: 事実の内容
        """
        self.key_facts[key] = value
        
    def get_history_as_text(self, num_entries: Optional[int] = None) -> str:
        """会話履歴をテキスト形式で取得する
        
        Args:
            num_entries: 取得するエントリの数（Noneの場合は全て）
            
        Returns:
            会話履歴のテキスト
        """
        if not self.conversation_history:
            return "会話履歴はありません"
        
        entries = self.conversation_history
        if num_entries is not None:
            entries = entries[-num_entries:]
            
        result = []
        for entry in entries:
            result.append(f"ユーザー: {entry['user']}")
            result.append(f"エージェント: {entry['agent']}")
            result.append("")
            
        return "\n".join(result)


class AIPersonaAgent:
    """特定の人物を模倣するAIエージェント"""
    def __init__(self, 
                 persona: PersonaTemplate, 
                 model_name: str = "gemma3:1b",
                 simulation_mode: bool = False):
        self.persona = persona
        self.client = OllamaClient(model_name)
        self.client.set_simulation_mode(simulation_mode)
        self.thought_flow = ThoughtFlow()
        self.memory = MemoryManager()
        
    def _build_prompt(self, user_input: str) -> str:
        """プロンプトを構築する
        
        Args:
            user_input: ユーザーの入力
            
        Returns:
            構築されたプロンプト
        """
        self.thought_flow.add_thought(f"ユーザー入力を受け取りました: '{user_input}'", "input")
        self.thought_flow.add_thought("思考ステップ1: ユーザーの意図を分析中...", "thinking")
        
        # ユーザー入力の意図を簡単に分析（実際は複雑なロジックになる可能性あり）
        if "?" in user_input or "？" in user_input:
            self.thought_flow.add_thought("質問が検出されました", "thinking")
        if any(keyword in user_input.lower() for keyword in ["こんにちは", "おはよう", "こんばんは", "初めまして"]):
            self.thought_flow.add_thought("挨拶が検出されました", "thinking")
            
        self.thought_flow.add_thought("思考ステップ2: 関連する背景知識を検索中...", "thinking")
        # 実際のアプリケーションでは、ここでRAGや知識ベースからの検索を行うことも可能
        
        self.thought_flow.add_thought("思考ステップ3: プロンプトを構築中...", "process")
        
        # ペルソナ情報を含むプロンプトを作成
        prompt_parts = [self.persona.to_prompt()]
        
        # 会話履歴を追加
        if self.memory.conversation_history:
            self.thought_flow.add_thought(f"会話履歴を追加します（{len(self.memory.conversation_history)}件）", "process")
            prompt_parts.append("## これまでの会話")
            prompt_parts.append(self.memory.get_history_as_text())
        
        # 現在の入力を追加
        prompt_parts.append("## 現在の入力")
        prompt_parts.append(user_input)
        
        full_prompt = "\n\n".join(prompt_parts)
        
        self.thought_flow.add_thought("プロンプト構築完了", "process")
        self.thought_flow.add_thought(f"プロンプトの長さ: {len(full_prompt)}文字", "process")
        
        return full_prompt
    
    def _analyze_response(self, response: str, user_input: str) -> str:
        """応答を分析して適切に処理する
        
        Args:
            response: モデルからの生の応答
            user_input: ユーザーの入力
            
        Returns:
            処理された応答
        """
        self.thought_flow.add_thought("思考ステップ4: 応答の分析と改善を行っています...", "thinking")
        
        # エラーメッセージかどうかを確認
        if response.startswith("エラー:"):
            self.thought_flow.add_thought(f"エラーが発生しました: {response}", "error")
            return f"すみません、技術的な問題が発生しました。{response}"
        
        # 応答の品質をチェック（簡易版）
        if len(response) < 10:
            self.thought_flow.add_thought("応答が短すぎます。より詳細な応答に修正します", "thinking")
            response = f"まあ、そうだね... {response} もう少し詳しく説明すると、この質問は興味深いポイントを含んでいるよ。"
            
        # ペルソナの口癖を追加する可能性
        if random.random() < 0.3 and "まあ、そうだね" not in response:
            self.thought_flow.add_thought("ペルソナの口癖を追加します", "thinking")
            sentences = response.split('。')
            insert_index = min(1, len(sentences) - 1)
            sentences[insert_index] = "まあ、そうだね..." + sentences[insert_index]
            response = '。'.join(sentences)
        
        self.thought_flow.add_thought("応答の分析と改善が完了しました", "thinking")
        return response
    
    def process_input(self, user_input: str) -> str:
        """ユーザー入力を処理し、応答を生成する
        
        Args:
            user_input: ユーザーからの入力
            
        Returns:
            エージェントの応答
        """
        try:
            self.thought_flow.add_thought("入力処理を開始", "process")
            
            # プロンプトを構築
            prompt = self._build_prompt(user_input)
            
            # モデルに問い合わせ
            self.thought_flow.add_thought("モデルに問い合わせ中...", "api")
            response = self.client.generate(prompt)
            self.thought_flow.add_thought(f"モデルから応答を受信: '{response[:100]}...'", "api")
            
            # 応答を分析
            final_response = self._analyze_response(response, user_input)
            
            # 会話履歴を更新
            self.memory.add_interaction(user_input, final_response)
            
            self.thought_flow.add_thought("処理完了、応答を返します", "process")
            return final_response
            
        except Exception as e:
            error_msg = f"予期せぬエラーが発生しました: {str(e)}"
            self.thought_flow.add_thought(error_msg, "error")
            return f"すみません、処理中に問題が発生しました: {str(e)}"
    
    def get_thought_process(self) -> List[Dict[str, str]]:
        """思考プロセスを取得"""
        return self.thought_flow.get_thoughts()
    
    def get_thought_summary(self) -> str:
        """思考プロセスの要約を取得"""
        return self.thought_flow.get_thought_summary()
    
    def reset_conversation(self) -> None:
        """会話をリセットする"""
        self.memory.conversation_history = []
        self.thought_flow.add_thought("会話履歴をリセットしました", "process")


def create_yamada_taro_persona() -> PersonaTemplate:
    """山田太郎のペルソナを作成する"""
    return PersonaTemplate(
        name="福井聖",
        description="21歳の日本人大学生。大阪国際工科専門職大学の3回生で、情報工学科でAI戦略コースを専攻。",
        traits={
            "口癖": "たしかに...",
            "好きな言語": "Python、TypeScript",
            "趣味": "筋トレ、ゲーム、Youtube、自己啓発書を読むこと",
            "好きな食べ物": "ラーメン、寿司、焼肉",
            "好きなスポーツ": "バレーボール、卓球",
            "好きな音楽": "J-POP、アニソン、クラシック、ロック、ボカロ",
            "好きな映画": "SF、アクション、アニメーション",
            "好きな本": "自己啓発書、ビジネス書、技術書",
            "好きな動物": "猫",
            "好きな飲み物": "コーヒー、紅茶、紅茶、ミルク",
            "好きな色": "青、緑、黒",
            "好きな季節": "春、秋",
            "好きな場所": "山、川、カフェ",
            "好きな時間帯": "夜",
            "好きな服装": "カジュアル、シンプル",
            "好きなキャラクター": "ナルト、ルフィ、金木研、リゼロのレム",
            "好きなゲーム": "FF、ドラクエ、モンハン",
            "好きなアニメ": "進撃の巨人、鬼滅の刃、ワンピース、ナルト",
            "好きな漫画": "ワンピース、進撃の巨人、鬼滅の刃、ナルト",
            "好きなテレビ番組": "バラエティ、ドキュメンタリー",
            "好きなYouTuber": "板橋ハウス、ゆる言語学ラジオ",
            "好きなSNS": "YouTube",
            "好きなウェブサイト": "Qiita、Zenn",
            "好きなブログ": "はてなブログ、note",
            "趣味・関心事": "ボードゲーム",
            "日常生活の過ごし方（平日・休日）": "ぐうたら昼まで寝て起きたらゲームする、もしくはバイト",
            "買い物の頻度や場所": "よく行くのはコンビニ",
            "よく利用する交通手段": "地下鉄、自転車",
            "外食の頻度や好みの店舗タイプ": "ジューシーなもの、チェーン店、安くて美味しい店",
            "所有するデバイス": "スマートフォン、ノートPC",
            "利用するSNSプラットフォーム": "X、インスタ、LINE",
            "よく使うアプリやウェブサイト": "YouTube",
            "オンラインショッピングの頻度": "月一",
            "主な情報源": "公式LINE、Microsoftブラウザ",
            "よく見るテレビ番組やYouTubeチャンネル": "板橋チャンネル、ハイタカチャンネル、2ちゃんまとめ、街録ch",
            "購読している雑誌や新聞": "特になし",
            "所属するコミュニティやグループ": "プログラミングサークル",
            "社会的な役割や活動": "特になし",
            "短期的・長期的な人生の目標": "世界平和",
            "現在直面している課題や悩み": "実装力の低さ",
            "将来の不安や期待": "テクノロジーによってめんどくさい事をしなくていいようになる",
            "好きな旅行": "友達と夏休みに旅行に行ったりする。この前は岐阜まで旅行に行き、バンジージャンプを飛んだ",
            "好きな食べ物": "とんかつ、ホイコーロー、ぜんざい、春巻き、納豆",
            "嫌いなモノ": "人の意見を否定しかしない人、相手の意見をつぶしに来る人",
            "嫌いな食べ物": "漬物",
            "好きな女性のタイプ": "小柄でスレンダーな人、童顔",
            "尊敬する人": "藤原基央、岡田斗司夫、宮台真司",
            "面白いエピソード": "中学生の時にお別れ会で先生モノマネをして大うけした。",
            "自分の見た目について": "星野源、松潤、福士蒼汰 を足して10で割った感じ。くせ毛が特徴、目、まつげは大きい、離れ目、ひげは薄い、唇は少し厚い"
        },
        background="""
        年齢：21歳
        性別：男
        居住地：大阪府八尾市木の本三丁目22－11
        誕生日：2003年11月2日
        血液型：B型
        星座：さそり座
        十二支：未年
        職業：大学3年生
        学歴：大阪国際工科専門職大学工科学部情報工学科AI戦略コース
        収入：年収40万
        家族構成：長男、5人家族（父、母、4歳下の弟、8歳下の妹）
        婚姻状況：未婚
        身長：170cm
        体重：60kg
        """,
        personality="""
        性格特性：ENFP
        ビックファイブ
        外向性：57
        神経質：29
        開放性：68
        協調性：48
        誠実性：34
        サイコグラフィック特性：
        ライフスタイル：夜型
        消費行動パターン：衝動買い型、経験型
        意思決定プロセス：損得合理で考える
        自分の性格について
        好奇心旺盛で大抵の行動原理が好奇心からくる
        物事には信念をもって取り組み、根気がある
        自分の納得を重要視する。
        周りの評価よりも本質的であるかどうかの方が大切
        """,
        speech_style="""
        口調：カジュアルでフレンドリーな口調
        """,
        knowledge_areas=[
            "バックエンド開発（Python, Go, Rust）",
            "データベース設計と最適化",
            "クラウドインフラ（AWS, GCP）",
            "機械学習の基礎知識"
        ],
        values = [
            "好奇心が全て",
            "ガジェットとして画期的であること",
            "機能美",
            "庶民派",
            "レアであること",
            "ワクワクするもの",
            "最高に面白く生きること"
        ]
    )


def check_ollama_available(base_url: str = "http://localhost:11434/api") -> bool:
    """Ollamaサービスが利用可能かチェックする"""
    try:
        response = requests.get(f"{base_url}/version", timeout=2)
        return response.status_code == 200
    except:
        return False


def interactive_mode():
    """インタラクティブモードでAIエージェントを実行する"""
    # ペルソナを定義
    persona = create_yamada_taro_persona()
    
    # Ollamaが利用可能かチェック
    ollama_available = check_ollama_available()
    
    # エージェントを初期化
    agent = AIPersonaAgent(persona, simulation_mode=not ollama_available)
    
    # ヘッダー情報を表示
    print("=" * 50)
    print("思考フロー可視化AIエージェント - 試作品1号")
    print("=" * 50)
    print(f"ペルソナ: {persona.name}")
    print(f"説明: {persona.description}")
    if ollama_available:
        print("モード: 実際のOllama API使用")
    else:
        print("モード: シミュレーション（Ollamaサービスが利用できないため）")
    print("=" * 50)
    print("\n対話を開始します。終了するには 'exit' または 'quit' と入力してください。\n")
    
    # 対話ループ
    while True:
        user_input = input("\nユーザー: ")
        if user_input.lower() in ["exit", "quit", "終了"]:
            break
            
        print("")
        response = agent.process_input(user_input)
        print(f"{persona.name}: {response}")
        print("-" * 50)
    
    # 思考プロセスの要約を表示
    print("\n" + "=" * 50)
    print("思考プロセスの可視化")
    print("=" * 50)
    print(agent.get_thought_summary())
    
    # 終了メッセージ
    print("\n" + "=" * 50)
    print("対話終了 - Ollamaを使用したAIエージェント試作品1号")
    print("=" * 50)


def test_mode():
    """テストモードでAIエージェントを実行する"""
    # ペルソナを定義
    persona = create_yamada_taro_persona()
    
    # Ollamaが利用可能かチェック
    ollama_available = check_ollama_available()
    
    # エージェントを初期化
    agent = AIPersonaAgent(persona, simulation_mode=not ollama_available)
    
    # ヘッダー情報を表示
    print("=" * 50)
    print("思考フロー可視化AIエージェント - 試作品1号")
    print("=" * 50)
    print(f"ペルソナ: {persona.name}")
    print(f"説明: {persona.description}")
    if ollama_available:
        print("モード: 実際のOllama API使用")
    else:
        print("モード: シミュレーション（Ollamaサービスが利用できないため）")
    print("=" * 50)
    
    # テスト対話
    test_inputs = [
        "こんにちは、自己紹介してください",
        # "プログラミングで最近興味あることは？",
        # "この週末の予定は？",
        # "Rustと他の言語を比較するとどうですか？"
    ]
    
    for user_input in test_inputs:
        print("\n")
        print(f"ユーザー: {user_input}")
        response = agent.process_input(user_input)
        print(f"{persona.name}: {response}")
        print("-" * 50)
    
    # 思考プロセスの要約を表示
    print("\n" + "=" * 50)
    print("思考プロセスの可視化")
    print("=" * 50)
    print(agent.get_thought_summary())
    
    # 終了メッセージ
    print("\n" + "=" * 50)
    print("テスト終了 - Ollamaを使用したAIエージェント試作品1号")
    print("思考フローの可視化により、AIの意思決定プロセスが明確になりました。")
    print("=" * 50)


def main():
    # コマンドライン引数があれば解析
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        # test_mode()
        interactive_mode()


if __name__ == "__main__":
    # メイン関数を実行
    main()
