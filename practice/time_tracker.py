import time
from datetime import datetime


def main():
    print("⏱️ 간단한 작업 시간 추적기입니다.")
    task = input("💼 작업 이름을 입력하세요: ").strip()

    input("▶️ 작업을 시작하려면 Enter를 누르세요...")
    start_time = time.time()
    print("🟢 작업 시작!")

    input("⏹️ 작업을 종료하려면 Enter를 누르세요...")
    end_time = time.time()
    print("🔴 작업 종료!")

    duration = end_time - start_time
    minutes, seconds = divmod(int(duration), 60)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = f"[{now}] 작업: {task} | 소요 시간: {minutes}분 {seconds}초\n"

    print("\n📄 결과:")
    print(summary)

    with open("time_log.txt", "a", encoding="utf-8") as f:
        f.write(summary)

    print("✅ 기록이 time_log.txt에 저장되었습니다.")


if __name__ == "__main__":
    main()
