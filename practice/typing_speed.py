import time
import random

# 연습할 문장 리스트
sentences = [
    "The quick brown fox jumps over the lazy dog.",
    "Python is an amazing programming language.",
    "Fast typing skills improve productivity.",
    "Practice makes perfect in everything you do.",
]


def typing_speed_test():
    sentence = random.choice(sentences)  # 랜덤 문장 선택
    print("\n✍️ 아래 문장을 입력하세요:")
    print(f'"{sentence}"\n')

    input("⏳ 준비되면 Enter 키를 눌러 시작하세요...")

    start_time = time.time()
    user_input = input("\n타이핑 시작: ")
    end_time = time.time()

    elapsed_time = end_time - start_time  # 걸린 시간 계산
    words = len(sentence.split())

    # 속도 및 정확도 계산
    speed = words / (elapsed_time / 60)  # WPM (Words Per Minute)
    accuracy = (
        sum(1 for a, b in zip(user_input, sentence) if a == b) / len(sentence) * 100
    )

    print(f"\n⏰ 타이핑 속도: {speed:.2f} WPM")
    print(f"🎯 정확도: {accuracy:.2f}%")


# 실행
typing_speed_test()
