import os
import re
from collections import Counter


def clean_text(text):
    """불필요한 기호 제거 및 소문자 변환"""
    text = re.sub(r"\n+", " ", text)  # 줄바꿈 제거
    text = re.sub(r"[^ㄱ-ㅎ가-힣a-zA-Z0-9\s\.]", "", text)  # 특수기호 제거
    return text.lower()


def split_sentences(text):
    """간단한 문장 분리 (마침표 기준)"""
    return [sentence.strip() for sentence in text.split(".") if sentence.strip()]


def get_keywords(text, top_n=5):
    """가장 많이 등장하는 단어 top_n 반환"""
    words = text.split()
    stopwords = {
        "the",
        "is",
        "a",
        "an",
        "in",
        "to",
        "of",
        "and",
        "on",
        "at",
        "for",
        "with",
        "as",
        "by",
        "was",
        "are",
    }
    words = [word for word in words if word not in stopwords and len(word) > 2]
    return [word for word, _ in Counter(words).most_common(top_n)]


def extract_summary(text, num_sentences=2):
    """키워드 기반으로 핵심 문장 추출"""
    cleaned = clean_text(text)
    keywords = get_keywords(cleaned)
    sentences = split_sentences(text)

    # 키워드 포함된 문장만 추출
    ranked_sentences = [s for s in sentences if any(k in s.lower() for k in keywords)]

    return (
        ranked_sentences[:num_sentences]
        if ranked_sentences
        else sentences[:num_sentences]
    )


def main():
    """텍스트 요약 실행"""
    print("📄 요약할 텍스트를 직접 입력하거나 .txt 파일 경로를 입력하세요.")
    path_or_text = input("📝 텍스트 또는 파일 경로: ").strip()

    if os.path.exists(path_or_text) and path_or_text.endswith(".txt"):
        with open(path_or_text, encoding="utf-8") as f:
            text = f.read()
    else:
        text = path_or_text

    summary = extract_summary(text)

    print("\n📌 요약 결과:")
    for idx, sentence in enumerate(summary, 1):
        print(f"{idx}. {sentence.strip()}")


# 실행
main()
