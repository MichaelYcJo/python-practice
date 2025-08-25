import re
from collections import Counter
from typing import List, Tuple, Dict, Optional, Union, Set
from functools import lru_cache


class KeywordExtractor:
    """
    개선된 키워드 추출기 (사용자 불용어 병합 지원)
    - stopwords_override: 사용자가 직접 지정한 불용어 세트(dict 또는 set)
    """

    def __init__(self, lang: str = "auto", to_lower: bool = True,
                 stopwords_override: Optional[Union[Dict[str, Set[str]], Set[str]]] = None):
        if lang not in ("auto", "en", "ko"):
            raise ValueError(f"Unsupported language: {lang}. Supported: 'auto', 'en', 'ko'")
        
        self.lang = lang
        self.to_lower = to_lower
        self.stopwords = self._build_stopwords()

        # 사용자 지정 불용어 병합
        if stopwords_override:
            self._merge_custom_stopwords(stopwords_override)
    
    def _merge_custom_stopwords(self, stopwords_override: Union[Dict[str, Set[str]], Set[str]]) -> None:
        """사용자 지정 불용어를 기본 불용어와 병합"""
        if isinstance(stopwords_override, dict):
            for k, v in stopwords_override.items():
                if k not in ("en", "ko"):
                    raise ValueError(f"Invalid language key: {k}. Use 'en' or 'ko'")
                if not isinstance(v, (set, list, tuple)):
                    raise TypeError(f"Stopwords for '{k}' must be a set, list, or tuple")
                if k in self.stopwords:
                    self.stopwords[k] = self.stopwords[k].union(set(v))
                else:
                    self.stopwords[k] = set(v)
        elif isinstance(stopwords_override, (set, list, tuple)):
            stopwords_set = set(stopwords_override) if not isinstance(stopwords_override, set) else stopwords_override
            if not stopwords_set:
                return
            detected = "ko" if any(re.search(r"[가-힣]", w) for w in stopwords_set) else "en"
            self.stopwords[detected] = self.stopwords[detected].union(stopwords_set)
        else:
            raise TypeError("stopwords_override must be a dict or set/list/tuple")

    # ───────── 내부 유틸 ─────────
    def _build_stopwords(self) -> Dict[str, Set[str]]:
        en = {"the", "a", "an", "and", "or", "but", "if", "on", "in", "at", "of", "for", 
              "to", "with", "from", "by", "about", "into", "through", "during", "before", "after",
              "above", "below", "between", "among", "under", "over", "is", "are", "was", "were",
              "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would",
              "could", "should", "may", "might", "must", "can", "this", "that", "these", "those"}
        ko = {"그리고", "그러나", "하지만", "또한", "이", "가", "은", "는", "을", "를", "에", "에서",
              "으로", "로", "와", "과", "도", "만", "까지", "부터", "처럼", "같이", "위해", "때문에",
              "대해", "관해", "통해", "의해", "에게", "한테", "더", "가장", "매우", "너무", "정말",
              "아주", "꽤", "조금", "많이", "좀", "잘", "못", "안", "없다", "있다", "하다", "되다",
              "것", "수", "때", "곳", "말", "일", "사람", "경우", "때문", "사이", "다음", "이전"}
        return {"en": en, "ko": ko}

    @lru_cache(maxsize=128)
    def _detect_lang(self, text: str) -> str:
        """언어 감지 (한글 문자 비율 기반)"""
        if self.lang in ("en", "ko"):
            return self.lang
        
        if not text:
            return "en"
        
        korean_chars = len(re.findall(r"[가-힣]", text))
        total_chars = len(re.sub(r"\s+", "", text))
        
        if total_chars == 0:
            return "en"
        
        korean_ratio = korean_chars / total_chars
        return "ko" if korean_ratio > 0.1 else "en"

    def _clean_text(self, text: str) -> str:
        """텍스트 정제 (URL 제거, 특수문자 제거, 공백 정규화)"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        
        text = text.strip()
        if not text:
            return ""
        
        if self.to_lower:
            text = text.lower()
        
        # URL 제거
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        # 이메일 제거
        text = re.sub(r"\S+@\S+\.\S+", " ", text)
        # 숫자와 영문, 한글, 공백만 유지
        text = re.sub(r"[^0-9A-Za-z가-힣\s]", " ", text)
        # 연속된 공백을 하나로
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()

    def _tokenize(self, text: str, lang: str, min_length: int = 2) -> List[str]:
        """토큰화 및 불용어 제거"""
        if not text:
            return []
        
        tokens = text.split()
        # 최소 길이 필터링
        tokens = [t for t in tokens if len(t) >= min_length]
        # 불용어 제거
        tokens = [t for t in tokens if t not in self.stopwords.get(lang, set())]
        # 숫자만으로 구성된 토큰 제거
        tokens = [t for t in tokens if not t.isdigit()]
        
        return tokens

    # ───────── 공개 API ─────────
    def extract_unigrams(self, text: str, top_k: int = 10, min_length: int = 2) -> List[Tuple[str, int]]:
        """유니그램 키워드 추출
        
        Args:
            text: 분석할 텍스트
            top_k: 반환할 상위 키워드 개수
            min_length: 토큰 최소 길이
            
        Returns:
            (키워드, 빈도) 튜플의 리스트
            
        Raises:
            ValueError: top_k나 min_length가 유효하지 않은 경우
            TypeError: text가 문자열이 아닌 경우
        """
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if min_length <= 0:
            raise ValueError("min_length must be positive")
        
        if not text.strip():
            return []
        
        lang = self._detect_lang(text)
        clean = self._clean_text(text)
        tokens = self._tokenize(clean, lang, min_length)
        
        if not tokens:
            return []
        
        counts = Counter(tokens)
        return counts.most_common(top_k)
    
    def get_stats(self, text: str) -> Dict[str, Union[str, int, float]]:
        """텍스트 분석 통계 반환"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        
        lang = self._detect_lang(text)
        clean = self._clean_text(text)
        tokens = self._tokenize(clean, lang)
        
        korean_chars = len(re.findall(r"[가-힣]", text))
        total_chars = len(re.sub(r"\s+", "", text))
        korean_ratio = korean_chars / total_chars if total_chars > 0 else 0
        
        return {
            "detected_language": lang,
            "original_length": len(text),
            "cleaned_length": len(clean),
            "token_count": len(tokens),
            "unique_tokens": len(set(tokens)),
            "korean_char_ratio": round(korean_ratio, 3)
        }


# ───────── 실행 예시 ─────────
if __name__ == "__main__":
    text = "AI 기술은 빠르게 발전하고 있으며, 특히 생성형 AI가 주목받고 있다. AI, AI, 그리고 AI."

    print("=== 기본 불용어 사용 ===")
    ke_default = KeywordExtractor()
    print("Keywords:", ke_default.extract_unigrams(text))
    print("Stats:", ke_default.get_stats(text))

    print("\n=== 사용자 불용어 merge (dict) ===")
    ke_custom = KeywordExtractor(stopwords_override={"ko": {"ai", "기술"}})
    print("Keywords:", ke_custom.extract_unigrams(text))

    print("\n=== 사용자 불용어 merge (set) ===")
    ke_custom_set = KeywordExtractor(stopwords_override={"ai", "특히"})
    print("Keywords:", ke_custom_set.extract_unigrams(text))
    
    print("\n=== 오류 처리 테스트 ===")
    try:
        ke_error = KeywordExtractor(lang="invalid")
    except ValueError as e:
        print(f"Language error: {e}")
    
    try:
        result = ke_default.extract_unigrams(123)
    except TypeError as e:
        print(f"Type error: {e}")