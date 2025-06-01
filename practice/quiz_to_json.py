import random

# 퀴즈 데이터
quiz_data = [
    {
        "question": "파이썬의 창시자는?",
        "choices": ["Guido", "Linus", "Brendan", "James"],
        "answer": "Guido",
        "difficulty": "easy",
    },
    {
        "question": "HTML의 약자는?",
        "choices": [
            "Hyper Tool ML",
            "Hyper Text Markup Language",
            "Home Tool Markup",
            "High Transfer ML",
        ],
        "answer": "Hyper Text Markup Language",
        "difficulty": "medium",
    },
    {
        "question": "Python에서 리스트는 어떤 기호로 묶나요?",
        "choices": ["()", "{}", "[]", "<>"],
        "answer": "[]",
        "difficulty": "easy",
    },
    {
        "question": "빅오 표기법에서 이진 탐색의 시간복잡도는?",
        "choices": ["O(n)", "O(n log n)", "O(log n)", "O(1)"],
        "answer": "O(log n)",
        "difficulty": "hard",
    },
    {
        "question": "TCP와 UDP 중 신뢰성 있는 프로토콜은?",
        "choices": ["UDP", "ICMP", "TCP", "IP"],
        "answer": "TCP",
        "difficulty": "medium",
    },
]


def run_quiz(quiz_list):
    print("🎯 랜덤 퀴즈에 오신 걸 환영합니다!\n")
    score = 0
    random.shuffle(quiz_list)

    for idx, quiz in enumerate(quiz_list, start=1):
        print(f"Q{idx}: {quiz['question']}")
        choices = quiz["choices"]
        random.shuffle(choices)

        for i, choice in enumerate(choices):
            print(f"  {i + 1}. {choice}")

        try:
            user_input = int(input("👉 정답 번호를 입력하세요: "))
            selected = choices[user_input - 1]
            if selected == quiz["answer"]:
                print("✅ 정답입니다!\n")
                score += 1
            else:
                print(f"❌ 오답입니다! 정답: {quiz['answer']}\n")
        except (ValueError, IndexError):
            print("⚠️ 올바른 번호를 입력하세요.\n")

    print("🎉 퀴즈 종료!")
    print(f"📊 최종 점수: {score} / {len(quiz_list)}")


def main():
    print("🧠 난이도를 선택하세요: easy / medium / hard / all")
    selected_level = input("👉 입력: ").strip().lower()

    valid_levels = ["easy", "medium", "hard", "all"]
    if selected_level not in valid_levels:
        print("⚠️ 유효하지 않은 난이도입니다. 종료합니다.")
        return

    if selected_level == "all":
        filtered_quizzes = quiz_data
    else:
        filtered_quizzes = [q for q in quiz_data if q["difficulty"] == selected_level]

    if not filtered_quizzes:
        print("❌ 해당 난이도의 문제가 없습니다.")
        return

    run_quiz(filtered_quizzes)


if __name__ == "__main__":
    main()
