import random


def guess_the_number():
    print("🎮 숫자 맞추기 게임 시작!")
    print("1부터 100 사이의 숫자를 맞춰보세요.")

    secret_number = random.randint(1, 100)
    attempts = 0

    while True:
        guess = input("🔢 숫자를 입력하세요: ").strip()
        if not guess.isdigit():
            print("❌ 숫자만 입력해주세요!")
            continue

        guess = int(guess)
        attempts += 1

        if guess < secret_number:
            print("📉 너무 작아요!")
        elif guess > secret_number:
            print("📈 너무 커요!")
        else:
            print(f"🎉 정답입니다! ({attempts}번 만에 맞춤)")
            break


if __name__ == "__main__":
    guess_the_number()
