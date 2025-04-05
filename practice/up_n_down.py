import random
import time
import os
from colorama import Fore, Style, init

init(autoreset=True)

BEST_SCORE_FILE = "best_score.txt"
TIME_LIMIT = 60  # 제한 시간 (초)


def load_best_score():
    if os.path.exists(BEST_SCORE_FILE):
        with open(BEST_SCORE_FILE) as f:
            return int(f.read())
    return None


def save_best_score(score):
    with open(BEST_SCORE_FILE, "w") as f:
        f.write(str(score))


def guess_the_number():
    print(Fore.MAGENTA + "🎮 숫자 맞추기 게임 시작!")
    print("1부터 100 사이의 숫자를 맞춰보세요. ⏱️ 제한 시간: 60초")

    secret_number = random.randint(1, 100)
    attempts = 0
    start_time = time.time()
    min_val, max_val = 1, 100
    best_score = load_best_score()

    while True:
        if time.time() - start_time > TIME_LIMIT:
            print(Fore.RED + "⏰ 제한 시간이 초과되었습니다! 게임 오버!")
            break

        guess = input(f"🔢 숫자 입력 ({min_val}~{max_val}): ").strip()
        if not guess.isdigit():
            print(Fore.YELLOW + "⚠️ 숫자만 입력해주세요!")
            continue

        guess = int(guess)
        if not (min_val <= guess <= max_val):
            print(Fore.YELLOW + "🚫 범위 내 숫자를 입력하세요!")
            continue

        attempts += 1

        if guess < secret_number:
            print(Fore.CYAN + "📉 너무 작아요!")
            min_val = max(min_val, guess + 1)
        elif guess > secret_number:
            print(Fore.CYAN + "📈 너무 커요!")
            max_val = min(max_val, guess - 1)
        else:
            print(Fore.GREEN + f"\n🎉 정답입니다! {attempts}번 만에 맞췄어요!")

            if best_score is None or attempts < best_score:
                print(Fore.GREEN + "🏆 새로운 최고 기록!")
                save_best_score(attempts)
            else:
                print(Fore.LIGHTBLUE_EX + f"📊 현재 최고 기록은 {best_score}번 입니다.")
            break


if __name__ == "__main__":
    guess_the_number()
