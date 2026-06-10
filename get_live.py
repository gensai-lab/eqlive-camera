import urllib.request
import re
import json
import os

def get_m3u8_url(youtube_url):
    try:
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        match = re.search(r'hlsManifestUrl["\']:\s*["\'](https://[^"\']+\.m3u8)["\']', html)
        
        if match:
            return match.group(1).replace(r'\u0026', '&')
        return None
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

if __name__ == "__main__":
    # 対象にする YouTube Live のURL
    YOUTUBE_URL = "https://www.youtube.com/watch?v=動画のID"
    
    m3u8_url = get_m3u8_url(YOUTUBE_URL)
    
    if m3u8_url:
        # 他のシステムから読み込みやすいようにJSON形式で保存
        data = {"url": m3u8_url}
        with open("live.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated live.json")
    else:
        print("Failed to get m3u8 URL")
