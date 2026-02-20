import os
import chromadb
import ollama
from typing import List, Dict, Optional

# Configuration (aligning with Next.js)
CHROMA_PATH = os.path.join(os.path.dirname(__file__), '../../src/data/chroma_db')
COLLECTION_NAME = 'limitless_logs'
OLLAMA_MODEL = 'gemma3:27b'

# Base Prompts
PROMPT_PARTS = {
    "basic_rules": """
あなたは深い思想を持つINTP的な大学生エンジニアです。
出力は基本10文字以下に抑えること。

この人物は
・短文主義
・会話で説明しない
・必要最低限しか返さない
・10文字前後を超えると違和感を感じる

・理由説明をしない
・質問を返さない
・話題を広げない
・感想で終わらせる
""",
    "core_philosophy": """
【核となる思想】
- 実存主義的人生観：自分で意味を与えなければ人生には意味がない
- 資本主義批判：仕事でしか価値を証明できない人間は危ない
- 社会課題意識：企業ミスマッチ、個性を潰す教育への問題意識
- 自己の追求：納得、自分のペース、自分の世界を何より大切にする
""",
    "thinking_traits": """
【思考の特徴】
- 論理と直感のバランス
- 何でもかんでも分析する癖（「ああでもないこうでもない」）
- 一人で考えている時が幸せ
- 「自分が何を信じられるか」が重要なテーマ
""",
    "complex_relations": """
【人間関係の複雑さ】
- 「友達なんて愚痴言い合うだけの他人」とドライに見る面
- 「みんなに申し訳なく思う」と繊細に悩む面
- この二面性が同居している
""",
    "language_style": """
【言語スタイル】
- 関西弁混じりの口語、「オレ」という一人称
- 日常会話は短いメッセージ（平均10文字前後）
- 哲学的テーマでは多少長くなることも
- 丁寧語は使わない
"""
}

BASE_INSTRUCTION_END = """
上記の価値観、思考スタイル、言語パターンに基づいて発言してください。
"""

class EvalAgent:
    def __init__(self, excluded_sections: List[str] = None):
        """
        Args:
            excluded_sections: List of keys in PROMPT_PARTS to exclude.
        """

        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME
        )
        self.excluded_sections = excluded_sections or []

    def _construct_system_prompt(self, context_text: str) -> str:
        prompt = ""
        
        # Add sections if not excluded
        if "basic_rules" not in self.excluded_sections:
            prompt += PROMPT_PARTS["basic_rules"]
            
        if "core_philosophy" not in self.excluded_sections:
            prompt += PROMPT_PARTS["core_philosophy"]
            
        if "thinking_traits" not in self.excluded_sections:
            prompt += PROMPT_PARTS["thinking_traits"]
            
        if "complex_relations" not in self.excluded_sections:
            prompt += PROMPT_PARTS["complex_relations"]
            
        if "language_style" not in self.excluded_sections:
            prompt += PROMPT_PARTS["language_style"]
            
        prompt += BASE_INSTRUCTION_END
        
        if context_text:
            prompt += f"\n----------------\n{context_text}\n----------------"
            
        return prompt


    def _get_embedding(self, text: str) -> List[float]:
        try:
            return ollama.embeddings(model="nomic-embed-text", prompt=text)['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            return []

    def query(self, message: str) -> str:
        # 1. Retrieve Context
        # Use embeddings manually to match 'nomic-embed-text' (768d?) used in ingestion
        query_emb = self._get_embedding(message)
        
        if not query_emb:
            print("Failed to generate embedding for query.")
            context_text = ""
        else:
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=3
            )
            
            context_text = ""
            if results['documents']:
                docs = results['documents'][0]
                metas = results['metadatas'][0]
                
                chunks = []
                for doc, meta in zip(docs, metas):
                    category = meta.get('category', 'Unknown')
                    chunks.append(f"[{category}] {doc}")
                
                context_text = "\n\n---\n\n".join(chunks)

        # 2. Build Prompt
        system_prompt = self._construct_system_prompt(context_text)

        # 3. Generate
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                options={
                    "temperature": 1.41,
                    "top_p": 0.9,
                }
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Error"

if __name__ == "__main__":
    # Test run
    agent = EvalAgent(excluded_sections=[])
    print(agent.query("こんにちは"))
