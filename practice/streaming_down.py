import os
import yt_dlp
import threading

SAVE_PATH = "downloaded_streams"

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


def download_stream(url, media_type="video"):
    """유튜브, 트위치 실시간 스트리밍 다운로드"""
    ydl_opts = {
        "outtmpl": os.path.join(SAVE_PATH, "%(title)s.%(ext)s"),
        "format": (
            "bestaudio/best" if media_type == "audio" else "bestvideo+bestaudio/best"
        ),
        "merge_output_format": "mp3" if media_type == "audio" else "mp4",
        "live-from-start": True,  # 실시간 스트리밍 다운로드 지원
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            media_text = "MP3 오디오" if media_type == "audio" else "MP4 비디오"
            print(f"✅ 실시간 {media_text} 다운로드 완료! 📂 저장 위치: {SAVE_PATH}")
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")


def threaded_stream_download(url, media_type):
    """멀티스레드 방식으로 실시간 스트리밍 다운로드"""
    thread = threading.Thread(target=download_stream, args=(url, media_type))
    thread.start()


def main():
    """유튜브 & 트위치 실시간 스트리밍 다운로드 메뉴"""
    print("\n📡 실시간 스트리밍 다운로드")
    stream_url = input("🌍 스트리밍 URL을 입력하세요: ").strip()

    print("\n🎞️ 다운로드 옵션을 선택하세요:")
    print("1. 🎥 MP4 비디오 다운로드")
    print("2. 🎵 MP3 오디오 다운로드")

    choice = input("👉 선택 (1 또는 2): ").strip()
    if choice == "1":
        media_type = "video"
    elif choice == "2":
        media_type = "audio"
    else:
        print("⚠️ 올바른 옵션을 선택하세요!")
        return

    threaded_stream_download(stream_url, media_type)


# 실행
main()
