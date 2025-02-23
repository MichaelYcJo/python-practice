from PyDictionary import PyDictionary


def get_word_meaning(word):
    """영어 단어의 뜻, 동의어, 반의어를 가져오는 함수"""
    dictionary = PyDictionary()

    # 단어 뜻 가져오기
    meaning = dictionary.meaning(word)
    if not meaning:
        print("❌ 단어의 의미를 찾을 수 없습니다.")
        return

    print(f"\n📖 '{word}'의 뜻:")
    for pos, definitions in meaning.items():
        print(f"🔹 {pos}: {', '.join(definitions[:2])}")  # 최대 2개 출력

    # 동의어 가져오기
    synonyms = dictionary.synonym(word)
    if synonyms:
        print(f"\n🔄 동의어: {', '.join(synonyms[:5])}")

    # 반의어 가져오기
    antonyms = dictionary.antonym(word)
    if antonyms:
        print(f"\n🔀 반의어: {', '.join(antonyms[:5])}")


# 사용 예시
word = input("🔍 뜻을 찾을 영어 단어를 입력하세요: ")
get_word_meaning(word)
