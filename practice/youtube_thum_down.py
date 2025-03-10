import requests
import os
import re
import webbrowser
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# 썸네일 저장 폴더
SAVE_PATH = "thumbnails"

# 지원하는 썸네일 해상도
THUMBNAIL_RESOLUTIONS = {
    "HD (최고 해상도)": "maxresdefault.jpg",
    "SD (고화질)": "sddefault.jpg",
    "MQ (중간 화질)": "mqdefault.jpg",
    "LQ (저화질)": "hqdefault.jpg",
}


def get_video_id(youtube_url):
    """유튜브 URL에서 비디오 ID 추출"""
    parsed_url = urlparse(youtube_url)
    if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.netloc in ["youtu.be"]:
        return parsed_url.path.lstrip("/")
    return None


def get_video_title(video_id):
    """유튜브 영상 제목 가져오기 (제목 기반 파일 저장)"""
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(youtube_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text.replace(" - YouTube", "").strip()
            title = re.sub(
                r'[\\/*?:"<>|]', "", title
            )  # 파일명에서 사용 불가능한 문자 제거
            return title
    return video_id  # 제목을 가져오지 못하면 기본적으로 video_id 사용


def download_thumbnail(video_id, resolution="maxresdefault.jpg"):
    """유튜브 썸네일 다운로드 (사용자 선택 가능)"""
    if not video_id:
        print("❌ 유효한 유튜브 URL이 아닙니다!")
        return

    video_title = get_video_title(video_id)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/{resolution}"
    response = requests.get(thumbnail_url, stream=True)

    if response.status_code == 200:
        if not os.path.exists(SAVE_PATH):
            os.makedirs(SAVE_PATH)

        file_path = os.path.join(SAVE_PATH, f"{video_title}.jpg")
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        print(f"✅ 썸네일 다운로드 완료! 📂 저장 위치: {file_path}")

        # 썸네일 미리보기
        show_thumbnail(file_path)
    else:
        print("❌ 썸네일을 다운로드할 수 없습니다.")


def show_thumbnail(file_path):
    """썸네일 미리보기 기능"""
    try:
        img = Image.open(file_path)
        img.show()
    except Exception as e:
        print(f"⚠️ 썸네일을 열 수 없습니다: {e}")


def main():
    """유튜브 썸네일 다운로드 프로그램 실행"""
    youtube_url = input("🎥 유튜브 영상 URL을 입력하세요: ").strip()
    video_id = get_video_id(youtube_url)

    if not video_id:
        print("❌ 올바른 유튜브 URL을 입력하세요.")
        return

    # 화질 선택 메뉴
    print("\n🎞️ 썸네일 해상도를 선택하세요:")
    resolutions = list(THUMBNAIL_RESOLUTIONS.keys())
    for i, res in enumerate(resolutions, 1):
        print(f"{i}. {res}")

    try:
        choice = int(input("👉 선택 (번호 입력): ")) - 1
        if choice < 0 or choice >= len(resolutions):
            raise ValueError
        selected_resolution = THUMBNAIL_RESOLUTIONS[resolutions[choice]]
    except ValueError:
        print("⚠️ 올바른 번호를 입력하세요!")
        return

    download_thumbnail(video_id, selected_resolution)


# 실행
main()
