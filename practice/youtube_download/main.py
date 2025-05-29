import os
import re
import requests
import yt_dlp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

SAVE_PATH = "./downloaded"
PROXY = None


def get_video_urls_from_page(url):
    response = requests.get(
        url, proxies={"http": PROXY, "https": PROXY} if PROXY else None
    )
    if response.status_code != 200:
        print("❌ 웹페이지를 불러올 수 없습니다.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    video_urls = []

    for tag in soup.find_all("video") + soup.find_all("source"):
        src = tag.get("src")
        if src:
            video_urls.append(urljoin(url, src))

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if ".m3u8" in href:
            video_urls.append(urljoin(url, href))

    return list(set(video_urls))


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"⬇️ {percent} | {speed} | 남은 시간: {eta}", end="\r")
    elif d["status"] == "finished":
        print(f"\n✅ 다운로드 완료: {d['filename']}")


def get_unique_filename(filepath):
    """중복 파일 방지용 유니크 파일 경로 반환"""
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base} ({counter}){ext}"
        counter += 1
    return filepath


def download_media(video_url, media_type="video"):
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    # 타이틀 미리 추출 (덮어쓰기 확인을 위해 필요)
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get("title", "downloaded")
            ext = "mp3" if media_type == "audio" else "mp4"
            file_path = os.path.join(SAVE_PATH, f"{title}.{ext}")
    except Exception as e:
        print(f"\n❌ 미리보기 실패: {e}")
        return

    # 파일이 이미 존재하면 덮어쓸지 확인
    if os.path.exists(file_path):
        print(f"\n⚠️ 파일이 이미 존재합니다: {file_path}")
        overwrite = input("👉 덮어쓰시겠습니까? (y/n): ").strip().lower()
        if overwrite != "y":
            file_path = get_unique_filename(file_path)
            print(f"📄 새 파일명으로 저장합니다: {file_path}")

    ydl_opts = {
        "outtmpl": file_path,
        "format": (
            "bestaudio/best" if media_type == "audio" else "bestvideo+bestaudio/best"
        ),
        "merge_output_format": "mp3" if media_type == "audio" else "mp4",
        "progress_hooks": [progress_hook],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            media_type_text = "MP3 오디오" if media_type == "audio" else "MP4 비디오"
            print(f"📂 저장 위치: {file_path}")
        except Exception as e:
            print(f"\n❌ 다운로드 실패: {e}")


def main():
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

        download_media(website_url, media_type)
        return

    video_urls = get_video_urls_from_page(website_url)
    if not video_urls:
        print("⚠️ 이 페이지에서 동영상 URL을 찾을 수 없습니다.")
        use_yt_dlp = input("📡 yt-dlp로 시도할까요? (y/n): ").strip().lower() == "y"
        if use_yt_dlp:
            download_media(website_url, "video")
        return

    print("\n🎥 찾은 동영상 목록:")
    for i, video_url in enumerate(video_urls, 1):
        print(f"{i}. {video_url}")

    choices = input(
        "👉 다운로드할 동영상 번호를 선택하세요 (예: 1,2 또는 all): "
    ).strip()
    selected_urls = []

    if choices == "all":
        selected_urls = video_urls
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choices.split(",")]
            selected_urls = [video_urls[i] for i in indices if 0 <= i < len(video_urls)]
        except ValueError:
            print("⚠️ 올바른 번호를 입력하세요!")
            return

    if not selected_urls:
        print("⚠️ 선택된 URL이 없습니다.")
        return

    print("\n🚀 다운로드 시작 (최대 동시 다운로드: 3)")
    with ThreadPoolExecutor(max_workers=3) as executor:
        for url in selected_urls:
            executor.submit(download_media, url, "video")


if __name__ == "__main__":
    main()
