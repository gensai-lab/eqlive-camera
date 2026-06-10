import urllib.request
import json
import os
import sys

def get_m3u8_via_innertube(video_id):
    try:
        url = "https://www.youtube.com/youtubei/v1/player"
        
        # Workersで検証を重ねたTVHTML5のクリーンなペイロード
        payload = {
            "videoId": videoId,
            "context": {
                "client": {
                    "clientName": "TVHTML5",
                    "clientVersion": "7.20260308.01.00",
                    "hl": "ja",
                    "gl": "JP",
                    "utcOffsetMinutes": 540
                }
            },
            "playbackContext": {
                "contentPlaybackContext": {
                    "signatureTimestamp": 20000
                }
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 SmartTV"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
        m3u8_url = None
        if "streamingData" in res_data and "hlsManifestUrl" in res_data["streamingData"]:
            m3u8_url = res_data["streamingData"]["hlsManifestUrl"]
            
        return m3u8_url
    except Exception as e:
        print(f"API通信中にエラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    # 対象：利島港ライブカメラ
    VIDEO_ID = "ZwuLUTTHnGE"
    
    print(f"=== InnerTube APIよりストリームURLの抽出を開始 (ID: {VIDEO_ID}) ===")
    m3u8_url = get_m3u8_via_innertube(VIDEO_ID)
    
    current_time = os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip()
    
    if m3u8_url:
        # 成功データを構造化して保存
        data = {
            "url": m3u8_url,
            "status": "success",
            "updated_at": current_time
        }
        print(f"【成功】最新のm3u8 URLを保存しました。\nURL: {m3u8_url}")
    else:
        print("【失敗】URLの取得に失敗しました。")
        data = {
            "url": "",
            "status": "failed",
            "updated_at": current_time
        }
        
    with open("live.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
