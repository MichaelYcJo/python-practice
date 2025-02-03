import time


def stopwatch():
    input("⏱️ Enter 키를 눌러 시작하세요...")
    start_time = time.time()  # 시작 시간 기록
    input("⏹ Enter 키를 눌러 정지하세요...")
    end_time = time.time()  # 종료 시간 기록

    elapsed_time = end_time - start_time  # 경과 시간 계산
    print(f"⏳ 경과 시간: {elapsed_time:.2f}초")


# 사용 예시
stopwatch()
