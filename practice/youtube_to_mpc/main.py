import os
import re
import tkinter as tk
from tkinter import messagebox
from pytube import YouTube
from moviepy.editor import AudioFileClip
from pathlib import Path
from datetime import datetime
import platform
import subprocess

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


def convert_url_to_mp3(url: str) -> str:
    yt = YouTube(url)
    title = yt.title
    safe_title = sanitize_filename(title)
    mp3_path = DOWNLOAD_DIR / f"{safe_title}.mp3"

    stream = yt.streams.filter(only_audio=True).first()
    if not stream:
        raise Exception("오디오 스트림을 찾을 수 없습니다.")

    video_path = Path(stream.download(output_path=DOWNLOAD_DIR))
    audio_clip = AudioFileClip(str(video_path))
    audio_clip.write_audiofile(str(mp3_path), verbose=False, logger=None)
    audio_clip.close()
    video_path.unlink()

    log_conversion(title, url, mp3_path.name)
    return mp3_path.name


def open_folder():
    if platform.system() == "Windows":
        os.startfile(DOWNLOAD_DIR)
    elif platform.system() == "Darwin":
        subprocess.call(["open", DOWNLOAD_DIR])
    elif platform.system() == "Linux":
        subprocess.call(["xdg-open", DOWNLOAD_DIR])
    else:
        messagebox.showinfo("알림", "이 OS에서는 폴더 열기 기능을 지원하지 않습니다.")


def start_conversion():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("입력 오류", "유튜브 URL을 입력해주세요.")
        return

    try:
        status_var.set("🎬 변환 중입니다...")
        root.update_idletasks()
        filename = convert_url_to_mp3(url)
        status_var.set(f"✅ 변환 완료: {filename}")
    except Exception as e:
        status_var.set("❌ 변환 실패")
        messagebox.showerror("오류 발생", str(e))


# 🖼️ GUI 구성
root = tk.Tk()
root.title("🎶 유튜브 MP3 변환기")
root.geometry("500x200")
root.resizable(False, False)

tk.Label(root, text="유튜브 URL 입력:", font=("Arial", 11)).pack(pady=10)
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

tk.Button(root, text="🎧 변환 시작", command=start_conversion, width=20).pack(pady=10)
tk.Button(root, text="📂 다운로드 폴더 열기", command=open_folder).pack()

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, fg="green", font=("Arial", 10))
status_label.pack(pady=10)

root.mainloop()

# python youtube_mp3_converter.py
# python youtube_mp3_converter.py --dry-run
