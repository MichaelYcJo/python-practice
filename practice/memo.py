"""
	•	사용자가 입력한 메모를 파일에 저장 & 불러오기 가능
	•	날짜별 파일 자동 생성 (memo_YYYY-MM-DD.txt)
	•	메모 추가, 보기, 삭제 기능 제공
"""

import os
from datetime import datetime


def get_memo_filename():
    """현재 날짜를 기반으로 메모 파일명 생성"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"memo_{today}.txt"


def save_memo():
    """메모 저장"""
    filename = get_memo_filename()
    memo = input("✍️ 저장할 메모를 입력하세요:\n> ")

    with open(filename, "a", encoding="utf-8") as file:
        file.write(memo + "\n")

    print(f"✅ 메모가 '{filename}'에 저장되었습니다!")


def view_memo():
    """메모 보기"""
    filename = get_memo_filename()

    if not os.path.exists(filename):
        print("📭 저장된 메모가 없습니다!")
        return

    print(f"\n📖 '{filename}' 내용:")
    with open(filename, "r", encoding="utf-8") as file:
        print(file.read())


def delete_memo():
    """메모 삭제"""
    filename = get_memo_filename()

    if os.path.exists(filename):
        os.remove(filename)
        print(f"🗑️ '{filename}' 파일이 삭제되었습니다!")
    else:
        print("📭 삭제할 메모가 없습니다!")


def memo_app():
    """메모장 프로그램 실행"""
    while True:
        print("\n📝 간단한 메모장")
        print("1. 메모 작성")
        print("2. 메모 보기")
        print("3. 메모 삭제")
        print("4. 종료")

        choice = input("👉 메뉴 선택: ")

        if choice == "1":
            save_memo()
        elif choice == "2":
            view_memo()
        elif choice == "3":
            delete_memo()
        elif choice == "4":
            print("👋 프로그램을 종료합니다!")
            break
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")


# 실행
memo_app()
