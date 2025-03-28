from sentence_transformers import SentenceTransformer, util


def levenshtein_distance(a: str, b: str) -> int:
    """두 문자열 사이의 레벤슈타인 거리 계산"""
    len_a, len_b = len(a), len(b)
    dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]

    for i in range(len_a + 1):
        dp[i][0] = i
    for j in range(len_b + 1):
        dp[0][j] = j

    for i in range(1, len_a + 1):
        for j in range(1, len_b + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # 삭제
                dp[i][j - 1] + 1,  # 삽입
                dp[i - 1][j - 1] + cost,  # 교체
            )
    return dp[len_a][len_b]


def similarity_score(a: str, b: str) -> float:
    """유사도 (%) 계산"""
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 100.0
    distance = levenshtein_distance(a, b)
    return round((1 - distance / max_len) * 100, 2)


def jaccard_similarity(a: str, b: str) -> float:
    """단어 기반 Jaccard 유사도 (%)"""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())

    intersection = set_a & set_b
    union = set_a | set_b

    if not union:
        return 0.0
    return round(len(intersection) / len(union) * 100, 2)


# 사전 훈련된 다국어 모델 사용 (한글도 지원!)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def bert_similarity(text1: str, text2: str) -> float:
    embeddings = model.encode([text1, text2], convert_to_tensor=True)
    cosine_sim = util.cos_sim(embeddings[0], embeddings[1])
    return round(float(cosine_sim[0]) * 100, 2)


def main():
    print("🔍 두 문장의 유사도를 비교합니다.")
    text1 = input("문장 1️⃣: ").strip()
    text2 = input("문장 2️⃣: ").strip()

    lev_score = similarity_score(text1, text2)
    jac_score = jaccard_similarity(text1, text2)
    bert_score = bert_similarity(text1, text2)

    print(f"\n📊 문자 기반 (Levenshtein): {lev_score}%")
    print(f"📘 단어 기반 (Jaccard): {jac_score}%")
    print(f"🧠 의미 기반 (BERT): {bert_score}%")

    if bert_score > 90:
        print("✅ 두 문장은 의미적으로 거의 동일합니다.")
    elif bert_score > 60:
        print("⚠️ 의미가 꽤 유사합니다.")
    else:
        print("❌ 의미 차이가 큰 문장입니다.")


# 실행
if __name__ == "__main__":
    main()
