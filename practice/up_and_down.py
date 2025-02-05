import random


def number_guessing_game():
    number_to_guess = random.randint(1, 100)  # 1~100 사이 랜덤 숫자
    attempts = 0

    print("🎯 숫자 맞추기 게임을 시작합니다! (1~100 사이의 숫자)")

    while True:
        try:
            user_guess = int(input("🔢 숫자를 입력하세요: "))
            attempts += 1

            if user_guess < number_to_guess:
                print("⬆️ 더 큰 숫자를 입력하세요!")
            elif user_guess > number_to_guess:
                print("⬇️ 더 작은 숫자를 입력하세요!")
            else:
                print(f"🎉 정답입니다! {attempts}번 만에 맞췄어요!")
                break
        except ValueError:
            print("❌ 숫자만 입력해주세요!")


# 실행
number_guessing_game()
