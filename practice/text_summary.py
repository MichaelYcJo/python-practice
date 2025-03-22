import os
import re
import math
from collections import defaultdict, Counter

"""
TF-IDF기반 -> 단순키워드 횟수 대신 문장 중요도 고려
문장별 점수를 통한 요약
"""


def clean_text(text):
    """기호 제거 및 소문자 변환"""
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"[^ㄱ-ㅎ가-힣a-zA-Z0-9\s\.]", "", text)
    return text.lower()


def split_sentences(text):
    """간단한 문장 분리"""
    return [s.strip() for s in re.split(r"\.\s*", text) if len(s.strip()) > 10]


def tokenize(text):
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
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if w not in stopwords and len(w) > 2]


def compute_tf(sent_tokens):
    """문장별 TF 계산"""
    return [Counter(tokenize(sent)) for sent in sent_tokens]


def compute_idf(sent_tokens):
    """IDF 계산"""
    N = len(sent_tokens)
    idf = defaultdict(lambda: 0)
    for tokens in sent_tokens:
        for word in set(tokenize(tokens)):
            idf[word] += 1
    for word in idf:
        idf[word] = math.log(N / (1 + idf[word]))
    return idf


def score_sentences(sentences, tf_list, idf):
    scores = []
    for i, tf in enumerate(tf_list):
        score = 0
        for word in tf:
            score += tf[word] * idf.get(word, 0)
        scores.append((score, sentences[i]))
    return sorted(scores, key=lambda x: x[0], reverse=True)


def extract_summary(text, top_n=3):
    sentences = split_sentences(text)
    if not sentences:
        return []

    tf = compute_tf(sentences)
    idf = compute_idf(sentences)
    ranked = score_sentences(sentences, tf, idf)

    summary = [sent for _, sent in ranked[:top_n]]
    return summary


def main():
    print("📄 요약할 텍스트를 직접 입력하거나 .txt 파일 경로를 입력하세요.")
    path_or_text = input("📝 텍스트 또는 파일 경로: ").strip()

    if os.path.exists(path_or_text) and path_or_text.endswith(".txt"):
        with open(path_or_text, encoding="utf-8") as f:
            text = f.read()
    else:
        text = path_or_text

    summary = extract_summary(text)

    print("\n📌 요약 결과:")
    for i, sentence in enumerate(summary, 1):
        print(f"{i}. {sentence.strip()}")


if __name__ == "__main__":
    main()
