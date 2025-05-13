import json
import random


def load_words(filepath="words.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❗ 파일 '{filepath}'을(를) 찾을 수 없습니다.")
        return []


def quiz_round(words, label="퀴즈", show_result=True):
    score = 0
    wrong_list = []

    for idx, item in enumerate(words, start=1):
        print(f"\n[{label} {idx}] 영어 단어: {item['word']}")
        answer = input("뜻을 입력하세요: ").strip()

        if answer == item["meaning"]:
            print("✅ 정답입니다!")
            score += 1
        else:
            print(f"❌ 오답입니다. 정답: {item['meaning']}")
            wrong_list.append(item)

    if show_result:
        print(f"\n🎯 {label} 종료! 점수: {score}/{len(words)}")

    return wrong_list


def run_quiz(words, num_questions=5):
    if not words:
        print("❗ 단어 리스트가 비어 있습니다.")
        return

    random.shuffle(words)
    quiz_words = words[:num_questions]

    print("\n🧠 메인 퀴즈 시작!")
    wrong_list = quiz_round(quiz_words, label="문제")

    if wrong_list:
        choice = (
            input(f"\n📚 오답 {len(wrong_list)}개 복습하시겠습니까? (y/n): ")
            .strip()
            .lower()
        )
        if choice == "y":
            print("\n🔁 오답 복습 시작!")
            quiz_round(wrong_list, label="복습", show_result=False)
        else:
            print("✅ 복습을 건너뜁니다.")
    else:
        print("🎉 모든 문제를 맞혔습니다! 완벽해요!")


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
