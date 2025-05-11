import json
import os
import random
import string
from getpass import getpass
from cryptography.fernet import Fernet
import base64
import hashlib

VAULT_FILE = "vault.json"


# ===============================
# 🔐 암호화 관련 함수
# ===============================
def generate_key(master_password: str) -> bytes:
    hashed = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)


def encrypt_data(data: str, fernet: Fernet) -> str:
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(data: str, fernet: Fernet) -> str:
    return fernet.decrypt(data.encode()).decode()


def load_vault():
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_vault(vault: dict):
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(vault, f, indent=2, ensure_ascii=False)


# ===============================
# 🔐 자동 비밀번호 생성기
# ===============================
def generate_password(length=12, use_digits=True, use_uppercase=True, use_special=True):
    characters = string.ascii_lowercase
    required = [random.choice(string.ascii_lowercase)]

    if use_digits:
        characters += string.digits
        required.append(random.choice(string.digits))
    if use_uppercase:
        characters += string.ascii_uppercase
        required.append(random.choice(string.ascii_uppercase))
    if use_special:
        characters += string.punctuation
        required.append(random.choice(string.punctuation))

    if length < len(required):
        raise ValueError(f"암호 길이는 최소 {len(required)}자 이상이어야 합니다.")

    remaining = [random.choice(characters) for _ in range(length - len(required))]
    full = required + remaining
    random.shuffle(full)
    return "".join(full)


# ===============================
# 📘 메인 로직
# ===============================
def main():
    print("🔐 패스워드 저장소 (자동 생성 포함)")
    master_password = getpass("마스터 비밀번호를 입력하세요: ")
    key = generate_key(master_password)
    fernet = Fernet(key)

    vault = load_vault()

    while True:
        print("\n[1] 저장하기  [2] 조회하기  [3] 사이트 목록 보기  [0] 종료")
        choice = input("선택: ").strip()

        if choice == "1":
            site = input("사이트 이름: ").strip()
            username = input("아이디: ").strip()

            print("\n비밀번호 입력 방식 선택:")
            print("[1] 직접 입력")
            print("[2] 자동 생성")
            pw_choice = input("선택: ").strip()

            if pw_choice == "2":
                try:
                    length = int(input("생성할 암호 길이 (예: 12): ").strip())
                    use_digits = input("숫자 포함? (y/n): ").lower() == "y"
                    use_upper = input("대문자 포함? (y/n): ").lower() == "y"
                    use_special = input("특수문자 포함? (y/n): ").lower() == "y"
                    password = generate_password(
                        length, use_digits, use_upper, use_special
                    )
                    print(f"\n✅ 생성된 비밀번호: {password}")
                except ValueError as e:
                    print(f"❗ 오류: {e}")
                    continue
            else:
                password = getpass("비밀번호 입력: ").strip()

            vault[site] = {
                "username": encrypt_data(username, fernet),
                "password": encrypt_data(password, fernet),
            }

            save_vault(vault)
            print("✅ 저장되었습니다.")

        elif choice == "2":
            site = input("조회할 사이트 이름: ").strip()
            entry = vault.get(site)

            if entry:
                try:
                    username = decrypt_data(entry["username"], fernet)
                    password = decrypt_data(entry["password"], fernet)
                    print(f"\n🔍 아이디: {username}")
                    print(f"🔐 비밀번호: {password}")
                except:
                    print("❗ 마스터 비밀번호가 잘못되었습니다.")
            else:
                print("❗ 해당 사이트가 존재하지 않습니다.")

        elif choice == "3":
            if not vault:
                print("📭 저장된 사이트가 없습니다.")
            else:
                print("\n📋 저장된 사이트 목록:")
                for site in sorted(vault.keys()):
                    print(f" - {site}")

        elif choice == "0":
            print("👋 종료합니다.")
            break

        else:
            print("❗ 올바른 메뉴를 선택하세요.")


if __name__ == "__main__":
    main()
