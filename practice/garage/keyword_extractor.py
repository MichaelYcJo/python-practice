import re
import json
import csv
import logging
import requests
import threading
from collections import Counter, defaultdict
from typing import List, Tuple, Dict, Optional, Union, Set, Any, Callable
from functools import lru_cache, wraps
from pathlib import Path
from dataclasses import dataclass, asdict, field
from math import log, sqrt
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from itertools import combinations
import time
import weakref
import gc
from contextlib import contextmanager


@dataclass
class ExtractionResult:
    """키워드 추출 결과를 담는 데이터 클래스"""
    keywords: List[Tuple[str, Union[int, float]]]
    stats: Dict[str, Union[str, int, float]]
    method: str
    parameters: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0


@dataclass
class KeywordTrend:
    """키워드 트렌드 분석 결과"""
    keyword: str
    frequency_history: List[Tuple[datetime, int]]
    trend_score: float
    is_trending: bool


class MemoryManager:
    """메모리 사용량 최적화를 위한 관리자"""
    
    def __init__(self, max_cache_size: int = 1000):
        self.max_cache_size = max_cache_size
        self._cache_refs = weakref.WeakValueDictionary()
        self._access_times = {}
        self._lock = threading.Lock()
    
    @contextmanager
    def memory_cleanup(self):
        """메모리 정리를 위한 컨텍스트 매니저"""
        try:
            yield
        finally:
            self._cleanup_cache()
            gc.collect()
    
    def _cleanup_cache(self):
        """캐시 정리"""
        with self._lock:
            if len(self._cache_refs) > self.max_cache_size:
                # 가장 오래된 항목들 제거
                sorted_items = sorted(self._access_times.items(), key=lambda x: x[1])
                to_remove = len(self._cache_refs) - self.max_cache_size + 100
                
                for key, _ in sorted_items[:to_remove]:
                    if key in self._cache_refs:
                        del self._cache_refs[key]
                    if key in self._access_times:
                        del self._access_times[key]
    
    def get_or_create(self, key: str, factory: Callable):
        """캐시에서 가져오거나 새로 생성"""
        with self._lock:
            if key in self._cache_refs:
                self._access_times[key] = time.time()
                return self._cache_refs[key]
            
            value = factory()
            self._cache_refs[key] = value
            self._access_times[key] = time.time()
            return value


