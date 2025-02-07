import random


def generate_lotto_numbers(count=1):
    print("🎰 로또 번호 생성기 🎰")

    for i in range(count):
        numbers = random.sample(range(1, 46), 6)  # 1~45 중 6개 랜덤 선택 (중복 없음)
        numbers.sort()  # 정렬
        print(f"🎟️ {i+1}번째 로또 번호: {numbers}")


# 사용 예시
try:
    num_tickets = int(input("몇 개의 로또 번호를 생성할까요? (예: 3): "))
    generate_lotto_numbers(num_tickets)
except ValueError:
    print("❌ 숫자만 입력해주세요!")
