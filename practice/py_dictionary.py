import nltk
from nltk.corpus import wordnet

# WordNet 데이터 다운로드 (최초 1회 실행 필요)
nltk.download("wordnet")
nltk.download("omw-1.4")


def get_word_meaning(word):
    """영어 단어의 뜻, 동의어, 반의어, 예제 문장을 가져오는 함수"""
    word = word.strip().lower()  # 공백 제거 & 소문자로 변환
    synsets = wordnet.synsets(word)

    if not synsets:
        print("❌ 단어의 의미를 찾을 수 없습니다.")
        return

    result_text = f"\n📖 '{word}'의 뜻:\n"

    for syn in synsets[:2]:  # 최대 2개 뜻 출력
        pos = syn.pos()  # 품사 가져오기
        definition = syn.definition()
        result_text += f"🔹 [{pos.upper()}] {definition}\n"

        # 예제 문장 추가
        examples = syn.examples()
        if examples:
            result_text += f"   💡 예제: {examples[0]}\n"  # 첫 번째 예제만 출력

    # 동의어(Synonyms) 출력
    synonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())

    if synonyms:
        result_text += f"\n🔄 동의어: {', '.join(list(synonyms)[:5])}\n"

    # 반의어(Antonyms) 출력
    antonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            if lemma.antonyms():
                antonyms.add(lemma.antonyms()[0].name())

    if antonyms:
        result_text += f"🔀 반의어: {', '.join(list(antonyms)[:5])}\n"

    print(result_text)

    # 검색 결과를 파일로 저장
    with open("dictionary_results.txt", "a", encoding="utf-8") as file:
        file.write(result_text + "\n" + "=" * 40 + "\n")

    print("💾 검색 결과가 'dictionary_results.txt' 파일에 저장되었습니다!")


# 사용 예시
word = input("🔍 뜻을 찾을 영어 단어를 입력하세요: ")
get_word_meaning(word)
