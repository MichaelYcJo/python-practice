import nltk
from nltk.corpus import wordnet

# WordNet 데이터 다운로드 (최초 1회 실행 필요)
nltk.download("wordnet")
nltk.download("omw-1.4")


def get_word_meaning(word):
    """영어 단어의 뜻, 동의어, 반의어를 가져오는 함수"""
    synsets = wordnet.synsets(word)

    if not synsets:
        print("❌ 단어의 의미를 찾을 수 없습니다.")
        return

    # 뜻(Definition) 출력
    print(f"\n📖 '{word}'의 뜻:")
    for syn in synsets[:2]:  # 최대 2개 뜻 출력
        print(f"🔹 {syn.definition()}")

    # 동의어(Synonyms) 출력
    synonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())

    if synonyms:
        print(f"\n🔄 동의어: {', '.join(list(synonyms)[:5])}")

    # 반의어(Antonyms) 출력
    antonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            if lemma.antonyms():
                antonyms.add(lemma.antonyms()[0].name())

    if antonyms:
        print(f"\n🔀 반의어: {', '.join(list(antonyms)[:5])}")


# 사용 예시
word = input("🔍 뜻을 찾을 영어 단어를 입력하세요: ")
get_word_meaning(word)
