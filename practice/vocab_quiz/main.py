import json
import random


def load_words(filepath="./words.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❗ 파일 '{filepath}'을(를) 찾을 수 없습니다.")
        return []


def run_quiz(words, num_questions=5):
    if not words:
        print("❗ 단어 리스트가 비어 있습니다.")
        return

    random.shuffle(words)
    quiz_words = words[:num_questions]

    score = 0
    for idx, item in enumerate(quiz_words, start=1):
        print(f"\n[{idx}] 영어 단어: {item['word']}")
        answer = input("뜻을 입력하세요: ").strip()

        if answer == item["meaning"]:
            print("✅ 정답입니다!")
            score += 1
        else:
            print(f"❌ 오답입니다. 정답: {item['meaning']}")

    print(f"\n🎯 퀴즈 종료! 최종 점수: {score}/{len(quiz_words)}")


def main():
    print("📘 단어 암기 테스트 CLI")
    words = load_words()

    if not words:
        return

    num = input(f"총 퀴즈 개수? (최대 {len(words)}개): ").strip()
    try:
        num_questions = min(int(num), len(words))
    except:
        num_questions = min(5, len(words))

    run_quiz(words, num_questions)


if __name__ == "__main__":
    main()
