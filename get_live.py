import urllib.request
import json
import os
import re

def get_live_m3u8_fallback(video_id):
    """
    YouTubeのボットブロックを回避するため、
    一般に公開されているYouTube解析用のエンドポイントを利用してm3u8を取得します。
    """
    try:
        # YouTubeの配信情報を安全に仲介してくれるパブリックな解析URLを利用
        api_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # ボット遮断を極力回避するヘッダー
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
        # 複数のパターンでhlsManifestUrlを精密に検索
        match = re.search(r'["\']hlsManifestUrl["\']\s*:\s*["\']([^"\']+?\.m3u8[^"\']*)["\']', html)
        if not match:
            match = re.search(r'hlsManifestUrl["\']:\s*["\'](https://[^"\']+\.m3u8)["\']', html)
        if not match:
            # 最終手段：HTML内から直接 manifest.googlevideo.com のm3u8リンクを探す
            match = re.search(r'(https://manifest\.googlevideo\.com/api/manifest/hls_playlist/[^"\']+?\.m3u8[^"\']*)', html)
            
        if match:
            url = match.group(1).replace(r'\u0026', '&').replace('\\/', '/')
            return url
            
        return None
    except Exception as e:
        print(f"解析中にエラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    # 対象：利島港（利島）ライブカメラ
    VIDEO_ID = "ZwuLUTTHnGE"
    YOUTUBE_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"
    
    print(f"=== 利島港ライブカメラ (ID: {VIDEO_ID}) のm3u8抽出を開始 ===")
    m3u8_url = get_live_m3u8_fallback(VIDEO_ID)
    
    # 現在のUTC時刻
    current_time = os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip()
    
    if m3u8_url:
        data = {
            "url": m3u8_url, 
            "status": "success",
            "updated_at": current_time
        }
        print("【成功】m3u8 URLを取得しました。")
    else:
        print("【失敗】直接の解析に失敗しました。")
        data = {
            "url": "", 
            "status": "failed_to_extract",
            "updated_at": current_time
        }
        
    # live.json に結果を保存
    with open("live.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
