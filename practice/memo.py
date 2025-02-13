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
        lines = file.readlines()
        for i, line in enumerate(lines, start=1):
            print(f"{i}. {line.strip()}")  # 줄번호 추가


def delete_memo():
    """메모 삭제"""
    filename = get_memo_filename()

    if os.path.exists(filename):
        os.remove(filename)
        print(f"🗑️ '{filename}' 파일이 삭제되었습니다!")
    else:
        print("📭 삭제할 메모가 없습니다!")


def edit_memo():
    """메모 수정"""
    filename = get_memo_filename()

    if not os.path.exists(filename):
        print("📭 수정할 메모가 없습니다!")
        return

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    view_memo()
    try:
        line_num = int(input("✏️ 수정할 줄 번호를 입력하세요: ")) - 1
        if 0 <= line_num < len(lines):
            new_text = input("📝 새 메모 내용을 입력하세요: ")
            lines[line_num] = new_text + "\n"

            with open(filename, "w", encoding="utf-8") as file:
                file.writelines(lines)
            print("✅ 메모 수정 완료!")
        else:
            print("⚠️ 올바른 줄 번호를 입력하세요.")
    except ValueError:
        print("⚠️ 숫자를 입력하세요.")


def search_memo():
    """메모 검색"""
    filename = get_memo_filename()

    if not os.path.exists(filename):
        print("📭 검색할 메모가 없습니다!")
        return

    keyword = input("🔍 검색할 키워드를 입력하세요: ").strip().lower()
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    matches = [line.strip() for line in lines if keyword in line.lower()]

    if matches:
        print("\n🔎 검색 결과:")
        for match in matches:
            print(f"- {match}")
    else:
        print("❌ 해당 키워드가 포함된 메모가 없습니다!")


def memo_app():
    """메모장 프로그램 실행"""
    while True:
        print("\n📝 간단한 메모장")
        print("1. 메모 작성")
        print("2. 메모 보기")
        print("3. 메모 수정 ✏️")
        print("4. 메모 삭제")
        print("5. 메모 검색 🔎")
        print("6. 종료")

        choice = input("👉 메뉴 선택: ")

        if choice == "1":
            save_memo()
        elif choice == "2":
            view_memo()
        elif choice == "3":
            edit_memo()  # 수정 기능 추가
        elif choice == "4":
            delete_memo()
        elif choice == "5":
            search_memo()  # 검색 기능 추가
        elif choice == "6":
            print("👋 프로그램을 종료합니다!")
            break
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")


# 실행
memo_app()
