import re
import json
import csv
import logging
from collections import Counter
from typing import List, Tuple, Dict, Optional, Union, Set, Any
from functools import lru_cache
from pathlib import Path
from dataclasses import dataclass, asdict
from math import log


@dataclass
class ExtractionResult:
    """키워드 추출 결과를 담는 데이터 클래스"""
    keywords: List[Tuple[str, Union[int, float]]]
    stats: Dict[str, Union[str, int, float]]
    method: str
    parameters: Dict[str, Any]


class KeywordExtractor:
    """
    고급 키워드 추출기 (N-gram, TF-IDF, 배치 처리 지원)
    - N-gram: 유니그램, 바이그램, 트라이그램 지원
    - TF-IDF: 용어 빈도-역문서 빈도 가중치
    - 배치 처리: 여러 문서 동시 처리
    - 다양한 내보내기 형식 지원
    """

    def __init__(self, 
                 lang: str = "auto", 
                 to_lower: bool = True,
                 stopwords_override: Optional[Union[Dict[str, Set[str]], Set[str]]] = None,
                 enable_logging: bool = False):
        if lang not in ("auto", "en", "ko"):
            raise ValueError(f"Unsupported language: {lang}. Supported: 'auto', 'en', 'ko'")
        
        self.lang = lang
        self.to_lower = to_lower
        self.stopwords = self._build_stopwords()
        self.document_corpus = []  # TF-IDF를 위한 문서 집합
        
        # 로깅 설정
        self.logger = self._setup_logging(enable_logging)
        
        # 사용자 지정 불용어 병합
        if stopwords_override:
            self._merge_custom_stopwords(stopwords_override)
            
        self.logger.info(f"KeywordExtractor initialized with lang={lang}")
    
    def _setup_logging(self, enable: bool) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO if enable else logging.WARNING)
        
        if enable and not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
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
        """확장된 불용어 사전 구축"""
        en = {
            "the", "a", "an", "and", "or", "but", "if", "on", "in", "at", "of", "for", 
            "to", "with", "from", "by", "about", "into", "through", "during", "before", "after",
            "above", "below", "between", "among", "under", "over", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "can", "this", "that", "these", "those",
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
            "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
            "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
            "what", "which", "who", "whom", "when", "where", "why", "how", "all", "any", "both",
            "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "so", "than", "too", "very", "just", "now", "get", "got", "also",
            "like", "one", "two", "first", "last", "new", "old", "good", "great", "big", "small"
        }
        
        ko = {
            "그리고", "그러나", "하지만", "또한", "이", "가", "은", "는", "을", "를", "에", "에서",
            "으로", "로", "와", "과", "도", "만", "까지", "부터", "처럼", "같이", "위해", "때문에",
            "대해", "관해", "통해", "의해", "에게", "한테", "더", "가장", "매우", "너무", "정말",
            "아주", "꽤", "조금", "많이", "좀", "잘", "못", "안", "없다", "있다", "하다", "되다",
            "것", "수", "때", "곳", "말", "일", "사람", "경우", "때문", "사이", "다음", "이전",
            "그", "그녀", "그것", "여기", "저기", "어디", "언제", "누구", "무엇", "어떻게", "왜",
            "모든", "각", "몇", "많은", "적은", "크다", "작다", "좋다", "나쁘다", "새로운", "오래된",
            "첫번째", "마지막", "하나", "둘", "셋", "년", "월", "일", "시간", "분", "초", "오늘", "어제", "내일"
        }
        
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

    def _clean_text(self, text: str, remove_numbers: bool = True) -> str:
        """향상된 텍스트 정제"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        
        text = text.strip()
        if not text:
            return ""
        
        if self.to_lower:
            text = text.lower()
        
        # URL, 이메일, 해시태그, 멘션 제거
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"\S+@\S+\.\S+", " ", text)
        text = re.sub(r"#\S+|@\S+", " ", text)
        
        # 괄호 안 내용 제거 (선택적)
        text = re.sub(r"\([^)]*\)|\[[^\]]*\]|\{[^}]*\}", " ", text)
        
        if remove_numbers:
            # 숫자와 영문, 한글, 공백만 유지
            text = re.sub(r"[^0-9A-Za-z가-힣\s]", " ", text)
        else:
            # 특수문자만 제거, 숫자는 유지
            text = re.sub(r"[^\w가-힣\s]", " ", text)
        
        # 연속된 공백을 하나로
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()

    def _tokenize(self, text: str, lang: str, min_length: int = 2, max_length: int = 20) -> List[str]:
        """향상된 토큰화 및 불용어 제거"""
        if not text:
            return []
        
        tokens = text.split()
        # 길이 필터링
        tokens = [t for t in tokens if min_length <= len(t) <= max_length]
        # 불용어 제거
        tokens = [t for t in tokens if t not in self.stopwords.get(lang, set())]
        # 순수 숫자 토큰 제거
        tokens = [t for t in tokens if not t.isdigit()]
        # 반복 문자 필터링 (예: "ㅋㅋㅋ", "aaa")
        tokens = [t for t in tokens if not re.match(r'^(.)\1{2,}$', t)]
        
        return tokens

    def _generate_ngrams(self, tokens: List[str], n: int) -> List[str]:
        """N-gram 생성"""
        if len(tokens) < n:
            return []
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

    def _calculate_tfidf(self, term_freq: Dict[str, int], doc_count: int, term_doc_count: Dict[str, int]) -> Dict[str, float]:
        """TF-IDF 점수 계산"""
        tfidf_scores = {}
        total_terms = sum(term_freq.values())
        
        for term, tf in term_freq.items():
            # TF: 정규화된 용어 빈도
            tf_normalized = tf / total_terms
            # IDF: 역문서 빈도
            df = term_doc_count.get(term, 1)
            idf = log(doc_count / df)
            # TF-IDF
            tfidf_scores[term] = tf_normalized * idf
        
        return tfidf_scores

    # ───────── 파일 처리 ─────────
    def load_from_file(self, file_path: Union[str, Path]) -> str:
        """파일에서 텍스트 로드 (txt, json 지원)"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.logger.info(f"Loading text from {path.name}")
        
        try:
            if path.suffix.lower() == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # JSON에서 텍스트 필드 찾기
                if isinstance(data, dict):
                    text_fields = ['text', 'content', 'body', 'message', 'description']
                    for field in text_fields:
                        if field in data:
                            return str(data[field])
                    # 첫 번째 문자열 값 반환
                    for value in data.values():
                        if isinstance(value, str):
                            return value
                    raise ValueError("No text content found in JSON")
                elif isinstance(data, list):
                    return ' '.join(str(item) for item in data)
                else:
                    return str(data)
            else:
                # 기본적으로 텍스트 파일로 처리
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"Failed to load file {path}: {e}")
            raise

    def save_results(self, results: ExtractionResult, output_path: Union[str, Path], format: str = 'json') -> None:
        """결과를 파일로 저장"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Saving results to {path.name} in {format} format")
        
        if format.lower() == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(asdict(results), f, ensure_ascii=False, indent=2)
        elif format.lower() == 'csv':
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['keyword', 'score', 'method'])
                for keyword, score in results.keywords:
                    writer.writerow([keyword, score, results.method])
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'")

    # ───────── 핵심 추출 메서드 ─────────
    def extract_keywords(self, 
                        text: str, 
                        method: str = "frequency",
                        n_gram: int = 1,
                        top_k: int = 10, 
                        min_length: int = 2,
                        max_length: int = 20,
                        include_stats: bool = True) -> ExtractionResult:
        """통합 키워드 추출 메서드"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        if method not in ["frequency", "tfidf"]:
            raise ValueError("Method must be 'frequency' or 'tfidf'")
        if n_gram not in [1, 2, 3]:
            raise ValueError("n_gram must be 1, 2, or 3")
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        
        if not text.strip():
            return ExtractionResult([], {}, method, {})
        
        self.logger.info(f"Extracting keywords using method={method}, n_gram={n_gram}")
        
        # 텍스트 전처리
        lang = self._detect_lang(text)
        clean = self._clean_text(text)
        tokens = self._tokenize(clean, lang, min_length, max_length)
        
        if not tokens:
            return ExtractionResult([], {}, method, {})
        
        # N-gram 생성
        if n_gram == 1:
            ngrams = tokens
        else:
            ngrams = self._generate_ngrams(tokens, n_gram)
        
        # 키워드 추출
        if method == "frequency":
            counts = Counter(ngrams)
            keywords = counts.most_common(top_k)
        elif method == "tfidf":
            # 현재 문서를 corpus에 추가
            current_doc = set(ngrams)
            if text not in [doc for doc, _ in self.document_corpus]:
                self.document_corpus.append((text, current_doc))
            
            # TF-IDF 계산
            term_freq = Counter(ngrams)
            doc_count = len(self.document_corpus)
            term_doc_count = {}
            
            for _, doc_terms in self.document_corpus:
                for term in doc_terms:
                    term_doc_count[term] = term_doc_count.get(term, 0) + 1
            
            tfidf_scores = self._calculate_tfidf(term_freq, doc_count, term_doc_count)
            keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # 통계 정보
        stats = {}
        if include_stats:
            stats = self.get_stats(text)
            stats.update({
                "method": method,
                "n_gram": n_gram,
                "total_ngrams": len(ngrams),
                "unique_ngrams": len(set(ngrams))
            })
        
        parameters = {
            "method": method,
            "n_gram": n_gram,
            "top_k": top_k,
            "min_length": min_length,
            "max_length": max_length
        }
        
        return ExtractionResult(keywords, stats, method, parameters)

    def extract_unigrams(self, text: str, top_k: int = 10, min_length: int = 2) -> List[Tuple[str, int]]:
        """유니그램 키워드 추출 (하위 호환성)"""
        result = self.extract_keywords(text, "frequency", 1, top_k, min_length)
        return result.keywords

    def extract_bigrams(self, text: str, top_k: int = 10, min_length: int = 2) -> List[Tuple[str, int]]:
        """바이그램 키워드 추출"""
        result = self.extract_keywords(text, "frequency", 2, top_k, min_length)
        return result.keywords

    def extract_trigrams(self, text: str, top_k: int = 10, min_length: int = 2) -> List[Tuple[str, int]]:
        """트라이그램 키워드 추출"""
        result = self.extract_keywords(text, "frequency", 3, top_k, min_length)
        return result.keywords

    def extract_with_tfidf(self, text: str, n_gram: int = 1, top_k: int = 10) -> List[Tuple[str, float]]:
        """TF-IDF 기반 키워드 추출"""
        result = self.extract_keywords(text, "tfidf", n_gram, top_k)
        return result.keywords

    def batch_extract(self, 
                     texts: List[str], 
                     method: str = "frequency",
                     n_gram: int = 1,
                     top_k: int = 10) -> List[ExtractionResult]:
        """배치 처리로 여러 텍스트에서 키워드 추출"""
        self.logger.info(f"Processing {len(texts)} texts in batch")
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.extract_keywords(text, method, n_gram, top_k)
                results.append(result)
                self.logger.debug(f"Processed text {i+1}/{len(texts)}")
            except Exception as e:
                self.logger.error(f"Failed to process text {i+1}: {e}")
                results.append(ExtractionResult([], {}, method, {}))
        
        return results

    def filter_keywords(self, 
                       keywords: List[Tuple[str, Union[int, float]]], 
                       pattern: str = None,
                       min_score: Union[int, float] = None,
                       exclude_pattern: str = None) -> List[Tuple[str, Union[int, float]]]:
        """키워드 필터링"""
        filtered = keywords.copy()
        
        if min_score is not None:
            filtered = [(k, s) for k, s in filtered if s >= min_score]
        
        if pattern:
            regex = re.compile(pattern, re.IGNORECASE)
            filtered = [(k, s) for k, s in filtered if regex.search(k)]
        
        if exclude_pattern:
            exclude_regex = re.compile(exclude_pattern, re.IGNORECASE)
            filtered = [(k, s) for k, s in filtered if not exclude_regex.search(k)]
        
        return filtered

    def get_stats(self, text: str) -> Dict[str, Union[str, int, float]]:
        """상세한 텍스트 분석 통계"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        
        lang = self._detect_lang(text)
        clean = self._clean_text(text)
        tokens = self._tokenize(clean, lang)
        
        korean_chars = len(re.findall(r"[가-힣]", text))
        english_chars = len(re.findall(r"[a-zA-Z]", text))
        total_chars = len(re.sub(r"\s+", "", text))
        
        return {
            "detected_language": lang,
            "original_length": len(text),
            "cleaned_length": len(clean),
            "token_count": len(tokens),
            "unique_tokens": len(set(tokens)),
            "korean_char_ratio": round(korean_chars / total_chars if total_chars > 0 else 0, 3),
            "english_char_ratio": round(english_chars / total_chars if total_chars > 0 else 0, 3),
            "avg_token_length": round(sum(len(t) for t in tokens) / len(tokens) if tokens else 0, 2),
            "sentence_count": len(re.findall(r'[.!?]+', text)),
            "word_density": round(len(tokens) / len(text) if text else 0, 4)
        }

    def clear_corpus(self) -> None:
        """TF-IDF용 문서 corpus 초기화"""
        self.document_corpus.clear()
        self.logger.info("Document corpus cleared")


# ───────── 실행 예시 ─────────
if __name__ == "__main__":
    # 테스트용 텍스트
    text1 = "인공지능 기술은 빠르게 발전하고 있으며, 특히 생성형 AI가 주목받고 있다. 머신러닝과 딥러닝 기술의 발전으로 AI 시스템의 성능이 크게 향상되었다."
    text2 = "Machine learning and artificial intelligence are revolutionizing technology. Deep learning algorithms show remarkable performance improvements."
    
    print("=== 고급 키워드 추출기 데모 ===")
    ke = KeywordExtractor(enable_logging=True)
    
    print("\n1. 유니그램 추출 (빈도 기반)")
    result1 = ke.extract_keywords(text1, method="frequency", n_gram=1, top_k=5)
    print("Keywords:", result1.keywords)
    print("Stats:", {k:v for k,v in result1.stats.items() if k in ['token_count', 'unique_tokens', 'detected_language']})
    
    print("\n2. 바이그램 추출")
    result2 = ke.extract_keywords(text1, method="frequency", n_gram=2, top_k=5)
    print("Bigrams:", result2.keywords)
    
    print("\n3. TF-IDF 기반 추출 (여러 문서)")
    texts = [text1, text2]
    batch_results = ke.batch_extract(texts, method="tfidf", n_gram=1, top_k=5)
    for i, result in enumerate(batch_results):
        print(f"Document {i+1} TF-IDF:", result.keywords[:3])
    
    print("\n4. 키워드 필터링")
    filtered = ke.filter_keywords(result1.keywords, pattern=r'기술|ai', min_score=1)
    print("Filtered keywords:", filtered)
    
    print("\n5. 영어 텍스트 처리")
    result_en = ke.extract_keywords(text2, method="frequency", n_gram=1, top_k=5)
    print("English keywords:", result_en.keywords)
    
    print("\n6. 상세 통계")
    stats = ke.get_stats(text1)
    print("Detailed stats:", {k:v for k,v in stats.items() if k in ['sentence_count', 'avg_token_length', 'word_density']})
    
    # 결과 저장 예시 (실제 실행시에는 주석 해제)
    # ke.save_results(result1, "keywords_result.json", "json")
    # print("\n결과가 keywords_result.json에 저장되었습니다.")