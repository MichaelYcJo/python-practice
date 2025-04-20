import random


def generate_account_number(existing_numbers):
    while True:
        account_number = "".join([str(random.randint(0, 9)) for _ in range(8)])
        if account_number not in existing_numbers:
            return account_number


def display_main_menu():
    print("\n=== 🏦 은행 시스템 ===")
    print("1. 신규 계좌 개설")
    print("2. 로그인 (계좌번호 + 비밀번호)")
    print("3. 전체 계좌 목록 보기")
    print("4. 종료")


def display_account_menu(account_number, user_name):
    print(f"\n👤 {user_name} 님 ({account_number}) 계좌")
    print("1. 입금")
    print("2. 출금")
    print("3. 잔액 확인")
    print("4. 거래 내역")
    print("5. 이자 1회 적용")
    print("6. 월별 이자 시뮬레이션")
    print("7. 로그아웃")


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


def get_valid_interest_rate():
    try:
        rate = float(input("📈 적용할 이자율을 입력하세요 (예: 3.5): ").strip())
        if rate < 0:
            print("❗ 이자율은 0 이상이어야 합니다.")
            return None
        return rate
    except ValueError:
        print("❗ 숫자 형식으로 입력해주세요.")
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


def apply_interest(account, month=None):
    rate = account["interest_rate"]
    interest = int(account["balance"] * (rate / 100))
    if interest > 0:
        account["balance"] += interest
        if month:
            account["log"].append(f"{month}개월차 이자: {interest}원")
            print(
                f"📅 {month}개월차 → 이자 {interest}원 적용 (잔액: {account['balance']}원)"
            )
        else:
            account["log"].append(f"이자 적용: {interest}원 (이자율 {rate}%)")
            print(f"💰 {rate}% 이자 적용 완료! 이자 {interest}원이 추가되었습니다.")
            print(f"💼 현재 잔액: {account['balance']}원")
    else:
        print("📉 잔액이 적어 이자가 0원입니다.")


def simulate_monthly_interest(account):
    months = get_valid_amount("⏳ 몇 개월을 시뮬레이션할까요? ")
    if not months:
        return

    print(f"\n🗓️ {months}개월 간 월별 이자 시뮬레이션 시작!")
    for month in range(1, months + 1):
        apply_interest(account, month)
    print(f"✅ 시뮬레이션 종료! 최종 잔액: {account['balance']}원")


def account_session(account_number, accounts):
    account = accounts[account_number]
    user_name = account["name"]

    while True:
        display_account_menu(account_number, user_name)
        choice = input("선택 (1~7): ").strip()

        if choice == "1":
            deposit(account)
        elif choice == "2":
            withdraw(account)
        elif choice == "3":
            check_balance(account)
        elif choice == "4":
            view_transaction_log(account)
        elif choice == "5":
            apply_interest(account)
        elif choice == "6":
            simulate_monthly_interest(account)
        elif choice == "7":
            print(f"👋 {user_name} 님 로그아웃되었습니다.")
            break
        else:
            print("❗ 올바른 번호를 입력해주세요.")


def login(accounts):
    account_number = input("🔐 계좌번호 8자리를 입력하세요: ").strip()
    if account_number not in accounts:
        print("❗ 존재하지 않는 계좌번호입니다.")
        return

    for attempt in range(3):
        password = input("🔑 비밀번호를 입력하세요: ").strip()
        if password == accounts[account_number]["password"]:
            print(f"✅ 로그인 성공! {accounts[account_number]['name']} 님 환영합니다.")
            account_session(account_number, accounts)
            return
        else:
            print(f"❗ 비밀번호가 일치하지 않습니다. (남은 시도: {2 - attempt})")

    print("🚫 로그인 3회 실패. 메인 메뉴로 돌아갑니다.")


def main():
    accounts = {}

    while True:
        display_main_menu()
        choice = input("선택 (1~4): ").strip()

        if choice == "1":
            user_name = input("👤 사용자 이름을 입력하세요: ").strip()
            password = input("🔑 사용할 비밀번호를 입력하세요: ").strip()
            interest_rate = get_valid_interest_rate()
            if interest_rate is None:
                continue

            new_account_number = generate_account_number(accounts)
            accounts[new_account_number] = {
                "name": user_name,
                "password": password,
                "interest_rate": interest_rate,
                "balance": 0,
                "log": [],
            }
            print(
                f"✅ 계좌 생성 완료! 계좌번호: {new_account_number}, 이자율: {interest_rate}%"
            )

        elif choice == "2":
            login(accounts)

        elif choice == "3":
            if not accounts:
                print("📂 생성된 계좌가 없습니다.")
            else:
                print("📋 전체 계좌 목록:")
                for number, info in accounts.items():
                    print(
                        f"  - {info['name']} | 계좌번호: {number} | 잔액: {info['balance']}원 | 이자율: {info['interest_rate']}%"
                    )

        elif choice == "4":
            print("👋 은행 시스템을 종료합니다.")
            break

        else:
            print("❗ 올바른 메뉴 번호를 입력해주세요.")


if __name__ == "__main__":
    main()
