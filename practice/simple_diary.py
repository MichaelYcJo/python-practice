import os
from datetime import datetime


def write_diary():
    # 현재 날짜 기반 파일명 생성
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"diary_{today}.txt"

    print("📖 오늘의 일기를 작성하세요! (종료하려면 빈 줄에서 Enter)")

    diary_content = []

    while True:
        line = input("> ")
        if line == "":  # 빈 줄 입력 시 종료
            break
        diary_content.append(line)

    # 파일 저장
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(diary_content))

    print(f"✅ '{filename}' 파일에 저장되었습니다!")


# 실행
write_diary()
