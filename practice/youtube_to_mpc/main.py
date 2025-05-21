import os
from pytube import YouTube
from moviepy.editor import AudioFileClip
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def download_youtube_video(url: str) -> Path:
    yt = YouTube(url)
    print(f"\n🎬 영상 제목: {yt.title}")

    video = yt.streams.filter(only_audio=True).first()
    if not video:
        raise Exception("❗ 오디오 스트림을 찾을 수 없습니다.")

    out_path = video.download(output_path=DOWNLOAD_DIR)
    print(f"⬇️ 다운로드 완료: {out_path}")
    return Path(out_path)


def convert_to_mp3(video_path: Path):
    mp3_path = video_path.with_suffix(".mp3")
    print(f"🎧 MP3 변환 중: {mp3_path.name}")
    try:
        audio_clip = AudioFileClip(str(video_path))
        audio_clip.write_audiofile(str(mp3_path), verbose=False, logger=None)
        audio_clip.close()
        video_path.unlink()  # mp4 파일 삭제
        print(f"✅ 저장 완료: {mp3_path.name}")
    except Exception as e:
        print(f"❗ 변환 실패: {e}")


def main():
    print("🎶 YouTube MP3 변환기 (CLI)")
    url = input("🔗 유튜브 영상 URL 입력: ").strip()

    try:
        video_path = download_youtube_video(url)
        convert_to_mp3(video_path)
    except Exception as e:
        print(f"❗ 오류 발생: {e}")


if __name__ == "__main__":
    main()
