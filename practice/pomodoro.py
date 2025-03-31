"""
✅ 25분 집중 → 5분 휴식
✅ 집중력 높이기 위한 시간 관리 기법
✅ 1시간을 2~3개의 “뽀모도로 단위”로 나눠서 일함
"""

import time

FOCUS_MINUTES = 25
BREAK_MINUTES = 5


def countdown(minutes, label):
    total_seconds = minutes * 60
    print(f"\n⏰ {label} 시작! ({minutes}분)")

    while total_seconds:
        mins, secs = divmod(total_seconds, 60)
        time_fmt = f"{mins:02d}:{secs:02d}"
        print(f"🕒 {label} 남은 시간: {time_fmt}", end="\r")
        time.sleep(1)
        total_seconds -= 1

    print(f"\n✅ {label} 종료!\n")


def main():
    print("🍅 Pomodoro 타이머에 오신 걸 환영합니다!")
    try:
        sessions = int(
            input("🎯 몇 세트를 진행하시겠습니까? (1세트 = 25분 집중 + 5분 휴식): ")
        )
    except ValueError:
        print("❌ 숫자를 입력해주세요.")
        return

    for i in range(1, sessions + 1):
        print(f"\n📚 {i}번째 세트")
        countdown(FOCUS_MINUTES, "집중")
        if i < sessions:
            countdown(BREAK_MINUTES, "휴식")

    print("🎉 모든 세션 완료! 수고하셨습니다!")


if __name__ == "__main__":
    main()
