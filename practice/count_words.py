import re
from collections import Counter


def word_count(text: str):
    # 소문자 변환 + 특수문자 제거
    words = re.findall(r"\b\w+\b", text.lower())

    # 단어 빈도 계산
    counter = Counter(words)
    return counter


def main():
    # 입력 텍스트 예시
    sample_text = """
    Python is great! Python is easy to learn. 
    Python can be used for web, data science, and AI.
    """

    counts = word_count(sample_text)

    # 결과 출력
    print("📊 단어 빈도:")
    for word, freq in counts.items():
        print(f"{word}: {freq}")


if __name__ == "__main__":
    main()
