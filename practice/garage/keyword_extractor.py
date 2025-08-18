import re
from collections import Counter
from typing import List, Tuple, Dict


class KeywordExtractor:
    """
    아주 기본적인 키워드 추출기:
    - 텍스트 정제(이모지/기호 제거, 소문자화 옵션)
    - 간단한 토큰화(영문: 단어 기준, 한글: 자모 제외 한글 음절 유지)
    - 불용어(stopwords) 제거
    - 단일어/바이그램 빈도 Top-N 추출
    """

    def __init__(self, lang: str = "auto", to_lower: bool = True):
        self.lang = lang
        self.to_lower = to_lower
        self.stopwords = self._build_stopwords()

    # ───────── 내부 유틸 ─────────
    def _build_stopwords(self) -> Dict[str, set]:
        # 아주 작은 베이스 불용어(필요시 계속 추가/커스터마이즈 가능)
        en = {
            "the", "a", "an", "and", "or", "but", "if", "on", "in", "at", "of", "for",
            "to", "from", "by", "as", "is", "are", "was", "were", "be", "been", "being",
            "with", "that", "this", "it", "its", "into", "about", "than", "then", "so",
            "such", "there", "their", "they", "them", "these", "those", "i", "you", "he",
            "she", "we", "us", "our", "your", "his", "her", "my", "me"
        }
        ko = {
            "그리고", "그러나", "하지만", "또한", "또", "및", "등", "이", "가", "은", "는", "을", "를",
            "의", "에", "에서", "으로", "와", "과", "하다", "했다", "합니다", "한다", "등등", "더", "것",
            "수", "있다", "없다", "같다", "위해", "대한", "에서의", "해서", "하여", "이는"
        }
        return {"en": en, "ko": ko}

    def _detect_lang(self, text: str) -> str:
        if self.lang in ("en", "ko"):
            return self.lang
        # 간단 감지: 한글 음절 범위가 있으면 ko
        return "ko" if re.search(r"[가-힣]", text) else "en"

    def _clean_text(self, text: str) -> str:
        text = text.strip()
        if self.to_lower:
            text = text.lower()
        # URL, 이메일, 특수기호 제거(한글/영문/숫자/공백/하이픈·언더스코어 일부 허용)
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", " ", text)
        text = re.sub(r"[^0-9A-Za-z가-힣\s\-_]", " ", text)
        # 연속 공백 정리
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _tokenize(self, text: str, lang: str) -> List[str]:
        # 매우 단순한 토큰화: 공백 기준
        tokens = text.split()
        # 숫자만 있는 토큰 제거
        tokens = [t for t in tokens if not re.fullmatch(r"\d+", t)]
        # 짧은 토큰(길이 1) 제거(한글 단일 조사/기호 노이즈 방지)
        tokens = [t for t in tokens if len(t) > 1]
        # 불용어 제거
        sw = self.stopwords[lang]
        tokens = [t for t in tokens if t not in sw]
        return tokens

    # ───────── 공개 API ─────────
    def extract_unigrams(self, text: str, top_k: int = 10) -> List[Tuple[str, int]]:
        lang = self._detect_lang(text)
        clean = self._clean_text(text)
        tokens = self._tokenize(clean, lang)
        counts = Counter(tokens)
        return counts.most_common(top_k)

    def extract_bigrams(self, text: str, top_k: int = 10, min_count: int = 2) -> List[Tuple[str, int]]:
        lang = self._detect_lang(text)
        clean = self._clean_text(text)
        tokens = self._tokenize(clean, lang)
        bigrams = [" ".join(pair) for pair in zip(tokens, tokens[1:])]
        counts = Counter(bigrams)
        # 너무 드문 바이그램은 제외
        items = [(k, c) for k, c in counts.items() if c >= min_count]
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:top_k]

    def extract_keywords(self, text: str, top_k: int = 10) -> Dict[str, List[Tuple[str, int]]]:
        return {
            "unigrams": self.extract_unigrams(text, top_k=top_k),
            "bigrams": self.extract_bigrams(text, top_k=top_k)
        }


# ───────── 실행 예시 ─────────
if __name__ == "__main__":
    sample_en = """
    Generative AI models like large language models (LLMs) enable text generation,
    code completion, and knowledge retrieval. Popular frameworks include Transformers
    and Diffusers, while vector databases support semantic search workflows.
    """

    sample_ko = """
    생성형 AI는 텍스트 생성, 코드 자동완성, 지식 검색을 가능하게 한다.
    특히 트랜스포머 기반 모델과 임베딩을 활용한 의미 검색이 널리 사용된다.
    """

    ke = KeywordExtractor(lang="auto")

    print("=== EN keywords ===")
    print(ke.extract_keywords(sample_en, top_k=8))

    print("\n=== KO keywords ===")
    print(ke.extract_keywords(sample_ko, top_k=8))