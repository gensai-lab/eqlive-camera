import urllib.request
import json
import os
import re
import sys

def get_m3u8_via_embed(video_id):
    try:
        # YouTubeの埋め込み用ページ（ここが一番ボットブロックが緩く、生のURLが含まれている）
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
        }
        
        req = urllib.request.Request(embed_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
        
        # 埋め込みプレイヤーの初期化JSON（ytInitialPlayerResponse）を抽出
        json_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
        
        if json_match:
            player_response = json.loads(json_match.group(1))
            
            # JSONの中からストリーミング配信の情報を探す
            streaming_data = player_response.get("streamingData", {})
            
            # パターンA: hlsManifestUrl を直接取得
            if "hlsManifestUrl" in streaming_data:
                return streaming_data["hlsManifestUrl"]
                
            # パターンB: 予測される記述形式（adaptiveFormatsなど）からサルベージ
            # ライブ配信の場合、通常は hlsManifestUrl に格納されています
            
        # 最終手段：正規表現で強引にmanifestURLを抜き出す
        fallback_match = re.search(r'(https://manifest\.googlevideo\.com/api/manifest/hls_playlist/[^"\']+?\.m3u8[^"\']*)', html)
        if fallback_match:
            return fallback_match.group(1).replace(r'\u0026', '&').replace('\\/', '/')

        return None
    except Exception as e:
        print(f"API/埋め込みデータの解析中にエラー: {e}")
        return None

if __name__ == "__main__":
    # 対象：利島港（利島）ライブカメラ
    VIDEO_ID = "ZwuLUTTHnGE"
    
    print(f"=== [公式埋め込みルート] 利島港ライブカメラ (ID: {VIDEO_ID}) の抽出を開始 ===")
    m3u8_url = get_m3u8_via_embed(VIDEO_ID)
    
    current_time = os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip()
    
    if m3u8_url:
        data = {
            "url": m3u8_url, 
            "status": "success",
            "updated_at": current_time
        }
        print(f"【超成功】m3u8 URLを検出しました！\nURL: {m3u8_url}")
    else:
        print("【全滅】すべてのルートでURLが検出できませんでした。")
        data = {
            "url": "", 
            "status": "failed_to_extract",
            "updated_at": current_time
        }
        
    with open("live.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
