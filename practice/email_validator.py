import re


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(pattern, email):
        return True
    return False


# 사용 예시
email = input("✉️ 이메일 주소를 입력하세요: ")

if validate_email(email):
    print("✅ 유효한 이메일 형식입니다!")
else:
    print("❌ 올바르지 않은 이메일 형식입니다. 다시 입력해주세요.")
