import json
import os
from getpass import getpass
from cryptography.fernet import Fernet
import base64
import hashlib

VAULT_FILE = "vault.json"


def generate_key(master_password: str) -> bytes:
    """마스터 비밀번호를 바탕으로 Fernet 키 생성"""
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


def main():
    print("🔐 패스워드 저장소 (암호화 포함)")
    master_password = getpass("마스터 비밀번호를 입력하세요: ")
    key = generate_key(master_password)
    fernet = Fernet(key)

    vault = load_vault()

    while True:
        print("\n[1] 저장하기  [2] 조회하기  [0] 종료")
        choice = input("선택: ").strip()

        if choice == "1":
            site = input("사이트 이름: ").strip()
            username = input("아이디: ").strip()
            password = getpass("비밀번호: ").strip()

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
                    print(f"🔍 아이디: {username}")
                    print(f"🔐 비밀번호: {password}")
                except:
                    print("❗ 마스터 비밀번호가 잘못되었습니다.")
            else:
                print("❗ 해당 사이트가 존재하지 않습니다.")

        elif choice == "0":
            print("👋 종료합니다.")
            break
        else:
            print("❗ 올바른 메뉴를 선택하세요.")


if __name__ == "__main__":
    main()
