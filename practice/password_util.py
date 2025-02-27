import base64
import json
import os

PASSWORD_FILE = "passwords.json"


def load_passwords():
    """저장된 비밀번호 파일 불러오기"""
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_passwords(passwords):
    """비밀번호 파일 저장"""
    with open(PASSWORD_FILE, "w", encoding="utf-8") as file:
        json.dump(passwords, file, indent=4)


def encode_password(password):
    """비밀번호 암호화 (Base64)"""
    return base64.b64encode(password.encode()).decode()


def decode_password(encoded_password):
    """비밀번호 복호화"""
    return base64.b64decode(encoded_password.encode()).decode()


def add_password():
    """비밀번호 저장"""
    site = input("🔐 저장할 사이트/서비스 이름을 입력하세요: ")
    username = input("👤 사용자 이름을 입력하세요: ")
    password = input("🔑 비밀번호를 입력하세요: ")

    passwords = load_passwords()
    passwords[site] = {"username": username, "password": encode_password(password)}

    save_passwords(passwords)
    print(f"✅ {site}의 비밀번호가 저장되었습니다!\n")


def get_password():
    """비밀번호 조회"""
    site = input("🔍 조회할 사이트/서비스 이름을 입력하세요: ")

    passwords = load_passwords()
    if site in passwords:
        print(f"\n🔐 {site}의 로그인 정보:")
        print(f"👤 사용자 이름: {passwords[site]['username']}")
        print(f"🔑 비밀번호: {decode_password(passwords[site]['password'])}\n")
    else:
        print("❌ 해당 사이트의 비밀번호가 없습니다!\n")


def delete_password():
    """비밀번호 삭제"""
    site = input("🗑 삭제할 사이트/서비스 이름을 입력하세요: ")

    passwords = load_passwords()
    if site in passwords:
        del passwords[site]
        save_passwords(passwords)
        print(f"🗑 {site}의 비밀번호가 삭제되었습니다!\n")
    else:
        print("❌ 해당 사이트의 비밀번호가 없습니다!\n")


def password_manager():
    """비밀번호 관리 프로그램 실행"""
    while True:
        print("\n🔐 비밀번호 관리 프로그램")
        print("1. 비밀번호 저장")
        print("2. 비밀번호 조회")
        print("3. 비밀번호 삭제")
        print("4. 종료")

        choice = input("👉 메뉴 선택: ")

        if choice == "1":
            add_password()
        elif choice == "2":
            get_password()
        elif choice == "3":
            delete_password()
        elif choice == "4":
            print("👋 프로그램을 종료합니다!")
            break
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")


# 실행
password_manager()
