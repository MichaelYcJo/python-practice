def display_menu():
    print("\n=== 🏦 은행 시뮬레이터 ===")
    print("1. 입금하기")
    print("2. 출금하기")
    print("3. 잔액 확인")
    print("4. 거래 내역 보기")
    print("5. 종료하기")


def get_valid_amount(prompt):
    try:
        amount = int(input(prompt).strip())
        if amount <= 0:
            print("❗ 0보다 큰 금액만 입력해주세요.")
            return None
        return amount
    except ValueError:
        print("❗ 숫자만 입력해주세요.")
        return None


def deposit(balance, log):
    amount = get_valid_amount("💰 입금할 금액을 입력하세요: ")
    if amount:
        balance += amount
        log.append(f"입금: {amount}원")
        print(f"✅ 입금 완료! 현재 잔액: {balance}원")
    return balance


def withdraw(balance, log):
    while True:
        amount = get_valid_amount("💸 출금할 금액을 입력하세요: ")
        if amount is None:
            continue
        if amount > balance:
            print(f"❗ 잔액이 부족합니다. 현재 잔액: {balance}원")
        else:
            balance -= amount
            log.append(f"출금: {amount}원")
            print(f"✅ 출금 완료! 현재 잔액: {balance}원")
            break
    return balance


def check_balance(balance):
    print(f"💼 현재 잔액: {balance}원")


def view_transaction_log(log):
    print("📋 거래 내역:")
    if not log:
        print("  - 거래 내역이 없습니다.")
    else:
        for entry in log:
            print(f"  - {entry}")


def main():
    balance = 0
    transaction_log = []

    while True:
        display_menu()
        choice = input("원하는 작업을 선택하세요 (1~5): ").strip()

        if choice == "1":
            balance = deposit(balance, transaction_log)
        elif choice == "2":
            balance = withdraw(balance, transaction_log)
        elif choice == "3":
            check_balance(balance)
        elif choice == "4":
            view_transaction_log(transaction_log)
        elif choice == "5":
            print("\n👋 이용해주셔서 감사합니다. 프로그램을 종료합니다.")
            break
        else:
            print("❗ 올바른 번호를 입력해주세요.")


if __name__ == "__main__":
    main()
