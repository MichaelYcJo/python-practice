import re
from collections import Counter
from typing import List, Tuple, Dict, Optional


class KeywordExtractor:
    """
    간단한 키워드 추출기 (사용자 불용어 지원)
    - stopwords_override: 사용자가 직접 지정한 불용어 세트(dict 또는 set)
    """

    def __init__(self, lang: str = "auto", to_lower: bool = True,
                 stopwords_override: Optional[Dict[str, set]] = None):
        self.lang = lang
        self.to_lower = to_lower
        self.stopwords = self._build_stopwords()

        # 사용자 덮어쓰기: dict 또는 set 허용
        if stopwords_override:
            if isinstance(stopwords_override, dict):
                for k, v in stopwords_override.items():
                    self.stopwords[k] = set(v)
            elif isinstance(stopwords_override, set):
                # 언어 자동 감지 기반 적용
                detected = "ko" if any(re.search(r"[가-힣]", w) for w in stopwords_override) else "en"
                self.stopwords[detected] = set(stopwords_override)

    # ───────── 내부 유틸 ─────────
    def _build_stopwords(self) -> Dict[str, set]:
        en = {"the", "a", "an", "and", "or", "but", "if", "on", "in", "at", "of", "for"}
        ko = {"그리고", "그러나", "하지만", "또한", "이", "가", "은", "는", "을", "를"}
        return {"en": en, "ko": ko}

    def _detect_lang(self, text: str) -> str:
        if self.lang in ("en", "ko"):
            return self.lang
        return "ko" if re.search(r"[가-힣]", text) else "en"

    def _clean_text(self, text: str) -> str:
        text = text.strip()
        if self.to_lower:
            text = text.lower()
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"[^0-9A-Za-z가-힣\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _tokenize(self, text: str, lang: str) -> List[str]:
        tokens = text.split()
        tokens = [t for t in tokens if len(t) > 1]  # 한 글자 제거
        tokens = [t for t in tokens if t not in self.stopwords[lang]]
        return tokens

    # ───────── 공개 API ─────────
    def extract_unigrams(self, text: str, top_k: int = 10) -> List[Tuple[str, int]]:
        lang = self._detect_lang(text)
        clean = self._clean_text(text)
        tokens = self._tokenize(clean, lang)
        counts = Counter(tokens)
        return counts.most_common(top_k)


# ───────── 실행 예시 ─────────
if __name__ == "__main__":
    text = "AI 기술은 빠르게 발전하고 있으며, 특히 생성형 AI가 주목받고 있다. AI, AI, 그리고 AI."

    print("=== 기본 불용어 사용 ===")
    ke_default = KeywordExtractor()
    print(ke_default.extract_unigrams(text))

    print("\n=== 사용자 불용어 override (dict) ===")
    ke_custom = KeywordExtractor(stopwords_override={"ko": {"ai", "기술", "빠르게"}})
    print(ke_custom.extract_unigrams(text))

    print("\n=== 사용자 불용어 override (set) ===")
    ke_custom_set = KeywordExtractor(stopwords_override={"ai", "특히"})
    print(ke_custom_set.extract_unigrams(text))