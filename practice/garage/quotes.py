import sys
import os
import random
from datetime import datetime

QUOTES_FILE = "quotes.txt"

def load_quotes():
    if not os.path.exists(QUOTES_FILE):
        return []
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_quotes(quotes):
    with open(QUOTES_FILE, "w", encoding="utf-8") as f:
        for quote in quotes:
            f.write(quote + "\n")

def add_quote(quote):
    quotes = load_quotes()
    quotes.append(quote)
    save_quotes(quotes)
    print(f"명언 추가됨: {quote}")

def list_quotes():
    quotes = load_quotes()
    if not quotes:
        print("저장된 명언이 없습니다.")
    else:
        for idx, quote in enumerate(quotes, 1):
            print(f"{idx}. {quote}")

def remove_quote(index):
    quotes = load_quotes()
    if 0 < index <= len(quotes):
        removed = quotes.pop(index - 1)
        save_quotes(quotes)
        print(f"명언 삭제됨: {removed}")
    else:
        print("잘못된 번호입니다.")

def random_quote():
    quotes = load_quotes()
    if not quotes:
        print("저장된 명언이 없습니다.")
    else:
        print("오늘의 명언:")
        print(random.choice(quotes))

def print_help():
    print("사용법:")
    print("  python garage.py add [명언]      # 명언 추가")
    print("  python garage.py list            # 명언 목록 보기")
    print("  python garage.py remove [번호]   # 명언 삭제")
    print("  python garage.py random          # 랜덤 명언 출력")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
    else:
        cmd = sys.argv[1]
        if cmd == "add" and len(sys.argv) >= 3:
            add_quote(" ".join(sys.argv[2:]))
        elif cmd == "list":
            list_quotes()
        elif cmd == "remove" and len(sys.argv) == 3 and sys.argv[2].isdigit():
            remove_quote(int(sys.argv[2]))
        elif cmd == "random":
            random_quote()
        else:
            print_help() 