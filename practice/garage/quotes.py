import sys
import os
import random
from datetime import datetime
from pathlib import Path

QUOTES_FILE = Path(__file__).parent / "quotes.txt"

def load_quotes():
    """명언 목록을 파일에서 로드합니다."""
    try:
        if not QUOTES_FILE.exists():
            return []
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except (IOError, OSError) as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return []

def save_quotes(quotes):
    """명언 목록을 파일에 저장합니다."""
    try:
        QUOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUOTES_FILE, "w", encoding="utf-8") as f:
            for quote in quotes:
                f.write(quote + "\n")
    except (IOError, OSError) as e:
        print(f"파일을 저장하는 중 오류가 발생했습니다: {e}")
        return False
    return True

def add_quote(quote):
    """새로운 명언을 추가합니다."""
    quote = quote.strip()
    if not quote:
        print("빈 명언은 추가할 수 없습니다.")
        return
    
    quotes = load_quotes()
    if quote in quotes:
        print("이미 존재하는 명언입니다.")
        return
    
    quotes.append(quote)
    if save_quotes(quotes):
        print(f"✅ 명언이 추가되었습니다: {quote}")
    else:
        print("❌ 명언 추가에 실패했습니다.")

def list_quotes():
    """모든 명언을 출력합니다."""
    quotes = load_quotes()
    if not quotes:
        print("📝 저장된 명언이 없습니다.")
    else:
        print(f"📚 총 {len(quotes)}개의 명언이 있습니다:")
        print("-" * 50)
        for idx, quote in enumerate(quotes, 1):
            print(f"{idx:2}. {quote}")

def remove_quote(index):
    """지정된 번호의 명언을 삭제합니다."""
    quotes = load_quotes()
    if not quotes:
        print("삭제할 명언이 없습니다.")
        return
    
    if 0 < index <= len(quotes):
        removed = quotes.pop(index - 1)
        if save_quotes(quotes):
            print(f"✅ 명언이 삭제되었습니다: {removed}")
        else:
            print("❌ 명언 삭제에 실패했습니다.")
    else:
        print(f"❌ 잘못된 번호입니다. (1-{len(quotes)} 범위의 숫자를 입력하세요)")

def random_quote():
    """랜덤 명언을 출력합니다."""
    quotes = load_quotes()
    if not quotes:
        print("📝 저장된 명언이 없습니다.")
    else:
        selected_quote = random.choice(quotes)
        print("🌟 오늘의 명언 🌟")
        print("-" * 50)
        print(f"💭 {selected_quote}")
        print("-" * 50)

def search_quotes(keyword):
    """키워드로 명언을 검색합니다."""
    quotes = load_quotes()
    if not quotes:
        print("📝 저장된 명언이 없습니다.")
        return
    
    keyword = keyword.lower()
    found_quotes = [(idx, quote) for idx, quote in enumerate(quotes, 1) 
                   if keyword in quote.lower()]
    
    if not found_quotes:
        print(f"🔍 '{keyword}'을(를) 포함한 명언을 찾을 수 없습니다.")
    else:
        print(f"🔍 '{keyword}'을(를) 포함한 {len(found_quotes)}개의 명언:")
        print("-" * 50)
        for idx, quote in found_quotes:
            print(f"{idx:2}. {quote}")

def print_help():
    """사용법을 출력합니다."""
    print("📖 명언 관리 프로그램")
    print("=" * 50)
    print("사용법:")
    print("  python quotes.py add [명언]       # 명언 추가")
    print("  python quotes.py list             # 명언 목록 보기")
    print("  python quotes.py remove [번호]    # 명언 삭제")
    print("  python quotes.py random           # 랜덤 명언 출력")
    print("  python quotes.py search [키워드]  # 명언 검색")
    print("  python quotes.py help             # 도움말 출력")
    print("=" * 50)

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == "add":
        if len(sys.argv) >= 3:
            add_quote(" ".join(sys.argv[2:]))
        else:
            print("❌ 추가할 명언을 입력하세요.")
            print("예: python quotes.py add \"인생은 아름다워\"")
    
    elif cmd == "list":
        list_quotes()
    
    elif cmd == "remove":
        if len(sys.argv) == 3 and sys.argv[2].isdigit():
            remove_quote(int(sys.argv[2]))
        else:
            print("❌ 삭제할 명언의 번호를 입력하세요.")
            print("예: python quotes.py remove 1")
    
    elif cmd == "random":
        random_quote()
    
    elif cmd == "search":
        if len(sys.argv) >= 3:
            search_quotes(" ".join(sys.argv[2:]))
        else:
            print("❌ 검색할 키워드를 입력하세요.")
            print("예: python quotes.py search 인생")
    
    elif cmd == "help":
        print_help()
    
    else:
        print(f"❌ 알 수 없는 명령어: {cmd}")
        print_help()

if __name__ == "__main__":
    main() 