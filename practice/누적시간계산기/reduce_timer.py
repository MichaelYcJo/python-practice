import re
from datetime import timedelta


def parse_duration(line):
    """한 줄에서 분/초 추출 후 timedelta로 반환"""
    match = re.search(r"소요 시간: (\d+)분 (\d+)초", line)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        return timedelta(minutes=minutes, seconds=seconds)
    return timedelta(0)


def calculate_total_time(file_path="time_log.txt"):
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("❌ time_log.txt 파일이 없습니다.")
        return

    total_time = timedelta()

    for line in lines:
        total_time += parse_duration(line)

    total_minutes = total_time.total_seconds() // 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    seconds = int(total_time.total_seconds() % 60)

    print("\n⏳ 전체 누적 작업 시간:")
    print(f"🕒 {hours}시간 {minutes}분 {seconds}초")


if __name__ == "__main__":
    calculate_total_time()
