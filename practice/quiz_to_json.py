import random
import json

# 퀴즈 데이터 (파일로도 분리 가능)
quiz_data = [
    {
        "question": "파이썬의 창시자는?",
        "choices": ["Guido", "Linus", "Brendan", "James"],
        "answer": "Guido",
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
    },
    {
        "question": "Python에서 리스트는 어떤 기호로 묶나요?",
        "choices": ["()", "{}", "[]", "<>"],
        "answer": "[]",
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


if __name__ == "__main__":
    run_quiz(quiz_data)
