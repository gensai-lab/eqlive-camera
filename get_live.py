import urllib.request
import re
import json
import os
import sys

def get_m3u8_url(youtube_url):
    try:
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        # YouTubeの最新仕様に合わせた2パターンの正規表現で検索
        match = re.search(r'hlsManifestUrl["\']:\s*["\'](https://[^"\']+\.m3u8)["\']', html)
        if not match:
            # 別パターンの記述形式をパース
            match = re.search(r'["\']hlsManifestUrl["\']\s*:\s*["\']([^"\']+?\.(?:m3u8))["\']', html)
            
        if match:
            url = match.group(1).replace(r'\u0026', '&')
            return url
        return None
    except Exception as e:
        print(f"通信または解析中にエラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    # 対象にする YouTube Live のURL（★ここが正しいか今一度ご確認ください）
    YOUTUBE_URL = "https://www.youtube.com/watch?v=ZwuLUTTHnGE"
    
    print(r"=== YouTube Liveからm3u8の抽出を開始 ===")
    m3u8_url = get_m3u8_url(YOUTUBE_URL)
    
    if m3u8_url:
        data = {"url": m3u8_url, "status": "success"}
        with open("live.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("【成功】live.json を更新しました。")
        print(f"抽出URL: {m3u8_url}")
    else:
        print("【警告】m3u8のURLが見つかりませんでした。配信中ではないか、YouTubeの仕様が変わった可能性があります。")
        # 追跡しやすくするため、失敗時もステータスを書き込む
        data = {"url": "", "status": "failed_to_extract"}
        with open("live.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # Actions側に失敗を知らせる場合は sys.exit(1) にしますが、今回はログ確認のために正常終了させます
