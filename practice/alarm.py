import time
import os


def countdown_timer(seconds):
    """사용자가 입력한 시간(초) 동안 타이머 실행"""
    while seconds:
        mins, secs = divmod(seconds, 60)
        timer_display = f"{mins:02}:{secs:02}"
        print(f"\r⏳ 남은 시간: {timer_display}", end="")
        time.sleep(1)
        seconds -= 1

    print("\n⏰ 타이머 종료! 알람이 울립니다!")

    # 알람 소리 출력 (운영체제별 방식)
    try:
        if os.name == "nt":  # Windows
            import winsound

            winsound.Beep(1000, 1000)  # 주파수(1000Hz), 지속시간(1초)
        else:  # macOS, Linux
            os.system("echo -e '\a'")  # 터미널 알람 소리
    except Exception as e:
        print("⚠️ 알람 소리를 재생할 수 없습니다:", e)


# 실행
try:
    seconds = int(input("⏳ 타이머 시간을 입력하세요 (초 단위): "))
    countdown_timer(seconds)
except ValueError:
    print("⚠️ 숫자만 입력해주세요!")
