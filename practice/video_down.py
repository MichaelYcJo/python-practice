import os
import re
import requests
import yt_dlp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from tqdm import tqdm
import threading

SAVE_PATH = "downloaded_videos"


def get_video_urls_from_page(url):
    """웹페이지에서 비디오 URL 찾기"""
    response = requests.get(url)

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

    # 중복 제거 후 반환
    return list(set(video_urls))


def get_video_title(url):
    """웹페이지에서 비디오 제목 가져오기"""
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text.strip()
            title = re.sub(
                r'[\\/*?:"<>|]', "", title
            )  # 파일명에서 사용 불가능한 문자 제거
            return title
    return "video"


def download_video(video_url):
    """단순 HTTP 다운로드 (MP4, WebM 등)"""
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    file_name = get_video_title(video_url)
    file_extension = os.path.splitext(urlparse(video_url).path)[-1]
    file_path = os.path.join(SAVE_PATH, f"{file_name}{file_extension}")

    response = requests.get(video_url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    if response.status_code == 200:
        with open(file_path, "wb") as file, tqdm(
            total=total_size, unit="B", unit_scale=True, desc=file_name
        ) as progress_bar:
            for chunk in response.iter_content(1024):
                file.write(chunk)
                progress_bar.update(len(chunk))

        print(f"\n✅ 동영상 다운로드 완료! 📂 저장 위치: {file_path}")
    else:
        print("❌ 동영상을 다운로드할 수 없습니다.")


def download_streaming_video(video_url):
    """스트리밍 동영상 다운로드 (yt-dlp 사용)"""
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    ydl_opts = {
        "outtmpl": os.path.join(SAVE_PATH, "%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            print(f"✅ 스트리밍 동영상 다운로드 완료!")
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")


def threaded_download(video_url):
    """멀티스레드 다운로드 실행"""
    thread = threading.Thread(target=download_video, args=(video_url,))
    thread.start()


def main():
    """사용자 입력을 받아 웹사이트에서 동영상 다운로드"""
    website_url = input("🌐 동영상이 포함된 웹페이지 URL을 입력하세요: ").strip()
    video_urls = get_video_urls_from_page(website_url)

    if not video_urls:
        print("⚠️ 이 페이지에서 직접 찾을 수 있는 동영상 URL이 없습니다.")
        use_yt_dlp = (
            input("📡 yt-dlp를 사용하여 다운로드를 시도할까요? (y/n): ").strip().lower()
            == "y"
        )
        if use_yt_dlp:
            download_streaming_video(website_url)
        return

    print("\n🎥 찾은 동영상 목록:")
    for i, video_url in enumerate(video_urls, 1):
        print(f"{i}. {video_url}")

    try:
        choice = int(
            input("👉 다운로드할 동영상 번호를 선택하세요 (0: 취소): ").strip()
        )
        if choice == 0:
            return
        selected_video_url = video_urls[choice - 1]
        threaded_download(selected_video_url)  # 멀티스레드 다운로드 실행
    except (ValueError, IndexError):
        print("⚠️ 올바른 번호를 입력하세요!")


# 실행
main()
