import os
import re
import requests
import yt_dlp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import threading
import subprocess

SAVE_PATH = "./downloaded"
PROXY = None  # 필요하면 여기에 프록시 설정 ("http://proxyserver:port")


def get_video_urls_from_page(url):
    """웹페이지에서 비디오 URL 찾기"""
    response = requests.get(
        url, proxies={"http": PROXY, "https": PROXY} if PROXY else None
    )

    if response.status_code != 200:
        print("❌ 웹페이지를 불러올 수 없습니다.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    video_tags = soup.find_all("video")
    source_tags = soup.find_all("source")
    m3u8_tags = soup.find_all("a", href=True)

    video_urls = []

    for tag in video_tags:
        src = tag.get("src")
        if src:
            video_urls.append(urljoin(url, src))

    for tag in source_tags:
        src = tag.get("src")
        if src:
            video_urls.append(urljoin(url, src))

    for tag in m3u8_tags:
        href = tag["href"]
        if ".m3u8" in href:
            video_urls.append(urljoin(url, href))

    return list(set(video_urls))


def progress_hook(d):
    """다운로드 상태 표시"""
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"⬇️ {percent} | {speed} | 남은 시간: {eta}", end="\r")
    elif d["status"] == "finished":
        print(f"\n✅ 다운로드 완료: {d['filename']}")


def download_media(video_url, media_type="video"):
    """MP4 비디오 또는 MP3 오디오 다운로드"""
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    ydl_opts = {
        "outtmpl": os.path.join(SAVE_PATH, "%(title)s.%(ext)s"),
        "format": (
            "bestaudio/best" if media_type == "audio" else "bestvideo+bestaudio/best"
        ),
        "merge_output_format": "mp3" if media_type == "audio" else "mp4",
        "progress_hooks": [progress_hook],
        "quiet": True,  # 일반 로그 출력 제거 (진행률만 표시)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            media_type_text = "MP3 오디오" if media_type == "audio" else "MP4 비디오"
            print(f"📂 저장 위치: {SAVE_PATH}")
        except Exception as e:
            print(f"\n❌ 다운로드 실패: {e}")


def threaded_download(video_url, media_type):
    """멀티스레드 다운로드 실행"""
    thread = threading.Thread(target=download_media, args=(video_url, media_type))
    thread.start()


def main():
    """사용자 입력을 받아 동영상 또는 오디오 다운로드"""
    website_url = input("🌐 동영상이 포함된 웹페이지 URL을 입력하세요: ").strip()

    if any(
        x in website_url
        for x in ["youtube.com", "youtu.be", "twitch.tv", "netflix.com"]
    ):
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

        threaded_download(website_url, media_type)
        return

    video_urls = get_video_urls_from_page(website_url)

    if not video_urls:
        print("⚠️ 이 페이지에서 직접 찾을 수 있는 동영상 URL이 없습니다.")
        use_yt_dlp = (
            input("📡 yt-dlp를 사용하여 다운로드를 시도할까요? (y/n): ").strip().lower()
            == "y"
        )
        if use_yt_dlp:
            threaded_download(website_url, "video")
        return

    print("\n🎥 찾은 동영상 목록:")
    for i, video_url in enumerate(video_urls, 1):
        print(f"{i}. {video_url}")

    choices = input(
        "👉 다운로드할 동영상 번호를 선택하세요 (예: 1,2,3 또는 all): "
    ).strip()

    if choices == "all":
        for video_url in video_urls:
            threaded_download(video_url, "video")
    else:
        try:
            selected_indices = [int(x) - 1 for x in choices.split(",")]
            for index in selected_indices:
                if 0 <= index < len(video_urls):
                    threaded_download(video_urls[index], "video")
        except ValueError:
            print("⚠️ 올바른 번호를 입력하세요!")


if __name__ == "__main__":
    main()
