# python youtube_mp3_converter.py
# python youtube_mp3_converter.py --dry-run
# brew install ffmpeg  # macOS는 반드시 필요
# streamlit run main.py

import streamlit as st
from pytube import YouTube
import ffmpeg
import re, os
from pathlib import Path
from datetime import datetime

# 설정
DOWNLOAD_DIR = Path("downloads")
LOG_FILE = DOWNLOAD_DIR / "log.txt"
DOWNLOAD_DIR.mkdir(exist_ok=True)


def sanitize_filename(title: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", title)


def log_conversion(title: str, url: str, mp3_filename: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] 🎬 {title}\n")
        f.write(f"URL: {url}\n")
        f.write(f"MP3: {mp3_filename}\n\n")


def convert_to_mp3_ffmpeg(video_path: Path, mp3_path: Path):
    try:
        (
            ffmpeg.input(str(video_path))
            .output(
                str(mp3_path), format="mp3", acodec="libmp3lame", audio_bitrate="192k"
            )
            .overwrite_output()
            .run(quiet=True)
        )
        st.write(f"✅ MP3 변환 완료: `{mp3_path.name}`")
        video_path.unlink()
    except ffmpeg.Error as e:
        raise RuntimeError(f"ffmpeg 변환 실패: {e.stderr.decode()}")


def download_and_convert(url: str):
    try:
        yt = YouTube(url)
        title = "yt.title"  # 여기서 HTTPError 400이 발생할 수 있음
    except Exception as e:
        st.error("❌ 유튜브 영상 정보를 불러오는 데 실패했습니다.")
        st.exception(e)
        return

    st.write(f"🎬 **제목:** {title}")
    try:
        stream = yt.streams.filter(only_audio=True).first()
        out_path = stream.download(output_path=DOWNLOAD_DIR)
        video_path = Path(out_path)
        st.write(f"⬇️ 다운로드 완료: `{video_path.name}`")

        # MP3 변환
        safe_title = sanitize_filename(title)
        mp3_path = DOWNLOAD_DIR / f"{safe_title}.mp3"
        convert_to_mp3_ffmpeg(video_path, mp3_path)

        # 로그 기록
        log_conversion(title, url, mp3_path.name)
        return mp3_path
    except Exception as e:
        st.error("❌ 다운로드 또는 변환 중 오류가 발생했습니다.")
        st.exception(e)
        return


# Streamlit UI
st.title("🎶 YouTube MP3 변환기 (ffmpeg-python + 안정성 향상)")
url = st.text_input("🔗 유튜브 URL을 입력하세요")

if st.button("▶️ 변환 시작"):
    if not url:
        st.warning("URL을 입력해주세요.")
    else:
        st.write(f"📎 입력된 URL: `{url}`")
        mp3_file = download_and_convert(url)
        if mp3_file:
            st.success(f"파일 저장됨: `{mp3_file.name}`")
            with st.expander("📂 다운로드 폴더 경로"):
                st.write(f"`{DOWNLOAD_DIR.resolve()}`")

st.markdown("---")
st.write("#### 📄 변환 로그")
if LOG_FILE.exists():
    st.code(LOG_FILE.read_text(), language=None)
else:
    st.write("로그 파일이 없습니다.")
