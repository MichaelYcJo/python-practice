import os
import re
import requests
import yt_dlp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from tqdm import tqdm
import threading
import subprocess

SAVE_PATH = "downloaded_videos"
PROXY = None  # 필요하면 여기에 프록시 설정 ("http://proxyserver:port")


def convert_to_mp4(input_file):
    """WebM을 MP4로 변환 (FFmpeg 사용)"""
    output_file = input_file.replace(".webm", ".mp4")
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_file, "-c:v", "copy", "-c:a", "aac", output_file],
            check=True,
        )
        os.remove(input_file)  # 변환 후 원본 WebM 삭제
        print(f"✅ WebM → MP4 변환 완료: {output_file}")
    except Exception as e:
        print(f"⚠️ 변환 실패: {e}")


def get_video_urls_from_page(url):
    """웹페이지에서 비디오 URL 찾기"""
    response = requests.get(
        url, proxies={"http": PROXY, "https": PROXY} if PROXY else None
    )

    if response.status_code != 200:
        print("❌ 웹페이지를 불러올 수 없습니다.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # <video> 태그 내 src 속성 찾기
    video_tags = soup.find_all("video")
    source_tags = soup.find_all("source")
    m3u8_tags = soup.find_all("a", href=True)

    video_urls = []

    for tag in video_tags:
        src = tag.get("src")
        if src:
            video_urls.append(urljoin(url, src))  # 상대경로 처리

    for tag in source_tags:
        src = tag.get("src")
        if src:
            video_urls.append(urljoin(url, src))

    for tag in m3u8_tags:
        href = tag["href"]
        if ".m3u8" in href:
            video_urls.append(urljoin(url, href))

    return list(set(video_urls))  # 중복 제거


def download_streaming_video(video_url):
    """스트리밍 동영상 다운로드 (yt-dlp 사용, MP4 강제 설정)"""
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    ydl_opts = {
        "outtmpl": os.path.join(SAVE_PATH, "%(title)s.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            print(f"✅ MP4 동영상 다운로드 완료! 📂 저장 위치: {SAVE_PATH}")
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")


def threaded_download(video_url):
    """멀티스레드 다운로드 실행"""
    thread = threading.Thread(target=download_streaming_video, args=(video_url,))
    thread.start()


def main():
    """사용자 입력을 받아 웹사이트에서 동영상 다운로드"""
    website_url = input("🌐 동영상이 포함된 웹페이지 URL을 입력하세요: ").strip()

    # 유튜브, 트위치, 넷플릭스 등 자동 감지
    if any(
        x in website_url
        for x in ["youtube.com", "youtu.be", "twitch.tv", "netflix.com"]
    ):
        print("🎞️ 스트리밍 사이트 감지됨! yt-dlp를 사용하여 다운로드합니다.")
        threaded_download(website_url)
        return

    video_urls = get_video_urls_from_page(website_url)

    if not video_urls:
        print("⚠️ 이 페이지에서 직접 찾을 수 있는 동영상 URL이 없습니다.")
        use_yt_dlp = (
            input("📡 yt-dlp를 사용하여 다운로드를 시도할까요? (y/n): ").strip().lower()
            == "y"
        )
        if use_yt_dlp:
            threaded_download(website_url)
        return

    print("\n🎥 찾은 동영상 목록:")
    for i, video_url in enumerate(video_urls, 1):
        print(f"{i}. {video_url}")

    choices = input(
        "👉 다운로드할 동영상 번호를 선택하세요 (예: 1,2,3 또는 all): "
    ).strip()

    if choices == "all":
        for video_url in video_urls:
            threaded_download(video_url)  # 모든 동영상 다운로드
    else:
        try:
            selected_indices = [int(x) - 1 for x in choices.split(",")]
            for index in selected_indices:
                if 0 <= index < len(video_urls):
                    threaded_download(video_urls[index])
        except ValueError:
            print("⚠️ 올바른 번호를 입력하세요!")


# 실행
main()
