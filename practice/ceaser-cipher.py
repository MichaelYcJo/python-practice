"""
	문장을 입력하면 간단한 암호화된 텍스트로 변환
	다시 입력하면 원래 문장으로 복호화 가능
	저 암호(Caesar Cipher) 기법 사용 (문자를 일정 값만큼 밀어 변환)
"""


def caesar_cipher(text, shift):
    encrypted_text = ""

    for char in text:
        if char.isalpha():
            start = ord("A") if char.isupper() else ord("a")
            encrypted_text += chr(start + (ord(char) - start + shift) % 26)
        else:
            encrypted_text += char  # 알파벳이 아니면 그대로 유지

    return encrypted_text


def caesar_decipher(text, shift):
    return caesar_cipher(text, -shift)  # 암호화를 반대로 적용하면 복호화


# 사용 예시
message = input("🔐 암호화할 문장을 입력하세요: ")
shift_value = int(input("➡️ 몇 글자 이동할까요? (예: 3): "))

encrypted = caesar_cipher(message, shift_value)
print(f"🔒 암호화된 텍스트: {encrypted}")

decrypted = caesar_decipher(encrypted, shift_value)
print(f"🔓 복호화된 텍스트: {decrypted}")
