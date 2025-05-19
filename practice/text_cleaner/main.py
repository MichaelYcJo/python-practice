from cleantext import clean
import emoji
import re

# 간단한 한국어 stopwords 예시
KOR_STOPWORDS = {
    "그리고",
    "하지만",
    "그러나",
    "그래서",
    "또한",
    "때문에",
    "즉",
    "등",
    "이런",
    "저런",
    "있는",
    "하는",
}

# 영어 stopwords (일부)
ENG_STOPWORDS = {
    "and",
    "but",
    "so",
    "or",
    "the",
    "a",
    "an",
    "in",
    "on",
    "at",
    "is",
    "are",
    "was",
    "were",
    "be",
}


def clean_text_basic(text: str) -> str:
    cleaned = clean(
        text,
        fix_unicode=True,
        to_ascii=False,
        lower=True,
        no_line_breaks=True,
        no_urls=True,
        no_emails=True,
        no_phone_numbers=True,
        no_numbers=False,
        no_digits=False,
        no_currency_symbols=True,
        no_punct=True,
        replace_with_url="",
        replace_with_email="",
        replace_with_phone_number="",
        replace_with_number="",
        replace_with_digit="",
        replace_with_currency_symbol="",
    )
    cleaned = emoji.replace_emoji(cleaned, replace="")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def remove_non_kor_eng_num(text: str) -> str:
    return re.sub(r"[^가-힣a-zA-Z0-9\s]", "", text)


def remove_stopwords(text: str) -> str:
    words = text.split()
    filtered = [
        word
        for word in words
        if word not in KOR_STOPWORDS and word not in ENG_STOPWORDS
    ]
    return " ".join(filtered)


def main():
    print("🧼 텍스트 정리기 + 불용어 제거")
    text = input("\n정제할 텍스트를 입력하세요:\n\n>>> ")

    print("\n[1] 기본 정리만")
    print("[2] + 한글/영어/숫자만 남기기")
    print("[3] + 불용어 제거까지")
    mode = input("모드 선택 (1/2/3): ").strip()

    cleaned = clean_text_basic(text)

    if mode == "2":
        cleaned = remove_non_kor_eng_num(cleaned)

    if mode == "3":
        cleaned = remove_non_kor_eng_num(cleaned)
        cleaned = remove_stopwords(cleaned)

    print("\n🧾 정제 결과:")
    print("-" * 40)
    print(cleaned)
    print("-" * 40)


if __name__ == "__main__":
    main()
