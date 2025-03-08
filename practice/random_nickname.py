import random

# 카테고리별 닉네임 리스트
NICKNAME_CATEGORIES = {
    "판타지": {
        "형용사": ["마법의", "신비한", "어둠의", "빛나는", "고대의"],
        "명사": ["드래곤", "마법사", "전사", "요정", "늑대"],
    },
    "게임 스타일": {
        "형용사": ["빠른", "강한", "독특한", "무서운", "전설의"],
        "명사": ["헌터", "스나이퍼", "닌자", "사신", "전투기"],
    },
    "귀여운 스타일": {
        "형용사": ["작은", "귀여운", "몽글몽글한", "달콤한", "반짝이는"],
        "명사": ["토끼", "곰돌이", "강아지", "햄스터", "펭귄"],
    },
    "한국식": {
        "형용사": ["멋진", "고요한", "강인한", "순수한", "유쾌한"],
        "명사": ["호랑이", "바람", "별", "나무", "강"],
    },
}


def generate_nickname(category):
    """선택한 카테고리에서 랜덤 닉네임 생성"""
    if category not in NICKNAME_CATEGORIES:
        print("❌ 존재하지 않는 카테리입니다! 다시 선택하세요.")
        return None

    adj = random.choice(NICKNAME_CATEGORIES[category]["형용사"])
    noun = random.choice(NICKNAME_CATEGORIES[category]["명사"])
    return f"{adj} {noun}"


def nickname_generator():
    """닉네임 생성기 실행"""
    print("\n🎭 랜덤 닉네임 생성기")
    print("카테고리를 선택하세요:")

    categories = list(NICKNAME_CATEGORIES.keys())
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")

    try:
        choice = int(input("👉 카테고리 번호 입력: ")) - 1
        if choice < 0 or choice >= len(categories):
            raise ValueError
    except ValueError:
        print("⚠️ 올바른 번호를 입력하세요!")
        return

    selected_category = categories[choice]
    nickname = generate_nickname(selected_category)
    if nickname:
        print(f"\n✨ 생성된 닉네임: {nickname} ✨")


# 실행
nickname_generator()
