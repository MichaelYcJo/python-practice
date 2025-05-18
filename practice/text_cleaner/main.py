from cleantext import clean
import emoji
import re


def clean_text_basic(text: str) -> str:
    """기본 텍스트 정리 (이모지, HTML, 공백 등)"""
    cleaned = clean(
        text,
        fix_unicode=True,
        to_ascii=False,
        lower=False,
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
    # 이모지 제거
    cleaned = emoji.replace_emoji(cleaned, replace="")
    # 다중 공백 제거
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def remove_non_kor_eng_num(text: str) -> str:
    """한글, 영어, 숫자만 남기고 제거"""
    return re.sub(r"[^가-힣a-zA-Z0-9\s]", "", text)


def main():
    print("🧼 텍스트 정리기 (CleanText + emoji + re)")
    text = input("\n정제할 텍스트를 입력하세요:\n\n>>> ")

    print("\n[1] 기본 정리만")
    print("[2] + 한글/영어/숫자만 남기기")
    mode = input("모드 선택 (1/2): ").strip()

    cleaned = clean_text_basic(text)

    if mode == "2":
        cleaned = remove_non_kor_eng_num(cleaned)

    print("\n🧾 정제 결과:")
    print("-" * 40)
    print(cleaned)
    print("-" * 40)


if __name__ == "__main__":
    main()
