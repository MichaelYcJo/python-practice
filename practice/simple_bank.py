def display_main_menu():
    print("\n=== 🏦 은행 시스템 ===")
    print("1. 로그인 또는 계좌 생성")
    print("2. 전체 계좌 목록 보기")
    print("3. 종료")


def display_account_menu(username):
    print(f"\n👤 {username} 님의 계좌")
    print("1. 입금")
    print("2. 출금")
    print("3. 잔액 확인")
    print("4. 거래 내역")
    print("5. 로그아웃")


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


def deposit(account):
    amount = get_valid_amount("💰 입금할 금액: ")
    if amount:
        account["balance"] += amount
        account["log"].append(f"입금: {amount}원")
        print(f"✅ 입금 완료! 현재 잔액: {account['balance']}원")


def withdraw(account):
    while True:
        amount = get_valid_amount("💸 출금할 금액: ")
        if amount is None:
            continue
        if amount > account["balance"]:
            print(f"❗ 잔액 부족. 현재 잔액: {account['balance']}원")
        else:
            account["balance"] -= amount
            account["log"].append(f"출금: {amount}원")
            print(f"✅ 출금 완료! 현재 잔액: {account['balance']}원")
            break


def check_balance(account):
    print(f"💼 현재 잔액: {account['balance']}원")


def view_transaction_log(account):
    print("📋 거래 내역:")
    if not account["log"]:
        print("  - 거래 내역이 없습니다.")
    else:
        for entry in account["log"]:
            print(f"  - {entry}")


def account_session(username, accounts):
    account = accounts[username]

    while True:
        display_account_menu(username)
        choice = input("선택 (1~5): ").strip()

        if choice == "1":
            deposit(account)
        elif choice == "2":
            withdraw(account)
        elif choice == "3":
            check_balance(account)
        elif choice == "4":
            view_transaction_log(account)
        elif choice == "5":
            print(f"👋 {username} 님 로그아웃되었습니다.")
            break
        else:
            print("❗ 올바른 번호를 입력해주세요.")


def main():
    accounts = {}

    while True:
        display_main_menu()
        choice = input("선택 (1~3): ").strip()

        if choice == "1":
            username = input("👤 사용자 이름을 입력하세요: ").strip()
            if username not in accounts:
                print("🆕 신규 계좌 생성 중...")
                accounts[username] = {"balance": 0, "log": []}
                print(f"✅ {username} 님의 계좌가 생성되었습니다.")
            else:
                print(f"🔐 {username} 님 로그인 성공.")
            account_session(username, accounts)

        elif choice == "2":
            if not accounts:
                print("📂 생성된 계좌가 없습니다.")
            else:
                print("📋 전체 계좌 목록:")
                for user in accounts:
                    print(f"  - {user} (잔액: {accounts[user]['balance']}원)")

        elif choice == "3":
            print("👋 은행 시스템을 종료합니다.")
            break

        else:
            print("❗ 올바른 메뉴 번호를 입력해주세요.")


if __name__ == "__main__":
    main()
