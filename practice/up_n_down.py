import random
import time
import os
from colorama import Fore, Style, init

init(autoreset=True)

HIGH_SCORE_FILE = "high_score.txt"

DIFFICULTY_SETTINGS = {
    "1": ("Easy", 1, 50, 45),
    "2": ("Normal", 1, 100, 60),
    "3": ("Hard", 1, 500, 90),
}


def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE) as f:
            return int(f.read())
    return 0


def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))


def calculate_score(attempts, elapsed_time):
    base_score = 1000
    penalty = (attempts * 15) + int(elapsed_time)
    return max(base_score - penalty, 0)


def choose_difficulty():
    print(Fore.YELLOW + "\n🎮 난이도를 선택하세요:")
    print("1. Easy   (1~50)")
    print("2. Normal (1~100)")
    print("3. Hard   (1~500)")

    while True:
        choice = input("👉 선택 (1/2/3): ").strip()
        if choice in DIFFICULTY_SETTINGS:
            return DIFFICULTY_SETTINGS[choice]
        else:
            print(Fore.RED + "❌ 올바른 선택지를 입력하세요 (1, 2, 3)")


def play_game():
    difficulty_name, min_num, max_num, time_limit = choose_difficulty()

    print(
        Fore.MAGENTA
        + f"\n🔢 {difficulty_name} 모드 시작! 범위: {min_num}~{max_num} ⏱️ 제한 시간: {time_limit}초"
    )

    answer = random.randint(min_num, max_num)
    attempts = 0
    start_time = time.time()
    best_score = load_high_score()

    while True:
        if time.time() - start_time > time_limit:
            print(Fore.RED + "\n⏰ 제한 시간이 초과되었습니다! GAME OVER.")
            return

        guess = input(f"🔢 숫자를 입력하세요 ({min_num}~{max_num}): ").strip()

        if not guess.isdigit():
            print(Fore.YELLOW + "⚠️ 숫자만 입력해주세요.")
            continue

        guess = int(guess)

        if not (min_num <= guess <= max_num):
            print(Fore.YELLOW + "🚫 범위를 벗어났습니다!")
            continue

        attempts += 1

        if guess < answer:
            print(Fore.CYAN + "📉 너무 작아요!")
        elif guess > answer:
            print(Fore.CYAN + "📈 너무 커요!")
        else:
            elapsed = time.time() - start_time
            score = calculate_score(attempts, elapsed)
            print(Fore.GREEN + f"\n🎉 정답입니다! {attempts}번 만에 맞췄어요!")
            print(Fore.BLUE + f"🧠 걸린 시간: {int(elapsed)}초")
            print(Fore.LIGHTGREEN_EX + f"🏅 점수: {score}")

            if score > best_score:
                print(Fore.MAGENTA + "🏆 새로운 최고 점수 갱신!")
                save_high_score(score)
            else:
                print(Fore.LIGHTBLACK_EX + f"📊 현재 최고 점수: {best_score}")

            break


if __name__ == "__main__":
    print(Fore.CYAN + "🎯 숫자 맞추기 챌린지에 오신 걸 환영합니다!")
    play_game()
