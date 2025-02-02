import random
import string

def generate_password(length=12, use_digits=True, use_uppercase=True, use_special=True):
    # 기본 소문자 포함
    characters = string.ascii_lowercase
    
    if use_digits:
        characters += string.digits
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_special:
        characters += string.punctuation
    
    # 암호 생성
    password = ''.join(random.choice(characters) for _ in range(length))
    
    return password

# 사용 예시
password_length = int(input("암호 길이를 입력하세요 (예: 12): "))
include_digits = input("숫자를 포함할까요? (y/n): ").lower() == "y"
include_uppercase = input("대문자를 포함할까요? (y/n): ").lower() == "y"
include_special = input("특수문자를 포함할까요? (y/n): ").lower() == "y"

generated_password = generate_password(password_length, include_digits, include_uppercase, include_special)
print("\n생성된 암호:", generated_password)