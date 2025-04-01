"""
✅ 25분 집중 → 5분 휴식
✅ 집중력 높이기 위한 시간 관리 기법
✅ 1시간을 2~3개의 “뽀모도로 단위”로 나눠서 일함
"""

import time
from datetime import datetime
from playsound import playsound
from colorama import init, Fore, Style
import os

init(autoreset=True)  # 컬러 초기화


def get_minutes_input(prompt, default):
    user_input = input(f"{prompt} (기본: {default}분): ").strip()
    return int(user_input) if user_input.isdigit() else default


def countdown(minutes, label, use_sound=True):
    total_seconds = minutes * 60
    print(Fore.YELLOW + f"\n⏰ {label} 시작! ({minutes}분)")

    while total_seconds:
        mins, secs = divmod(total_seconds, 60)
        time_fmt = f"{mins:02d}:{secs:02d}"
        print(Fore.CYAN + f"🕒 {label} 남은 시간: {time_fmt}", end="\r")
        time.sleep(1)
        total_seconds -= 1

    print(Fore.GREEN + f"\n✅ {label} 종료!")

    if use_sound:
        try:
            # 사용자 경로에 ding.mp3가 있어야 함
            playsound("ding.mp3")
        except:
            print(Fore.RED + "⚠️ 알림음 재생 실패 (ding.mp3 파일을 확인하세요)")


def log_session(session_count, focus_time, break_time):
    log_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 세션 {session_count}회 | 집중 {focus_time}분 / 휴식 {break_time}분\n"
    with open("pomodoro_log.txt", "a", encoding="utf-8") as f:
        f.write(log_line)


def main():
    print(Fore.MAGENTA + "🍅 Pomodoro 타이머에 오신 걸 환영합니다!")

    try:
        sessions = int(
            input("🎯 몇 세트를 진행하시겠습니까? (1세트 = 집중 + 휴식): ").strip()
        )
    except ValueError:
        print(Fore.RED + "❌ 유효한 숫자를 입력해주세요.")
        return

    focus_time = get_minutes_input("🧠 집중 시간", 25)
    break_time = get_minutes_input("🛋️ 휴식 시간", 5)
    sound_option = (
        input("🔔 종료 시 알림음을 재생할까요? (y/n, 기본: y): ").strip().lower()
    )
    use_sound = sound_option != "n"

    for i in range(1, sessions + 1):
        print(Fore.BLUE + f"\n📚 {i}번째 세트")
        countdown(focus_time, "집중", use_sound=use_sound)

        if i < sessions:
            countdown(break_time, "휴식", use_sound=use_sound)

    print(Fore.GREEN + "\n🎉 모든 세션 완료! 수고하셨습니다!")

    log_session(sessions, focus_time, break_time)
    print(Fore.LIGHTBLACK_EX + "📖 로그가 pomodoro_log.txt에 저장되었습니다.")


if __name__ == "__main__":
    main()
