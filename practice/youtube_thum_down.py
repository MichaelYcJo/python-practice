import requests
import os
from urllib.parse import urlparse, parse_qs


def get_video_id(youtube_url):
    """유튜브 URL에서 비디오 ID 추출"""
    parsed_url = urlparse(youtube_url)
    if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.netloc in ["youtu.be"]:
        return parsed_url.path.lstrip("/")
    return None


def download_thumbnail(video_id, save_path="thumbnails"):
    """유튜브 썸네일 다운로드"""
    if not video_id:
        print("❌ 유효한 유튜브 URL이 아닙니다!")
        return

    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    response = requests.get(thumbnail_url, stream=True)

    if response.status_code == 200:
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path = os.path.join(save_path, f"{video_id}.jpg")
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        print(f"✅ 썸네일 다운로드 완료! 📂 저장 위치: {file_path}")
    else:
        print("⚠️ HD 썸네일이 존재하지 않습니다. 기본 품질로 다운로드합니다.")
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        response = requests.get(thumbnail_url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(save_path, f"{video_id}_hq.jpg")
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"✅ 기본 품질 썸네일 다운로드 완료! 📂 저장 위치: {file_path}")
        else:
            print("❌ 썸네일을 다운로드할 수 없습니다.")


def main():
    """유튜브 썸네일 다운로드 프로그램 실행"""
    youtube_url = input("🎥 유튜브 영상 URL을 입력하세요: ").strip()
    video_id = get_video_id(youtube_url)
    download_thumbnail(video_id)


# 실행
main()
