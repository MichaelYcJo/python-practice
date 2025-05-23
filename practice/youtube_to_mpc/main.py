import os
from pytube import YouTube
from moviepy.editor import AudioFileClip
from pathlib import Path
from datetime import datetime
import re


# 설정
DOWNLOAD_DIR = Path("downloads")
LOG_FILE = DOWNLOAD_DIR / "log.txt"
URL_FILE = Path("urls.txt")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def sanitize_filename(title: str) -> str:
    # 위험 문자 제거
    return re.sub(r'[\\/*?:"<>|]', "", title)


def log_conversion(title: str, url: str, mp3_filename: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] 🎬 {title}\n")
        f.write(f"URL: {url}\n")
        f.write(f"MP3: {mp3_filename}\n\n")


def download_youtube_video(url: str) -> tuple[Path, str]:
    yt = YouTube(url)
    print(f"\n🎬 영상 제목: {yt.title}")
    video = yt.streams.filter(only_audio=True).first()
    if not video:
        raise Exception("❗ 오디오 스트림을 찾을 수 없습니다.")
    out_path = video.download(output_path=DOWNLOAD_DIR)
    print(f"⬇️ 다운로드 완료: {out_path}")
    return Path(out_path), yt.title


def convert_to_mp3(video_path: Path, title: str) -> Path:
    safe_title = sanitize_filename(title)
    mp3_path = DOWNLOAD_DIR / f"{safe_title}.mp3"
    print(f"🎧 MP3 변환 중: {mp3_path.name}")
    try:
        audio_clip = AudioFileClip(str(video_path))
        audio_clip.write_audiofile(str(mp3_path), verbose=False, logger=None)
        audio_clip.close()
        video_path.unlink()
        print(f"✅ 저장 완료: {mp3_path.name}")
        return mp3_path
    except Exception as e:
        print(f"❗ 변환 실패: {e}")
        return None


def process_url(url: str):
    try:
        video_path, title = download_youtube_video(url)
        mp3_path = convert_to_mp3(video_path, title)
        if mp3_path:
            log_conversion(title, url, mp3_path.name)
    except Exception as e:
        print(f"❗ [{url}] 오류 발생: {e}")


def main():
    print("🎶 YouTube MP3 변환기 (다중 URL 지원)")

    if not URL_FILE.exists():
        print("❗ 'urls.txt' 파일이 존재하지 않습니다.")
        return

    with open(URL_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("❗ 'urls.txt'에 유효한 URL이 없습니다.")
        return

    print(f"🔗 총 {len(urls)}개의 URL 변환 시작...\n")

    for idx, url in enumerate(urls, start=1):
        print(f"▶️ [{idx}/{len(urls)}] 처리 중: {url}")
        process_url(url)

    print("\n🎉 전체 변환 완료!")


if __name__ == "__main__":
    main()
