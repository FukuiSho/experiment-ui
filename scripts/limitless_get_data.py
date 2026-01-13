import requests
import time
import json
import os

# 設定
API_KEY = "sk-1e04edd3-1db0-4333-a662-026471baaabd"
BASE_URL = "https://api.limitless.ai/v1"

def fetch_all_limitless_data(endpoint_name="lifelogs"):
    """
    指定したエンドポイント（lifelogs または chats）の全データを一括取得する
    """
    headers = {"X-API-Key": API_KEY}
    all_data = []
    cursor = None
    
    print(f"--- {endpoint_name} の取得を開始します ---")

    while True:
        # パラメータの設定（cursorがある場合は追加）
        params = {
            "limit": 10 if endpoint_name == "lifelogs" else 50, # lifelogsの最大は10
            "includeContents": "true"
        }
        if cursor:
            params["cursor"] = cursor

        response = requests.get(f"{BASE_URL}/{endpoint_name}", headers=headers, params=params)

        # レートリミット（429）への対応
        if response.status_code == 429:
            retry_after = int(response.json().get("retryAfter", 60))
            print(f"レート制限中。{retry_after}秒待機します...")
            time.sleep(retry_after)
            continue
        
        response.raise_for_status()
        res_json = response.json()
        
        # データの追加
        data_list = res_json.get("data", {}).get(endpoint_name, [])
        all_data.extend(data_list)
        print(f"現在 {len(all_data)} 件取得済み...")

        # 次のページがあるか確認
        cursor = res_json.get("meta", {}).get(endpoint_name, {}).get("nextCursor")
        if not cursor:
            break

    return all_data

if __name__ == "__main__":
    # ライフログ（録音・文字起こしデータ）の一括取得
    lifelogs = fetch_all_limitless_data("lifelogs")
    print(f"\n合計 {len(lifelogs)} 件のライフログを取得しました。")

    # --- 保存処理の追加 ---
    # 保存先ディレクトリのパス
    output_dir = r"C:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\limitless"
    
    # ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)

    # ライフログの保存
    if lifelogs:
        file_path = os.path.join(output_dir, "lifelogs.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(lifelogs, f, ensure_ascii=False, indent=4)
        print(f"データを保存しました: {file_path}")

    # チャット（Ask AIの履歴）の一括取得
    # chats = fetch_all_limitless_data("chats")
    # print(f"合計 {len(chats)} 件のチャットを取得しました。")
    # if chats:
    #     chat_file_path = os.path.join(output_dir, "chats.json")
    #     with open(chat_file_path, "w", encoding="utf-8") as f:
    #         json.dump(chats, f, ensure_ascii=False, indent=4)
    #     print(f"チャットデータを保存しました: {chat_file_path}")