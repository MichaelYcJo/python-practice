import random
import string


def generate_password(length=12, use_digits=True, use_uppercase=True, use_special=True):
    characters = string.ascii_lowercase
    required = [random.choice(string.ascii_lowercase)]  # 소문자 최소 1개는 항상 포함

    if use_digits:
        characters += string.digits
        required.append(random.choice(string.digits))
    if use_uppercase:
        characters += string.ascii_uppercase
        required.append(random.choice(string.ascii_uppercase))
    if use_special:
        characters += string.punctuation
        required.append(random.choice(string.punctuation))

    # 최소 포함 문자 수보다 길이가 짧으면 오류
    if length < len(required):
        raise ValueError(f"❗ 암호 길이는 최소 {len(required)}자 이상이어야 합니다.")

    remaining_length = length - len(required)
    remaining = [random.choice(characters) for _ in range(remaining_length)]

    full_password = required + remaining
    random.shuffle(full_password)
    return "".join(full_password)


def get_boolean_input(prompt):
    return input(prompt).strip().lower() == "y"


def main():
    print("=== 🔐 안전한 비밀번호 생성기 ===")

    try:
        password_length = int(input("암호 길이를 입력하세요 (예: 12): "))
        if password_length <= 0:
            raise ValueError
    except ValueError:
        print("❗ 올바른 양의 정수를 입력해주세요.")
        return

    include_digits = get_boolean_input("숫자를 포함할까요? (y/n): ")
    include_uppercase = get_boolean_input("대문자를 포함할까요? (y/n): ")
    include_special = get_boolean_input("특수문자를 포함할까요? (y/n): ")

    if not any([include_digits, include_uppercase, include_special]):
        print("⚠️ 선택된 옵션이 없어 소문자만으로 암호를 생성합니다.")

    try:
        generated_password = generate_password(
            password_length,
            use_digits=include_digits,
            use_uppercase=include_uppercase,
            use_special=include_special,
        )
        print("\n✅ 생성된 암호:", generated_password)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
