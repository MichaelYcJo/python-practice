import random


def get_user_choice():
    choices = ["가위", "바위", "보"]
    while True:
        user_input = input("당신의 선택 (가위, 바위, 보): ").strip()
        if user_input in choices:
            return user_input
        print("❗ 잘못된 입력입니다. 다시 입력해주세요.")


def get_computer_choice():
    return random.choice(["가위", "바위", "보"])


def determine_winner(user, computer):
    if user == computer:
        return "비겼습니다!"
    elif (
        (user == "가위" and computer == "보")
        or (user == "바위" and computer == "가위")
        or (user == "보" and computer == "바위")
    ):
        return "🎉 당신이 이겼습니다!"
    else:
        return "😢 컴퓨터가 이겼습니다!"


def main():
    print("=== 🎮 가위바위보 게임 ===")
    while True:
        user = get_user_choice()
        computer = get_computer_choice()
        print(f"🤖 컴퓨터의 선택: {computer}")
        result = determine_winner(user, computer)
        print(f"🧾 결과: {result}")

        again = input("다시 하시겠습니까? (y/n): ").strip().lower()
        if again != "y":
            print("👋 게임을 종료합니다.")
            break


if __name__ == "__main__":
    main()