class RakeAlgorithm:
    """RAKE (Rapid Automatic Keyword Extraction) 구현"""
    
    def __init__(self, stopwords: Set[str], min_chars: int = 1, max_words: int = 3):
        self.stopwords = stopwords
        self.min_chars = min_chars
        self.max_words = max_words
    
    def _generate_candidate_keywords(self, sentences: List[str]) -> List[str]:
        """후보 키워드 생성"""
        phrase_list = []
        for sentence in sentences:
            words = sentence.split()
            phrase = []
            for word in words:
                word = word.strip().lower()
                if word in self.stopwords or len(word) < self.min_chars:
                    if phrase:
                        phrase_list.append(' '.join(phrase))
                        phrase = []
                else:
                    phrase.append(word)
            if phrase:
                phrase_list.append(' '.join(phrase))
        return phrase_list
    
    def _calculate_word_scores(self, phrase_list: List[str]) -> Dict[str, float]:
        """단어별 점수 계산"""
        word_frequency = defaultdict(int)
        word_degree = defaultdict(int)
        
        for phrase in phrase_list:
            words = phrase.split()
            if len(words) <= self.max_words:
                for word in words:
                    word_frequency[word] += 1
                    word_degree[word] += len(words) - 1
        
        word_scores = {}
        for word in word_frequency:
            word_scores[word] = (word_degree[word] + word_frequency[word]) / word_frequency[word]
        
        return word_scores
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """RAKE 알고리즘으로 키워드 추출"""
        sentences = re.split(r'[.!?;]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        phrase_list = self._generate_candidate_keywords(sentences)
        word_scores = self._calculate_word_scores(phrase_list)
        
        phrase_scores = {}
        for phrase in phrase_list:
            words = phrase.split()
            if len(words) <= self.max_words:
                phrase_scores[phrase] = sum(word_scores.get(word, 0) for word in words)
        
        return sorted(phrase_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]


class SemanticAnalyzer:
    """향상된 의미론적 분석기"""
    
    def __init__(self, vector_dim: int = 128):
        self.vector_dim = vector_dim
        self.word_vectors = {}
        self.similarity_cache = {}
        self.memory_manager = MemoryManager()
    
    def _enhanced_word_vector(self, word: str) -> List[float]:
        """향상된 단어 벡터 생성"""
        cache_key = f"vector_{word}_{self.vector_dim}"
        
        def create_vector():
            vector = [0.0] * self.vector_dim
            
            # 문자 기반 특성
            for i, char in enumerate(word.lower()):
                if i < self.vector_dim - 10:  # 마지막 10개는 다른 특성용
                    vector[i] = ord(char) / 255.0
            
            # 단어 길이 특성 (정규화)
            vector[-10] = min(len(word) / 20.0, 1.0)
            
            # 첫 글자와 마지막 글자 특성
            if len(word) > 0:
                vector[-9] = ord(word[0]) / 255.0
                vector[-8] = ord(word[-1]) / 255.0
            
            # 자음/모음 비율 (한국어)
            if re.search(r'[가-힣]', word):
                consonant_count = len(re.findall(r'[ㄱ-ㅎ]', word))
                vowel_count = len(re.findall(r'[ㅏ-ㅣ]', word))
                total = consonant_count + vowel_count
                if total > 0:
                    vector[-7] = consonant_count / total
                    vector[-6] = vowel_count / total
            
            # 영어 알파벳 비율
            alpha_count = len(re.findall(r'[a-zA-Z]', word))
            vector[-5] = alpha_count / len(word) if word else 0
            
            # 숫자 포함 여부
            vector[-4] = 1.0 if re.search(r'\d', word) else 0.0
            
            # 대문자 비율
            upper_count = len(re.findall(r'[A-Z]', word))
            vector[-3] = upper_count / len(word) if word else 0
            
            # 특수문자 포함 여부
            vector[-2] = 1.0 if re.search(r'[^a-zA-Z가-힣0-9]', word) else 0.0
            
            # 단어 복잡도 (고유 문자 수)
            vector[-1] = len(set(word.lower())) / len(word) if word else 0
            
            return vector
        
        return self.memory_manager.get_or_create(cache_key, create_vector)
    
    def calculate_similarity(self, word1: str, word2: str) -> float:
        """두 단어의 코사인 유사도 계산"""
        cache_key = tuple(sorted([word1, word2]))
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        vec1 = self._simple_word_vector(word1)
        vec2 = self._simple_word_vector(word2)
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sqrt(sum(a * a for a in vec1))
        magnitude2 = sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            similarity = 0.0
        else:
            similarity = dot_product / (magnitude1 * magnitude2)
        
        self.similarity_cache[cache_key] = similarity
        return similarity
    
    def cluster_keywords(self, keywords: List[str], threshold: float = 0.7) -> Dict[str, List[str]]:
        """키워드를 유사도 기반으로 클러스터링"""
        clusters = {}
        processed = set()
        
        for keyword in keywords:
            if keyword in processed:
                continue
            
            cluster_name = keyword
            cluster = [keyword]
            processed.add(keyword)
            
            for other_keyword in keywords:
                if other_keyword in processed:
                    continue
                
                similarity = self.calculate_similarity(keyword, other_keyword)
                if similarity >= threshold:
                    cluster.append(other_keyword)
                    processed.add(other_keyword)
            
            clusters[cluster_name] = cluster
        
        return clusters


class WebScraper:
    """웹 스크래핑 기능"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> str:
        """URL에서 텍스트 추출"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # HTML에서 텍스트 추출 (간단한 버전)
            text = re.sub(r'<[^>]+>', ' ', response.text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            raise Exception(f"Failed to scrape {url}: {e}")
    
    def scrape_multiple_urls(self, urls: List[str], max_workers: int = 5) -> Dict[str, str]:
        """여러 URL을 병렬로 스크래핑"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.scrape_url, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    text = future.result()
                    results[url] = text
                except Exception as e:
                    results[url] = f"Error: {e}"
        
        return results


def timing_decorator(func: Callable) -> Callable:
    """함수 실행 시간 측정 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # ExtractionResult인 경우 processing_time 설정
        if hasattr(result, 'processing_time'):
            result.processing_time = end_time - start_time
        
        return result
    return wrapper


class KeywordExtractor:
    """
    최첨단 키워드 추출기 (RAKE, 의미 분석, 웹 스크래핑, 트렌드 분석)
    """

    def __init__(self, 
                 lang: str = "auto", 
                 to_lower: bool = True,
                 stopwords_override: Optional[Union[Dict[str, Set[str]], Set[str]]] = None,
                 enable_logging: bool = False,
                 enable_semantic_analysis: bool = True,
                 domain_stopwords: Optional[Dict[str, Set[str]]] = None):
        if lang not in ("auto", "en", "ko"):
            raise ValueError(f"Unsupported language: {lang}. Supported: 'auto', 'en', 'ko'")
        
        self.lang = lang
        self.to_lower = to_lower
        self.stopwords = self._build_stopwords()
        self.document_corpus = []  # TF-IDF를 위한 문서 집합
        self.keyword_history = defaultdict(list)  # 트렌드 분석용
        
        # 고급 기능
        self.enable_semantic = enable_semantic_analysis
        self.semantic_analyzer = SemanticAnalyzer() if enable_semantic_analysis else None
        self.rake = None  # 나중에 초기화
        self.scraper = WebScraper()
        
        # 로깅 설정
        self.logger = self._setup_logging(enable_logging)
        
        # 도메인별 불용어 병합
        if domain_stopwords:
            self._merge_domain_stopwords(domain_stopwords)
        
        # 사용자 지정 불용어 병합
        if stopwords_override:
            self._merge_custom_stopwords(stopwords_override)
        
        # RAKE 초기화
        self._initialize_rake()
            
        self.logger.info(f"AdvancedKeywordExtractor initialized with lang={lang}")
    
    def _setup_logging(self, enable: bool) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO if enable else logging.WARNING)
        
        if enable and not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _merge_domain_stopwords(self, domain_stopwords: Dict[str, Set[str]]) -> None:
        """도메인별 불용어 병합"""
        for domain, words in domain_stopwords.items():
            self.logger.info(f"Adding {len(words)} stopwords for domain: {domain}")
            for lang in self.stopwords:
                self.stopwords[lang].update(words)
    
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

    def _initialize_rake(self) -> None:
        """RAKE 알고리즘 초기화"""
        all_stopwords = set()
        for stopword_set in self.stopwords.values():
            all_stopwords.update(stopword_set)
        self.rake = RakeAlgorithm(all_stopwords)

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
            "like", "one", "two", "first", "last", "new", "old", "good", "great", "big", "small",
            # 기술 도메인
            "system", "data", "user", "time", "way", "work", "use", "using", "used", "make",
            "create", "build", "develop", "software", "application", "program", "code", "file"
        }
        
        ko = {
            "그리고", "그러나", "하지만", "또한", "이", "가", "은", "는", "을", "를", "에", "에서",
            "으로", "로", "와", "과", "도", "만", "까지", "부터", "처럼", "같이", "위해", "때문에",
            "대해", "관해", "통해", "의해", "에게", "한테", "더", "가장", "매우", "너무", "정말",
            "아주", "꽤", "조금", "많이", "좀", "잘", "못", "안", "없다", "있다", "하다", "되다",
            "것", "수", "때", "곳", "말", "일", "사람", "경우", "때문", "사이", "다음", "이전",
            "그", "그녀", "그것", "여기", "저기", "어디", "언제", "누구", "무엇", "어떻게", "왜",
            "모든", "각", "몇", "많은", "적은", "크다", "작다", "좋다", "나쁘다", "새로운", "오래된",
            "첫번째", "마지막", "하나", "둘", "셋", "년", "월", "일", "시간", "분", "초", "오늘", "어제", "내일",
            # 기술 도메인 한국어
            "시스템", "데이터", "사용자", "방법", "사용", "개발", "프로그램", "코드", "파일", "서비스"
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

    def _clean_text(self, text: str, remove_numbers: bool = True, aggressive: bool = False) -> str:
        """향상된 텍스트 정제"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        
        text = text.strip()
        if not text:
            return ""
        
        if self.to_lower:
            text = text.lower()
        
        # 기본 정제
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"\S+@\S+\.\S+", " ", text)
        text = re.sub(r"#\S+|@\S+", " ", text)
        
        if aggressive:
            # 공격적 정제: 괄호, 인용부호 등 제거
            text = re.sub(r"\([^)]*\)|\[[^\]]*\]|\{[^}]*\}", " ", text)
            text = re.sub(r'"[^"]*"|\'[^\']*\'', " ", text)
            text = re.sub(r"[^\w가-힣\s-]", " ", text)
        else:
            # 기본 정제
            text = re.sub(r"[^0-9A-Za-z가-힣\s\-_]", " ", text)
        
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
        # 반복 문자 필터링
        tokens = [t for t in tokens if not re.match(r'^(.)\1{2,}$', t)]
        # 하이픈으로만 구성된 토큰 제거
        tokens = [t for t in tokens if not re.match(r'^-+$', t)]
        
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
            idf = log(doc_count / df) if df > 0 else 0
            # TF-IDF
            tfidf_scores[term] = tf_normalized * idf
        
        return tfidf_scores

    def _calculate_advanced_scores(self, keywords: List[Tuple[str, Union[int, float]]], 
                                 text: str) -> List[Tuple[str, float]]:
        """고급 점수 계산 (위치, 길이, 빈도 조합)"""
        advanced_scores = []
        text_length = len(text)
        
        for keyword, score in keywords:
            # 기본 점수 (빈도 또는 TF-IDF)
            base_score = float(score)
            
            # 위치 점수 (문서 앞부분에 있으면 가산점)
            first_occurrence = text.lower().find(keyword.lower())
            position_score = 1 - (first_occurrence / text_length) if first_occurrence != -1 else 0.5
            
            # 길이 점수 (너무 짧거나 길지 않은 키워드 선호)
            length_score = 1.0
            if len(keyword.split()) == 1:  # 단일 단어
                if 3 <= len(keyword) <= 8:
                    length_score = 1.2
                elif len(keyword) < 3:
                    length_score = 0.8
            else:  # 구문
                length_score = 1.1
            
            # 최종 점수 계산
            final_score = base_score * (0.7 * 1 + 0.2 * position_score + 0.1 * length_score)
            advanced_scores.append((keyword, final_score))
        
        return sorted(advanced_scores, key=lambda x: x[1], reverse=True)

    # ───────── 파일 처리 ─────────
    def load_from_file(self, file_path: Union[str, Path]) -> str:
        """파일에서 텍스트 로드 (txt, json, pdf 지원)"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.logger.info(f"Loading text from {path.name}")
        
        try:
            if path.suffix.lower() == '.pdf':
                return self._extract_pdf_text(path)
            elif path.suffix.lower() == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return self._extract_text_from_json(data)
            else:
                # 기본적으로 텍스트 파일로 처리
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"Failed to load file {path}: {e}")
            raise
    
    def _extract_pdf_text(self, path: Path) -> str:
        """PDF에서 텍스트 추출 (PyPDF2 없이 간단 구현)"""
        try:
            # PDF 처리를 위해서는 실제로 PyPDF2나 pdfplumber가 필요
            # 여기서는 간단한 플레이스홀더
            with open(path, 'rb') as f:
                content = f.read()
                # 실제 구현에서는 PDF 파싱 라이브러리 사용
                return "PDF content extraction requires additional libraries"
        except Exception as e:
            raise Exception(f"PDF processing failed: {e}")
    
    def _extract_text_from_json(self, data: Any) -> str:
        """JSON에서 텍스트 추출"""
        if isinstance(data, dict):
            text_fields = ['text', 'content', 'body', 'message', 'description', 'title']
            for field in text_fields:
                if field in data:
                    return str(data[field])
            # 모든 문자열 값 결합
            texts = []
            for value in data.values():
                if isinstance(value, str):
                    texts.append(value)
            return ' '.join(texts) if texts else str(data)
        elif isinstance(data, list):
            return ' '.join(str(item) for item in data)
        else:
            return str(data)

    def save_results(self, results: Union[ExtractionResult, List[ExtractionResult]], 
                    output_path: Union[str, Path], format: str = 'json') -> None:
        """결과를 파일로 저장"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Saving results to {path.name} in {format} format")
        
        if isinstance(results, list):
            data = [asdict(result) for result in results]
        else:
            data = asdict(results)
        
        if format.lower() == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        elif format.lower() == 'csv':
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if isinstance(results, list):
                    writer.writerow(['keyword', 'score', 'method', 'timestamp'])
                    for result in results:
                        for keyword, score in result.keywords:
                            writer.writerow([keyword, score, result.method, result.timestamp])
                else:
                    writer.writerow(['keyword', 'score', 'method'])
                    for keyword, score in results.keywords:
                        writer.writerow([keyword, score, results.method])
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'")

    # ───────── 핵심 추출 메서드 ─────────
    @timing_decorator
    def extract_keywords(self, 
                        text: str, 
                        method: str = "frequency",
                        n_gram: int = 1,
                        top_k: int = 10, 
                        min_length: int = 2,
                        max_length: int = 20,
                        include_stats: bool = True,
                        advanced_scoring: bool = False) -> ExtractionResult:
        """통합 키워드 추출 메서드"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        if method not in ["frequency", "tfidf", "rake"]:
            raise ValueError("Method must be 'frequency', 'tfidf', or 'rake'")
        if n_gram not in [1, 2, 3]:
            raise ValueError("n_gram must be 1, 2, or 3")
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        
        if not text.strip():
            return ExtractionResult([], {}, method, {})
        
        self.logger.info(f"Extracting keywords using method={method}, n_gram={n_gram}")
        
        # 키워드 추출
        if method == "rake":
            keywords = self.rake.extract_keywords(text, top_k)
        else:
            # 기존 방법들
            lang = self._detect_lang(text)
            clean = self._clean_text(text, aggressive=(method == "tfidf"))
            tokens = self._tokenize(clean, lang, min_length, max_length)
            
            if not tokens:
                return ExtractionResult([], {}, method, {})
            
            if n_gram == 1:
                ngrams = tokens
            else:
                ngrams = self._generate_ngrams(tokens, n_gram)
            
            if method == "frequency":
                counts = Counter(ngrams)
                keywords = counts.most_common(top_k)
            elif method == "tfidf":
                current_doc = set(ngrams)
                if text not in [doc for doc, _ in self.document_corpus]:
                    self.document_corpus.append((text, current_doc))
                
                term_freq = Counter(ngrams)
                doc_count = len(self.document_corpus)
                term_doc_count = {}
                
                for _, doc_terms in self.document_corpus:
                    for term in doc_terms:
                        term_doc_count[term] = term_doc_count.get(term, 0) + 1
                
                tfidf_scores = self._calculate_tfidf(term_freq, doc_count, term_doc_count)
                keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # 고급 점수 계산
        if advanced_scoring and method != "rake":
            keywords = self._calculate_advanced_scores(keywords, text)[:top_k]
        
        # 키워드 히스토리 업데이트 (트렌드 분석용)
        timestamp = datetime.now()
        for keyword, score in keywords:
            self.keyword_history[keyword].append((timestamp, score))
        
        # 통계 정보
        stats = {}
        if include_stats:
            stats = self.get_stats(text)
            if method != "rake":
                stats.update({
                    "method": method,
                    "n_gram": n_gram,
                    "total_ngrams": len(ngrams) if 'ngrams' in locals() else 0,
                    "unique_ngrams": len(set(ngrams)) if 'ngrams' in locals() else 0
                })
        
        parameters = {
            "method": method,
            "n_gram": n_gram,
            "top_k": top_k,
            "min_length": min_length,
            "max_length": max_length,
            "advanced_scoring": advanced_scoring
        }
        
        return ExtractionResult(keywords, stats, method, parameters)

    def extract_with_rake(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """RAKE 알고리즘으로 키워드 추출"""
        result = self.extract_keywords(text, "rake", top_k=top_k)
        return result.keywords

    def extract_with_clustering(self, text: str, top_k: int = 10, similarity_threshold: float = 0.7) -> Dict[str, List[str]]:
        """의미 기반 클러스터링으로 키워드 추출"""
        if not self.enable_semantic:
            raise ValueError("Semantic analysis is disabled")
        
        result = self.extract_keywords(text, "frequency", top_k=top_k * 2)
        keywords = [kw for kw, _ in result.keywords]
        
        return self.semantic_analyzer.cluster_keywords(keywords, similarity_threshold)

    def batch_extract_parallel(self, 
                             texts: List[str], 
                             method: str = "frequency",
                             n_gram: int = 1,
                             top_k: int = 10,
                             max_workers: int = 4) -> List[ExtractionResult]:
        """병렬 처리로 배치 키워드 추출"""
        self.logger.info(f"Processing {len(texts)} texts in parallel with {max_workers} workers")
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self.extract_keywords, text, method, n_gram, top_k): i 
                for i, text in enumerate(texts)
            }
            
            # 순서 보장을 위한 딕셔너리
            indexed_results = {}
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    indexed_results[index] = result
                except Exception as e:
                    self.logger.error(f"Failed to process text {index}: {e}")
                    indexed_results[index] = ExtractionResult([], {}, method, {})
            
            # 원래 순서대로 정렬
            results = [indexed_results[i] for i in range(len(texts))]
        
        return results

    def extract_from_web(self, urls: List[str], method: str = "frequency", top_k: int = 10) -> Dict[str, ExtractionResult]:
        """웹 페이지에서 키워드 추출"""
        self.logger.info(f"Extracting keywords from {len(urls)} web pages")
        
        # 웹 스크래핑
        scraped_data = self.scraper.scrape_multiple_urls(urls)
        
        # 키워드 추출
        results = {}
        for url, text in scraped_data.items():
            if text.startswith("Error:"):
                results[url] = ExtractionResult([], {}, method, {"error": text})
            else:
                try:
                    result = self.extract_keywords(text, method, top_k=top_k)
                    results[url] = result
                except Exception as e:
                    results[url] = ExtractionResult([], {}, method, {"error": str(e)})
        
        return results

    def analyze_trends(self, keyword: str, days: int = 30) -> KeywordTrend:
        """키워드 트렌드 분석"""
        if keyword not in self.keyword_history:
            return KeywordTrend(keyword, [], 0.0, False)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_history = [
            (timestamp, score) for timestamp, score in self.keyword_history[keyword]
            if timestamp >= cutoff_date
        ]
        
        if len(recent_history) < 2:
            return KeywordTrend(keyword, recent_history, 0.0, False)
        
        # 간단한 트렌드 점수 계산
        scores = [score for _, score in recent_history]
        if len(scores) >= 2:
            trend_score = (scores[-1] - scores[0]) / max(scores[0], 0.001)
        else:
            trend_score = 0.0
        
        is_trending = trend_score > 0.1  # 10% 이상 증가
        
        return KeywordTrend(keyword, recent_history, trend_score, is_trending)

    def get_stats(self, text: str) -> Dict[str, Union[str, int, float]]:
        """상세한 텍스트 분석 통계"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        
        lang = self._detect_lang(text)
        clean = self._clean_text(text)
        tokens = self._tokenize(clean, lang)
        
        korean_chars = len(re.findall(r"[가-힣]", text))
        english_chars = len(re.findall(r"[a-zA-Z]", text))
        number_chars = len(re.findall(r"[0-9]", text))
        total_chars = len(re.sub(r"\s+", "", text))
        
        # 문장 복잡도 분석
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        return {
            "detected_language": lang,
            "original_length": len(text),
            "cleaned_length": len(clean),
            "token_count": len(tokens),
            "unique_tokens": len(set(tokens)),
            "korean_char_ratio": round(korean_chars / total_chars if total_chars > 0 else 0, 3),
            "english_char_ratio": round(english_chars / total_chars if total_chars > 0 else 0, 3),
            "number_char_ratio": round(number_chars / total_chars if total_chars > 0 else 0, 3),
            "avg_token_length": round(sum(len(t) for t in tokens) / len(tokens) if tokens else 0, 2),
            "sentence_count": len(sentences),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "word_density": round(len(tokens) / len(text) if text else 0, 4),
            "lexical_diversity": round(len(set(tokens)) / len(tokens) if tokens else 0, 3)
        }

    def clear_corpus(self) -> None:
        """TF-IDF용 문서 corpus 초기화"""
        self.document_corpus.clear()
        self.logger.info("Document corpus cleared")

    def clear_history(self) -> None:
        """키워드 히스토리 초기화"""
        self.keyword_history.clear()
        self.logger.info("Keyword history cleared")


# ───────── 실행 예시 ─────────
if __name__ == "__main__":
    # 테스트용 텍스트
    text1 = """
    인공지능과 머신러닝 기술이 급속도로 발전하면서 우리 일상생활에 미치는 영향이 커지고 있다. 
    특히 자연어 처리, 컴퓨터 비전, 딥러닝 분야에서의 혁신이 두드러진다. 
    챗봇과 같은 대화형 AI 시스템은 고객 서비스를 혁신하고 있으며, 
    자율주행 자동차는 교통 시스템의 패러다임을 바꾸고 있다.
    """
    
    text2 = """
    Artificial intelligence and machine learning technologies are rapidly advancing, 
    significantly impacting our daily lives. Natural language processing, computer vision, 
    and deep learning innovations are particularly noteworthy. Conversational AI systems 
    like chatbots are revolutionizing customer service, while autonomous vehicles 
    are transforming transportation paradigms.
    """
    
    print("=== 최첨단 키워드 추출기 데모 ===")
    
    # 도메인별 불용어 설정
    tech_stopwords = {
        "technology": {"tech", "system", "data", "use", "way", "work"},
        "ai": {"ai", "artificial", "intelligence", "smart", "auto"}
    }
    
    ke = KeywordExtractor(
        enable_logging=True, 
        enable_semantic_analysis=True,
        domain_stopwords=tech_stopwords
    )
    
    print("\n1. RAKE 알고리즘")
    rake_result = ke.extract_with_rake(text1, top_k=5)
    print("RAKE Keywords:", rake_result)
    
    print("\n2. 고급 점수 계산")
    advanced_result = ke.extract_keywords(text1, method="frequency", top_k=5, advanced_scoring=True)
    print("Advanced scored keywords:", advanced_result.keywords)
    print(f"Processing time: {advanced_result.processing_time:.3f}s")
    
    print("\n3. 의미 기반 클러스터링")
    try:
        clusters = ke.extract_with_clustering(text1, top_k=8, similarity_threshold=0.6)
        print("Keyword clusters:")
        for cluster_name, cluster_words in clusters.items():
            print(f"  {cluster_name}: {cluster_words}")
    except Exception as e:
        print(f"Clustering error: {e}")
    
    print("\n4. 병렬 배치 처리")
    texts = [text1, text2]
    batch_results = ke.batch_extract_parallel(texts, method="tfidf", max_workers=2)
    for i, result in enumerate(batch_results):
        print(f"Batch result {i+1}: {result.keywords[:3]}")
    
    print("\n5. 트렌드 분석")
    # 몇 번 더 실행하여 히스토리 생성
    for _ in range(3):
        ke.extract_keywords(text1, method="frequency")
    
    trend = ke.analyze_trends("인공지능", days=30)
    print(f"Trend for '인공지능': score={trend.trend_score:.3f}, trending={trend.is_trending}")
    
    print("\n6. 상세 통계")
    stats = ke.get_stats(text1)
    important_stats = {k: v for k, v in stats.items() 
                      if k in ['lexical_diversity', 'avg_sentence_length', 'sentence_count']}
    print("Advanced stats:", important_stats)
    
    print("\n7. 웹 스크래핑 예시 (주석 처리됨)")
    # urls = ["https://example.com"]  # 실제 사용시 활성화
    # web_results = ke.extract_from_web(urls)
    # print("Web extraction results:", web_results)
    
    # 결과 저장 예시
    # ke.save_results(advanced_result, "advanced_keywords.json", "json")
    # print("\n결과가 advanced_keywords.json에 저장되었습니다.")