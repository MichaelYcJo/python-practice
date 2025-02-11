import os

TODO_FILE = "todo_list.txt"

def load_tasks():
    """할 일 목록을 파일에서 불러오기"""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    return []

def save_tasks(tasks):
    """할 일 목록을 파일에 저장"""
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(tasks))

def show_tasks(tasks):
    """할 일 목록 출력"""
    if not tasks:
        print("📭 할 일이 없습니다!")
    else:
        print("\n📌 현재 할 일 목록:")
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task}")
    print()

def add_task(tasks):
    """할 일 추가"""
    task = input("➕ 추가할 할 일을 입력하세요: ")
    tasks.append(task)
    save_tasks(tasks)
    print(f"✅ '{task}' 추가 완료!\n")

def remove_task(tasks):
    """할 일 삭제"""
    show_tasks(tasks)
    try:
        index = int(input("❌ 삭제할 번호를 입력하세요: ")) - 1
        if 0 <= index < len(tasks):
            removed = tasks.pop(index)
            save_tasks(tasks)
            print(f"🗑️ '{removed}' 삭제 완료!\n")
        else:
            print("⚠️ 올바른 번호를 입력하세요.\n")
    except ValueError:
        print("⚠️ 숫자를 입력하세요.\n")

def todo_app():
    """할 일 관리 프로그램 실행"""
    tasks = load_tasks()

    while True:
        print("📋 할 일 관리 프로그램")
        print("1. 할 일 목록 보기")
        print("2. 할 일 추가")
        print("3. 할 일 삭제")
        print("4. 종료")
        
        choice = input("👉 메뉴 선택: ")
        
        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            remove_task(tasks)
        elif choice == "4":
            print("👋 프로그램을 종료합니다!")
            break
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")

# 실행
todo_app()