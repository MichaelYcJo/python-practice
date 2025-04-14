def display_menu():
    print("\n=== 🏦 은행 시뮬레이터 ===")
    print("1. 입금하기")
    print("2. 출금하기")
    print("3. 잔액 확인")
    print("4. 종료하기")


def deposit(balance):
    amount = input("💰 입금할 금액을 입력하세요: ")
    if amount.isdigit():
        balance += int(amount)
        print(f"✅ 입금 완료! 현재 잔액: {balance}원")
    else:
        print("❗ 잘못된 입력입니다.")
    return balance


def withdraw(balance):
    amount = input("💸 출금할 금액을 입력하세요: ")
    if amount.isdigit():
        amount = int(amount)
        if amount <= balance:
            balance -= amount
            print(f"✅ 출금 완료! 현재 잔액: {balance}원")
        else:
            print("❗ 잔액이 부족합니다.")
    else:
        print("❗ 잘못된 입력입니다.")
    return balance


def check_balance(balance):
    print(f"💼 현재 잔액: {balance}원")


def main():
    balance = 0
    while True:
        display_menu()
        choice = input("원하는 작업을 선택하세요 (1~4): ").strip()

        if choice == "1":
            balance = deposit(balance)
        elif choice == "2":
            balance = withdraw(balance)
        elif choice == "3":
            check_balance(balance)
        elif choice == "4":
            print("👋 이용해주셔서 감사합니다!")
            break
        else:
            print("❗ 올바른 번호를 입력해주세요.")


if __name__ == "__main__":
    main()
