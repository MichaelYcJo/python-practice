import os
import base64
from cryptography.fernet import Fernet

# 암호화 키 저장 파일
KEY_FILE = "secret.key"


def generate_key():
    """AES 암호화 키 생성"""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    print("✅ 암호화 키가 생성되었습니다!")


def load_key():
    """저장된 암호화 키 불러오기"""
    if not os.path.exists(KEY_FILE):
        print("❌ 암호화 키가 없습니다. 먼저 키를 생성하세요!")
        return None
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()


def encrypt_message(message, key):
    """메시지 암호화"""
    cipher = Fernet(key)
    encrypted_text = cipher.encrypt(message.encode())
    return base64.b64encode(encrypted_text).decode()


def decrypt_message(encrypted_message, key):
    """암호화된 메시지 복호화"""
    cipher = Fernet(key)
    decrypted_text = cipher.decrypt(base64.b64decode(encrypted_message)).decode()
    return decrypted_text


def save_encrypted_memo():
    """메모 암호화 후 저장"""
    key = load_key()
    if not key:
        return

    memo = input("📝 저장할 메모를 입력하세요: ")
    encrypted_memo = encrypt_message(memo, key)

    with open("encrypted_memo.txt", "w", encoding="utf-8") as file:
        file.write(encrypted_memo)

    print("✅ 메모가 암호화되어 저장되었습니다!")


def read_encrypted_memo():
    """저장된 암호화된 메모 복호화 후 출력"""
    key = load_key()
    if not key:
        return

    if not os.path.exists("encrypted_memo.txt"):
        print("📭 저장된 메모가 없습니다!")
        return

    with open("encrypted_memo.txt", "r", encoding="utf-8") as file:
        encrypted_memo = file.read()

    decrypted_memo = decrypt_message(encrypted_memo, key)
    print(f"\n🔓 복호화된 메모:\n{decrypted_memo}")


def memo_app():
    """메모 암호화 프로그램 실행"""
    while True:
        print("\n🔐 암호화 메모장")
        print("1. 암호화 키 생성")
        print("2. 메모 저장 (암호화)")
        print("3. 메모 보기 (복호화)")
        print("4. 종료")

        choice = input("👉 메뉴 선택: ")

        if choice == "1":
            generate_key()
        elif choice == "2":
            save_encrypted_memo()
        elif choice == "3":
            read_encrypted_memo()
        elif choice == "4":
            print("👋 프로그램을 종료합니다!")
            break
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")


# 실행
memo_app()
