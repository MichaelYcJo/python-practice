import os
import yt_dlp
import threading
import time
import sys

SAVE_PATH = "downloaded_streams"
LOG_FILE = os.path.join(SAVE_PATH, "stream_log.txt")
MAX_DOWNLOAD_SIZE_MB = 50  # 최대 다운로드 크기 (MB 단위, 0이면 무제한)
MAX_DURATION_MINUTES = 1  # 최대 다운로드 시간 (분 단위, 0이면 무제한)
PROXY = None  # 필요하면 "http://proxyserver:port" 설정

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

# 다운로드 시작 시간 저장
start_time = time.time()


def log_message(message):
    """로그 파일에 메시지 기록"""
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)


def download_progress_hook(d):
    """다운로드 진행률 표시 및 자동 종료 조건 추가"""
    global start_time

    if d["status"] == "downloading":
        file_size_mb = d.get("total_bytes", 0) / (1024 * 1024)  # MB 단위 변환
        elapsed_time = (time.time() - start_time) / 60  # 분 단위 변환

        log_message(
            f"📥 진행 중... {file_size_mb:.2f}MB 다운로드됨 | 경과 시간: {elapsed_time:.2f}분"
        )

        # 🚨 파일 크기 초과 시 즉시 종료
        if MAX_DOWNLOAD_SIZE_MB > 0 and file_size_mb > MAX_DOWNLOAD_SIZE_MB:
            log_message(
                f"⚠️ 최대 파일 크기 {MAX_DOWNLOAD_SIZE_MB}MB 초과! 다운로드 중단!"
            )
            sys.exit(1)  # 강제 종료

        # 🚨 다운로드 시간 초과 시 즉시 종료
        if MAX_DURATION_MINUTES > 0 and elapsed_time > MAX_DURATION_MINUTES:
            log_message(
                f"⚠️ 최대 녹화 시간 {MAX_DURATION_MINUTES}분 초과! 다운로드 중단!"
            )
            sys.exit(1)  # 강제 종료

    elif d["status"] == "finished":
        log_message(f"✅ 다운로드 완료: {d['filename']}")


def download_stream(url, media_type="video"):
    """유튜브, 트위치 실시간 스트리밍 다운로드"""
    global start_time
    start_time = time.time()  # 다운로드 시작 시간 초기화

    log_message(f"📡 다운로드 시작: {url} ({media_type.upper()})")

    ydl_opts = {
        "outtmpl": os.path.join(SAVE_PATH, "%(title)s.%(ext)s"),
        "format": (
            "bestaudio/best"
            if media_type == "audio"
            else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
        ),
        "merge_output_format": "mp3" if media_type == "audio" else "mp4",
        "live-from-start": True,  # 실시간 스트리밍 다운로드 지원
        "progress_hooks": [
            download_progress_hook
        ],  # 진행률 표시 및 자동 종료 기능 추가
        "proxy": PROXY,  # 프록시 지원
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            media_text = "MP3 오디오" if media_type == "audio" else "MP4 비디오"
            log_message(f"✅ {media_text} 다운로드 완료! 저장 위치: {SAVE_PATH}")
        except Exception as e:
            log_message(f"❌ 다운로드 실패: {e}")
            sys.exit(1)  # 예외 발생 시 강제 종료


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
