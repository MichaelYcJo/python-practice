import os
import base64
import time
import getpass
import hashlib
from cryptography.fernet import Fernet

STORAGE_DIR = "./encrypted_memos"
AUTO_LOGOUT_TIME = 60  # 60초 동안 입력 없으면 자동 종료

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)


def derive_key(password):
    """사용자 비밀번호를 기반으로 암호화 키 생성 (PBKDF2 적용)"""
    salt = b"secret_salt_value"  # 보안 강화를 위해 설정
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return base64.urlsafe_b64encode(key[:32])  # AES-256 키 크기(32바이트)


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
    password = getpass.getpass("🔑 비밀번호를 입력하세요: ")
    key = derive_key(password)

    memo_title = input("📝 저장할 메모 제목을 입력하세요: ").strip()
    memo_content = input("📄 메모 내용을 입력하세요: ")

    encrypted_memo = encrypt_message(memo_content, key)
    memo_file = os.path.join(STORAGE_DIR, f"memo_{memo_title}.txt")

    with open(memo_file, "w", encoding="utf-8") as file:
        file.write(encrypted_memo)

    print(f"✅ 메모 '{memo_title}'가 암호화되어 저장되었습니다!")


def list_memos():
    """저장된 암호화된 메모 목록 출력"""
    files = os.listdir(STORAGE_DIR)
    memo_list = [f.replace("memo_", "").replace(".txt", "") for f in files]

    if not memo_list:
        print("📭 저장된 메모가 없습니다!")
    else:
        print("\n📜 저장된 메모 목록:")
        for i, title in enumerate(memo_list, 1):
            print(f"{i}. {title}")

    return memo_list


def read_encrypted_memo():
    """저장된 암호화된 메모 복호화 후 출력"""
    password = getpass.getpass("🔑 비밀번호를 입력하세요: ")
    key = derive_key(password)

    memo_list = list_memos()
    if not memo_list:
        return

    choice = input("\n🔎 복호화할 메모 제목을 입력하세요: ").strip()
    memo_file = os.path.join(STORAGE_DIR, f"memo_{choice}.txt")

    if not os.path.exists(memo_file):
        print("❌ 해당 메모가 존재하지 않습니다!")
        return

    with open(memo_file, "r", encoding="utf-8") as file:
        encrypted_memo = file.read()

    try:
        decrypted_memo = decrypt_message(encrypted_memo, key)
        print(f"\n🔓 복호화된 메모:\n{decrypted_memo}")
    except Exception:
        print("⚠️ 잘못된 비밀번호입니다!")


def delete_memo():
    """암호화된 메모 삭제"""
    memo_list = list_memos()
    if not memo_list:
        return

    choice = input("\n🗑 삭제할 메모 제목을 입력하세요: ").strip()
    memo_file = os.path.join(STORAGE_DIR, f"memo_{choice}.txt")

    if os.path.exists(memo_file):
        os.remove(memo_file)
        print(f"🗑 메모 '{choice}'가 삭제되었습니다!")
    else:
        print("❌ 해당 메모가 존재하지 않습니다!")


def memo_app():
    """암호화 메모장 실행 (자동 로그아웃 적용)"""
    last_action_time = time.time()

    while True:
        print("\n🔐 보안 메모장")
        print("1. 메모 저장 (암호화)")
        print("2. 메모 목록 보기")
        print("3. 메모 보기 (복호화)")
        print("4. 메모 삭제")
        print("5. 종료")

        choice = input("👉 메뉴 선택: ").strip()
        last_action_time = time.time()  # 사용자 입력 시 시간 업데이트

        if choice == "1":
            save_encrypted_memo()
        elif choice == "2":
            list_memos()
        elif choice == "3":
            read_encrypted_memo()
        elif choice == "4":
            delete_memo()
        elif choice == "5":
            print("👋 프로그램을 종료합니다!")
            break
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")

        # 자동 로그아웃 기능 (일정 시간 동안 입력 없으면 종료)
        if time.time() - last_action_time > AUTO_LOGOUT_TIME:
            print("\n⏳ 자동 로그아웃되었습니다. 다시 실행해주세요.")
            break


# 실행
memo_app()
